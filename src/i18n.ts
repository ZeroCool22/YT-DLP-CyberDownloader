import type { Language } from "./types";

export function storageLocationLabel(path: string, language: Language): string {
  const drive = /^([a-z]):(?:[\\/]|$)/i.exec(path.trim());
  if (drive) {
    const letter = drive[1].toUpperCase();
    return language === "es" ? `LOCAL · UNIDAD ${letter}:` : `LOCAL · DRIVE ${letter}:`;
  }
  if (/^(?:\\\\|\/\/)/.test(path.trim())) {
    return language === "es" ? "RED · UBICACIÓN COMPARTIDA" : "NETWORK · SHARED LOCATION";
  }
  return language === "es" ? "UBICACIÓN LOCAL" : "LOCAL LOCATION";
}

export const copy = {
  es: {
    downloads: "Descargas", settings: "Ajustes avanzados", active: "Activo", missing: "No encontrado",
    url: "URL del video/playlist", urlHint: "Pegá el link de YouTube, Instagram, Twitch, TikTok, etc. acá…",
    paste: "Pegar", quality: "Calidad y formato", best: "Mejor calidad disponible (MP4/MKV)",
    fullHd: "Full HD (máx. 1080p)", hd: "HD estándar (máx. 720p)", audio: "Solo audio (MP3 a 320 kbps)",
    subtitles: "Incluir subtítulos", clean: "Limpiar repeticiones automáticas", destination: "Carpeta de guardado",
    browse: "Buscar", start: "EMPEZAR DESCARGA", cancel: "CANCELAR DESCARGA", stopping: "Frenando descarga…",
    ready: "Listo para iniciar descarga…", speed: "Velocidad", remaining: "Tiempo restante", logs: "TERMINAL DE CONTROL Y LOGS",
    advanced: "Configuración avanzada", cookies: "Habilitar cookies del navegador", browserProfile: "Perfil del navegador", browserProfileHint: "Opcional: Default, Profile 2 o ruta del perfil", proxy: "Servidor proxy",
    optional: "Opcional…", maintenance: "Mantenimiento del motor", update: "Actualizar yt-dlp",
    updating: "Actualizando motor…", updateHelp: "Actualizá el motor cuando un sitio cambie y las descargas comiencen a fallar.",
    invalidUrl: "Che, poné una URL válida para descargar algo.", selectFolder: "Seleccioná una carpeta de destino.",
    clipboardEmpty: "No se encontró texto en el portapapeles.", success: "¡Descarga completada!", failed: "Fallo en la descarga",
    cookieErrorHelp: "YouTube rechazó o limitó la solicitud. Probá activar las cookies y elegí el navegador donde tengas iniciada sesión en YouTube. Encontrás ambas opciones en Ajustes avanzados.",
    engineMissing: "No se encontró yt-dlp. Copiá yt-dlp.exe dentro de tools.", close: "Aceptar", downloading: "Descargando",
    language: "English", folderDialog: "Elegí la carpeta de guardado", info: "Información", error: "Error",
  },
  en: {
    downloads: "Downloads", settings: "Advanced settings", active: "Active", missing: "Not found",
    url: "Video/playlist URL", urlHint: "Paste a YouTube, Instagram, Twitch, TikTok, etc. link here…",
    paste: "Paste", quality: "Quality and format", best: "Best available quality (MP4/MKV)",
    fullHd: "Full HD (max. 1080p)", hd: "Standard HD (max. 720p)", audio: "Audio only (320 kbps MP3)",
    subtitles: "Include subtitles", clean: "Clean automatic repetitions", destination: "Save folder",
    browse: "Browse", start: "START DOWNLOAD", cancel: "CANCEL DOWNLOAD", stopping: "Stopping download…",
    ready: "Ready to start download…", speed: "Speed", remaining: "Time remaining", logs: "CONTROL AND LOG TERMINAL",
    advanced: "Advanced settings", cookies: "Enable browser cookies", browserProfile: "Browser profile", browserProfileHint: "Optional: Default, Profile 2, or profile path", proxy: "Proxy server",
    optional: "Optional…", maintenance: "Engine maintenance", update: "Update yt-dlp",
    updating: "Updating engine…", updateHelp: "Update the engine when a site changes and downloads begin to fail.",
    invalidUrl: "Enter a valid URL to start a download.", selectFolder: "Select a destination folder.",
    clipboardEmpty: "No text was found on the clipboard.", success: "Download completed!", failed: "Download failed",
    cookieErrorHelp: "YouTube rejected or limited the request. Try enabling cookies and select the browser where you are signed in to YouTube. Both options are under Advanced settings.",
    engineMissing: "yt-dlp was not found. Copy yt-dlp.exe into tools.", close: "OK", downloading: "Downloading",
    language: "Español", folderDialog: "Choose the save folder", info: "Information", error: "Error",
  },
} as const;

export type Translation = (typeof copy)[Language];
