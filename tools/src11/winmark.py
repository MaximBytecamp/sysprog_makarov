"""Рамки на кадрах командной строки Windows (шрифт консоли 8×16, первая строка — y=47)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
SRC = Path.home() / 'sysprog-shots/win'
OUT = Path(sys.argv[1]) / 'win'; OUT.mkdir(parents=True, exist_ok=True)
RED = (229, 40, 40); F = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 22)
# кадр: (имя в главе, высота обрезки, [(строка, строк, столбцов)])
SPEC = {
 'w01-sizes': ('01-sizes', 250, [(4, 1, 10), (5, 1, 10), (6, 1, 10), (8, 1, 10)]),
 'w02-sysinfo': ('02-uname', 200, [(2, 3, 14), (5, 1, 14)]),
 'w03-hostbuf': ('03-hostbuf', 200, [(3, 1, 59), (5, 1, 29), (6, 1, 26)]),
 'w04-errors': ('04-errors', 160, [(3, 1, 47), (4, 1, 47)]),
 'w07-info': ('07-info', 230, [(4, 4, 18), (8, 1, 13)]),
 'w08-warning': ('08-warning', 220, [(2, 2, 97), (4, 1, 79)]),
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
