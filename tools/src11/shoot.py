"""Кадры главы 1.1: python3 shoot.py mac|linux [кадр ...]. Рамки — в marks.json, рисует mark.py."""
import asyncio, json, shutil, subprocess, sys, time
from pathlib import Path
import cdp
from sh import E, stand, put, RAW, SRC

OS = sys.argv[1]
ONLY = set(sys.argv[2:])
MARKS = Path(__file__).parent / 'marks.json'
CC = {'mac': 'clang', 'linux': 'gcc'}[OS]
SECRET = {'mac': '/etc/sudoers', 'linux': '/etc/shadow'}[OS]


def fresh_profile():
    P = Path(cdp.PROFILE)
    shutil.rmtree(P / 'data', ignore_errors=True)
    (P / 'data/User').mkdir(parents=True)
    shutil.copy(Path(__file__).parent / 'settings.json', P / 'data/User/settings.json')


async def find(e, kind, text, upto=None):
    """Прямоугольник строки редактора (ed) или терминала (tm), по подстроке; upto — до строки с другой подстрокой."""
    rows = await (e.lines() if kind == 'ed' else e.rows())
    exact = kind == 'tq'
    T = lambda r: r[-1].replace('\xa0', ' ')
    i = next((k for k, r in enumerate(rows) if (T(r).strip() == text.strip() if exact else text in T(r))), None)
    if i is None:
        raise LookupError([T(r) for r in rows if T(r).strip()])
    j = i if upto is None else next(k for k in range(i, len(rows)) if upto in T(rows[k]))
    sel = rows[i:j + 1]
    x = min(r[0] for r in sel); y = sel[0][1]
    w = max(r[0] + r[2] for r in sel) - x; h = sel[-1][1] + sel[-1][3] - y
    return [x, y, w, h]


async def frame(e, name, marks):
    out = RAW / OS / f'{name}.png'
    out.parent.mkdir(exist_ok=True)
    await asyncio.sleep(0.8)
    rects = []
    for m in marks:
        for t in range(8):
            try:
                rects.append(await find(e, *m)); break
            except LookupError as err:
                last = err; await asyncio.sleep(1)
        else:
            raise SystemExit(f'{name}: нет строки {m}: {last}')
    await e.shot(str(out))
    db = json.loads(MARKS.read_text()) if MARKS.exists() else {}
    db[f'{OS}/{name}'] = rects
    MARKS.write_text(json.dumps(db, ensure_ascii=False, indent=1))


async def run(e, cmds, wait=2.5):
    await e.term_type('clear', 0.8)
    for c in cmds:
        await e.term_type(c, wait)


async def show(e, name, panel=True):
    await e.palette('View: Close All Editors', 0.8)
    await e.open(name)
    if panel:
        await e.palette('Terminal: Focus Terminal', 0.8)


async def main():
    d = stand(OS)
    shutil.rmtree(d.parent, ignore_errors=True); d.mkdir(parents=True)
    put(OS, 'sizes.c')
    fresh_profile()
    cdp.launch(str(d))
    await asyncio.sleep(4)
    async with E() as e:
        await e.size(1240, 900)
        await e.send('Emulation.setFocusEmulationEnabled', enabled=True)
        await asyncio.sleep(1.5)
        # боковая панель уже: тянем границу
        sash = await e.js("""(() => { const s=[...document.querySelectorAll('.monaco-sash.vertical')].map(x=>x.getBoundingClientRect()).filter(r=>r.height>300 && r.x>150 && r.x<400)[0]; return s?[s.x+2,s.y+200]:null })()""")
        if sash:
            await e.send('Input.dispatchMouseEvent', type='mouseMoved', x=sash[0], y=sash[1])
            await e.send('Input.dispatchMouseEvent', type='mousePressed', x=sash[0], y=sash[1], button='left', clickCount=1)
            for k in range(1, 11):
                await e.send('Input.dispatchMouseEvent', type='mouseMoved', x=sash[0] - (sash[0]-235)*k/10, y=sash[1], button='left')
                await asyncio.sleep(0.05)
            await e.send('Input.dispatchMouseEvent', type='mouseReleased', x=235, y=sash[1], button='left', clickCount=1)
            await asyncio.sleep(0.6)
        await e.open('sizes.c')
        await e.palette('Terminal: Create New Terminal', 3)
        hs = await e.js("""(() => { const s=[...document.querySelectorAll('.monaco-sash.horizontal')].map(x=>x.getBoundingClientRect()).filter(r=>r.width>500 && r.y>300)[0]; return s?[s.x+300,s.y+2]:null })()""")
        if hs:
            await e.send('Input.dispatchMouseEvent', type='mouseMoved', x=hs[0], y=hs[1])
            await e.send('Input.dispatchMouseEvent', type='mousePressed', x=hs[0], y=hs[1], button='left', clickCount=1)
            for k in range(1, 11):
                await e.send('Input.dispatchMouseEvent', type='mouseMoved', x=hs[0], y=hs[1] + (640-hs[1])*k/10, button='left')
                await asyncio.sleep(0.05)
            await e.send('Input.dispatchMouseEvent', type='mouseReleased', x=hs[0], y=640, button='left', clickCount=1)
            await asyncio.sleep(0.6)
        if OS == 'linux':
            await e.term_type(f'docker run -it --rm --hostname lab-linux -v {d}:/home/user/pair02 -w /home/user/pair02 sp-gcc bash', 6)
        W = '-Wall -Wextra'
        await run(e, [f'{CC} {W} -o sizes sizes.c && ./sizes'])
        await frame(e, '01-sizes', [('tm', 'long'), ('tm', 'void *'), ('tm', 'int64_t')])

        put(OS, 'sysname.c'); await show(e, 'sysname.c')
        await run(e, [f'{CC} {W} -o sysname sysname.c && ./sysname'])
        await frame(e, '02-uname', [('ed', 'struct utsname u;'), ('ed', 'uname(&u)'), ('tm', 'sysname ', 'nodename'), ('tm', 'sizeof')])

        put(OS, 'hostbuf.c'); await show(e, 'hostbuf.c')
        await run(e, [f'{CC} {W} -o hostbuf hostbuf.c && ./hostbuf'])
        rows = await e.rows()
        dumps = [r[-1] for r in rows if r[-1].count(' ') > 3 and all(len(t) == 2 for t in r[-1].split())]
        await frame(e, '03-hostbuf', [('ed', 'char tiny[4];'), ('tm', 'host  "'), ('tq', dumps[0]), ('tm', 'tiny  rc'), ('tq', dumps[1])])

        put(OS, 'errors.c'); await show(e, 'errors.c')
        await run(e, [f'{CC} {W} -o errors errors.c && ./errors'])
        await frame(e, '04-errors', [('ed', 'int code = errno;'), ('tm', 'no-such-file'), ('tm', SECRET + ' ')])

        put(OS, 'core.h'); await show(e, 'core.h')
        await run(e, [])
        await e.palette('View: Close Panel', 0.8)
        await frame(e, '05-core-h', [('ed', 'struct core_info {', '};'), ('ed', 'int core_get_info')])

        put(OS, 'core_info.c'); await show(e, 'core_info.c', False)
        await frame(e, '06-core-info', [('ed', 'int core_get_info'), ('ed', 'out->pid', 'out->page_size'), ('ed', 'return errno;')])

        put(OS, 'show_info.c'); await show(e, 'show_info.c')
        await run(e, [f'{CC} {W} -o show_info show_info.c core_info.c && ./show_info'])
        await frame(e, '07-info', [('ed', 'core_get_info(&info)'), ('tm', 'pid ', 'host '), ('tm', 'sizeof')])

        warn = (SRC[OS] / 'show_info.c').read_text().replace('"pid       %" PRId64 "\\n"', '"pid       %d\\n"')
        assert warn != (SRC[OS] / 'show_info.c').read_text()
        put(OS, 'show_info.c', warn); await asyncio.sleep(1.5)
        await run(e, [f'{CC} {W} -o show_info show_info.c core_info.c'], 3)
        await frame(e, '08-warning', [('ed', '"pid       %d'), ('tm', 'warning:'), ('tm', '%ld' if False else 'warning generated' if OS == 'mac' else 'printf(')])
        put(OS, 'show_info.c')
        if OS == 'linux':
            await e.term_type('exit', 2)
    subprocess.run(['pkill', '-f', f'user-data-dir={cdp.PROFILE}/data'])

asyncio.run(main())
