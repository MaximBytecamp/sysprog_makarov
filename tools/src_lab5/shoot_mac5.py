"""Съёмка пяти кадров macOS ЛР 5 (mac5.py open — до запуска; в нижнем окне уже запущен bash).
Команду в нижнее окно и остановку fs_usage выполняет фоновый zsh: fs_usage по умолчанию не пишет события zsh,
поэтому сама съёмка в запись не попадает. Шумные процессы (Docker, VS Code, launchd) исключены списком после -e."""
import subprocess, tempfile, time
from pathlib import Path
import mac5
T, B = mac5.IDS.read_text().split()
NOISE = '"Code Helper (Plugin)" "Docker Desktop" claude launchd xpcproxy Yandex'


def frame(name, cmd, mode='exec', wait=1.5, pipe=''):
    mac5.run(B, 'clear')
    mac5.run(T, f'clear; sudo fs_usage -e -f {mode} {NOISE}{pipe}')
    esc = cmd.replace('\\', '\\\\').replace('"', '\\"')
    scpt = Path(tempfile.mkdtemp()) / 'cmd.scpt'
    scpt.write_text(f'tell application "Terminal" to do script "{esc}" in window id {B}\n')
    subprocess.run(['zsh', '-c', f'sleep 4; osascript {scpt}; sleep {wait}; pkill -TERM -f "^sudo fs_usage"'])
    time.sleep(1)
    mac5.shot(name, T, B)


def libs(name):
    """Шаг 2: запись в файл, остановка Ctrl+C в верхнем окне (так fs_usage дописывает буфер), затем grep."""
    mac5.run(B, 'clear')
    mac5.run(T, f'clear; rm -f fs.txt; sudo fs_usage -e -f pathname > fs.txt')
    scpt = Path(tempfile.mkdtemp()) / 'cmd.scpt'
    scpt.write_text(f'''tell application "Terminal" to do script "hostname" in window id {B}
delay 1.5
tell application "Terminal"
  set index of window id {T} to 1
  activate
end tell
delay 0.5
tell application "System Events" to keystroke "c" using control down
delay 1.5
tell application "Terminal" to do script "clear; grep 'hostname\\\\.' fs.txt | head -26" in window id {T}
''')
    subprocess.run(['zsh', '-c', f'sleep 4; osascript {scpt}'])
    time.sleep(2)
    mac5.shot(name, T, B)


import sys
only = sys.argv[1:]
for n, f in [('01-birth', lambda: frame('01-birth', 'echo $$; hostname')),
             ('02-libs', lambda: frame('02-libs', 'hostname', mode='pathname', wait=6, pipe=' | grep hostname')),
             ('03-exit', lambda: frame('03-exit', "bash -c 'exit 7'; echo code $?")),
             ('04-path', lambda: frame('04-path', 'env nosuch; echo code $?')),
             ('05-python', lambda: frame('05-python', '''python3 -c "import subprocess; r = subprocess.run(['hostname'], capture_output=True); print('code', r.returncode)"''', wait=2.5))]:
    if not only or n in only:
        f()
