# Plan de migración a Tauri 2

## Auditoría de la aplicación Python

La aplicación de referencia tiene tres capas:

1. `main.py`: interfaz CustomTkinter, traducciones ES/EN, estado de descarga,
   diálogos, portapapeles, selector de directorio, ajustes y actualización.
2. `downloader.py`: configuración de yt-dlp, perfiles de formato, progreso,
   cancelación, FFmpeg portable, cookies, proxy y postprocesadores.
3. `subtitle_cleaner.py`: detección y limpieza conservadora de VTT rodantes de
   YouTube, eliminación de solapamientos y ajuste de líneas a 44 caracteres.

### Inventario que debe conservarse

- URL única o playlist de cualquier sitio soportado por yt-dlp.
- Perfiles: mejor video, hasta 1080p, hasta 720p y MP3 a 320 kbps.
- Salida combinada MP4 y uso de FFmpeg/FFprobe portables.
- Progreso con porcentaje, archivo, velocidad y ETA; terminal de logs.
- Cancelación de la descarga activa.
- Carpeta por defecto `Downloads` y selector de carpeta.
- Cookies de Brave, Chrome, Chromium, Edge, Firefox, Opera, Vivaldi o Whale,
  con perfil opcional, activables por el usuario.
- Proxy opcional.
- Subtítulos manuales y automáticos en español, inglés o portugués.
- Salida VTT o conversión a SRT.
- Limpieza opcional de repeticiones de subtítulos automáticos de YouTube.
- Interfaz oscura cyberpunk, navegación Descargas/Ajustes y diálogos propios.
- Cambio de idioma español/inglés sin reiniciar.
- Actualización local del motor yt-dlp con salida visible en logs.
- Mensajes específicos para detección de Instagram, Twitch y TikTok.

## Arquitectura de destino

### Frontend — React + TypeScript

- Estado tipado para formulario, progreso, ejecución y preferencias.
- Componentes para sidebar, descarga, ajustes, terminal y diálogo modal.
- Eventos de Tauri para logs, progreso y finalización.
- Portapapeles mediante API web y selector de carpeta mediante plugin oficial.
- Traducciones embebidas ES/EN, sin servicios externos.

### Backend — Rust + Tauri 2

- Estado compartido que guarda como máximo un proceso hijo activo.
- Comandos `start_download`, `cancel_download`, `update_ytdlp` y consulta de
  disponibilidad/versión del motor.
- Ejecución directa del binario yt-dlp como proceso hijo, con stdout/stderr
  capturados y emisión de eventos al frontend.
- Plantilla de progreso estable de yt-dlp para evitar depender de texto humano.
- Búsqueda de herramientas en recursos empaquetados, `tools` del proyecto y PATH.
- Terminación explícita del proceso hijo al cancelar.
- Opciones de formato equivalentes a las usadas por `downloader.py`.
- Postprocesado de VTT implementado en Rust antes de conversión a SRT.

## Estrategia para herramientas pesadas

- `tools/ffmpeg.exe` y `tools/ffprobe.exe` se mantienen fuera de Git y se copian
  desde una instalación local autorizada durante desarrollo/empaquetado.
- El motor yt-dlp se resuelve desde `tools/yt-dlp.exe` o PATH. No se usa ni se
  modifica el venv del proyecto Python de referencia.
- `.npmrc` fija `store-dir=D:\.pnpm-store\v11`.
- `.cargo/config.toml` fija `target-dir` dentro del workspace en D.

## Fases y estado

- [x] Auditar `main.py`, `downloader.py` y `subtitle_cleaner.py` antes de crear el
  proyecto.
- [x] Registrar reglas permanentes e inventario funcional.
- [x] Crear el scaffold Tauri 2 + React + TypeScript.
- [x] Implementar UI y traducciones.
- [x] Implementar backend de descargas, logs, progreso y cancelación.
- [x] Portar y probar la limpieza de VTT.
- [x] Integrar herramientas locales y configuración de empaquetado.
- [x] Ejecutar pruebas, chequeo de tipos, `cargo check`, Clippy y build de
  producción.
- [x] Inicializar Git local y preparar la publicación autorizada en la rama
  `tauri-v2` del repositorio oficial.

## Criterios de aceptación

La migración se considera completa cuando los cuatro perfiles generan los mismos
tipos de salida, las opciones avanzadas y de subtítulos producen argumentos
equivalentes, cancelar no deja procesos huérfanos, la UI funciona en ambos
idiomas, las pruebas del limpiador pasan y Tauri compila usando únicamente el
toolchain local definido.

## Verificación final (18 de julio de 2026)

- `pnpm check`: 2 tests frontend, TypeScript, Vite y `cargo check` correctos.
- `cargo test`: 6 tests Rust correctos (VTT, argumentos, perfiles, EJS y salida).
- Clippy con warnings tratados como errores: correcto.
- `pnpm tauri build`: ejecutable release generado correctamente.
- Smoke test local: ventana Tauri iniciada y cerrada de forma controlada.
- Git: publicación de la migración preparada mediante rama y pull request, sin
  reemplazar directamente `main`.

### Corrección EJS de YouTube (18 de julio de 2026)

El backend detecta Node 22+ y lo registra explícitamente con
`--js-runtimes node:RUTA`, además de habilitar `ejs:github`. Esto conserva la
configuración `js_runtimes` del Python original y evita que YouTube exponga sólo
formatos de imagen cuando falla la resolución de firmas y desafíos `n`.

### Corrección de salida CP1252 y código 120 (18 de julio de 2026)

La salida canalizada de yt-dlp se fuerza a UTF-8 y el lector Rust consume bytes
con decodificación tolerante. Antes, un solo byte CP1252 no válido para UTF-8
detenía `BufRead::lines()`, cerraba el pipe y hacía que yt-dlp terminara con
`OSError [Errno 22] Invalid argument` y código 120. La regresión está cubierta
por una prueba con salida CP1252 seguida de una segunda línea válida.
