"""Кадры ЛР 3 «Библиотеки программы»: python3 shoot3.py mac|linux|win.

mac — VS Code на этом Mac (профиль /private/tmp/vsc-lab2, порт 9362).
linux — VS Code для Linux в контейнере sp-lab2-linux с виртуальным экраном, порт 9363 проброшен наружу.
Рамки пишутся в marks.json (координаты в точках страницы), рисует mark.py."""
import asyncio, json, shutil, subprocess, sys, time
from pathlib import Path
from lab2 import *

OS = sys.argv[1]
MARKS = HERE / 'marks.json'
STAND = Path(f'/private/tmp/sp-lab3/{OS}/03-libraries')
CC = {'mac': 'clang', 'linux': 'gcc', 'win': 'cl'}[OS]
FN = {'mac': 'debug!', 'linux': '', 'win': 'debug.exe!'}[OS]  # так стек вызовов подписывает функции
if OS in ('linux', 'win'):
    async def _open(self, name):
        await self.key('Ctrl+P', 0.8)
        await self.paste(name, 0.8)
        await self.key('Enter', 1.0)
    E.open = _open


def prepare():
    if OS == 'win':
        return  # файлы раскладывает start.cmd внутри ВМ
    shutil.rmtree(STAND, ignore_errors=True)
    (STAND / '.vscode').mkdir(parents=True)
    shutil.copy(HERE / 'src/libs.c', STAND / 'libs.c')
    (STAND / '.vscode').rmdir()


async def rect_rows(e, prefix, upto=None, scope=''):
    """Прямоугольник строк дерева (переменные, стек, точки) от строки с prefix до строки с upto."""
    js = """((p, u, scope) => {
      const rows = [...document.querySelectorAll((scope ? scope + ' ' : '') + '.monaco-list-row')]
        .filter(r => r.getBoundingClientRect().height > 0);
      const t = r => r.textContent.replace(/\\s+/g, ' ').trim();
      const i = rows.findIndex(r => t(r).startsWith(p));
      if (i < 0) return null;
      const j = u ? rows.findIndex((r, k) => k >= i && t(r).startsWith(u)) : i;
      const a = rows[i].getBoundingClientRect(), b = rows[j < 0 ? i : j].getBoundingClientRect();
      const x = a.x + 14;
      return [x, a.y, (a.x < 560 ? Math.min(a.right, 560) : a.right) - x - 6, b.bottom - a.y];
    })(%s, %s, %s)""" % (json.dumps(prefix), json.dumps(upto), json.dumps(scope))
    for _ in range(10):
        r = await e.js(js)
        if r:
            return r
        await asyncio.sleep(0.8)
    rows = await e.js("[...document.querySelectorAll('.monaco-list-row')].map(r => r.textContent.trim()).filter(Boolean)")
    raise SystemExit(f'нет строки {prefix}: {rows[:40]}')


async def rect_ed(e, text, upto=None):
    rows = await e.lines()
    T = lambda r: r[-1].replace('\xa0', ' ')
    i = next((k for k, r in enumerate(rows) if text in T(r)), None)
    if i is None:
        raise SystemExit(f'нет строки редактора {text}: {[T(r) for r in rows]}')
    j = i if upto is None else next(k for k in range(i, len(rows)) if upto in T(rows[k]))
    sel = rows[i:j + 1]
    x = min(r[0] for r in sel); y = sel[0][1]
    return [x, y, max(r[0] + r[2] for r in sel) - x, sel[-1][1] + sel[-1][3] - y]


async def rect_text(e, sel, first, last=None):
    """Строки списка (машинный код, консоль): от первой строки со словом из first до строки со словом из last."""
    return await e.js("""((sel, f, l) => {
      const rows = [...document.querySelectorAll(sel)].filter(r => r.getBoundingClientRect().height > 0);
      const has = (r, ws) => ws.some(w => r.textContent.includes(w));
      let i = rows.findIndex(r => r.classList.contains('focused') || r.querySelector('.codicon-debug-stackframe'));
      if (i < 0 || !has(rows[i], f)) i = rows.findIndex(r => has(r, f));
      if (i < 0) return null;
      let j = i; if (l) { j = rows.findIndex((r, k) => k > i && has(r, l)); if (j < 0) j = i; }
      const a = rows[i].getBoundingClientRect(), b = rows[j].getBoundingClientRect();
      const right = Math.max(...rows.slice(i, j + 1).flatMap(ROW => [...(function* (r) { const w = document.createTreeWalker(r, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) if (n.textContent.trim()) yield n; })(ROW)].map(n => { const g = document.createRange(); g.selectNodeContents(n); return g.getBoundingClientRect().right; })));
      const x = a.x + 16; return [x, a.y, Math.min(right, a.right - 8) - x, b.bottom - a.y]; })(%s, %s, %s)""" % (json.dumps(sel), json.dumps(first), json.dumps(last)))


async def rect_disasm(e):
    """Три рамки машинного кода строки 10: загрузка x и y, умножение, запись в s."""
    return await e.js("""(() => {
      const rows = [...document.querySelectorAll('.disassembly-view .monaco-list-row')].filter(r => r.getBoundingClientRect().height > 0);
      const m = rows.findIndex(r => /mul/.test(r.textContent));
      const box = (i, j) => { const a = rows[i].getBoundingClientRect(), b = rows[j].getBoundingClientRect();
        const right = Math.max(...rows.slice(i, j + 1).flatMap(ROW => [...(function* (r) { const w = document.createTreeWalker(r, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) if (n.textContent.trim()) yield n; })(ROW)].map(n => { const g = document.createRange(); g.selectNodeContents(n); return g.getBoundingClientRect().right; })));
        return [a.x + 16, a.y, right - a.x - 16, b.bottom - a.y]; };
      const s = /ldr/.test(rows[m - 2].textContent) ? m - 2 : m - 1;
      return [box(s, m - 1), box(m, m), box(m + 1, m + 1)]; })()""")


async def rect_css(e, sel):
    return await e.js("""(() => { const el = [...document.querySelectorAll(%s)].find(x => x.getBoundingClientRect().width > 0);
      if (!el) return null; const r = el.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })()""" % json.dumps(sel))


async def rect_term(e, text):
    rows = await e.rows()
    for r in rows:
        if text in r[-1].replace('\xa0', ' ') and r[3] > 0:
            return [r[0], r[1], r[2], r[3]]
    raise SystemExit(f'нет строки терминала {text}: {[r[-1] for r in rows if r[-1].strip()]}')


async def frame(e, name, rects):
    await e.move(620, 14, 0.6)
    await asyncio.sleep(1.2)
    out = RAW / OS / f'{name}.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    await e.shot(str(out))
    db = json.loads(MARKS.read_text()) if MARKS.exists() else {}
    db[f'{OS}/{name}'] = rects
    MARKS.write_text(json.dumps(db, ensure_ascii=False, indent=1))


async def collapse(e, prefix):
    pos = await e.js("""((p) => {
      const r = [...document.querySelectorAll('.monaco-list-row')].find(r => r.textContent.replace(/\\s+/g,' ').trim().startsWith(p));
      if (!r || r.getAttribute('aria-expanded') !== 'true') return null;
      const b = (r.querySelector('.monaco-tl-twistie') || r).getBoundingClientRect(); return [b.x + b.width / 2, b.y + b.height / 2]; })(%s)""" % json.dumps(prefix))
    if pos:
        await e.click(*pos, wait=1.0)


async def expand(e, prefix):
    """Раскрыть строку дерева переменных, если она свёрнута."""
    ok = await e.js("""((p) => {
      const r = [...document.querySelectorAll('.monaco-list-row')].find(r => r.textContent.replace(/\\s+/g,' ').trim().startsWith(p));
      if (!r) return 'нет';
      if (r.getAttribute('aria-expanded') === 'true') return 'уже';
      const tw = r.querySelector('.monaco-tl-twistie'); const b = (tw || r).getBoundingClientRect();
      return [b.x + b.width / 2, b.y + b.height / 2]; })(%s)""" % json.dumps(prefix))
    if isinstance(ok, list):
        await e.click(*ok, wait=1.2)
    elif ok == 'нет':
        raise SystemExit(f'нет строки дерева {prefix}')


async def debug_cmd(e, cmd, wait=2.5):
    await e.palette(cmd, wait)



LIB = {'mac': ('libpcap.dylib', 'pcap_lib_version', 'pcap'),
       'linux': ('libsqlite3.so.0', 'sqlite3_libversion', 'sqlite'),
       'win': ('winsqlite3.dll', 'sqlite3_libversion', 'winsqlite3')}[OS]
BUILD = {'mac': 'clang -o libs libs.c && ./libs',
         'linux': 'gcc -o libs libs.c -lm && ./libs',
         'win': 'cl /nologo libs.c && libs.exe'}[OS]
DEPS = {'mac': 'otool -L libs', 'linux': 'ldd libs', 'win': 'dumpbin /nologo /dependents libs.exe | findstr /i .dll'}[OS]
PYDEPS = {'mac': 'otool -L "$(python3 -c \'import sys; print(sys.executable)\')"',
          'linux': 'ldd "$(which python3)"',
          'win': 'for /f "delims=" %p in (\'python -c "import sys; print(sys.executable)"\') do dumpbin /nologo /dependents "%p" | findstr /i .dll'}[OS]
PY = 'python' if OS == 'win' else 'python3'


COUNT = {'mac': "vmmap $P | grep -o '/[^ ]*\\.dylib' | sort -u | wc -l",
         'linux': "grep -o '/[^ ]*\\.so[^ ]*' /proc/$P/maps | sort -u | wc -l",
         'win': 'powershell -c "(Get-Process -Id %P%).Modules.Count"'}[OS]
FIND = {'mac': "vmmap $P | grep -o '/[^ ]*pcap[^ ]*' | sort -u",
        'linux': "grep -o '/[^ ]*sqlite[^ ]*' /proc/$P/maps | sort -u",
        'win': 'tasklist /m winsqlite3.dll /fi "PID eq %P%"'}[OS]
KEY = {'mac': "dylib'", 'linux': "so[^ ]*'", 'win': 'Count"'}[OS]
FOUND = {'mac': '/usr/lib/libpcap', 'linux': '-gnu/libsqlite3', 'win': 'python.exe'}[OS]


async def rect_next(e, text):
    """Первая строка-число после строки с text: результат подсчёта."""
    rows = [r for r in await e.rows() if r[3] > 0]
    T = lambda r: r[-1].replace('\xa0', ' ')
    k = max(i for i, r in enumerate(rows) if text in T(r))
    r = next(r for r in rows[k + 1:] if T(r).strip().isdigit())
    return [r[0], r[1], r[2], r[3]]


async def last_rows(e):
    return [r for r in await e.rows() if r[3] > 0 and r[-1].strip()]


async def main():
    prepare()
    if OS == 'mac':
        profile('lab3', 9364)
        cdp.launch(str(STAND))
    elif OS == 'linux':
        profile('lab3-linux', 9363, {
            'terminal.integrated.defaultProfile.linux': 'bash',
            'terminal.integrated.profiles.linux': {'bash': {'path': '/bin/bash', 'args': ['--norc']}},
            'terminal.integrated.env.linux': {'PS1': '\\W $ '},
            'window.titleBarStyle': 'custom'})
        launch_linux()
    else:
        launch_win()
    await asyncio.sleep(5)
    async with E() as e:
        await e.size(1240, 820)
        await e.send('Emulation.setFocusEmulationEnabled', enabled=True)
        await asyncio.sleep(1.5)
        await e.open('libs.c')
        await e.palette('Terminal: Create New Terminal', 3)
        clear = 'cls' if OS == 'win' else 'clear'

        # 1. Сборка и запуск
        await e.term_type(clear, 0.8)
        await e.term_type(BUILD, 12 if OS == 'win' else 4)
        await frame(e, '01-build', [await rect_ed(e, '#include <math.h>'), await rect_term(e, BUILD[:10]), await rect_term(e, 'sqrt(2) =')])

        # 2. Библиотеки файла
        await e.term_type(clear, 0.8)
        await e.term_type(DEPS, 6 if OS == 'win' else 3)
        marks = {'mac': [('libs:',), ('libSystem',)], 'linux': [('libm.so',), ('libc.so',)],
                 'win': [('KERNEL32.dll',)]}[OS]
        await frame(e, '02-deps', [await rect_term(e, DEPS[:9])] + [await rect_term(e, m[0]) for m in marks])

        # 3. Библиотеки интерпретатора Python
        await e.palette('View: Toggle Maximized Panel', 1.0)
        await e.palette('View: Close Primary Side Bar', 1.0)
        await e.term_type(clear, 0.8)
        await e.term_type(PYDEPS, 6 if OS == 'win' else 3)
        marks = {'mac': ['Python3 (', 'libSystem'], 'linux': ['libz.so', 'libc.so'], 'win': ['python314.dll', 'KERNEL32.dll']}[OS]
        await frame(e, '03-python-deps', [await rect_term(e, m) for m in marks])

        # 4. Python в первом терминале: номер процесса
        await e.term_type(clear, 0.8)
        await e.term_type(PY, 3)
        await e.term_type('import os', 1)
        await e.term_type('os.getpid()', 1.5)
        rows = await last_rows(e)
        pid = next(r[-1].strip() for r in reversed(rows) if r[-1].strip().isdigit())
        await frame(e, '04-pid', [await rect_term(e, 'os.getpid()'), await rect_term(e, pid)])

        # 5. Во втором терминале: сколько библиотек и нет нужной
        await e.palette('Terminal: Split Terminal', 3)
        await e.term_type(clear, 0.8)
        await e.term_type(f'set P={pid}' if OS == 'win' else f'P={pid}', 0.8)
        await e.term_type(COUNT, 6 if OS != 'linux' else 2)
        await e.term_type(FIND, 6 if OS != 'linux' else 2)
        await frame(e, '05-before', [await rect_term(e, 'P=' + pid), await rect_next(e, KEY), await rect_term(e, {'mac': 'pcap[', 'linux': 'sqlite[', 'win': 'eq %P%"'}[OS])])

        # 6. В Python: загрузить библиотеку и вызвать функцию
        await e.palette('Terminal: Focus Previous Terminal in Terminal Group', 1.0)
        await e.term_type('import ctypes', 1.5)
        await e.term_type(f'lib = ctypes.CDLL("{LIB[0]}")', 1.5)
        await e.term_type(f'lib.{LIB[1]}.restype = ctypes.c_char_p', 1)
        await e.term_type(f'lib.{LIB[1]}()', 1.5)
        await frame(e, '06-load', [await rect_term(e, 'lib = ctypes.CDLL'), await rect_term(e, f'lib.{LIB[1]}()'), await rect_term(e, "b'")])

        # 7. Снова во втором терминале
        await e.palette('Terminal: Focus Next Terminal in Terminal Group', 1.0)
        await e.term_type(clear, 0.8)
        await e.term_type(COUNT, 6 if OS != 'linux' else 2)
        await e.term_type(FIND, 6 if OS != 'linux' else 2)
        await frame(e, '07-after', [await rect_next(e, KEY), await rect_term(e, FOUND)])
    await stop()


def launch_win():
    """VS Code в ВМ Win11-lab: start.cmd с хоста, порт 9365 гостя → 9366 (portproxy) → 9365 хоста (NAT)."""
    sys.path.insert(0, str(Path.home() / 'sysprog_makarov/tools'))
    import w  # noqa: F401  ввод в ВМ скан-кодами
    cdp.PORT = 9365
    vm = w.vm
    subprocess.run(['VBoxManage', 'controlvm', 'Win11-lab', 'natpf1', 'cdp,tcp,127.0.0.1,9365,,9366'], capture_output=True)
    vm.key('win+r'); time.sleep(1.5)
    vm.text(r'cmd /c curl.exe --noproxy * -s -o %TEMP%\st3.cmd http://10.0.2.2:8811/start3.cmd && %TEMP%\st3.cmd')
    vm.key('enter')
    time.sleep(12)  # start.cmd сначала закрывает прежний VS Code
    for _ in range(90):
        try:
            if cdp.page_ws():
                return
        except OSError:
            pass
        time.sleep(1)
    raise SystemExit('порт отладки VS Code в ВМ не открылся')


async def stop():
    if OS == 'win':
        return  # окно VS Code в ВМ закрывается вручную или следующим запуском
    if OS == 'mac':
        subprocess.run(['pkill', '-f', f'user-data-dir={cdp.PROFILE}/data'])
    else:
        subprocess.run(['docker', 'rm', '-f', 'sp-lab3-vsc'], capture_output=True)


def launch_linux():
    """VS Code для Linux в контейнере: виртуальный экран Xvfb, порт отладки наружу через socat."""
    subprocess.run(['docker', 'rm', '-f', 'sp-lab3-vsc'], capture_output=True)
    inner = ('Xvfb :99 -screen 0 1600x1000x24 >/dev/null 2>&1 & export DISPLAY=:99; sleep 1; '
             'socat TCP-LISTEN:9364,fork,reuseaddr TCP:127.0.0.1:9363 & '
             'dbus-launch code --no-sandbox --disable-gpu --user-data-dir /home/user/vsc/data '
             '--extensions-dir /home/user/vsc/ext --remote-debugging-port=9363 /home/user/03-libraries; sleep infinity')
    subprocess.run(['docker', 'run', '-d', '--name', 'sp-lab3-vsc', '--hostname', 'lab-linux',
                    '--shm-size', '1g', '--cap-add', 'SYS_PTRACE', '--security-opt', 'seccomp=unconfined', '-p', '127.0.0.1:9363:9364',
                    '-v', f'{STAND}:/home/user/03-libraries', '-v', f'{cdp.PROFILE}:/home/user/vsc',
                    'sp-lab2-linux', 'bash', '-c', inner], check=True, capture_output=True)
    for _ in range(60):
        try:
            if cdp.page_ws():
                return
        except OSError:
            pass
        time.sleep(1)
    raise SystemExit('порт отладки VS Code в контейнере не открылся')


asyncio.run(main())
