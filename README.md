# YT-DLP CyberDownloader

Una interfaz de escritorio moderna y bilingüe para `yt-dlp`, desarrollada en Python con CustomTkinter.

![CyberDownloader](assests/youtube.png)

## Características

- Interfaz en español e inglés con cambio instantáneo.
- Descargas desde YouTube, Instagram, Twitch, TikTok y otros sitios compatibles con `yt-dlp`.
- Selección de calidad: mejor disponible, 1080p, 720p o audio MP3.
- Descarga y conversión de subtítulos VTT/SRT.
- Limpieza opcional de repeticiones en subtítulos automáticos.
- Cookies del navegador y servidor proxy opcionales.
- Progreso, velocidad, tiempo restante y registro integrado.
- Actualización de `yt-dlp` desde la propia aplicación.
- Sin DRM ni activación.

## Captura de pantalla

<img width="980" height="690" alt="Screenshot_1" src="https://github.com/user-attachments/assets/aec3a684-45ca-4e15-a17d-16b0b6bd11f3" />
<img width="983" height="694" alt="Screenshot_2" src="https://github.com/user-attachments/assets/5e1c15ba-1ff8-45d8-a44b-55aed2e9aeec" />


## Ejecutar desde el código fuente

Requiere Python 3.10 o posterior.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Para combinar audio y video, convertir formatos y procesar subtítulos, instalá FFmpeg y FFprobe en el `PATH` o colocá ambos ejecutables dentro de una carpeta `tools` en la raíz del proyecto.

## Crear el ejecutable

El proyecto puede empaquetarse con PyInstaller o Auto Py to Exe en modo **One Directory**. La carpeta `_internal` generada debe conservarse junto al ejecutable.

El script [CYBERDOWNLOADER_v1.1.iss](CYBERDOWNLOADER_v1.1.iss) permite crear el instalador con Inno Setup después de generar el ejecutable.

## Licencias

El código original de CyberDownloader se distribuye bajo la [licencia MIT](license.txt).

FFmpeg, FFprobe, yt-dlp, CustomTkinter y las demás dependencias conservan sus respectivas licencias. Consultá [THIRD-PARTY-NOTICES.txt](licenses/THIRD-PARTY-NOTICES.txt) y [FFmpeg-GPLv3.txt](licenses/FFmpeg-GPLv3.txt).

## Autor

[ZeroCool22](https://github.com/ZeroCool22)

---

## English

YT-DLP CyberDownloader is a modern bilingual desktop GUI for `yt-dlp`, built with Python and CustomTkinter. It supports video, audio and subtitle downloads, quality selection, browser cookies, proxies and integrated progress reporting.

Run it from source using the commands above, then use the language button in the sidebar to switch the interface to English.

