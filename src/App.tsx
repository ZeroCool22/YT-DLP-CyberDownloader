import { useEffect, useMemo, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { open } from "@tauri-apps/plugin-dialog";
import { copy, storageLocationLabel } from "./i18n";
import { DownloadIcon, FolderIcon, GlobeIcon, PasteIcon, RefreshIcon, SettingsIcon, StopIcon } from "./icons";
import type {
  Browser,
  DownloadMode,
  DownloadRequest,
  EngineInfo,
  EngineUpdateFinishedEvent,
  FinishedEvent,
  Language,
  ProgressEvent,
  SubtitleFormat,
  SubtitleLanguage,
} from "./types";

type Tab = "download" | "settings";
type Notice = { title: string; message: string; kind: "info" | "error" } | null;

const initialProgress: ProgressEvent = { percent: 0, speed: "0 B/s", eta: "--:--", filename: "" };

function logTokenClass(token: string) {
  const key = token.slice(1, -1).trim().toUpperCase();
  if (key === "SISTEMA" || key === "SYSTEM") return "log-system";
  if (key === "INFO") return "log-info";
  if (key === "DEBUG") return "log-debug";
  if (key === "WARNING" || key === "WARN") return "log-warning";
  if (key === "ERROR") return "log-error";
  if (key === "YT-DLP" || key === "DOWNLOAD" || key === "MERGER") return "log-engine";
  if (key === "UPDATE" || key === "PIP") return "log-update";
  if (key === "YOUTUBE") return "log-youtube";
  return "log-source";
}

function ConsoleLine({ line }: { line: string }) {
  return <>{line.split(/(\[[^\]\r\n]+\])/g).map((part, index) =>
    part.startsWith("[") && part.endsWith("]")
      ? <span className={`log-prefix ${logTokenClass(part)}`} key={`${index}-${part}`}>{part}</span>
      : part,
  )}</>;
}

function isTextContextMenuTarget(target: EventTarget | null) {
  if (!(target instanceof Element)) return false;
  const editable = target.closest("input, textarea, [contenteditable='true']");
  if (!editable) return false;
  if (!(editable instanceof HTMLInputElement)) return true;
  return ["text", "search", "url", "email", "tel", "password", "number"].includes(editable.type);
}

export default function App() {
  const [language, setLanguage] = useState<Language>("es");
  const [tab, setTab] = useState<Tab>("download");
  const [url, setUrl] = useState("");
  const [destination, setDestination] = useState("");
  const [mode, setMode] = useState<DownloadMode>("video_best");
  const [subtitles, setSubtitles] = useState(false);
  const [subtitleLanguage, setSubtitleLanguage] = useState<SubtitleLanguage>("es");
  const [subtitleFormat, setSubtitleFormat] = useState<SubtitleFormat>("vtt");
  const [cleanSubtitles, setCleanSubtitles] = useState(true);
  const [useCookies, setUseCookies] = useState(false);
  const [browser, setBrowser] = useState<Browser>("chrome");
  const [browserProfile, setBrowserProfile] = useState("");
  const [proxy, setProxy] = useState("");
  const [running, setRunning] = useState(false);
  const [stopping, setStopping] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [progress, setProgress] = useState(initialProgress);
  const [logs, setLogs] = useState<string[]>([]);
  const [notice, setNotice] = useState<Notice>(null);
  const [engine, setEngine] = useState<EngineInfo>({ available: false, version: null, executable: null, ffmpegAvailable: false, jsRuntimeAvailable: false, jsRuntime: null });
  const consoleRef = useRef<HTMLDivElement>(null);
  const languageRef = useRef<Language>(language);
  const t = copy[language];

  const appendLog = (line: string) => setLogs((current) => [...current.slice(-499), line]);

  const refreshEngine = async () => {
    try {
      setEngine(await invoke<EngineInfo>("engine_info"));
    } catch {
      setEngine({ available: false, version: null, executable: null, ffmpegAvailable: false, jsRuntimeAvailable: false, jsRuntime: null });
    }
  };

  useEffect(() => {
    languageRef.current = language;
  }, [language]);

  useEffect(() => {
    const restrictContextMenu = (event: MouseEvent) => {
      if (!isTextContextMenuTarget(event.target)) event.preventDefault();
    };
    document.addEventListener("contextmenu", restrictContextMenu);
    return () => document.removeEventListener("contextmenu", restrictContextMenu);
  }, []);

  useEffect(() => {
    void invoke<string>("default_download_dir").then(setDestination).catch(() => undefined);
    void refreshEngine();
    const subscriptions = Promise.all([
      listen<string>("download-log", ({ payload }) => appendLog(payload)),
      listen<ProgressEvent>("download-progress", ({ payload }) => setProgress(payload)),
      listen<FinishedEvent>("download-finished", ({ payload }) => {
        const activeCopy = copy[languageRef.current];
        setRunning(false);
        setStopping(false);
        if (payload.success) {
          setProgress((current) => ({ ...current, percent: 100, speed: "0 B/s", eta: "00:00" }));
          setNotice({ title: activeCopy.info, message: activeCopy.success, kind: "info" });
        } else if (!payload.cancelled) {
          if (payload.cookieHelpRecommended) {
            appendLog(`[${languageRef.current === "es" ? "SISTEMA" : "SYSTEM"}] ${activeCopy.cookieErrorHelp}`);
          }
          setNotice({ title: activeCopy.error, message: payload.cookieHelpRecommended ? activeCopy.cookieErrorHelp : payload.message, kind: "error" });
        }
      }),
      listen<EngineUpdateFinishedEvent>("engine-update-finished", ({ payload }) => {
        const activeCopy = copy[languageRef.current];
        setUpdating(false);
        void refreshEngine();
        const version = payload.version ?? activeCopy.unknownVersion;
        const successMessage = payload.updated === true
          ? `${activeCopy.updatedSuccessfully}\n${activeCopy.installedVersion}: ${version}`
          : payload.updated === false
            ? `${activeCopy.alreadyUpdated}\n${activeCopy.installedVersion}: ${version}`
            : `${activeCopy.updateChecked}\n${activeCopy.installedVersion}: ${version}`;
        if (payload.success) {
          appendLog(`[${languageRef.current === "es" ? "SISTEMA" : "SYSTEM"}] ${successMessage.replace("\n", " · ")}`);
        }
        setNotice({
          title: payload.success ? activeCopy.info : activeCopy.error,
          message: payload.success
            ? successMessage
            : languageRef.current === "es" ? "No se pudo actualizar yt-dlp. Revisá los logs." : "yt-dlp could not be updated. Check the logs.",
          kind: payload.success ? "info" : "error",
        });
      }),
    ]);
    return () => { void subscriptions.then((unlisten) => unlisten.forEach((fn) => fn())); };
  }, []);

  useEffect(() => {
    consoleRef.current?.scrollTo({ top: consoleRef.current.scrollHeight });
  }, [logs]);

  const statusText = useMemo(() => {
    if (running) return progress.filename ? `${t.downloading}: ${progress.filename}` : t.ready;
    if (progress.percent >= 100) return t.success;
    return t.ready;
  }, [progress, running, t]);

  const chooseFolder = async () => {
    const chosen = await open({ directory: true, multiple: false, title: t.folderDialog, defaultPath: destination || undefined });
    if (typeof chosen === "string") {
      setDestination(chosen);
      appendLog(`[SISTEMA] Ruta de descarga actualizada a: ${chosen}`);
    }
  };

  const paste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (!text.trim()) throw new Error("empty");
      setUrl(text.trim());
      appendLog(language === "es" ? "[SISTEMA] Enlace pegado desde el portapapeles." : "[SYSTEM] Link pasted from the clipboard.");
    } catch {
      setNotice({ title: t.error, message: t.clipboardEmpty, kind: "error" });
    }
  };

  const start = async () => {
    if (running) {
      setStopping(true);
      try { await invoke("cancel_download"); } catch (error) { setStopping(false); appendLog(`[ERROR] ${String(error)}`); }
      return;
    }
    if (!url.trim()) {
      setNotice({ title: t.error, message: t.invalidUrl, kind: "error" });
      return;
    }
    if (!destination.trim()) {
      setNotice({ title: t.error, message: t.selectFolder, kind: "error" });
      return;
    }
    if (!engine.available) {
      setNotice({ title: t.error, message: t.engineMissing, kind: "error" });
      return;
    }

    const request: DownloadRequest = {
      url: url.trim(), destination, mode, useCookies, browser, browserProfile: browserProfile.trim(), proxy: proxy.trim(), subtitles,
      subtitleLanguage, subtitleFormat, cleanSubtitles,
    };
    setProgress(initialProgress);
    setRunning(true);
    setStopping(false);
    try {
      await invoke("start_download", { request });
    } catch (error) {
      setRunning(false);
      setNotice({ title: t.error, message: String(error), kind: "error" });
    }
  };

  const updateEngine = async () => {
    setUpdating(true);
    try { await invoke("update_ytdlp"); } catch (error) { setUpdating(false); setNotice({ title: t.error, message: String(error), kind: "error" }); }
  };

  const openGithub = async () => {
    try { await invoke("open_github"); }
    catch (error) { setNotice({ title: t.error, message: String(error), kind: "error" }); }
  };

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">▶</span><div><strong>CYBER</strong><small>DOWNLOADER</small></div></div>
        <nav>
          <button className={tab === "download" ? "active" : ""} onClick={() => setTab("download")}><DownloadIcon className="button-icon" />{t.downloads}</button>
          <button className={tab === "settings" ? "active" : ""} onClick={() => setTab("settings")}><SettingsIcon className="button-icon" />{t.settings}</button>
        </nav>
        <button className="language-button" onClick={() => setLanguage(language === "es" ? "en" : "es")}><GlobeIcon className="button-icon" />{t.language}</button>
        <div className="engine-card">
          <small>yt-dlp</small>
          <div className="engine-status-row"><span className={engine.available ? "status-dot" : "status-dot offline"} /><strong>{engine.available ? `${t.active}${engine.version ? ` · ${engine.version}` : ""}` : t.missing}</strong></div>
        </div>
        <button className="github-button" onClick={() => void openGithub()} title="github.com/ZeroCool22"><img src="/github.png" alt="" /> <span>By ZeroCool22</span></button>
        <div className="version">TAURI EDITION · v2.0</div>
      </aside>

      <section className="workspace">
        {tab === "download" ? (
          <div className="download-view">
            <section className="card url-card">
              <label htmlFor="url">🔗 {t.url}</label>
              <div className="input-row"><input id="url" value={url} onChange={(e) => setUrl(e.target.value)} placeholder={t.urlHint} disabled={running} />
                <button className="secondary" onClick={() => void paste()} disabled={running}><PasteIcon className="button-icon" />{t.paste}</button></div>
            </section>

            <div className="two-columns">
              <section className="card"><h2>⚡ {t.quality}</h2>
                <div className="radio-list">
                  {([[
                    "video_best", t.best], ["video_1080p", t.fullHd], ["video_720p", t.hd], ["audio_mp3", t.audio]] as [DownloadMode, string][]).map(([value, label]) =>
                    <label key={value}><input type="radio" checked={mode === value} onChange={() => setMode(value)} disabled={running} /><span>{label}</span></label>)}
                </div>
                <div className="subtitle-line"><label><input type="checkbox" checked={subtitles} onChange={(e) => setSubtitles(e.target.checked)} disabled={running} /> {t.subtitles}</label>
                  <select value={subtitleFormat} onChange={(e) => setSubtitleFormat(e.target.value as SubtitleFormat)} disabled={!subtitles || running}><option value="vtt">VTT</option><option value="srt">SRT</option></select>
                  <select value={subtitleLanguage} onChange={(e) => setSubtitleLanguage(e.target.value as SubtitleLanguage)} disabled={!subtitles || running}>
                    <option value="es">{language === "es" ? "Español" : "Spanish"}</option><option value="en">{language === "es" ? "Inglés" : "English"}</option><option value="pt">{language === "es" ? "Portugués" : "Portuguese"}</option>
                  </select></div>
                <label className="clean-line"><input type="checkbox" checked={cleanSubtitles} onChange={(e) => setCleanSubtitles(e.target.checked)} disabled={!subtitles || running} /> {t.clean}</label>
              </section>

              <section className="card destination-card"><h2>📁 {t.destination}</h2>
                <div className="path-box" title={destination}>{destination || "—"}</div>
                <button className="secondary full" onClick={() => void chooseFolder()} disabled={running}><FolderIcon className="button-icon" />{t.browse}</button>
                <div className="disk-hint"><span>●</span> {storageLocationLabel(destination, language)}</div>
              </section>
            </div>

            <section className="progress-card">
              <div className="progress-copy"><strong title={statusText}>{statusText}</strong><span>{progress.percent.toFixed(1)}%</span></div>
              <div className="progress-track"><div style={{ width: `${Math.min(progress.percent, 100)}%` }} /></div>
              <div className="metrics"><span>{t.speed}: <b>{progress.speed}</b></span><span>{t.remaining}: <b>{progress.eta}</b></span></div>
              <button className={running ? "action cancel" : "action"} onClick={() => void start()} disabled={stopping}>{running ? <StopIcon className="button-icon" /> : <DownloadIcon className="button-icon" />}{stopping ? t.stopping : running ? t.cancel : t.start}</button>
            </section>

            <section className="terminal-card"><header><span>⌁ {t.logs}</span><i /><i /><i /></header><div className="terminal" ref={consoleRef}>
              {logs.length ? logs.map((line, index) => <div key={`${index}-${line}`}><ConsoleLine line={line} /></div>) : <div className="muted"><ConsoleLine line="[SISTEMA] CyberDownloader listo." /></div>}
            </div></section>
          </div>
        ) : (
          <div className="settings-view">
            <h1>{t.advanced}</h1>
            <section className="card settings-card"><h2>🌐 {t.cookies}</h2>
              <label className="toggle-row"><input type="checkbox" checked={useCookies} onChange={(e) => setUseCookies(e.target.checked)} disabled={running} /><span>{t.cookies}</span>
                <select value={browser} onChange={(e) => setBrowser(e.target.value as Browser)} disabled={!useCookies || running}><option value="brave">Brave</option><option value="chrome">Chrome</option><option value="chromium">Chromium</option><option value="edge">Edge</option><option value="firefox">Firefox</option><option value="opera">Opera</option><option value="vivaldi">Vivaldi</option><option value="whale">Whale</option></select></label>
              <label className="field-label profile-field">{t.browserProfile}<input value={browserProfile} onChange={(e) => setBrowserProfile(e.target.value)} placeholder={t.browserProfileHint} disabled={!useCookies || running} /></label>
              <label className="field-label">{t.proxy}<input value={proxy} onChange={(e) => setProxy(e.target.value)} placeholder="http://127.0.0.1:8080" disabled={running} /></label>
            </section>
            <section className="card maintenance-card"><div><h2>↻ {t.maintenance}</h2><p>{t.updateHelp}</p><div className="engine-version-label">{t.installedVersion}: <strong>{engine.version ?? t.unknownVersion}</strong></div></div>
              <button className="secondary" onClick={() => void updateEngine()} disabled={updating || running || !engine.available}><RefreshIcon className={`button-icon ${updating ? "spinning" : ""}`} />{updating ? t.updating : t.update}</button></section>
          </div>
        )}
      </section>

      {notice && <div className="modal-backdrop" onMouseDown={() => setNotice(null)}><div className={`modal ${notice.kind}`} onMouseDown={(e) => e.stopPropagation()}>
        <h2>{notice.kind === "error" ? "⚠" : "⚡"} {notice.title}</h2><p>{notice.message}</p><button onClick={() => setNotice(null)}>{t.close}</button>
      </div></div>}
    </main>
  );
}
