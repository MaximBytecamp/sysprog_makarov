"""Рамки с номерами на кадрах ЛР 8. python3 mark6.py <папка img страницы>

Сырые кадры — ~/sysprog-shots/raw/lab8/<система>: Linux — ВМ 1280×800 (координаты сняты с копии шириной 1200
и пересчитываются), macOS — склейки окон из src_lab6_mac.py (координаты в пикселях самого кадра). Координаты — marks8.json."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

RAW = Path.home() / 'sysprog-shots/raw/lab8'
OUT = Path(sys.argv[1])
RED = (229, 40, 40)
F = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 15)

for key, rects in json.loads((Path(__file__).parent / 'marks8.json').read_text()).items():
    os_, name = key.split('/')
    im = Image.open(RAW / os_ / f'{name}.png').convert('RGB')
    d = ImageDraw.Draw(im)
    k = im.width / 1200 if os_ == 'linux' else 1
    for n, r in enumerate(rects, 1):
        x, y, w, h = (v * k for v in r)
        x0, y0, x1, y1 = x - 3, y - 1, x + w + 3, y + h + 1
        d.rectangle([x0, y0, x1, y1], outline=RED, width=3)
        t = str(n); b = 20
        bx, by = x1 + 4, y0 + (y1 - y0 - b) / 2
        if bx + b > im.width: bx = x0 - b - 4
        d.rectangle([bx, by, bx + b, by + b], fill=RED)
        d.text((bx + (b - d.textlength(t, font=F)) / 2, by + 1), t, font=F, fill='white')
    dst = OUT / os_ / f'{name}.png'
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, optimize=True)
    print(dst, im.size)
