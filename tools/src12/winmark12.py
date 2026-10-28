"""Рамки на кадрах командной строки Windows (шрифт консоли 8×16, первая строка — y=47)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
SRC = Path.home() / 'sysprog-shots/win'
OUT = Path(sys.argv[1]) / 'win'; OUT.mkdir(parents=True, exist_ok=True)
RED = (229, 40, 40); F = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 22)
# кадр: (имя в главе, высота обрезки, [(строка, строк, столбцов)])
SPEC = {
 'w12-01-build': ('01-build', 200, [(2, 1, 67), (5, 1, 15)]),
 'w12-02-exports': ('02-exports', 380, [(12, 2, 33), (17, 1, 45)]),
 'w12-03-load': ('03-load', 150, [(1, 1, 97), (3, 1, 40)]),
 'w12-04-struct': ('04-struct', 170, [(1, 1, 10), (2, 4, 30)]),
 'w12-05-call': ('05-call', 160, [(2, 1, 36), (5, 1, 24)]),
 'w12-06-swap': ('06-swap', 170, [(3, 2, 16)]),
 'w12-07-null': ('07-null', 130, [(1, 1, 32)]),
 'w12-08-brain': ('08-brain', 230, [(1, 8, 26)]),
 'w12-arm': ('09-arm', 290, [(1, 1, 6), (6, 1, 49), (11, 1, 57)]),
}
for src, (name, h, marks) in SPEC.items():
    im = Image.open(SRC / f'{src}.png').convert('RGB').crop((0, 0, 778, h))
    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for n, (row, rows, cols) in enumerate(marks, 1):
        x0, y0 = 0, (47 + 16 * row) * 2 - 3
        x1, y1 = min(cols * 8 * 2 + 6, im.width - 4), (47 + 16 * (row + rows)) * 2 + 4
        d.rectangle([x0 + 1, y0, x1, y1], outline=RED, width=4)
        bx, by = x1 + 6, (y0 + y1) // 2 - 15
        if bx + 32 > im.width: bx, by = x1 - 34, y1 + 4
        d.rectangle([bx, by, bx + 30, by + 30], fill=RED)
        d.text((bx + 15 - d.textlength(str(n), font=F) / 2, by + 3), str(n), font=F, fill='white')
    im.save(OUT / f'{name}.png', optimize=True); print(OUT / f'{name}.png', im.size)
