"""Красные рамки с номерами поверх кадров (стиль ЛР 1). python3 mark.py <выходная папка>"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

RAW = Path(__file__).parent / 'raw'
OUT = Path(sys.argv[1])
RED = (229, 40, 40)
F = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 26)
S = 2  # плотность кадра

for key, rects in json.loads((Path(__file__).parent / 'marks.json').read_text()).items():
    os_, name = key.split('/')
    im = Image.open(RAW / os_ / f'{name}.png').convert('RGB')
    d = ImageDraw.Draw(im)
    for n, (x, y, w, h) in enumerate(rects, 1):
        x0, y0, x1, y1 = (x - 5) * S, (y - 2) * S, (x + w + 5) * S, (y + h + 2) * S
        d.rectangle([x0, y0, x1, y1], outline=RED, width=5)
        t = str(n); bw = 34; bh = 34
        bx, by = x1 + 6, y0 + (y1 - y0 - bh) // 2
        if bx + bw > im.width: bx = x0 - bw - 6
        d.rectangle([bx, by, bx + bw, by + bh], fill=RED)
        tw = d.textlength(t, font=F)
        d.text((bx + (bw - tw) / 2, by + 3), t, font=F, fill='white')
    dst = OUT / os_ / f'{name}.png'
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS)
    im.save(dst, optimize=True)
    print(dst, im.size)
