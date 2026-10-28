"""Рамки на кадрах n8n и Mailpit (координаты в точках страницы, плотность 2)."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
RAW = Path(__file__).parent / 'raw'
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
RED = (229, 40, 40); F = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 26); S = 2
for name, rects in json.loads((Path(__file__).parent / 'marks.json').read_text()).items():
    im = Image.open(RAW / f'{name}.png').convert('RGB'); d = ImageDraw.Draw(im)
    for n, (x, y, w, h) in enumerate(rects, 1):
        x0, y0, x1, y1 = (x - 4) * S, (y - 3) * S, (x + w + 4) * S, (y + h + 3) * S
        d.rectangle([x0, y0, x1, y1], outline=RED, width=5)
        bx, by = x1 + 6, y0 + (y1 - y0 - 34) // 2
        if bx + 34 > im.width: bx = x0 - 40
        if bx < 0: bx, by = x1 - 38, y1 + 6
        d.rectangle([bx, by, bx + 34, by + 34], fill=RED)
        d.text((bx + 17 - d.textlength(str(n), font=F) / 2, by + 3), str(n), font=F, fill='white')
    im = im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS)
    im.save(OUT / f'{name}.png', optimize=True)
print(len(list(OUT.glob('*.png'))))
