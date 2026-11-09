"""Кадры macOS для ЛР 5: два окна Терминала одно над другим — сверху fs_usage, снизу команды; снимок обоих окон по номеру.
python3 mac5.py open — открыть окна; python3 mac5.py <кадр> — снять. Нужно правило sudoers для /usr/bin/fs_usage.
Нижнее окно получает обычный PATH нового Mac: иначе pyenv засыпает запись строками своих bash."""
import re, subprocess, sys, time
from pathlib import Path
from PIL import Image

OUT = Path.home() / 'sysprog-shots/raw/lab5/mac'
IDS = Path(__file__).with_name('mac5.ids')
PATH = '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'


def osa(s):
    r = subprocess.run(['osascript', '-e', s], capture_output=True, text=True)
    if r.returncode:
        print('OSA', r.stderr.strip())
    return r.stdout.strip()


def new_win(bounds):
    wid = re.search(r'window id (\d+)', osa('tell application "Terminal" to do script ""')).group(1)
    osa(f'tell application "Terminal" to set bounds of window id {wid} to {{{bounds}}}')
    return wid


def run(wid, cmd):
    cmd = cmd.replace('\\', '\\\\').replace('"', '\\"')
    osa(f'tell application "Terminal" to do script "{cmd}" in window id {wid}')


def ctrl_c(wid):
    osa(f'''tell application "Terminal" to set index of window id {wid} to 1
tell application "Terminal" to activate
delay 0.3
tell application "System Events" to keystroke "c" using control down''')


def text(wid):
    return osa(f'tell application "Terminal" to get history of selected tab of window id {wid}')


def grab(wid, path):
    subprocess.run(['screencapture', '-x', '-o', f'-l{wid}', str(path)])


def shot(name, top, bottom):
    OUT.mkdir(parents=True, exist_ok=True)
    grab(top, OUT / '_t.png'); grab(bottom, OUT / '_b.png')
    a, b = Image.open(OUT / '_t.png'), Image.open(OUT / '_b.png')
    W = Image.new('RGB', (max(a.width, b.width) + 16, a.height + b.height + 36), (236, 234, 228))
    W.paste(a, (8, 12), a); W.paste(b, (8, a.height + 24), b)
    W = W.resize((W.width // 2, W.height // 2), Image.LANCZOS)
    W.save(OUT / f'{name}.png'); print(name, W.size)


if __name__ == '__main__':
    if sys.argv[1] == 'open':
        top = new_win('20, 40, 1260, 520')
        bottom = new_win('20, 540, 1260, 760')
        run(bottom, f'export PATH={PATH}; clear')
        IDS.write_text(f'{top} {bottom}')
        print(top, bottom)
    else:
        top, bottom = IDS.read_text().split()
        shot(sys.argv[1], top, bottom)
