# 🎬 YT-DLP CyberDownloader — Tauri Edition

Aplicación de escritorio bilingüe para descargar video, audio y subtítulos con
yt-dlp. Esta versión 2 fue reconstruida con **Tauri 2, React, TypeScript y Rust**.

## ✨ Características

- Descargas desde YouTube, Instagram, Twitch, TikTok y demás sitios compatibles.
- Mejor calidad disponible, video hasta 1080p/720p o audio MP3 a 320 kbps.
- Progreso, velocidad, tiempo restante, cancelación y terminal coloreada.
- Subtítulos manuales o automáticos en VTT/SRT con limpieza de repeticiones.
- Cookies de Brave, Chrome, Chromium, Edge, Firefox, Opera, Vivaldi o Whale.
- Selección opcional de perfil del navegador y proxy.
- Interfaz instantánea en español e inglés.
- Actualización integrada del motor yt-dlp.
- Binarios portables de yt-dlp, FFmpeg y FFprobe en el instalador.

> 🪟 Plataforma compatible: Windows de 64 bits.

## Requisitos locales

- Node 22 o superior y pnpm 11 (Node se usa también para resolver los desafíos
  JavaScript/EJS de YouTube)
- Rust/Cargo con target MSVC
- Visual Studio Build Tools y WebView2
- `tools/yt-dlp.exe`, `tools/ffmpeg.exe` y `tools/ffprobe.exe`

Las herramientas `.exe` no se versionan. Las dependencias pnpm usan el store
`D:\.pnpm-store\v11` y los artefactos de Cargo quedan en `target` dentro de este
disco.

## 🛠️ Desarrollo

```powershell
pnpm install
pnpm tauri dev
```

## ✅ Verificación y compilación

```powershell
pnpm check
pnpm tauri build --no-bundle
```

Para generar el instalador NSIS:

```powershell
pnpm tauri build --config '{"bundle":{"active":true}}' --bundles nsis
```

Los ejecutables pesados de `tools/` no se versionan. Se incluyen como recursos
al compilar localmente y el instalador generado se publica mediante GitHub
Releases, no dentro del historial Git.

Consultá [MIGRATION_PLAN.md](MIGRATION_PLAN.md) para el inventario funcional y
las decisiones de migración.

## 👤 Autor

Desarrollado por [ZeroCool22](https://github.com/ZeroCool22).

## ⚖️ Licencia

Distribuido bajo licencia MIT. yt-dlp, FFmpeg y el resto de las dependencias
conservan sus respectivas licencias.
