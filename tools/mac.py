"""Съёмка ЛР 1 на macOS: Терминал слева, Мониторинг системы справа; снимок области двух окон."""
import subprocess, sys, time
OUT = '/Users/makarovmn/sysprog-shots/mac/'
L = (0, 38, 735, 760)      # Терминал
R = (735, 38, 1470, 760)   # Мониторинг системы

def osa(script):
    r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if r.returncode: print('OSA ERR', r.stderr.strip())
    return r.stdout.strip()

def shot(name, rect=(0, 38, 1470, 722)):
    x, y, w, h = rect
    subprocess.run(['screencapture', '-x', f'-R{x},{y},{w},{h}', OUT + name + '.png'])

def term(cmd):
    osa(f'tell application "Terminal" to do script "{cmd}" in front window')

def keys(k, mods=''):
    m = f' using {{{mods}}}' if mods else ''
    osa(f'tell application "System Events" to keystroke "{k}"{m}')

def keycode(c, mods=''):
    m = f' using {{{mods}}}' if mods else ''
    osa(f'tell application "System Events" to key code {c}{m}')

def front(app):
    osa(f'tell application "{app}" to activate'); time.sleep(0.8)

if __name__ == '__main__':
    exec(sys.argv[1])
