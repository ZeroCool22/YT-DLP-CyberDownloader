mod vtt;

use serde::{Deserialize, Serialize};
use std::{
    collections::HashMap,
    fs,
    io::{BufRead, BufReader, Read},
    path::{Path, PathBuf},
    process::{Child, Command, Stdio},
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc, Mutex,
    },
    thread,
    time::{Duration, SystemTime},
};
use tauri::{AppHandle, Emitter, Manager, State};

#[cfg(windows)]
use std::os::windows::process::CommandExt;

const CREATE_NO_WINDOW: u32 = 0x0800_0000;
const PROGRESS_PREFIX: &str = "__CYBER_PROGRESS__";

#[derive(Default)]
struct ProcessState {
    child: Mutex<Option<Child>>,
    cancelled: AtomicBool,
}

#[derive(Debug, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
struct DownloadRequest {
    url: String,
    destination: String,
    mode: String,
    use_cookies: bool,
    browser: String,
    browser_profile: String,
    proxy: String,
    subtitles: bool,
    subtitle_language: String,
    subtitle_format: String,
    clean_subtitles: bool,
}

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct ProgressEvent {
    percent: f64,
    speed: String,
    eta: String,
    filename: String,
}

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct FinishedEvent {
    success: bool,
    cancelled: bool,
    message: String,
    cookie_help_recommended: bool,
}

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct EngineUpdateFinishedEvent {
    success: bool,
    updated: Option<bool>,
    previous_version: Option<String>,
    version: Option<String>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct EngineInfo {
    available: bool,
    version: Option<String>,
    executable: Option<String>,
    ffmpeg_available: bool,
    js_runtime_available: bool,
    js_runtime: Option<String>,
}

fn hidden_command(program: &Path) -> Command {
    let mut command = Command::new(program);
    // yt-dlp's embedded Python otherwise inherits the Windows ANSI code page.
    // Its output is piped to Rust, so keeping it UTF-8 avoids broken pipes when
    // a title or status line contains characters outside ASCII/CP1252.
    command
        .env("PYTHONUTF8", "1")
        .env("PYTHONIOENCODING", "utf-8");
    #[cfg(windows)]
    command.creation_flags(CREATE_NO_WINDOW);
    command
}

fn for_each_output_line<R, F>(stream: R, mut callback: F)
where
    R: Read,
    F: FnMut(String),
{
    let mut reader = BufReader::new(stream);
    loop {
        let mut bytes = Vec::new();
        match reader.read_until(b'\n', &mut bytes) {
            Ok(0) | Err(_) => break,
            Ok(_) => {
                while bytes
                    .last()
                    .is_some_and(|byte| matches!(byte, b'\r' | b'\n'))
                {
                    bytes.pop();
                }
                callback(decode_process_output(&bytes));
            }
        }
    }
}

fn decode_process_output(bytes: &[u8]) -> String {
    if let Ok(utf8) = std::str::from_utf8(bytes) {
        return utf8.to_owned();
    }

    // The official Windows yt-dlp executable writes redirected output using
    // CP1252 even when PYTHONIOENCODING is set. Decode that code page instead
    // of displaying replacement glyphs such as `V�deos`.
    bytes
        .iter()
        .map(|byte| match byte {
            0x80 => '\u{20ac}',
            0x82 => '\u{201a}',
            0x83 => '\u{0192}',
            0x84 => '\u{201e}',
            0x85 => '\u{2026}',
            0x86 => '\u{2020}',
            0x87 => '\u{2021}',
            0x88 => '\u{02c6}',
            0x89 => '\u{2030}',
            0x8a => '\u{0160}',
            0x8b => '\u{2039}',
            0x8c => '\u{0152}',
            0x8e => '\u{017d}',
            0x91 => '\u{2018}',
            0x92 => '\u{2019}',
            0x93 => '\u{201c}',
            0x94 => '\u{201d}',
            0x95 => '\u{2022}',
            0x96 => '\u{2013}',
            0x97 => '\u{2014}',
            0x98 => '\u{02dc}',
            0x99 => '\u{2122}',
            0x9a => '\u{0161}',
            0x9b => '\u{203a}',
            0x9c => '\u{0153}',
            0x9e => '\u{017e}',
            0x9f => '\u{0178}',
            0x81 | 0x8d | 0x8f | 0x90 | 0x9d => '\u{fffd}',
            value => char::from(*value),
        })
        .collect()
}

fn tool_directories(app: &AppHandle) -> Vec<PathBuf> {
    let mut directories = Vec::new();
    if let Ok(resource) = app.path().resource_dir() {
        directories.push(resource.join("tools"));
        directories.push(resource);
    }
    if let Ok(executable) = std::env::current_exe() {
        if let Some(parent) = executable.parent() {
            directories.push(parent.join("tools"));
            directories.push(parent.to_owned());
        }
    }
    if let Ok(current) = std::env::current_dir() {
        directories.push(current.join("tools"));
    }
    directories.push(
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("tools"),
    );
    directories
}

fn locate_tool(app: &AppHandle, names: &[&str], probe_argument: &str) -> Option<PathBuf> {
    for directory in tool_directories(app) {
        for name in names {
            let candidate = directory.join(name);
            if candidate.is_file() {
                return Some(candidate);
            }
        }
    }
    for name in names {
        let candidate = PathBuf::from(name);
        if hidden_command(&candidate)
            .arg(probe_argument)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .is_ok_and(|status| status.success())
        {
            return Some(candidate);
        }
    }
    None
}

fn locate_ytdlp(app: &AppHandle) -> Option<PathBuf> {
    locate_tool(app, &["yt-dlp.exe", "yt-dlp"], "--version")
}

fn locate_ffmpeg(app: &AppHandle) -> Option<PathBuf> {
    locate_tool(app, &["ffmpeg.exe", "ffmpeg"], "-version")
}

fn executable_version(path: &Path) -> Option<String> {
    hidden_command(path)
        .arg("--version")
        .output()
        .ok()
        .filter(|output| output.status.success())
        .map(|output| String::from_utf8_lossy(&output.stdout).trim().to_owned())
        .filter(|version| !version.is_empty())
}

fn update_changed(
    success: bool,
    previous_version: Option<&str>,
    version: Option<&str>,
) -> Option<bool> {
    if !success {
        return None;
    }
    match (previous_version, version) {
        (Some(before), Some(after)) => Some(before != after),
        _ => None,
    }
}

fn node_is_supported(path: &Path) -> bool {
    hidden_command(path)
        .arg("--version")
        .output()
        .ok()
        .filter(|output| output.status.success())
        .and_then(|output| {
            String::from_utf8_lossy(&output.stdout)
                .trim()
                .trim_start_matches('v')
                .split('.')
                .next()
                .and_then(|major| major.parse::<u32>().ok())
        })
        .is_some_and(|major| major >= 22)
}

fn locate_node(app: &AppHandle) -> Option<PathBuf> {
    let mut candidates = Vec::new();
    if let Some(program_files) = std::env::var_os("ProgramFiles") {
        candidates.push(PathBuf::from(program_files).join("nodejs").join("node.exe"));
    }
    if let Some(path) = locate_tool(app, &["node.exe", "node"], "--version") {
        candidates.push(path);
    }
    candidates.into_iter().find(|path| node_is_supported(path))
}

fn emit_log(app: &AppHandle, line: impl Into<String>) {
    let _ = app.emit("download-log", line.into());
}

fn kill_process_tree(child: &mut Child) -> std::io::Result<()> {
    #[cfg(windows)]
    {
        let process_id = child.id().to_string();
        let status = hidden_command(Path::new("taskkill.exe"))
            .args(["/PID", &process_id, "/T", "/F"])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status();
        if status.is_ok_and(|status| status.success()) {
            return Ok(());
        }
    }
    child.kill()
}

fn snapshot_vtt(directory: &Path) -> HashMap<PathBuf, Option<SystemTime>> {
    let mut snapshot = HashMap::new();
    let Ok(entries) = fs::read_dir(directory) else {
        return snapshot;
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if path
            .extension()
            .is_some_and(|ext| ext.eq_ignore_ascii_case("vtt"))
        {
            snapshot.insert(
                path,
                entry
                    .metadata()
                    .ok()
                    .and_then(|metadata| metadata.modified().ok()),
            );
        }
    }
    snapshot
}

fn changed_vtt(directory: &Path, before: &HashMap<PathBuf, Option<SystemTime>>) -> Vec<PathBuf> {
    snapshot_vtt(directory)
        .into_iter()
        .filter_map(|(path, modified)| (before.get(&path) != Some(&modified)).then_some(path))
        .collect()
}

fn postprocess_subtitles(
    app: &AppHandle,
    request: &DownloadRequest,
    before: &HashMap<PathBuf, Option<SystemTime>>,
) {
    if !request.subtitles {
        return;
    }
    let files = changed_vtt(Path::new(&request.destination), before);
    for path in &files {
        if request.clean_subtitles {
            match fs::read_to_string(path) {
                Ok(original) => {
                    let (cleaned, removed) = vtt::clean_youtube_vtt(&original);
                    if cleaned != original {
                        match fs::write(path, cleaned) {
                            Ok(()) => emit_log(app, format!("[SISTEMA] Subtítulos limpiados: {} bloque(s) repetido(s) eliminado(s) en {}", removed, path.file_name().unwrap_or_default().to_string_lossy())),
                            Err(error) => emit_log(app, format!("[WARNING] No se pudo limpiar {}: {error}", path.display())),
                        }
                    }
                }
                Err(error) => emit_log(
                    app,
                    format!("[WARNING] No se pudo leer {}: {error}", path.display()),
                ),
            }
        }
        if request.subtitle_format == "srt" {
            let Some(ffmpeg) = locate_ffmpeg(app) else {
                emit_log(
                    app,
                    "[ERROR] No se encontró FFmpeg para convertir subtítulos a SRT.",
                );
                continue;
            };
            let output = path.with_extension("srt");
            let result = hidden_command(&ffmpeg)
                .args(["-y", "-loglevel", "error", "-i"])
                .arg(path)
                .arg(&output)
                .status();
            match result {
                Ok(status) if status.success() => {
                    if let Err(error) = fs::remove_file(path) {
                        emit_log(app, format!("[WARNING] Se creó SRT pero no se pudo quitar el VTT temporal: {error}"));
                    }
                    emit_log(
                        app,
                        format!("[SISTEMA] Subtítulo convertido a SRT: {}", output.display()),
                    );
                }
                Ok(status) => emit_log(
                    app,
                    format!(
                        "[ERROR] FFmpeg no pudo convertir {} (código {status}).",
                        path.display()
                    ),
                ),
                Err(error) => emit_log(app, format!("[ERROR] No se pudo invocar FFmpeg: {error}")),
            }
        }
    }
}

fn progress_from_line(line: &str) -> Option<ProgressEvent> {
    let payload = line.strip_prefix(PROGRESS_PREFIX)?;
    let fields: Vec<&str> = payload.splitn(4, '|').collect();
    if fields.len() != 4 {
        return None;
    }
    let percent = fields[0]
        .trim()
        .trim_end_matches('%')
        .trim()
        .parse()
        .unwrap_or(0.0);
    let filename = Path::new(fields[3].trim())
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    Some(ProgressEvent {
        percent,
        speed: fields[1].trim().to_owned(),
        eta: fields[2].trim().to_owned(),
        filename,
    })
}

fn build_arguments(
    request: &DownloadRequest,
    ffmpeg: Option<&Path>,
    node: Option<&Path>,
) -> Vec<String> {
    let format = match request.mode.as_str() {
        "audio_mp3" => "bestaudio/best",
        "video_1080p" => "bestvideo[height<=1080]+bestaudio/best",
        "video_720p" => "bestvideo[height<=720]+bestaudio/best",
        _ => "bestvideo+bestaudio/best",
    };
    let output = Path::new(&request.destination)
        .join("%(title)s.%(ext)s")
        .to_string_lossy()
        .into_owned();
    let mut arguments = vec![
        "--newline".into(), "--no-color".into(), "--progress".into(),
        "--progress-template".into(), format!("download:{PROGRESS_PREFIX}%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s|%(info.filename)s"),
        "--no-continue".into(), "--merge-output-format".into(), "mp4".into(),
        "--remote-components".into(), "ejs:github".into(),
        "--format".into(), format.into(), "--output".into(), output,
    ];
    if request.mode == "audio_mp3" {
        arguments.extend([
            "--extract-audio".into(),
            "--audio-format".into(),
            "mp3".into(),
            "--audio-quality".into(),
            "320K".into(),
        ]);
    }
    if let Some(path) = ffmpeg {
        arguments.extend([
            "--ffmpeg-location".into(),
            path.parent().unwrap_or(path).to_string_lossy().into_owned(),
        ]);
    }
    if let Some(path) = node {
        arguments.extend([
            "--js-runtimes".into(),
            format!("node:{}", path.to_string_lossy()),
        ]);
    }
    if request.use_cookies {
        let browser = if request.browser_profile.trim().is_empty() {
            request.browser.clone()
        } else {
            format!("{}:{}", request.browser, request.browser_profile.trim())
        };
        arguments.extend(["--cookies-from-browser".into(), browser]);
    }
    if !request.proxy.is_empty() {
        arguments.extend(["--proxy".into(), request.proxy.clone()]);
    }
    if request.subtitles {
        let language = match request.subtitle_language.as_str() {
            "en" => "en(?:-.*)?",
            "pt" => "pt(?:-.*)?",
            _ => "es(?:-.*)?",
        };
        arguments.extend([
            "--write-subs".into(),
            "--write-auto-subs".into(),
            "--sub-langs".into(),
            language.into(),
            "--sub-format".into(),
            "vtt/best".into(),
        ]);
    }
    arguments.push(request.url.clone());
    arguments
}

#[tauri::command]
fn default_download_dir() -> String {
    std::env::var_os("USERPROFILE")
        .map(PathBuf::from)
        .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")))
        .join("Downloads")
        .to_string_lossy()
        .into_owned()
}

fn recommends_cookie_help(line: &str) -> bool {
    let normalized = line.to_ascii_lowercase();
    normalized.contains("http error 429")
        || normalized.contains("too many requests")
        || normalized.contains("http error 403")
        || normalized.contains("403: forbidden")
}

#[tauri::command]
fn open_github() -> Result<(), String> {
    hidden_command(Path::new("explorer.exe"))
        .arg("https://github.com/ZeroCool22")
        .spawn()
        .map(|_| ())
        .map_err(|error| format!("No se pudo abrir GitHub: {error}"))
}

#[tauri::command]
fn engine_info(app: AppHandle) -> EngineInfo {
    let engine = locate_ytdlp(&app);
    let node = locate_node(&app);
    let version = engine.as_deref().and_then(executable_version);
    EngineInfo {
        available: engine.is_some(),
        executable: engine
            .as_ref()
            .map(|path| path.to_string_lossy().into_owned()),
        version,
        ffmpeg_available: locate_ffmpeg(&app).is_some(),
        js_runtime_available: node.is_some(),
        js_runtime: node.map(|path| path.to_string_lossy().into_owned()),
    }
}

#[tauri::command]
fn start_download(
    app: AppHandle,
    state: State<ProcessState>,
    request: DownloadRequest,
) -> Result<(), String> {
    let url = request.url.trim();
    if !(url.starts_with("https://") || url.starts_with("http://")) {
        return Err("La URL debe comenzar con http:// o https://".into());
    }
    if request.use_cookies
        && !matches!(
            request.browser.as_str(),
            "brave" | "chrome" | "chromium" | "edge" | "firefox" | "opera" | "vivaldi" | "whale"
        )
    {
        return Err("El navegador seleccionado no es compatible con yt-dlp.".into());
    }
    let destination = PathBuf::from(request.destination.trim());
    fs::create_dir_all(&destination)
        .map_err(|error| format!("No se pudo crear la carpeta de destino: {error}"))?;
    let engine =
        locate_ytdlp(&app).ok_or("No se encontró yt-dlp. Copiá yt-dlp.exe dentro de tools.")?;
    let ffmpeg = locate_ffmpeg(&app);
    let node = locate_node(&app);
    if request.mode == "audio_mp3" && ffmpeg.is_none() {
        return Err("El modo MP3 requiere ffmpeg.exe dentro de tools.".into());
    }

    let mut active = state
        .child
        .lock()
        .map_err(|_| "No se pudo acceder al estado del proceso")?;
    if active
        .as_mut()
        .is_some_and(|child| child.try_wait().ok().flatten().is_none())
    {
        return Err("Ya hay una descarga activa.".into());
    }
    *active = None;
    state.cancelled.store(false, Ordering::SeqCst);
    let snapshot = snapshot_vtt(&destination);
    if request.url.to_lowercase().contains("youtube.com") && node.is_none() {
        return Err(
            "YouTube requiere Node.js 22 o superior para resolver sus desafíos JavaScript.".into(),
        );
    }
    let args = build_arguments(&request, ffmpeg.as_deref(), node.as_deref());
    emit_log(
        &app,
        format!("[SISTEMA] Iniciando descarga de: {}", request.url),
    );
    emit_log(
        &app,
        format!("[SISTEMA] Carpeta de destino: {}", destination.display()),
    );
    emit_log(&app, format!("[SISTEMA] Modo: {}", request.mode));
    if let Some(path) = &ffmpeg {
        emit_log(
            &app,
            format!("[SISTEMA] Usando FFmpeg desde: {}", path.display()),
        );
    }
    if let Some(path) = &node {
        emit_log(
            &app,
            format!(
                "[SISTEMA] Usando runtime JavaScript Node desde: {}",
                path.display()
            ),
        );
    }
    if request.url.to_lowercase().contains("instagram.com") {
        emit_log(
            &app,
            "[SISTEMA] ¡Enlace de Instagram detectado! Iniciando extracción…",
        );
    }
    if request.url.to_lowercase().contains("twitch.tv") {
        emit_log(
            &app,
            "[SISTEMA] ¡Enlace de Twitch detectado! Iniciando extracción…",
        );
    }
    if request.url.to_lowercase().contains("tiktok.com") {
        emit_log(
            &app,
            "[SISTEMA] ¡Enlace de TikTok detectado! Iniciando extracción…",
        );
    }

    let mut child = hidden_command(&engine)
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|error| format!("No se pudo iniciar yt-dlp: {error}"))?;
    let stdout = child.stdout.take();
    let stderr = child.stderr.take();
    *active = Some(child);
    drop(active);

    let cookie_help_recommended = Arc::new(AtomicBool::new(false));
    let stdout_cookie_help = Arc::clone(&cookie_help_recommended);
    let stdout_app = app.clone();
    let stdout_thread = thread::spawn(move || {
        if let Some(stream) = stdout {
            for_each_output_line(stream, |line| {
                if recommends_cookie_help(&line) {
                    stdout_cookie_help.store(true, Ordering::SeqCst);
                }
                if let Some(progress) = progress_from_line(&line) {
                    let _ = stdout_app.emit("download-progress", progress);
                } else if !line.trim().is_empty() {
                    emit_log(&stdout_app, format!("[INFO] {line}"));
                }
            });
        }
    });
    let stderr_cookie_help = Arc::clone(&cookie_help_recommended);
    let stderr_app = app.clone();
    let stderr_thread = thread::spawn(move || {
        if let Some(stream) = stderr {
            for_each_output_line(stream, |line| {
                if !line.trim().is_empty() {
                    if recommends_cookie_help(&line) {
                        stderr_cookie_help.store(true, Ordering::SeqCst);
                    }
                    emit_log(&stderr_app, format!("[YT-DLP] {line}"));
                }
            });
        }
    });

    thread::spawn(move || {
        let status = loop {
            let result = app
                .state::<ProcessState>()
                .child
                .lock()
                .ok()
                .and_then(|mut slot| {
                    slot.as_mut()
                        .and_then(|child| child.try_wait().ok().flatten())
                });
            if let Some(status) = result {
                break status;
            }
            thread::sleep(Duration::from_millis(100));
        };
        let _ = stdout_thread.join();
        let _ = stderr_thread.join();
        let cancelled = app.state::<ProcessState>().cancelled.load(Ordering::SeqCst);
        let cookie_help_recommended = cookie_help_recommended.load(Ordering::SeqCst);
        let success = status.success() && !cancelled;
        if success {
            postprocess_subtitles(&app, &request, &snapshot);
            emit_log(&app, "[SISTEMA] ¡Descarga completada con éxito!");
        } else if cancelled {
            emit_log(&app, "[SISTEMA] Descarga cancelada por el usuario.");
        } else {
            emit_log(&app, format!("[ERROR] yt-dlp finalizó con {status}."));
        }
        if let Ok(mut slot) = app.state::<ProcessState>().child.lock() {
            *slot = None;
        }
        let message = if success {
            "Descarga completada exitosamente.".into()
        } else if cancelled {
            "Descarga cancelada por el usuario.".into()
        } else {
            format!("yt-dlp finalizó con {status}.")
        };
        let _ = app.emit(
            "download-finished",
            FinishedEvent {
                success,
                cancelled,
                message,
                cookie_help_recommended,
            },
        );
    });
    Ok(())
}

#[tauri::command]
fn cancel_download(app: AppHandle, state: State<ProcessState>) -> Result<(), String> {
    state.cancelled.store(true, Ordering::SeqCst);
    emit_log(&app, "[SISTEMA] Solicitando cancelación…");
    let mut slot = state
        .child
        .lock()
        .map_err(|_| "No se pudo acceder al proceso")?;
    let child = slot.as_mut().ok_or("No hay una descarga activa.")?;
    kill_process_tree(child).map_err(|error| format!("No se pudo cancelar la descarga: {error}"))
}

#[tauri::command]
fn update_ytdlp(app: AppHandle, state: State<ProcessState>) -> Result<(), String> {
    let engine = locate_ytdlp(&app).ok_or("No se encontró yt-dlp.")?;
    let previous_version = executable_version(&engine);
    let mut slot = state
        .child
        .lock()
        .map_err(|_| "No se pudo acceder al estado del proceso")?;
    if slot
        .as_mut()
        .is_some_and(|child| child.try_wait().ok().flatten().is_none())
    {
        return Err("Hay otra operación activa.".into());
    }
    emit_log(&app, "[SISTEMA] Buscando actualizaciones para yt-dlp…");
    let mut child = hidden_command(&engine)
        .arg("-U")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|error| format!("No se pudo iniciar la actualización: {error}"))?;
    let stdout = child.stdout.take();
    let stderr = child.stderr.take();
    *slot = Some(child);
    drop(slot);
    thread::spawn(move || {
        if let Some(stream) = stdout {
            for_each_output_line(stream, |line| {
                emit_log(&app, format!("[UPDATE] {line}"));
            });
        }
        if let Some(stream) = stderr {
            for_each_output_line(stream, |line| {
                emit_log(&app, format!("[UPDATE] {line}"));
            });
        }
        let status = app
            .state::<ProcessState>()
            .child
            .lock()
            .ok()
            .and_then(|mut child| child.as_mut().and_then(|child| child.wait().ok()));
        if let Ok(mut child) = app.state::<ProcessState>().child.lock() {
            *child = None;
        }
        let success = status.is_some_and(|status| status.success());
        let version = executable_version(&engine);
        let updated = update_changed(success, previous_version.as_deref(), version.as_deref());
        let _ = app.emit(
            "engine-update-finished",
            EngineUpdateFinishedEvent {
                success,
                updated,
                previous_version,
                version,
            },
        );
    });
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let application = tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .manage(ProcessState::default())
        .invoke_handler(tauri::generate_handler![
            default_download_dir,
            open_github,
            engine_info,
            start_download,
            cancel_download,
            update_ytdlp
        ])
        .build(tauri::generate_context!())
        .expect("error while building CyberDownloader");
    application.run(|app, event| {
        if matches!(event, tauri::RunEvent::ExitRequested { .. }) {
            if let Ok(mut slot) = app.state::<ProcessState>().child.lock() {
                if let Some(child) = slot.as_mut() {
                    let _ = kill_process_tree(child);
                }
            }
        }
    });
}

#[cfg(test)]
mod tests {
    use super::{
        build_arguments, for_each_output_line, recommends_cookie_help, update_changed,
        DownloadRequest,
    };
    use std::path::Path;

    fn video_request() -> DownloadRequest {
        DownloadRequest {
            url: "https://www.youtube.com/watch?v=test".into(),
            destination: "D:\\Videos".into(),
            mode: "video_best".into(),
            use_cookies: false,
            browser: "firefox".into(),
            browser_profile: String::new(),
            proxy: String::new(),
            subtitles: false,
            subtitle_language: "es".into(),
            subtitle_format: "vtt".into(),
            clean_subtitles: true,
        }
    }

    #[test]
    fn recognizes_errors_that_may_be_solved_with_cookies() {
        assert!(recommends_cookie_help("HTTP Error 429: Too Many Requests"));
        assert!(recommends_cookie_help("ERROR: TOO MANY REQUESTS"));
        assert!(recommends_cookie_help("HTTP Error 403: Forbidden"));
        assert!(recommends_cookie_help("403: FORBIDDEN"));
        assert!(!recommends_cookie_help("HTTP Error 404: Not Found"));
    }

    #[test]
    fn distinguishes_updates_from_an_already_current_engine() {
        assert_eq!(
            update_changed(true, Some("2026.07.01"), Some("2026.07.20")),
            Some(true)
        );
        assert_eq!(
            update_changed(true, Some("2026.07.20"), Some("2026.07.20")),
            Some(false)
        );
        assert_eq!(
            update_changed(false, Some("2026.07.20"), Some("2026.07.20")),
            None
        );
        assert_eq!(update_changed(true, None, Some("2026.07.20")), None);
    }

    #[test]
    fn enables_node_runtime_with_explicit_path() {
        let node = Path::new(r"C:\Program Files\nodejs\node.exe");
        let arguments = build_arguments(&video_request(), None, Some(node));
        let runtime_index = arguments
            .iter()
            .position(|argument| argument == "--js-runtimes")
            .expect("JavaScript runtime argument must be present");
        assert_eq!(
            arguments[runtime_index + 1],
            r"node:C:\Program Files\nodejs\node.exe"
        );
        assert!(arguments
            .windows(2)
            .any(|pair| { pair == ["--remote-components", "ejs:github"] }));
    }

    #[test]
    fn passes_browser_and_optional_profile_to_ytdlp() {
        let mut request = video_request();
        request.use_cookies = true;
        request.browser = "brave".into();
        request.browser_profile = "Profile 2".into();
        let arguments = build_arguments(&request, None, None);
        assert!(arguments
            .windows(2)
            .any(|pair| pair == ["--cookies-from-browser", "brave:Profile 2"]));
    }

    #[test]
    fn legacy_encoded_output_does_not_close_the_reader() {
        let input = b"t\xedtulo cp1252\nnext line\n";
        let mut lines = Vec::new();
        for_each_output_line(&input[..], |line| lines.push(line));
        assert_eq!(lines.len(), 2);
        assert_eq!(lines[0], "título cp1252");
        assert_eq!(lines[1], "next line");
    }
}
