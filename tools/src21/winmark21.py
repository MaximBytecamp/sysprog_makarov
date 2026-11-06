"""Рамки на кадре win/05-brain главы 2.1: снимок экрана ВМ 800×600 (без протокола отладки — сеть ВМ не работала).
python3 winmark21.py <папка img главы>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

RAW = Path.home() / 'sysprog-shots/m21/raw/win/05-brain-vm.png'
RECTS = [(72, 90, 505, 17), (85, 251, 122, 17), (85, 270, 150, 142)]
RED = (229, 40, 40)
F = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 15)

im = Image.open(RAW).convert('RGB')
d = ImageDraw.Draw(im)
for n, (x, y, w, h) in enumerate(RECTS, 1):
    x0, y0, x1, y1 = x - 3, y - 1, x + w + 3, y + h + 1
    d.rectangle([x0, y0, x1, y1], outline=RED, width=3)
    b = 20; bx, by = x1 + 4, y0 + (y1 - y0 - b) / 2
    d.rectangle([bx, by, bx + b, by + b], fill=RED)
    d.text((bx + (b - d.textlength(str(n), font=F)) / 2, by + 1), str(n), font=F, fill='white')
dst = Path(sys.argv[1]) / 'win/05-brain.png'
im.save(dst, optimize=True)
print(dst, im.size)
