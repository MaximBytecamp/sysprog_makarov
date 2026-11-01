"""Кадры ЛР 2 «Программа в отладчике»: python3 shoot.py mac|linux.

mac — VS Code на этом Mac (профиль /private/tmp/vsc-lab2, порт 9362).
linux — VS Code для Linux в контейнере sp-lab2-linux с виртуальным экраном, порт 9363 проброшен наружу.
Рамки пишутся в marks.json (координаты в точках страницы), рисует mark.py."""
import asyncio, json, shutil, subprocess, sys, time
from pathlib import Path
from lab2 import *

OS = sys.argv[1]
MARKS = HERE / 'marks.json'
STAND = Path(f'/private/tmp/sp-lab2/{OS}/02-debugger')
CC = {'mac': 'clang', 'linux': 'gcc'}[OS]
FN = {'mac': 'debug!', 'linux': ''}[OS]  # так стек вызовов подписывает функции
if OS == 'linux':
    async def _open(self, name):
        await self.key('Ctrl+P', 0.8)
        await self.paste(name, 0.8)
        await self.key('Enter', 1.0)
    E.open = _open


def prepare():
    shutil.rmtree(STAND, ignore_errors=True)
    (STAND / '.vscode').mkdir(parents=True)
    shutil.copy(HERE / 'src/debug.c', STAND / 'debug.c')
    for f in ('launch.json', 'tasks.json'):
        shutil.copy(HERE / f'src/vscode-{OS}/{f}', STAND / '.vscode' / f)


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
      return [box(m - 2, m - 1), box(m, m), box(m + 1, m + 1)]; })()""")


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


async def main():
    prepare()
    if OS == 'mac':
        profile('lab2', 9362)
        cdp.launch(str(STAND))
    else:
        profile('lab2-linux', 9363, {
            'terminal.integrated.defaultProfile.linux': 'bash',
            'terminal.integrated.profiles.linux': {'bash': {'path': '/bin/bash', 'args': ['--norc']}},
            'terminal.integrated.env.linux': {'PS1': '\\W $ '},
            'window.titleBarStyle': 'custom'})
        launch_linux()
    await asyncio.sleep(5)
    async with E() as e:
        await e.size(1240, 820)
        await e.send('Emulation.setFocusEmulationEnabled', enabled=True)
        await asyncio.sleep(1.5)
        await e.open('debug.c')

        # 1. Сборка и запуск без отладчика
        await e.palette('Terminal: Create New Terminal', 3)
        await e.term_type('clear', 0.8)
        await e.term_type(f'{CC} -g -O0 -Wall -Wextra -o debug debug.c && ./debug', 4)
        await frame(e, '01-build', [await rect_term(e, f'{CC} -g'), await rect_term(e, 'agent: total')])

        # 2. Настройки запуска
        await e.palette('View: Close Panel', 0.8)
        await e.palette('View: Show Explorer', 0.8)
        await e.open('launch.json')
        await expand(e, '.vscode')
        await frame(e, '02-launch', [await rect_rows(e, '.vscode', 'tasks.json'), await rect_ed(e, '"program"'),
                                     await rect_ed(e, '"MIMode"'), await rect_ed(e, '"preLaunchTask"')])

        # 3. Точка останова
        await e.palette('View: Close All Editors', 0.8)
        await e.open('debug.c')
        await goto(e, 15)
        await e.palette('Debug: Toggle Breakpoint', 0.8)
        await e.palette('View: Show Run and Debug', 1.5)
        await frame(e, '03-breakpoint', [await rect_ed(e, 'struct point p ='), await rect_rows(e, 'debug.c', scope='.debug-breakpoints')])

        # 4. Запуск под отладчиком: остановка на строке 15
        await e.palette('Debug: Start Debugging', 1.5)
        await e.key('Enter', 14)
        # отладчик открывает файл второй вкладкой: остаётся одна
        await e.palette('View: Close All Editors', 1.0)
        await e.palette('View: Close Panel', 0.8)
        await e.palette('View: Show Run and Debug', 1.0)
        r = await rect_rows(e, FN + 'main', scope='.debug-call-stack')
        await e.click(r[0] + 20, r[1] + r[3] / 2, wait=1.5)
        await expand(e, 'Locals')
        await expand(e, 'p')
        await frame(e, '04-paused', [await rect_ed(e, 'struct point p ='), await rect_rows(e, 'Locals', 'a ='),
                                     await rect_rows(e, FN + 'main', scope='.debug-call-stack')])

        # 5. Шаг с обходом: строка 15 выполнена
        await debug_cmd(e, 'Debug: Step Over')
        await frame(e, '05-step', [await rect_ed(e, 'int total = 0;'), await rect_rows(e, 'p', 'y')])

        # 6. strcpy: буквы в массиве name
        await debug_cmd(e, 'Debug: Step Over')
        await debug_cmd(e, 'Debug: Step Over')
        await collapse(e, 'p =')
        await expand(e, 'name')
        await frame(e, '06-strcpy', [await rect_ed(e, 'for (int i'), await rect_rows(e, 'name', '[7]')])

        # 7. Цикл: наблюдение за i и total
        for expr in ('i', 'total'):
            await e.js("[...document.querySelectorAll('.action-label')].find(x => x.getAttribute('aria-label') === 'Add Expression').click()")
            await asyncio.sleep(0.8)
            await e.paste(expr, 0.3)
            await e.key('Enter', 1.0)
        for _ in range(3):
            await debug_cmd(e, 'Debug: Step Over')
        await frame(e, '07-loop', [await rect_ed(e, 'total += i;'), await rect_rows(e, 'i =', 'total =', scope='.debug-watch')])

        # 8. Шаг с заходом в area
        for _ in range(8):
            cur = await e.js("""(() => { const g = document.querySelector('.codicon-debug-stackframe'); if (!g) return 0;
               const y = g.getBoundingClientRect().y; const n = [...document.querySelectorAll('.line-numbers')].find(n => Math.abs(n.getBoundingClientRect().y - y) < 6);
               return n ? +n.textContent : 0; })()""")
            if cur == 22:
                break
            await debug_cmd(e, 'Debug: Step Over')
        await e.js("[...document.querySelectorAll('.action-label')].find(x => x.getAttribute('aria-label') === 'Remove All Expressions').click()")
        await asyncio.sleep(0.8)
        await debug_cmd(e, 'Debug: Step Into', 3)
        await expand(e, 'p')
        await frame(e, '08-step-into', [await rect_ed(e, 'int s = p.x'), await rect_rows(e, 's =', 'y ='),
                                        await rect_rows(e, FN + 'area', FN + 'main', scope='.debug-call-stack')])

        # 9. Машинный код строки 10
        await e.palette('Open Disassembly View', 4)
        await frame(e, '09-disasm', await rect_disasm(e))

        # 10. Выход из area: a = 12
        await debug_cmd(e, 'Debug: Step Out', 3)
        await debug_cmd(e, 'Debug: Step Over', 3)
        tab = await e.js("""(() => { const t = [...document.querySelectorAll('.tab')].find(x => x.textContent.trim().startsWith('debug.c'));
          const r = t.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; })()""")
        await e.click(*tab, wait=1.0)
        dis = await e.js("""(() => { const t = [...document.querySelectorAll('.tab')].find(x => x.textContent.includes('Disassembly'));
          const c = t && t.querySelector('.codicon-close'); if (!c) return null; const r = c.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; })()""")
        if dis:
            await e.move(*dis, 0.5)
            await e.click(*dis, wait=1.0)
        await frame(e, '10-step-out', [await rect_ed(e, 'printf('), await rect_rows(e, 'a', scope='.debug-variables')])

        # 11. Продолжить до конца
        await debug_cmd(e, 'Debug: Continue', 5)
        if OS == 'linux':
            # в Linux программа под отладчиком пишет в отдельный терминал
            await e.palette('Terminal: Focus Terminal', 1.5)
            pos = await e.js("""(() => { const r = [...document.querySelectorAll('.terminal-tabs-entry, .tabs-list .monaco-list-row')]
              .find(x => x.textContent.includes('cppdbg')); if (!r) return null; const b = r.getBoundingClientRect(); return [b.x + b.width / 2, b.y + b.height / 2]; })()""")
            if not pos:
                raise SystemExit('нет вкладки терминала cppdbg')
            await e.click(*pos, wait=1.5)
            await frame(e, '11-finish', [await rect_term(e, 'agent: total'), await rect_rows(e, 'cppdbg')])
            return await stop()
        await e.palette('Debug Console: Focus on Debug Console View', 1.5)
        await frame(e, '11-finish', [await rect_text(e, '.repl .monaco-list-row', ('agent: total',)),
                                     await rect_text(e, '.repl .monaco-list-row', ('exited with code',))])
    await stop()


async def stop():
    if OS == 'mac':
        subprocess.run(['pkill', '-f', f'user-data-dir={cdp.PROFILE}/data'])
    else:
        subprocess.run(['docker', 'rm', '-f', 'sp-lab2-vsc'], capture_output=True)


def launch_linux():
    """VS Code для Linux в контейнере: виртуальный экран Xvfb, порт отладки наружу через socat."""
    subprocess.run(['docker', 'rm', '-f', 'sp-lab2-vsc'], capture_output=True)
    inner = ('Xvfb :99 -screen 0 1600x1000x24 >/dev/null 2>&1 & export DISPLAY=:99; sleep 1; '
             'socat TCP-LISTEN:9364,fork,reuseaddr TCP:127.0.0.1:9363 & '
             'dbus-launch code --no-sandbox --disable-gpu --user-data-dir /home/user/vsc/data '
             '--extensions-dir /home/user/vsc/ext --remote-debugging-port=9363 /home/user/02-debugger; sleep infinity')
    subprocess.run(['docker', 'run', '-d', '--name', 'sp-lab2-vsc', '--hostname', 'lab-linux',
                    '--shm-size', '1g', '--cap-add', 'SYS_PTRACE', '--security-opt', 'seccomp=unconfined', '-p', '127.0.0.1:9363:9364',
                    '-v', f'{STAND}:/home/user/02-debugger', '-v', f'{cdp.PROFILE}:/home/user/vsc',
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
