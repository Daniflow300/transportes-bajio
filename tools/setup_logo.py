"""
Script para guardar la imagen del logo.
Copia la imagen adjunta a static/img/logo.png
"""
import os
import shutil
from PIL import Image
import io

# Create directory if needed
os.makedirs('static/img', exist_ok=True)

# Si tienes el archivo en el temp, cópialo aquí. 
# O si lo tienes en otra ruta, actualiza esta ruta:
possible_sources = [
    os.path.expanduser('~/Downloads/logo.png'),
    os.path.expanduser('~/OneDrive/Downloads/logo.png'),
    'logo.png',
]

# Si ninguno existe, creamos un logo placeholder desde PIL
# pero lo ideal es que coloques el .png adjunto manualmente en static/img/logo.png

# Para ahora, si no existe la fuente, creamos un placeholder básico
if not any(os.path.exists(p) for p in possible_sources):
    print("Creando logo placeholder con PIL...")
    from PIL import Image, ImageDraw
    
    # Create a simple shield logo
    size = 256
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Shield shape (simplified)
    draw.rectangle([(30, 30), (226, 200)], outline=(12, 108, 199, 255), width=8, fill=(12, 108, 199, 20))
    draw.text((50, 100), "LOGO", fill=(12, 108, 199, 255), font=None)
    
    img.save('static/img/logo.png')
    print("Logo placeholder creado en static/img/logo.png")
else:
    for src in possible_sources:
        if os.path.exists(src):
            shutil.copy(src, 'static/img/logo.png')
            print(f"Logo copiado desde {src} a static/img/logo.png")
            break

print("Hecho. Coloca el archivo de logo en static/img/logo.png si quieres reemplazar el placeholder.")
