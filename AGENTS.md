# Instrucciones del proyecto

## Objetivo

Migrar CyberDownloader desde la aplicación Python ubicada en
`D:\Portables\yt-dlp` a una aplicación de escritorio local basada en Tauri 2,
React, TypeScript y Rust.

## Reglas obligatorias

- El proyecto Python es exclusivamente una referencia de solo lectura. No se
  modifica, actualiza ni ejecuta ninguna operación que escriba en sus archivos,
  su entorno virtual o sus herramientas.
- Se conservan todas las funciones visibles y de descarga de la aplicación
  Python.
- Se usa `pnpm`; nunca `npm`, `npx`, Yarn ni Bun para gestionar el proyecto.
- La ejecución, las dependencias y la compilación permanecen locales; no se usan
  servicios externos para procesar descargas.
- El único remote autorizado es `origin`, asociado a
  `https://github.com/ZeroCool22/YT-DLP-CyberDownloader.git`. Publicar ramas,
  tags o releases requiere una solicitud explícita del propietario.
- Se reutilizan Node, pnpm, Rust, Cargo, Visual Studio Build Tools y WebView2 ya
  instalados.
- El store compartido de pnpm debe ser `D:\.pnpm-store\v11`.
- Dependencias, artefactos y archivos pesados se mantienen en el disco D siempre
  que sea posible. `CARGO_TARGET_DIR` debe apuntar al directorio `target` de este
  proyecto en D.
- No se incorporan secretos, cookies exportadas ni credenciales al repositorio.
- Los procesos externos se invocan sin pasar por un shell y con argumentos
  separados para evitar inyección de comandos.

## Fuente funcional auditada antes de iniciar

Se analizaron completamente estos archivos el 18 de julio de 2026:

- `D:\Portables\yt-dlp\main.py`
- `D:\Portables\yt-dlp\downloader.py`
- `D:\Portables\yt-dlp\subtitle_cleaner.py`

El inventario funcional y las decisiones de equivalencia viven en
`MIGRATION_PLAN.md`.

## Comandos de trabajo

```powershell
pnpm install
pnpm dev
pnpm tauri dev
pnpm test
pnpm build
pnpm tauri build
```

Antes de entregar cambios, ejecutar al menos las pruebas, el chequeo de tipos y
`cargo check` (directamente o mediante los scripts de pnpm).
