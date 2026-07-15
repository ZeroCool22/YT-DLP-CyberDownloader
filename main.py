import os
import sys
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image
from downloader import YtdlpDownloader


def resource_path(relative_path):
    """ Obtiene la ruta absoluta a un recurso, compatible con dev y PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Intentamos la ruta normal especificada (ej. assests/pegar-como-texto.png)
    full_path = os.path.join(base_path, relative_path)
    if os.path.exists(full_path):
        return full_path

    # Fallback: si no existe en la subcarpeta, buscamos solo el nombre de archivo en la raíz del directorio base
    filename = os.path.basename(relative_path)
    fallback_path = os.path.join(base_path, filename)
    if os.path.exists(fallback_path):
        return fallback_path

    return full_path


def create_icon_label(parent, icon, text, font_size=13, text_color=None, weight="bold", font_family=None, spacing=6):
    """
    Crea un frame contenedor con un icono/emoji y un texto perfectamente alineados
    verticalmente usando grid.
    """
    container = ctk.CTkFrame(parent, fg_color="transparent")
    
    # El emoji suele verse un toque desplazado. Usando grid y centrándolo
    # logramos que quede alineado perfecto con el texto de al lado.
    icon_font = ctk.CTkFont(family="Segoe UI Emoji", size=font_size + 1)
    
    if font_family:
        text_font = ctk.CTkFont(family=font_family, size=font_size, weight=weight)
    else:
        text_font = ctk.CTkFont(size=font_size, weight=weight)
        
    lbl_icon = ctk.CTkLabel(
        container,
        text=icon,
        font=icon_font,
        text_color=text_color
    )
    lbl_icon.grid(row=0, column=0, sticky="")
    
    lbl_text = ctk.CTkLabel(
        container,
        text=text,
        font=text_font,
        text_color=text_color
    )
    lbl_text.grid(row=0, column=1, padx=(spacing, 0), sticky="")
    
    container.lbl_icon = lbl_icon
    container.lbl_text = lbl_text
    
    return container


# Configuración inicial del tema visual
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # Tema base, pero redefiniremos colores para darle más facha

# Colores Cyberpunk Premium
COLOR_BG = "#0f0f13"          # Fondo ultra oscuro
COLOR_SIDEBAR = "#16161e"     # Sidebar
COLOR_CARD = "#1f1f2e"        # Contenedores/tarjetas
COLOR_TEXT = "#a9b1d6"        # Texto secundario
COLOR_TEXT_BRIGHT = "#ffffff" # Texto brillante
COLOR_ACCENT = "#9acd32"      # Verde Amarillo (YellowGreen)
COLOR_ACCENT_HOVER = "#80ab2a" # Verde Amarillo Oscuro (Hover)
COLOR_YELLOW = "#ffee00"      # Amarillo Neón (Secundario)
COLOR_GREEN = "#00ff66"       # Verde Neón (Completado)
COLOR_RED = "#ffe600"         # Amarillo Neón (Errores/Cancelar)
COLOR_CONSOLE_BG = "#09090d"  # Consola negra pura

I18N = {
    "es": {
        "language_button": "🌐  English",
        "downloads": " Descargas",
        "settings": " Ajustes Avanzados",
        "engine_status": "●  yt-dlp: Activo",
        "url_label": "URL del Video/Playlist:",
        "url_placeholder": "Pegá el link de YouTube, Instagram, Twitch, TikTok, etc. acá...",
        "paste": " Pegar",
        "quality_title": "Calidad y Formato",
        "best_quality": "Mejor Calidad Disponible (MP4/MKV)",
        "full_hd": "Full HD (Máx 1080p)",
        "standard_hd": "HD Estándar (Máx 720p)",
        "audio_only": "Solo Audio (MP3 a 320kbps) 🎧",
        "include_subtitles": "Incluir subtítulos",
        "clean_subtitles": "Limpiar repeticiones automáticas",
        "destination_title": "Carpeta de Guardado",
        "browse": "🔍 Buscar",
        "start_download": " EMPEZAR DESCARGA",
        "cancel_download": " CANCELAR DESCARGA",
        "stopping_download": " Frenando descarga...",
        "ready": "Listo para iniciar descarga...",
        "speed": "Velocidad",
        "remaining": "Tiempo Restante",
        "control_console": "TERMINAL DE CONTROL Y LOGS",
        "advanced_settings": "Configuración Avanzada",
        "browser_cookies": "Habilitar Cookies del Navegador (Si requiere autenticación):",
        "proxy_label": "Servidor Proxy (ej. http://127.0.0.1:8080):",
        "optional": "Opcional...",
        "maintenance_title": "Mantenimiento del Motor",
        "maintenance_desc": "Si los videos tiran error de descarga o velocidad ultra lenta, YouTube puede haber modificado su código.\nActualizar el motor de yt-dlp soluciona el 99% de los problemas.",
        "update_engine": " Actualizar yt-dlp a la última versión",
        "updating_engine": " Actualizando motor...",
        "downloading": "Descargando",
        "calculating": "Calculando...",
        "finished": "Finalizado",
        "download_success": "¡Descarga finalizada con éxito!",
        "download_failed": "Fallo en la descarga.",
        "warning": "Advertencia",
        "clipboard_empty": "No se encontró texto en el portapapeles.",
        "error": "Error",
        "invalid_url": "Che, poné una URL válida para descargar algo.",
        "success": "Éxito",
        "download_completed": "¡Descarga completada!",
        "download_error": "Error de Descarga",
        "download_error_detail": "Se produjo un error durante la descarga:\n{message}",
        "update_success": "¡yt-dlp actualizado correctamente!",
        "update_failed": "No se pudo actualizar yt-dlp. Revisá el registro de logs.",
        "update_invoke_error": "Se produjo un error al invocar la actualización.",
    },
    "en": {
        "language_button": "🌐  Español",
        "downloads": " Downloads",
        "settings": " Advanced Settings",
        "engine_status": "●  yt-dlp: Active",
        "url_label": "Video/Playlist URL:",
        "url_placeholder": "Paste a YouTube, Instagram, Twitch, TikTok, etc. link here...",
        "paste": " Paste",
        "quality_title": "Quality and Format",
        "best_quality": "Best Available Quality (MP4/MKV)",
        "full_hd": "Full HD (Max 1080p)",
        "standard_hd": "Standard HD (Max 720p)",
        "audio_only": "Audio Only (320kbps MP3) 🎧",
        "include_subtitles": "Include subtitles",
        "clean_subtitles": "Clean automatic repetitions",
        "destination_title": "Save Folder",
        "browse": "🔍 Browse",
        "start_download": " START DOWNLOAD",
        "cancel_download": " CANCEL DOWNLOAD",
        "stopping_download": " Stopping download...",
        "ready": "Ready to start download...",
        "speed": "Speed",
        "remaining": "Time Remaining",
        "control_console": "CONTROL AND LOG TERMINAL",
        "advanced_settings": "Advanced Settings",
        "browser_cookies": "Enable Browser Cookies (If authentication is required):",
        "proxy_label": "Proxy Server (e.g. http://127.0.0.1:8080):",
        "optional": "Optional...",
        "maintenance_title": "Engine Maintenance",
        "maintenance_desc": "If videos fail to download or become extremely slow, YouTube may have changed its code.\nUpdating the yt-dlp engine solves most of these problems.",
        "update_engine": " Update yt-dlp to the latest version",
        "updating_engine": " Updating engine...",
        "downloading": "Downloading",
        "calculating": "Calculating...",
        "finished": "Finished",
        "download_success": "Download completed successfully!",
        "download_failed": "Download failed.",
        "warning": "Warning",
        "clipboard_empty": "No text was found on the clipboard.",
        "error": "Error",
        "invalid_url": "Enter a valid URL to start a download.",
        "success": "Success",
        "download_completed": "Download completed!",
        "download_error": "Download Error",
        "download_error_detail": "An error occurred during the download:\n{message}",
        "update_success": "yt-dlp was updated successfully!",
        "update_failed": "Could not update yt-dlp. Check the logs for details.",
        "update_invoke_error": "An error occurred while starting the update.",
    },
}

SUBTITLE_LANGUAGES = {
    "es": {"es": "Español", "en": "Inglés", "pt": "Portugués"},
    "en": {"es": "Spanish", "en": "English", "pt": "Portuguese"},
}

GLOBAL_APP = None

class CyberMessageBox(ctk.CTkToplevel):
    def __init__(self, parent, title, message, type_icon="info"):
        super().__init__(parent)
        self.title(title)
        self.geometry("460x220")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Centrar
        if parent:
            parent.update_idletasks()
            px = parent.winfo_x()
            py = parent.winfo_y()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + (pw // 2) - 230
            y = py + (ph // 2) - 110
            self.geometry(f"+{x}+{y}")
            
        # CustomTkinter aplica su icono predeterminado con un pequeño retraso.
        # Lo reemplazamos al crear el diálogo y nuevamente cuando CTk termina
        # de inicializar la ventana para que también funcione en el EXE.
        def set_dialog_icon():
            try:
                if not self.winfo_exists():
                    return

                icon_path = resource_path(os.path.join("assests", "youtube.ico"))
                if os.path.exists(icon_path):
                    self.iconbitmap(icon_path)

                png_path = resource_path(os.path.join("assests", "youtube.png"))
                if os.path.exists(png_path):
                    from PIL import ImageTk
                    icon_image = Image.open(png_path).resize((32, 32), Image.Resampling.LANCZOS)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    self.iconphoto(False, icon_photo)
                    self._dialog_icon_photo = icon_photo
            except Exception:
                pass

        set_dialog_icon()
        self.after(300, set_dialog_icon)

        # Estilos según el tipo de ventana
        if type_icon == "error":
            accent_color = "#ec4899"  # Rosa neón
            btn_text = "Aceptar"
            title_prefix = "❌  "
        elif type_icon == "warning":
            accent_color = COLOR_YELLOW  # Amarillo neón
            btn_text = "Entendido"
            title_prefix = "⚠️  "
        else:
            accent_color = COLOR_ACCENT  # Verde
            btn_text = "Excelente"
            title_prefix = "⚡  "

        # Contenedor con bordes redondeados y estilo premium
        card = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            border_color="#2b2b3d",
            border_width=1,
            corner_radius=16
        )
        card.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Contenedor interno
        text_frame = ctk.CTkFrame(card, fg_color="transparent")
        text_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Título del mensaje
        lbl_title = ctk.CTkLabel(
            text_frame,
            text=f"{title_prefix}{title.upper()}",
            font=ctk.CTkFont(family="Outfit", size=15, weight="bold"),
            text_color=accent_color,
            anchor="w"
        )
        lbl_title.pack(fill="x", pady=(0, 10))

        # Contenido del mensaje
        lbl_message = ctk.CTkLabel(
            text_frame,
            text=message,
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=COLOR_TEXT_BRIGHT,
            justify="left",
            wraplength=380,
            anchor="nw"
        )
        lbl_message.pack(fill="both", expand=True)

        def on_close():
            self.grab_release()
            self.destroy()

        # Botón de cierre estilizado
        btn = ctk.CTkButton(
            card,
            text=btn_text,
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color=accent_color,
            hover_color=COLOR_ACCENT_HOVER if type_icon == "info" else "#ccb800" if type_icon == "warning" else "#d03783",
            text_color="#0f0f13" if type_icon == "warning" else COLOR_TEXT_BRIGHT,
            height=36,
            width=110,
            corner_radius=8,
            command=on_close
        )
        btn.pack(side="bottom", anchor="e", pady=(0, 20), padx=25)

        self.bind("<Return>", lambda e: on_close())
        self.bind("<Escape>", lambda e: on_close())
        
        self.lift()
        self.after(50, lambda: (self.focus_force(), btn.focus()))


class CyberMessageBoxWrapper:
    @staticmethod
    def showinfo(title, message, **kwargs):
        parent = kwargs.get("parent", GLOBAL_APP)
        CyberMessageBox(parent, title, message, "info")

    @staticmethod
    def showerror(title, message, **kwargs):
        parent = kwargs.get("parent", GLOBAL_APP)
        CyberMessageBox(parent, title, message, "error")

    @staticmethod
    def showwarning(title, message, **kwargs):
        parent = kwargs.get("parent", GLOBAL_APP)
        CyberMessageBox(parent, title, message, "warning")

messagebox = CyberMessageBoxWrapper()

class YtdlpGuiApp(ctk.CTk):
    def tr(self, key, **kwargs):
        return I18N[self.language][key].format(**kwargs)

    def toggle_language(self):
        self.language = "en" if self.language == "es" else "es"
        self.apply_language()

    def apply_language(self):
        """Actualiza todos los textos visibles sin reconstruir la interfaz."""
        self.btn_language.configure(text=self.tr("language_button"))
        self.btn_tab_download.configure(text=self.tr("downloads"))
        self.btn_tab_settings.configure(text=self.tr("settings"))
        self.version_label.configure(text=self.tr("engine_status"))

        self.lbl_url.lbl_text.configure(text=self.tr("url_label"))
        self.entry_url.configure(placeholder_text=self.tr("url_placeholder"))
        self.btn_paste.configure(text=self.tr("paste"))
        self.lbl_quality.lbl_text.configure(text=self.tr("quality_title"))
        self.opt_best.configure(text=self.tr("best_quality"))
        self.opt_1080p.configure(text=self.tr("full_hd"))
        self.opt_720p.configure(text=self.tr("standard_hd"))
        self.opt_audio.configure(text=self.tr("audio_only"))
        self.opt_subtitles.configure(text=self.tr("include_subtitles"))
        self.opt_clean_subtitles.configure(text=self.tr("clean_subtitles"))
        self.lbl_dest.lbl_text.configure(text=self.tr("destination_title"))
        self.btn_browse.configure(text=self.tr("browse"))
        self.lbl_console_title.lbl_text.configure(text=self.tr("control_console"))

        self.lbl_sett_title.lbl_text.configure(text=self.tr("advanced_settings"))
        self.chk_cookies.configure(text=self.tr("browser_cookies"))
        self.lbl_proxy.configure(text=self.tr("proxy_label"))
        self.entry_proxy.configure(placeholder_text=self.tr("optional"))
        self.lbl_maint_title.lbl_text.configure(text=self.tr("maintenance_title"))
        self.lbl_maint_desc.configure(text=self.tr("maintenance_desc"))
        self.btn_update.configure(
            text=self.tr("updating_engine")
            if self.btn_update.cget("state") == "disabled"
            else self.tr("update_engine")
        )

        active = bool(self.downloader and self.download_thread and self.download_thread.is_alive())
        if active and self.btn_action.cget("state") == "disabled":
            action_text = self.tr("stopping_download")
        elif active:
            action_text = self.tr("cancel_download")
        else:
            action_text = self.tr("start_download")
        self.btn_action.configure(text=action_text)

        current_file = self.lbl_progress_file.cget("text")
        if current_file in (I18N["es"]["ready"], I18N["en"]["ready"]):
            self.lbl_progress_file.configure(text=self.tr("ready"))
        elif current_file in (I18N["es"]["download_success"], I18N["en"]["download_success"]):
            self.lbl_progress_file.configure(text=self.tr("download_success"))
        elif current_file in (I18N["es"]["download_failed"], I18N["en"]["download_failed"]):
            self.lbl_progress_file.configure(text=self.tr("download_failed"))
        else:
            for source_language in ("es", "en"):
                prefix = I18N[source_language]["downloading"] + ": "
                if current_file.startswith(prefix):
                    filename = current_file[len(prefix):]
                    self.lbl_progress_file.configure(text=f"{self.tr('downloading')}: {filename}")
                    break

        self._translate_metric(self.lbl_speed, "speed")
        self._translate_metric(self.lbl_eta, "remaining")
        if self.lbl_eta.cget("text") in (I18N["es"]["finished"], I18N["en"]["finished"]):
            self.lbl_eta.configure(text=self.tr("finished"))

        current_subtitle_language = self.subtitle_language_var.get()
        language_code = next(
            (
                code
                for labels in SUBTITLE_LANGUAGES.values()
                for code, label in labels.items()
                if label == current_subtitle_language
            ),
            "es",
        )
        translated_languages = list(SUBTITLE_LANGUAGES[self.language].values())
        self.subtitle_language.configure(values=translated_languages)
        self.subtitle_language_var.set(SUBTITLE_LANGUAGES[self.language][language_code])

    def _translate_metric(self, widget, key):
        current = widget.cget("text")
        for source_language in ("es", "en"):
            prefix = I18N[source_language][key] + ": "
            if current.startswith(prefix):
                widget.configure(text=f"{self.tr(key)}: {current[len(prefix):]}")
                return

    def __init__(self):
        super().__init__()

        self.language = "es"

        global GLOBAL_APP
        GLOBAL_APP = self

        # Configuración de la Ventana Principal
        self.title("YT-DLP CyberDownloader v1.1")
        self.geometry("980x660")
        self.minsize(900, 600)
        self.configure(fg_color=COLOR_BG)

        # Icono de la ventana principal y barra de tareas (Hack de Windows, kjjj)
        try:
            import ctypes
            myappid = 'forowarez.cyberdownloader.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        def set_window_icon():
            try:
                # TRUCO MÁGICO DE WINDOWS (HACK TOTAL):
                # Si está compilado como EXE, le clavamos el icono embebido directamente desde el ejecutable (sys.executable).
                # Como lo compilaste con el icono de YouTube en el launcher, Windows ya lo tiene adentro del binario!
                if getattr(sys, 'frozen', False) or hasattr(sys, '_MEIPASS'):
                    self.iconbitmap(sys.executable)
                else:
                    # En modo desarrollo local, buscamos el archivo .ico normal
                    icon_path = resource_path(os.path.join("assests", "youtube.ico"))
                    if os.path.exists(icon_path):
                        self.iconbitmap(icon_path)
            except Exception:
                # Si algo falla, fallback ultra resistente usando el PNG con iconphoto
                try:
                    icon_path = resource_path(os.path.join("assests", "youtube.png"))
                    if os.path.exists(icon_path):
                        from PIL import ImageTk
                        img = Image.open(icon_path)
                        img_resized = img.resize((32, 32), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img_resized)
                        self.iconphoto(True, photo)
                        self._icon_photo_ref = photo
                except Exception:
                    pass

        # Retardamos el seteo para asegurarnos de pisarle el icono default a CustomTkinter
        self.after(250, set_window_icon)

        # La aplicación es libre y no requiere activación.
        self.initialize_and_build_main()

    def initialize_and_build_main(self):
        # Reiniciar pesos de la grilla principal
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variables de estado
        self.downloader = None
        self.download_thread = None
        self.default_download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.selected_dir = tk.StringVar(value=self.default_download_dir)
        self.selected_mode = tk.StringVar(value="video_best")
        self.download_subtitles_var = tk.BooleanVar(value=False)
        self.subtitle_language_var = tk.StringVar(value="Español")
        self.subtitle_format_var = tk.StringVar(value="VTT")
        self.clean_subtitles_var = tk.BooleanVar(value=True)
        self.url_var = tk.StringVar()
        
        # Opciones avanzadas
        self.use_cookies_var = tk.BooleanVar(value=False)
        self.proxy_var = tk.StringVar()
        self.browser_var = tk.StringVar(value="chrome")

        # Cargar Iconos
        self.load_icons()

        # Armar UI
        self.create_sidebar()
        self.create_main_container()

        # Mostrar por defecto la pestaña "Descarga"
        self.select_tab("download")


    def load_icons(self):
        try:
            # Pegar
            img_paste = Image.open(resource_path(os.path.join("assests", "pegar-como-texto.png")))
            self.icon_paste = ctk.CTkImage(light_image=img_paste, dark_image=img_paste, size=(18, 18))
            
            # Empezar descarga
            img_download = Image.open(resource_path(os.path.join("assests", "descargar.png")))
            self.icon_download = ctk.CTkImage(light_image=img_download, dark_image=img_download, size=(20, 20))
            
            # Descargas Sidebar
            img_tab_dl = Image.open(resource_path(os.path.join("assests", "adjunto-archivo.png")))
            self.icon_tab_dl = ctk.CTkImage(light_image=img_tab_dl, dark_image=img_tab_dl, size=(20, 20))
            
            # Ajustes Avanzados Sidebar
            img_tab_settings = Image.open(resource_path(os.path.join("assests", "configuracion-de-sincronizacion.png")))
            self.icon_tab_settings = ctk.CTkImage(light_image=img_tab_settings, dark_image=img_tab_settings, size=(20, 20))
            
            # Actualizar yt-dlp
            img_update = Image.open(resource_path(os.path.join("assests", "actualizar-pagina.png")))
            self.icon_update = ctk.CTkImage(light_image=img_update, dark_image=img_update, size=(20, 20))

            # Perfil de GitHub
            img_github = Image.open(resource_path(os.path.join("assests", "github.png")))
            self.icon_github = ctk.CTkImage(light_image=img_github, dark_image=img_github, size=(22, 22))
            
            # Logo de la Marca (Calculando relación de aspecto de forma dinámica, kjjj)
            brand_path = resource_path(os.path.join("assests", "DH_Logo.png"))
            if os.path.exists(brand_path):
                img_brand = Image.open(brand_path)
                orig_w, orig_h = img_brand.size
                
                # Bounding box para el logo en el sidebar
                max_w = 280
                max_h = 120
                
                # Calculamos escala manteniendo proporción
                scale = min(max_w / orig_w, max_h / orig_h)
                new_w = int(orig_w * scale)
                new_h = int(orig_h * scale)
                
                self.brand_logo = ctk.CTkImage(light_image=img_brand, dark_image=img_brand, size=(new_w, new_h))
            else:
                self.brand_logo = None
            
        except Exception as e:
            messagebox.showerror("Error de Recursos", f"No se pudo cargar un icono/imagen:\n{e}\n\nDetalle: Asegurate de haber agregado los archivos en auto-py-to-exe.")
            self.icon_paste = None
            self.icon_download = None
            self.icon_tab_dl = None
            self.icon_tab_settings = None
            self.icon_update = None
            self.icon_github = None
            self.brand_logo = None


    def create_sidebar(self):
        # Frame del Sidebar
        self.sidebar_frame = ctk.CTkFrame(
            self, width=220, corner_radius=0, fg_color=COLOR_SIDEBAR, border_color=COLOR_CARD, border_width=1
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Logo/Título
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="⚡ CYBER_DL", 
            font=ctk.CTkFont(family="Outfit", size=24, weight="bold"),
            text_color=COLOR_ACCENT
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.subtitle_badge = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color="#242033",
            border_color="#463d68",
            border_width=1,
            corner_radius=14,
            width=126,
            height=28
        )
        self.subtitle_badge.grid(row=1, column=0, padx=20, pady=(0, 30))
        self.subtitle_badge.grid_propagate(False)

        self.subtitle_label = ctk.CTkLabel(
            self.subtitle_badge,
            text="YT-DLP  GUI",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#c4b5fd",
            fg_color="transparent"
        )
        self.subtitle_label.place(relx=0.5, rely=0.5, anchor="center")

        # Botones de navegación
        self.btn_tab_download = ctk.CTkButton(
            self.sidebar_frame, text=" Descargas", 
            image=self.icon_tab_dl,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent", text_color=COLOR_TEXT, hover_color=COLOR_CARD,
            anchor="w", height=45, corner_radius=8,
            command=lambda: self.select_tab("download")
        )
        self.btn_tab_download.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.btn_tab_settings = ctk.CTkButton(
            self.sidebar_frame, text=" Ajustes Avanzados", 
            image=self.icon_tab_settings,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent", text_color=COLOR_TEXT, hover_color=COLOR_CARD,
            anchor="w", height=45, corner_radius=8,
            command=lambda: self.select_tab("settings")
        )
        self.btn_tab_settings.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        self.btn_language = ctk.CTkButton(
            self.sidebar_frame,
            text=self.tr("language_button"),
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#242033",
            hover_color="#332d49",
            text_color="#c4b5fd",
            border_color="#463d68",
            border_width=1,
            anchor="center",
            height=38,
            corner_radius=10,
            command=self.toggle_language
        )
        self.btn_language.grid(row=4, column=0, padx=15, pady=(14, 5), sticky="ew")

        # Versión y estado abajo
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        self.info_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.info_frame.grid(row=6, column=0, padx=15, pady=20, sticky="ew")
        self.info_frame.grid_columnconfigure(0, weight=1)
        
        self.status_badge = ctk.CTkFrame(
            self.info_frame,
            fg_color="#102419",
            border_color="#235c38",
            border_width=1,
            corner_radius=14,
            height=30
        )
        self.status_badge.grid(row=0, column=0, sticky="ew", padx=12)
        self.status_badge.grid_propagate(False)

        self.version_label = ctk.CTkLabel(
            self.status_badge,
            text="●  yt-dlp: Activo",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#4ade80",
            fg_color="transparent"
        )
        self.version_label.place(relx=0.5, rely=0.5, anchor="center")

        self.github_button = ctk.CTkButton(
            self.info_frame,
            text="By ZeroCool22",
            image=self.icon_github,
            compound="left",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color=COLOR_CARD,
            text_color=COLOR_TEXT_BRIGHT,
            anchor="center",
            height=34,
            corner_radius=8,
            command=lambda: webbrowser.open_new_tab("https://github.com/ZeroCool22")
        )
        self.github_button.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        

    def create_main_container(self):
        # Contenedor dinámico de vistas
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # =====================================================================
        # PESTAÑA: DESCARGAS (Home)
        # =====================================================================
        self.view_download = ctk.CTkFrame(self.container, fg_color="transparent")
        self.view_download.grid_columnconfigure(0, weight=1)
        self.view_download.grid_rowconfigure(3, weight=1) # Fila del log se expande

        # 1. Entrada de URL
        self.url_frame = ctk.CTkFrame(self.view_download, fg_color=COLOR_CARD, corner_radius=12, border_color="#2b2b3d", border_width=1)
        self.url_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.url_frame.grid_columnconfigure(1, weight=1)

        self.lbl_url = create_icon_label(self.url_frame, "🔗", "URL del Video/Playlist:", font_size=12, text_color=COLOR_TEXT_BRIGHT, weight="bold")
        self.lbl_url.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="w")

        self.entry_url = ctk.CTkEntry(
            self.url_frame, textvariable=self.url_var, 
            placeholder_text="Pegá el link de YouTube, Instagram, Twitch, TikTok, etc. acá...",
            fg_color=COLOR_BG, border_color="#3e3e5a", text_color=COLOR_TEXT_BRIGHT,
            height=35
        )
        self.entry_url.grid(row=0, column=1, padx=(0, 10), pady=15, sticky="ew")

        self.btn_paste = ctk.CTkButton(
            self.url_frame, text=" Pegar", width=80, height=35,
            image=self.icon_paste,
            fg_color=COLOR_YELLOW, hover_color="#ccb800", text_color="#0f0f13",
            font=ctk.CTkFont(weight="bold"),
            command=self.paste_clipboard
        )
        self.btn_paste.grid(row=0, column=2, padx=(0, 15), pady=15)


        # 2. Configuración de descarga (Calidad + Destino)
        self.config_grid = ctk.CTkFrame(self.view_download, fg_color="transparent")
        self.config_grid.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.config_grid.grid_columnconfigure(0, weight=1)
        self.config_grid.grid_columnconfigure(1, weight=1)

        # Tarjeta Izquierda: Selección de Calidad
        self.quality_frame = ctk.CTkFrame(self.config_grid, fg_color=COLOR_CARD, corner_radius=12, border_color="#2b2b3d", border_width=1)
        self.quality_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        self.lbl_quality = create_icon_label(self.quality_frame, "🎯", "Calidad y Formato", font_size=14, text_color=COLOR_ACCENT, weight="bold")
        self.lbl_quality.pack(anchor="w", padx=15, pady=(15, 10))

        self.opt_best = ctk.CTkRadioButton(self.quality_frame, text="Mejor Calidad Disponible (MP4/MKV)", variable=self.selected_mode, value="video_best", fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
        self.opt_best.pack(anchor="w", padx=20, pady=5)

        self.opt_1080p = ctk.CTkRadioButton(self.quality_frame, text="Full HD (Máx 1080p)", variable=self.selected_mode, value="video_1080p", fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
        self.opt_1080p.pack(anchor="w", padx=20, pady=5)

        self.opt_720p = ctk.CTkRadioButton(self.quality_frame, text="HD Estándar (Máx 720p)", variable=self.selected_mode, value="video_720p", fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
        self.opt_720p.pack(anchor="w", padx=20, pady=5)

        self.opt_audio = ctk.CTkRadioButton(self.quality_frame, text="Solo Audio (MP3 a 320kbps) 🎧", variable=self.selected_mode, value="audio_mp3", fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
        self.opt_audio.pack(anchor="w", padx=20, pady=5)

        self.subtitle_options_frame = ctk.CTkFrame(self.quality_frame, fg_color="transparent")
        self.subtitle_options_frame.pack(fill="x", padx=20, pady=(5, 5))

        self.opt_subtitles = ctk.CTkCheckBox(
            self.subtitle_options_frame,
            text="Incluir subtítulos",
            variable=self.download_subtitles_var,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            command=self.update_subtitle_controls
        )
        self.opt_subtitles.pack(side="left")

        self.subtitle_language = ctk.CTkComboBox(
            self.subtitle_options_frame,
            values=["Español", "Inglés", "Portugués"],
            variable=self.subtitle_language_var,
            width=105,
            height=28,
            state="disabled",
            fg_color=COLOR_BG,
            border_color="#3e3e5a",
            button_color="#3e3e5a",
            button_hover_color="#505071",
            dropdown_fg_color=COLOR_CARD,
            text_color=COLOR_TEXT_BRIGHT
        )
        self.subtitle_language.pack(side="right", padx=(8, 0))

        self.subtitle_format = ctk.CTkComboBox(
            self.subtitle_options_frame,
            values=["VTT", "SRT"],
            variable=self.subtitle_format_var,
            width=65,
            height=28,
            state="disabled",
            fg_color=COLOR_BG,
            border_color="#3e3e5a",
            button_color="#3e3e5a",
            button_hover_color="#505071",
            dropdown_fg_color=COLOR_CARD,
            text_color=COLOR_TEXT_BRIGHT
        )
        self.subtitle_format.pack(side="right", padx=(8, 0))

        self.opt_clean_subtitles = ctk.CTkCheckBox(
            self.quality_frame,
            text="Limpiar repeticiones automáticas",
            variable=self.clean_subtitles_var,
            state="disabled",
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER
        )
        self.opt_clean_subtitles.pack(anchor="w", padx=40, pady=(0, 15))

        # Tarjeta Derecha: Destino e Inicio
        self.dest_frame = ctk.CTkFrame(self.config_grid, fg_color=COLOR_CARD, corner_radius=12, border_color="#2b2b3d", border_width=1)
        self.dest_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        self.lbl_dest = create_icon_label(self.dest_frame, "📂", "Carpeta de Guardado", font_size=14, text_color=COLOR_YELLOW, weight="bold")
        self.lbl_dest.pack(anchor="w", padx=15, pady=(15, 10))

        self.dir_selector_frame = ctk.CTkFrame(self.dest_frame, fg_color="transparent")
        self.dir_selector_frame.pack(fill="x", padx=15, pady=5)
        self.dir_selector_frame.grid_columnconfigure(0, weight=1)

        self.entry_dir = ctk.CTkEntry(
            self.dir_selector_frame, textvariable=self.selected_dir, 
            fg_color=COLOR_BG, border_color="#3e3e5a", text_color=COLOR_TEXT,
            height=32, state="readonly"
        )
        self.entry_dir.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.btn_browse = ctk.CTkButton(
            self.dir_selector_frame, text="🔍 Buscar", width=70, height=32,
            fg_color=COLOR_CARD, hover_color="#2d2d44", text_color=COLOR_TEXT_BRIGHT,
            border_color="#3e3e5a", border_width=1,
            command=self.browse_directory
        )
        self.btn_browse.grid(row=0, column=1)

        # Botón de Descarga Grande
        self.btn_action = ctk.CTkButton(
            self.dest_frame, text=" EMPEZAR DESCARGA", 
            image=self.icon_download,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color=COLOR_TEXT_BRIGHT,
            height=50, corner_radius=8,
            command=self.toggle_download
        )
        self.btn_action.pack(fill="x", padx=15, pady=(20, 15))


        # 3. Status & Progreso (Oculto/Inactivo por defecto, se activa dinámicamente)
        self.progress_frame = ctk.CTkFrame(self.view_download, fg_color=COLOR_CARD, corner_radius=12, border_color="#2b2b3d", border_width=1)
        self.progress_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.lbl_progress_file = ctk.CTkLabel(
            self.progress_frame, text="Listo para iniciar descarga...", 
            font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_BRIGHT, anchor="w"
        )
        self.lbl_progress_file.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="ew")

        self.progressbar = ctk.CTkProgressBar(
            self.progress_frame, fg_color=COLOR_BG, progress_color=COLOR_ACCENT, height=12
        )
        self.progressbar.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.progressbar.set(0.0)

        # Fila de datos: % | Velocidad | ETA
        self.data_frame = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.data_frame.grid(row=2, column=0, padx=15, pady=(2, 10), sticky="ew")
        
        self.lbl_pct = ctk.CTkLabel(self.data_frame, text="0.0%", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_ACCENT)
        self.lbl_pct.pack(side="left")

        self.lbl_speed = ctk.CTkLabel(self.data_frame, text="Velocidad: -- KB/s", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT)
        self.lbl_speed.pack(side="left", padx=25)

        self.lbl_eta = ctk.CTkLabel(self.data_frame, text="Tiempo Restante: --:--", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT)
        self.lbl_eta.pack(side="left")

        # 4. Terminal de Logs Integrada
        self.console_frame = ctk.CTkFrame(self.view_download, fg_color=COLOR_CONSOLE_BG, corner_radius=12, border_color="#2b2b3d", border_width=1)
        self.console_frame.grid(row=3, column=0, sticky="nsew")
        self.console_frame.grid_columnconfigure(0, weight=1)
        self.console_frame.grid_rowconfigure(1, weight=1)

        self.lbl_console_title = create_icon_label(
            self.console_frame, "⚡", "TERMINAL DE CONTROL Y LOGS", 
            font_size=11, text_color=COLOR_YELLOW, weight="bold", font_family="Consolas"
        )
        self.lbl_console_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        self.console_textbox = ctk.CTkTextbox(
            self.console_frame, fg_color="transparent", text_color="#c0caf5",
            font=ctk.CTkFont(family="Consolas", size=11),
            activate_scrollbars=True
        )
        self.console_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.console_textbox.configure(state="disabled") # Solo lectura de salida

        self.log_to_console("[SISTEMA] Sistema inicializado. Todo listo.")

        # =====================================================================
        # PESTAÑA: AJUSTES AVANZADOS
        # =====================================================================
        self.view_settings = ctk.CTkFrame(self.container, fg_color="transparent")
        self.view_settings.grid_columnconfigure(0, weight=1)

        # Tarjeta: Parámetros del Motor yt-dlp
        self.engine_card = ctk.CTkFrame(self.view_settings, fg_color=COLOR_CARD, corner_radius=12, border_color="#2b2b3d", border_width=1)
        self.engine_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        self.lbl_sett_title = create_icon_label(self.engine_card, "⚙️", "Configuración Avanzada", font_size=16, text_color=COLOR_YELLOW, weight="bold")
        self.lbl_sett_title.pack(anchor="w", padx=20, pady=(20, 15))

        # Frame de Cookies (Checkbox + Selector de Navegador)
        self.cookies_frame = ctk.CTkFrame(self.engine_card, fg_color="transparent")
        self.cookies_frame.pack(fill="x", padx=25, pady=8)

        self.chk_cookies = ctk.CTkCheckBox(
            self.cookies_frame, text="Habilitar Cookies del Navegador (Si requiere autenticación):",
            variable=self.use_cookies_var, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
            checkbox_width=20, checkbox_height=20
        )
        self.chk_cookies.pack(side="left")

        self.opt_browser = ctk.CTkOptionMenu(
            self.cookies_frame,
            values=["Chrome", "Firefox", "Edge", "Brave", "Opera", "Vivaldi"],
            variable=self.browser_var,
            width=110,
            height=28,
            fg_color=COLOR_BG,
            button_color=COLOR_ACCENT,
            button_hover_color=COLOR_ACCENT_HOVER,
            text_color=COLOR_TEXT_BRIGHT,
            dropdown_fg_color=COLOR_CARD,
            dropdown_text_color=COLOR_TEXT_BRIGHT
        )
        self.opt_browser.pack(side="left", padx=(10, 0))

        # Input Proxy
        self.proxy_frame = ctk.CTkFrame(self.engine_card, fg_color="transparent")
        self.proxy_frame.pack(fill="x", padx=25, pady=8)
        
        self.lbl_proxy = ctk.CTkLabel(self.proxy_frame, text="Servidor Proxy (ej. http://127.0.0.1:8080):", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT)
        self.lbl_proxy.pack(side="left", padx=(0, 10))

        self.entry_proxy = ctk.CTkEntry(
            self.proxy_frame, textvariable=self.proxy_var, placeholder_text="Opcional...",
            fg_color=COLOR_BG, border_color="#3e3e5a", text_color=COLOR_TEXT_BRIGHT,
            width=250, height=28
        )
        self.entry_proxy.pack(side="left")

        # Tarjeta: Mantenimiento del Sistema (Actualizar yt-dlp)
        self.maint_card = ctk.CTkFrame(self.view_settings, fg_color=COLOR_CARD, corner_radius=12, border_color="#2b2b3d", border_width=1)
        self.maint_card.grid(row=1, column=0, sticky="ew")

        self.lbl_maint_title = create_icon_label(self.maint_card, "🔧", "Mantenimiento del Motor", font_size=16, text_color=COLOR_ACCENT, weight="bold")
        self.lbl_maint_title.pack(anchor="w", padx=20, pady=(20, 10))

        self.lbl_maint_desc = ctk.CTkLabel(
            self.maint_card, 
            text="Si los videos tiran error de descarga o velocidad ultra lenta, YouTube puede haber modificado su código.\nActualizar el motor de yt-dlp soluciona el 99% de los problemas.",
            font=ctk.CTkFont(size=12), text_color=COLOR_TEXT, justify="left"
        )
        self.lbl_maint_desc.pack(anchor="w", padx=20, pady=(0, 15))

        self.btn_update = ctk.CTkButton(
            self.maint_card, text=" Actualizar yt-dlp a la última versión", 
            image=self.icon_update,
            font=ctk.CTkFont(weight="bold"),
            fg_color=COLOR_YELLOW, hover_color="#ccb800", text_color="#0f0f13",
            height=40,
            command=self.update_ytdlp
        )
        self.btn_update.pack(anchor="w", padx=20, pady=(0, 20))

    # =====================================================================
    # LOGICA DE LA APLICACIÓN
    # =====================================================================
    def select_tab(self, tab_name):
        # Desmarcar botones
        self.btn_tab_download.configure(fg_color="transparent", text_color=COLOR_TEXT)
        self.btn_tab_settings.configure(fg_color="transparent", text_color=COLOR_TEXT)

        # Ocultar vistas
        self.view_download.grid_forget()
        self.view_settings.grid_forget()

        # Activar vista seleccionada
        if tab_name == "download":
            self.view_download.grid(row=0, column=0, sticky="nsew")
            self.btn_tab_download.configure(fg_color=COLOR_CARD, text_color=COLOR_ACCENT)
        elif tab_name == "settings":
            self.view_settings.grid(row=0, column=0, sticky="nsew")
            self.btn_tab_settings.configure(fg_color=COLOR_CARD, text_color=COLOR_ACCENT)

    def paste_clipboard(self):
        try:
            clipboard_content = self.clipboard_get()
            self.url_var.set(clipboard_content)
            self.log_to_console(
                "[SYSTEM] Link pasted from the clipboard."
                if self.language == "en"
                else "[SISTEMA] Enlace pegado desde el portapapeles."
            )
        except Exception:
            messagebox.showwarning(self.tr("warning"), self.tr("clipboard_empty"))

    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.selected_dir.get())
        if directory:
            self.selected_dir.set(directory)
            self.log_to_console(f"[SISTEMA] Ruta de descarga actualizada a: {directory}")

    def log_to_console(self, message):
        # Inserción en la terminal de logs integrada de forma segura
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert("end", message + "\n")
        self.console_textbox.configure(state="disabled")
        self.console_textbox.see("end")

    def update_progress_ui(self, data):
        # Callback para procesar actualizaciones de progreso de yt-dlp
        percent = data.get('percent', 0.0)
        speed = data.get('speed', '0 B/s')
        eta = data.get('eta', '00:00')
        filename = data.get('filename', 'Video')

        # Acortamos el nombre del archivo si es gigante para que no rompa la UI
        if len(filename) > 65:
            filename = filename[:62] + "..."

        self.lbl_progress_file.configure(text=f"{self.tr('downloading')}: {filename}")
        self.progressbar.set(percent / 100.0)
        self.lbl_pct.configure(text=f"{percent:.1f}%")
        self.lbl_speed.configure(text=f"{self.tr('speed')}: {speed}")
        self.lbl_eta.configure(text=f"{self.tr('remaining')}: {eta}")

    def toggle_download(self):
        if self.downloader and self.download_thread and self.download_thread.is_alive():
            # Acción es Cancelar
            self.btn_action.configure(state="disabled", text=self.tr("stopping_download"), image=None)
            self.downloader.cancel()

        else:
            # Acción es Iniciar
            url = self.url_var.get().strip()
            if not url:
                messagebox.showerror(self.tr("error"), self.tr("invalid_url"))
                return

            self.start_download(url)

    def update_subtitle_controls(self):
        """Habilita el idioma solamente cuando se solicitan subtítulos."""
        state = "readonly" if self.download_subtitles_var.get() else "disabled"
        self.subtitle_language.configure(state=state)
        self.subtitle_format.configure(state=state)
        self.opt_clean_subtitles.configure(
            state="normal" if self.download_subtitles_var.get() else "disabled")

    def start_download(self, url):
        # Configurar botones para estado de descarga activa
        self.btn_action.configure(text=self.tr("cancel_download"), image=None, fg_color=COLOR_RED, hover_color="#ccb800")
        self.entry_url.configure(state="disabled")

        self.btn_paste.configure(state="disabled")
        self.btn_browse.configure(state="disabled")
        self.opt_best.configure(state="disabled")
        self.opt_1080p.configure(state="disabled")
        self.opt_720p.configure(state="disabled")
        self.opt_audio.configure(state="disabled")
        self.opt_subtitles.configure(state="disabled")
        self.subtitle_language.configure(state="disabled")
        self.subtitle_format.configure(state="disabled")
        self.opt_clean_subtitles.configure(state="disabled")
        
        # Resetear barra e labels de progreso
        self.progressbar.set(0.0)
        self.progressbar.configure(progress_color=COLOR_ACCENT)
        self.lbl_pct.configure(text="0.0%", text_color=COLOR_ACCENT)
        self.lbl_speed.configure(text=f"{self.tr('speed')}: {self.tr('calculating')}")
        self.lbl_eta.configure(text=f"{self.tr('remaining')}: --:--")

        # Construir opciones personalizadas a partir de la pestaña Ajustes
        custom_opts = {}
        if self.use_cookies_var.get():
            browser = self.browser_var.get().lower()
            # Usar cookies del navegador seleccionado por el usuario
            custom_opts['cookiesfrombrowser'] = (browser,)
            self.log_to_console(f"[SISTEMA] Usando cookies del navegador {browser.capitalize()} para autenticación.")
        
        proxy = self.proxy_var.get().strip()
        if proxy:
            custom_opts['proxy'] = proxy
            self.log_to_console(f"[SISTEMA] Usando servidor proxy: {proxy}")

        if self.download_subtitles_var.get():
            language_codes = {
                "Español": r"es(?:-.*)?",
                "Inglés": r"en(?:-.*)?",
                "Portugués": r"pt(?:-.*)?",
                "Spanish": r"es(?:-.*)?",
                "English": r"en(?:-.*)?",
                "Portuguese": r"pt(?:-.*)?",
            }
            subtitle_language = self.subtitle_language_var.get()
            subtitle_format = self.subtitle_format_var.get().lower()
            custom_opts.update({
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': [language_codes.get(subtitle_language, r'es(?:-.*)?')],
                'subtitlesformat': 'vtt/best',
                '_subtitle_output_format': subtitle_format,
                '_clean_subtitles': self.clean_subtitles_var.get(),
            })
            self.log_to_console(
                f"[SISTEMA] Se descargarán subtítulos en {subtitle_language} "
                f"(manuales o automáticos) en formato {subtitle_format.upper()}"
                f"{' con limpieza automática.' if self.clean_subtitles_var.get() else '.'}"
            )

        # Instanciar el downloader asíncrono
        self.downloader = YtdlpDownloader(
            progress_callback=self.update_progress_ui,
            log_callback=self.log_to_console
        )

        # Registro de detección para Instagram, Twitch y TikTok (kjjj)
        if "instagram.com" in url.lower():
            self.log_to_console("[SISTEMA] ¡Enlace de Instagram Reels detectado! Iniciando extracción de video...")
        elif "twitch.tv" in url.lower():
            self.log_to_console("[SISTEMA] ¡Enlace de Twitch detectado! Iniciando extracción de video...")
        elif "tiktok.com" in url.lower():
            self.log_to_console("[SISTEMA] ¡Enlace de TikTok detectado! Iniciando extracción de video...")

        # Ejecutar en hilo separado para no trabar la GUI
        mode = self.selected_mode.get()
        dest_dir = self.selected_dir.get()
        
        self.download_thread = threading.Thread(
            target=self.run_download_in_background,
            args=(url, dest_dir, mode, custom_opts),
            daemon=True
        )
        self.download_thread.start()

    def run_download_in_background(self, url, dest_dir, mode, custom_opts):
        success, message = self.downloader.download(url, dest_dir, mode, custom_opts)
        
        # Retornar el control al hilo principal de Tkinter para actualizar la interfaz
        self.after(0, lambda: self.finish_download(success, message))

    def finish_download(self, success, message):
        # Restaurar UI al estado inicial
        self.btn_action.configure(state="normal", text=self.tr("start_download"), image=self.icon_download, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
        self.entry_url.configure(state="normal")

        self.btn_paste.configure(state="normal")
        self.btn_browse.configure(state="normal")
        self.opt_best.configure(state="normal")
        self.opt_1080p.configure(state="normal")
        self.opt_720p.configure(state="normal")
        self.opt_audio.configure(state="normal")
        self.opt_subtitles.configure(state="normal")
        self.update_subtitle_controls()

        if success:
            self.progressbar.set(1.0)
            self.progressbar.configure(progress_color=COLOR_GREEN)
            self.lbl_pct.configure(text="100%", text_color=COLOR_GREEN)
            self.lbl_speed.configure(text=f"{self.tr('speed')}: 0 B/s")
            self.lbl_eta.configure(text=self.tr("finished"))
            self.lbl_progress_file.configure(text=self.tr("download_success"))
            messagebox.showinfo(self.tr("success"), self.tr("download_completed"))
        else:
            self.progressbar.configure(progress_color=COLOR_RED)
            self.lbl_pct.configure(text="ERROR", text_color=COLOR_RED)
            self.lbl_progress_file.configure(text=self.tr("download_failed"))
            
            if "cancelada" in message.lower():
                self.log_to_console("[SISTEMA] Operación cancelada exitosamente.")
            else:
                messagebox.showerror(
                    self.tr("download_error"),
                    self.tr("download_error_detail", message=message)
                )

    def update_ytdlp(self):
        # Deshabilitar botón durante el update
        self.btn_update.configure(state="disabled", text=self.tr("updating_engine"), image=None)
        self.log_to_console("[SISTEMA] Buscando actualizaciones para yt-dlp vía pip...")


        def run_update():
            import subprocess
            try:
                # Ejecutar comando pip install --upgrade yt-dlp usando el intérprete actual del venv
                python_exe = sys.executable
                process = subprocess.Popen(
                    [python_exe, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Leer la salida en tiempo real
                for line in process.stdout:
                    clean_line = line.strip()
                    if clean_line:
                        self.after(0, lambda l=clean_line: self.log_to_console(f"[PIP] {l}"))
                
                process.wait()
                
                if process.returncode == 0:
                    self.after(0, lambda: self.log_to_console("[SISTEMA] ¡yt-dlp se actualizó con éxito a la última versión!"))
                    self.after(0, lambda: messagebox.showinfo(self.tr("success"), self.tr("update_success")))
                else:
                    err_msg = process.stderr.read()
                    self.after(0, lambda e=err_msg: self.log_to_console(f"[ERROR] Pip falló: {e}"))
                    self.after(0, lambda: messagebox.showerror(self.tr("error"), self.tr("update_failed")))
            except Exception as e:
                self.after(0, lambda ex=e: self.log_to_console(f"[ERROR] Error crítico de actualización: {str(ex)}"))
                self.after(0, lambda: messagebox.showerror(self.tr("error"), self.tr("update_invoke_error")))
            finally:
                self.after(0, lambda: self.btn_update.configure(state="normal", text=self.tr("update_engine"), image=self.icon_update))

        threading.Thread(target=run_update, daemon=True).start()

if __name__ == "__main__":
    app = YtdlpGuiApp()
    app.mainloop()
