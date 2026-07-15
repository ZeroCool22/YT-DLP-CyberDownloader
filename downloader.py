import os
import sys
import yt_dlp
from yt_dlp.postprocessor import FFmpegSubtitlesConvertorPP

from subtitle_cleaner import YoutubeSubtitleCleanerPP

class YtdlpDownloader:
    def __init__(self, progress_callback=None, log_callback=None):
        """
        Clase controladora para interactuar con la API nativa de yt-dlp.
        :param progress_callback: Función a la que se le pasa un dict con {'percent', 'speed', 'eta', 'status', 'filename'}
        :param log_callback: Función que recibe strings para la terminal integrada.
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.is_cancelled = False

    class MyLogger:
        def __init__(self, log_callback):
            self.log_callback = log_callback

        def debug(self, msg):
            # yt-dlp manda mucho debug, filtramos un poco para que no explote la consola
            if msg.startswith('[debug]') or 'stdout' in msg:
                return
            if self.log_callback:
                self.log_callback(f"[DEBUG] {msg}")

        def info(self, msg):
            if self.log_callback:
                self.log_callback(f"[INFO] {msg}")

        def warning(self, msg):
            if self.log_callback:
                self.log_callback(f"[WARNING] {msg}")

        def error(self, msg):
            if self.log_callback:
                self.log_callback(f"[ERROR] {msg}")

    def _progress_hook(self, d):
        if self.is_cancelled:
            # Para frenar la descarga tiramos una excepción que yt-dlp capture
            raise Exception("DESCARGA_CANCELADA_POR_USUARIO")

        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            
            percent = 0.0
            if total > 0:
                percent = (downloaded / total) * 100
            else:
                # Si no viene el total, intentamos sacar del percent_str de yt-dlp
                percent_str = d.get('_percent_str', '0%').replace('%', '').strip()
                try:
                    percent = float(percent_str)
                except ValueError:
                    percent = 0.0

            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            filename = os.path.basename(d.get('filename', 'Video'))

            if self.progress_callback:
                self.progress_callback({
                    'status': 'downloading',
                    'percent': percent,
                    'speed': speed,
                    'eta': eta,
                    'filename': filename
                })

        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback({
                    'status': 'finished',
                    'percent': 100.0,
                    'speed': '0 B/s',
                    'eta': '00:00',
                    'filename': os.path.basename(d.get('filename', 'Video'))
                })

    def download(self, url, download_dir, mode='video_best', custom_options=None):
        """
        Inicia la descarga de la URL.
        :param url: URL del video o playlist.
        :param download_dir: Carpeta destino.
        :param mode: 'video_best', 'video_1080p', 'video_720p', 'audio_mp3'
        :param custom_options: Dict con opciones adicionales para sobreescribir,
            incluyendo writesubtitles/writeautomaticsub para bajar subtítulos.
        """
        self.is_cancelled = False

        # Opción interna de la GUI: yt-dlp descarga VTT y FFmpeg lo convierte
        # posteriormente si el usuario eligió SRT. Copiamos el dict para no
        # modificar las opciones que conserva la interfaz.
        custom_options = dict(custom_options or {})
        subtitle_output_format = custom_options.pop('_subtitle_output_format', 'vtt').lower()
        clean_subtitles = bool(custom_options.pop('_clean_subtitles', False))
        
        # Crear la carpeta de descargas si no existe
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # Detectar directorio base del binario / script
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))

        # Usar FFmpeg/FFprobe portables sin depender del PATH de Windows.
        # En la aplicación instalada quedan junto a main.exe; durante el
        # desarrollo también aceptamos que estén dentro de ./tools.
        ffmpeg_location = None
        for candidate_dir in (app_dir, os.path.join(app_dir, 'tools')):
            portable_ffmpeg = os.path.join(candidate_dir, 'ffmpeg.exe')
            portable_ffprobe = os.path.join(candidate_dir, 'ffprobe.exe')
            if os.path.isfile(portable_ffmpeg) and os.path.isfile(portable_ffprobe):
                ffmpeg_location = candidate_dir
                break

        js_runtimes_config = {
            'deno': {},
            'node': {},
            'bun': {},
            'quickjs': {}
        }

        # Buscar y mapear ejecutables de JS portables que estén al lado del EXE de Cyber_DL.exe
        portable_qjs = os.path.join(app_dir, 'qjs.exe')
        portable_node = os.path.join(app_dir, 'node.exe')
        portable_deno = os.path.join(app_dir, 'deno.exe')

        if os.path.exists(portable_qjs):
            js_runtimes_config['quickjs'] = {'path': portable_qjs}
        elif os.path.exists(os.path.join(app_dir, 'qjs')):
            js_runtimes_config['quickjs'] = {'path': os.path.join(app_dir, 'qjs')}

        if os.path.exists(portable_node):
            js_runtimes_config['node'] = {'path': portable_node}
        elif os.path.exists(os.path.join(app_dir, 'node')):
            js_runtimes_config['node'] = {'path': os.path.join(app_dir, 'node')}

        if os.path.exists(portable_deno):
            js_runtimes_config['deno'] = {'path': portable_deno}
        elif os.path.exists(os.path.join(app_dir, 'deno')):
            js_runtimes_config['deno'] = {'path': os.path.join(app_dir, 'deno')}

        # Configuración básica de yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'logger': self.MyLogger(self.log_callback),
            'progress_hooks': [self._progress_hook],
            'noprogress': True, # Desactivamos el progreso por consola propio para no saturar
            'ignoreerrors': False,
            'merge_output_format': 'mp4',
            'js_runtimes': js_runtimes_config,
            'remote_components': ['ejs:github'],
        }

        if ffmpeg_location:
            ydl_opts['ffmpeg_location'] = ffmpeg_location
            if self.log_callback:
                self.log_callback(f"[SISTEMA] Usando FFmpeg portable desde: {ffmpeg_location}")

        # Aplicar perfiles de descarga
        if mode == 'audio_mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            })
        elif mode == 'video_1080p':
            ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
        elif mode == 'video_720p':
            ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'
        else: # video_best
            ydl_opts['format'] = 'bestvideo+bestaudio/best'

        # Sobreescribir con opciones custom si hay
        if custom_options:
            ydl_opts.update(custom_options)

        try:
            if self.log_callback:
                self.log_callback(f"[SISTEMA] Iniciando descarga de: {url}")
                self.log_callback(f"[SISTEMA] Carpeta de destino: {download_dir}")
                self.log_callback(f"[SISTEMA] Modo: {mode}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                subtitles_enabled = (
                    ydl_opts.get('writesubtitles') or ydl_opts.get('writeautomaticsub'))
                if clean_subtitles and subtitles_enabled:
                    # Se agrega primero para que SRT se genere desde el VTT limpio.
                    ydl.add_post_processor(YoutubeSubtitleCleanerPP(ydl), when='before_dl')
                if subtitle_output_format == 'srt' and subtitles_enabled:
                    ydl.add_post_processor(
                        FFmpegSubtitlesConvertorPP(ydl, format='srt'),
                        when='before_dl'
                    )
                ydl.download([url])
                
            if self.log_callback:
                self.log_callback("[SISTEMA] ¡Descarga completada con éxito!")
            return True, "Descarga completada exitosamente."
        
        except Exception as e:
            error_str = str(e)
            if "DESCARGA_CANCELADA_POR_USUARIO" in error_str:
                if self.log_callback:
                    self.log_callback("[SISTEMA] Descarga cancelada por el usuario.")
                return False, "Descarga cancelada por el usuario."
            
            if "ffmpeg" in error_str.lower() or "ffprobe" in error_str.lower():
                msg = (
                    "No se pudo usar FFmpeg/FFprobe. Reinstalá Cyber Downloader o "
                    "verificá que ffmpeg.exe y ffprobe.exe estén junto a main.exe."
                )
                if self.log_callback:
                    self.log_callback(f"[ERROR] {msg}")
                return False, msg

            if self.log_callback:
                self.log_callback(f"[ERROR] Ocurrió un fallo en la descarga: {error_str}")
            return False, error_str

    def cancel(self):
        """Cancela la descarga activa en el siguiente tick del progress_hook."""
        self.is_cancelled = True
        if self.log_callback:
            self.log_callback("[SISTEMA] Solicitando cancelación...")
