from PIL import Image, ImageDraw
import os

OUT = os.path.join('static', 'img')
if not os.path.exists(OUT):
    os.makedirs(OUT, exist_ok=True)

W = 512
H = 256
img = Image.new('RGBA', (W, H), (255,255,255,0))
d = ImageDraw.Draw(img)

# Truck body
body_color = (12, 108, 199, 255)  # blue
cab_color = (12, 108, 199, 255)
wheel_color = (0,0,0,255)
window_color = (255,255,255,180)

# cargo rectangle
d.rounded_rectangle([(40,40),(380,170)], radius=12, fill=body_color)
# cab
d.rounded_rectangle([(380,70),(480,150)], radius=10, fill=cab_color)
# window
d.rectangle([(395,80),(455,130)], fill=window_color)
# wheels
d.ellipse([(80,150),(140,210)], fill=wheel_color)
d.ellipse([(340,150),(400,210)], fill=wheel_color)
# wheel highlights
d.ellipse([(100,170),(120,190)], fill=(255,255,255,50))

# speed lines left
for i,off in enumerate([10,30,50]):
    d.line([(10,60+i*6),(40,60+i*6)], fill=body_color, width=8)

# save as PNG
path = os.path.join(OUT, 'truck.png')
img.save(path)
print('Wrote', path)
