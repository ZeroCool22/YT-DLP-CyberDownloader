# 🎬 YT-DLP CyberDownloader

> 🚀 Aplicación de escritorio bilingüe, rápida y completamente local para
> descargar video, audio y subtítulos con **yt-dlp**.

<img width="1042" height="752" alt="Screenshot_5" src="https://github.com/user-attachments/assets/aa9435c2-fc1b-4b0b-8591-025c16c9686b" />

<img width="1041" height="752" alt="Screenshot_4" src="https://github.com/user-attachments/assets/37e849c9-a7ca-401e-b92e-1a50d42290e1" />

## ✨ Características

- 📥 Descargas desde YouTube, Instagram, Twitch, TikTok y demás sitios compatibles.
- 🎥 Mejor calidad disponible, Full HD hasta 1080p o HD hasta 720p.
- 🎵 Extracción de audio en MP3 a 320 kbps mediante FFmpeg.
- 📊 Progreso, velocidad, tiempo restante y cancelación en tiempo real.
- 💻 Terminal integrada con etiquetas y mensajes coloreados.
- 📝 Subtítulos manuales o automáticos en VTT/SRT.
- 🧹 Limpieza de repeticiones en subtítulos generados automáticamente.
- 🍪 Cookies de Brave, Chrome, Chromium, Edge, Firefox, Opera, Vivaldi o Whale.
- 👤 Selección opcional del perfil del navegador.
- 🌐 Compatibilidad con proxy.
- 🌎 Interfaz instantánea en español e inglés.
- 🔄 Actualización integrada del motor yt-dlp.
- 🧰 Binarios portables de yt-dlp, FFmpeg y FFprobe incluidos en el instalador.

> 🪟 **Plataforma compatible:** Windows de 64 bits.

## 🧱 Tecnologías

- 🦀 **Rust** para el backend, la gestión de procesos y las descargas.
- ⚛️ **React + TypeScript** para la interfaz.
- 🖥️ **Tauri 2 + WebView2**.
- 📦 **pnpm** para dependencias y scripts del frontend.
- 🎞️ **yt-dlp + FFmpeg** para extracción, conversión y combinación multimedia.

## 📋 Requisitos para desarrollo

- 🟢 Node 22 o superior y pnpm 11. Node también resuelve los desafíos
  JavaScript/EJS actuales de YouTube.
- 🦀 Rust/Cargo con target MSVC.
- 🛠️ Visual Studio Build Tools y WebView2.
- 📁 `tools/yt-dlp.exe`, `tools/ffmpeg.exe` y `tools/ffprobe.exe`.

Las herramientas `.exe` no se versionan. pnpm utiliza el store configurado en
el sistema de cada desarrollador y los artefactos de Cargo se generan dentro de
`target` en este proyecto.

## 🚀 Desarrollo

```powershell
pnpm install
pnpm tauri dev
```

## 🧪 Verificación

```powershell
pnpm check
```

Este comando ejecuta las pruebas del frontend, el chequeo de TypeScript, la
compilación web y `cargo check`.

## 🏗️ Compilación

### 📄 Solo el ejecutable

```powershell
pnpm tauri build --no-bundle
```

### 📦 Instalador NSIS

```powershell
pnpm tauri build --bundles nsis
```

Los ejecutables pesados de `tools/` se incorporan como recursos durante la
compilación, pero no forman parte del historial de Git.

## 🏷️ Releases

Los instaladores compilados se publican en
[GitHub Releases](https://github.com/ZeroCool22/YT-DLP-CyberDownloader/releases).
Cada versión puede descargarse e instalarse sin configurar Python, Rust ni Node.

## 👤 Autor

Desarrollado con ☕ por [ZeroCool22](https://github.com/ZeroCool22).

## ⚖️ Licencia

Distribuido bajo licencia MIT. yt-dlp, FFmpeg y el resto de las dependencias
conservan sus respectivas licencias.
