export type Language = "es" | "en";
export type DownloadMode = "video_best" | "video_1080p" | "video_720p" | "audio_mp3";
export type SubtitleLanguage = "es" | "en" | "pt";
export type SubtitleFormat = "vtt" | "srt";
export type Browser = "brave" | "chrome" | "chromium" | "edge" | "firefox" | "opera" | "vivaldi" | "whale";

export interface DownloadRequest {
  url: string;
  destination: string;
  mode: DownloadMode;
  useCookies: boolean;
  browser: Browser;
  browserProfile: string;
  proxy: string;
  subtitles: boolean;
  subtitleLanguage: SubtitleLanguage;
  subtitleFormat: SubtitleFormat;
  cleanSubtitles: boolean;
}

export interface ProgressEvent {
  percent: number;
  speed: string;
  eta: string;
  filename: string;
}

export interface FinishedEvent {
  success: boolean;
  cancelled: boolean;
  message: string;
  cookieHelpRecommended: boolean;
}

export interface EngineInfo {
  available: boolean;
  version: string | null;
  executable: string | null;
  ffmpegAvailable: boolean;
  jsRuntimeAvailable: boolean;
  jsRuntime: string | null;
}

export interface EngineUpdateFinishedEvent {
  success: boolean;
  updated: boolean | null;
  previousVersion: string | null;
  version: string | null;
}
