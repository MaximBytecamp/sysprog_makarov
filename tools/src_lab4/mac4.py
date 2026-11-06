"""Кадры macOS для ЛР 4: Терминал слева, Мониторинг системы справа (иерархический вид), снимок двух окон по номеру.
python3 mac4.py <имя кадра> [команда в Терминал] [поиск в Мониторинге]. Окна должны быть на текущем рабочем столе."""
import subprocess, sys, time
from pathlib import Path
from PIL import Image
import Quartz

OUT = Path.home() / 'sysprog-shots/raw/lab4/mac'
TERM_ID = 33058


def osa(s):
    r = subprocess.run(['osascript', '-e', s], capture_output=True, text=True)
    if r.returncode:
        print('OSA', r.stderr.strip())
    return r.stdout.strip()


def am_win():
    for w in Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID):
        if w.get('kCGWindowLayer') == 0 and w.get('kCGWindowName') == 'Мониторинг системы' and w['kCGWindowBounds']['X'] >= 0:
            return w


def am_id():
    w = am_win()
    if not w:
        return None
    on = {x['kCGWindowNumber'] for x in Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)}
    return w['kCGWindowNumber'] if TERM_ID in on else None


def expand_all():
    """Option-щелчок по треугольнику первой строки раскрывает всё дерево."""
    b = am_win()['kCGWindowBounds']
    x, y = b['X'] + 14, b['Y'] + 97
    for t in (Quartz.kCGEventLeftMouseDown, Quartz.kCGEventLeftMouseUp):
        e = Quartz.CGEventCreateMouseEvent(None, t, (x, y), Quartz.kCGMouseButtonLeft)
        Quartz.CGEventSetFlags(e, Quartz.kCGEventFlagMaskAlternate)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, e)
        time.sleep(0.1)


def focus():
    subprocess.run(['open', '-a', 'Activity Monitor'])
    for _ in range(30):
        if am_id():
            break
        time.sleep(0.3)
    time.sleep(0.8)


def term(cmd):
    osa(f'tell application "Terminal" to do script "{cmd}" in window id {TERM_ID}')


def search(text):
    osa(f'set the clipboard to "{text}"')
    osa(f'''tell application "Activity Monitor" to activate
delay 0.5
tell application "System Events" to tell process "Activity Monitor"
  click menu item "Фильтровать процессы" of menu 1 of menu bar item "Вид" of menu bar 1
  delay 0.3
  keystroke "a" using command down
  key code 9 using command down
end tell''')


def expand():
    osa('''tell application "Activity Monitor" to activate
delay 0.4
tell application "System Events" to tell process "Activity Monitor"
  key code 48
  delay 0.3
  key code 125
  delay 0.3
  key code 126
  delay 0.3
  repeat 6 times
    key code 124
    delay 0.25
    key code 125
    delay 0.25
  end repeat
  key code 126 using option down
end tell''')


def grab(name, refocus=True):
    if refocus:
        focus()
    parts = []
    for i, wid in enumerate((TERM_ID, am_id())):
        p = OUT / f'_{i}.png'
        subprocess.run(['screencapture', '-x', '-o', f'-l{wid}', str(p)], check=True)
        parts.append(Image.open(p))
    a, b = parts
    H = max(a.height, b.height)
    W = Image.new('RGB', (a.width + b.width + 24, H + 24), (236, 234, 228))
    W.paste(a, (8, 12), a if a.mode == 'RGBA' else None)
    W.paste(b, (a.width + 16, 12), b if b.mode == 'RGBA' else None)
    W = W.resize((W.width // 2, W.height // 2), Image.LANCZOS)
    W.save(OUT / f'{name}.png')
    print(name, W.size)


if __name__ == '__main__':
    name = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2]:
        term(sys.argv[2]); time.sleep(2)
    if len(sys.argv) > 3:
        focus(); search(sys.argv[3]); time.sleep(6)
        focus(); expand_all(); time.sleep(1.0)
        grab(name, refocus=False); sys.exit()
    grab(name)
