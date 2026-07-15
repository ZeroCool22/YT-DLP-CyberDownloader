import os
from PIL import Image

ico_path = os.path.join("iconos", "youtube.ico")
png_path = os.path.join("iconos", "youtube.png")

print(f"Buscando {ico_path}...")
if os.path.exists(ico_path):
    print("El archivo .ico existe!")
    try:
        img = Image.open(ico_path)
        print(f"Pillow abrió el .ico! Formato: {img.format}, Tamaño: {img.size}")
        # Guardar como PNG
        img.save(png_path, "PNG")
        print(f"Guardado como PNG exitosamente en: {png_path}!")
    except Exception as e:
        print(f"Error al procesar con PIL: {e}")
else:
    print("El archivo .ico NO existe!")
