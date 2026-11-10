"""Кадры macOS для ЛР 6: Терминал слева, Мониторинг системы справа; окно «История ЦП» — отдельным кадром.
python3 src_lab6_mac.py <кадр> [команда в Терминал] [пауза]"""
import re, subprocess, sys, time
from pathlib import Path
from PIL import Image
import Quartz

OUT = Path.home() / 'sysprog-shots/raw/lab6/mac'
IDS = Path('/private/tmp/lab6mac.ids')


def osa(s):
    r = subprocess.run(['osascript', '-e', s], capture_output=True, text=True)
    if r.returncode:
        print('OSA', r.stderr.strip())
    return r.stdout.strip()


def wins(owner):
    return [w for w in Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
            if (w.get('kCGWindowOwnerName') or '').startswith(owner) and w.get('kCGWindowLayer') == 0]


def grab(wid, path):
    subprocess.run(['screencapture', '-x', '-o', f'-l{wid}', str(path)])


def term(cmd, wid):
    cmd = cmd.replace('\\', '\\\\').replace('"', '\\"')
    osa(f'tell application "Terminal" to do script "{cmd}" in window id {wid}')


def setup():
    t = re.search(r'window id (\d+)', osa('tell application "Terminal" to do script ""')).group(1)
    osa(f'tell application "Terminal" to set bounds of window id {t} to {{0, 30, 700, 560}}')
    term('export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin; clear', t)
    IDS.write_text(t)
    return t


def front_am(search=None):
    subprocess.run(['open', '-a', 'Activity Monitor'])
    time.sleep(1.5)
    if search is not None:
        osa(f'set the clipboard to "{search}"')
        osa('''tell application "System Events" to tell process "Activity Monitor"
  click menu item "Фильтровать процессы" of menu 1 of menu bar item "Вид" of menu bar 1
  delay 0.3
  keystroke "a" using command down
  key code 9 using command down
end tell''')
    time.sleep(2.5)


def flat():
    osa('''tell application "System Events" to tell process "Activity Monitor"
  click menu item "Все процессы" of menu 1 of menu bar item "Вид" of menu bar 1
end tell''')


def pair(name, t, title='Мониторинг системы'):
    for _ in range(4):
        am = [w for w in wins('Мониторинг') if title in (w.get('kCGWindowName') or '')]
        if am:
            break
        subprocess.run(['open', '-a', 'Activity Monitor']); time.sleep(2)
    grab(t, OUT / '_t.png'); grab(am[0]['kCGWindowNumber'], OUT / '_m.png')
    a, b = Image.open(OUT / '_t.png'), Image.open(OUT / '_m.png')
    H = max(a.height, b.height)
    W = Image.new('RGB', (a.width + b.width + 24, H + 24), (236, 234, 228))
    W.paste(a, (8, 12), a); W.paste(b, (a.width + 16, 12), b)
    W = W.resize((W.width // 2, W.height // 2), Image.LANCZOS)
    W.save(OUT / f'{name}.png'); print(name, W.size)


def history(name, t):
    osa('tell application "System Events" to tell process "Activity Monitor" to keystroke "3" using command down')
    time.sleep(4)
    pair(name, t, 'ЦП')
    return
    h = [w for w in wins('Мониторинг') if 'ЦП' in (w.get('kCGWindowName') or '') and w.get('kCGWindowName') != 'Мониторинг системы']
    grab(h[0]['kCGWindowNumber'], OUT / f'{name}.png')
    im = Image.open(OUT / f'{name}.png'); im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS); im.save(OUT / f'{name}.png')
    print(name, im.size, h[0].get('kCGWindowName'))
