from PIL import Image
import os

"""
Usage:
1. Put your truck image (the one you attached) as `static/img/truck.png` (or .jpg/.jpeg).
2. Run this script from the project root inside the virtualenv:
   & ".\venv\Scripts\Activate.ps1"; python tools\generate_favicon.py
3. The script will create these files under `static/img/`:
   - favicon.ico (contains multiple sizes)
   - favicon-16.png
   - favicon-32.png

This helps browsers pick an appropriately sized favicon.
"""

SRC = os.path.join('static', 'img', 'truck.png')
OUT_DIR = os.path.join('static', 'img')

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR, exist_ok=True)

if not os.path.exists(SRC):
    print(f"Source image not found: {SRC}")
    print("Place your attached truck image at that path (e.g. save it as truck.png) and re-run this script.")
    raise SystemExit(1)

sizes = [(16,16),(32,32),(48,48),(64,64),(128,128)]

img = Image.open(SRC)
# convert to RGBA to preserve transparency if any
if img.mode not in ('RGBA','RGB'):
    img = img.convert('RGBA')

# create PNGs
for w,h in [(16,16),(32,32)]:
    fn = os.path.join(OUT_DIR, f'favicon-{w}.png')
    im = img.copy()
    im.thumbnail((w,h), Image.LANCZOS)
    # ensure exact size by pasting onto transparent background
    canvas = Image.new('RGBA', (w,h), (255,255,255,0))
    canvas.paste(im, ((w-im.width)//2, (h-im.height)//2), im if im.mode=='RGBA' else None)
    canvas.save(fn)
    print('Wrote', fn)

# create multi-size ICO (Windows style icon)
ico_path = os.path.join(OUT_DIR, 'favicon.ico')
icon_sizes = [(16,16),(32,32),(48,48),(64,64),(128,128)]
imgs_for_ico = []
for (w,h) in icon_sizes:
    im = img.copy()
    im.thumbnail((w,h), Image.LANCZOS)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # create square canvas
    canvas = Image.new('RGBA', (w,h), (255,255,255,0))
    canvas.paste(im, ((w-im.width)//2, (h-im.height)//2), im)
    imgs_for_ico.append(canvas)

# Pillow allows saving ICO with multiple sizes by passing a list in "sizes"
# Save as ICO using first image and sizes param
try:
    imgs_for_ico[0].save(io := ico_path, format='ICO', sizes=[(s[0], s[1]) for s in icon_sizes])
    print('Wrote', ico_path)
except Exception as e:
    # fallback: save only 64x64
    imgs_for_ico[0].save(ico_path)
    print('Wrote fallback', ico_path)

print('Done. Add the favicon files to your repo or refresh your browser cache to see changes.')
