"""Кадры главы 1.2: python3 shoot12.py mac|linux. Рамки — в marks12.json."""
import asyncio, json, shutil, subprocess, sys
from pathlib import Path
import cdp
from sh import E

OS = sys.argv[1]
S12 = Path.home() / 'sysprog_makarov/tools/src12'
S11 = Path.home() / 'sysprog_makarov/tools/src11/posix'
ROOT = Path(f'/private/tmp/sp12-{OS}/sysprog-start')
RAW = Path(__file__).parent / 'raw12' / OS
MARKS = Path(__file__).parent / 'marks12.json'
CC = {'mac': 'clang', 'linux': 'gcc'}[OS]
LIB = {'mac': 'libsentry_core.dylib', 'linux': 'libsentry_core.so'}[OS]
NM = {'mac': f'nm -gU {LIB}', 'linux': f'nm -D --defined-only {LIB}'}[OS]
from shoot import find  # noqa: E402  (find из главы 1.1)


async def frame(e, name, marks):
    RAW.mkdir(parents=True, exist_ok=True)
    await asyncio.sleep(0.8)
    rects = []
    for m in marks:
        last = None
        for _ in range(8):
            try:
                rects.append(await find(e, *m)); break
            except LookupError as err:
                last = err; await asyncio.sleep(1)
        else:
            raise SystemExit(f'{name}: нет строки {m}: {last}')
    await e.shot(str(RAW / f'{name}.png'))
    db = json.loads(MARKS.read_text()) if MARKS.exists() else {}
    db[f'{OS}/{name}'] = rects
    MARKS.write_text(json.dumps(db, ensure_ascii=False, indent=1))


async def run(e, cmds, wait=2.5):
    await e.term_type('clear', 0.8)
    for c in cmds:
        await e.term_type(c, wait)


async def show(e, rel):
    await e.palette('View: Close All Editors', 0.8)
    await e.open(rel)
    await e.palette('Terminal: Focus Terminal', 0.8)


def brain(version):
    (ROOT / 'agent/brain/brain.py').write_text((S12 / 'py' / f'{version}.py').read_text())


async def main():
    shutil.rmtree(ROOT.parent, ignore_errors=True)
    (ROOT / 'agent/core').mkdir(parents=True); (ROOT / 'agent/brain').mkdir(parents=True)
    for f in ('core.h', 'core_info.c', 'show_info.c'):
        shutil.copy(S11 / f, ROOT / 'agent/core' / f)
    P = Path(cdp.PROFILE)
    shutil.rmtree(P / 'data', ignore_errors=True); (P / 'data/User').mkdir(parents=True)
    shutil.copy(Path(__file__).parent / 'settings.json', P / 'data/User/settings.json')
    cdp.launch(str(ROOT))
    await asyncio.sleep(4)
    async with E() as e:
        await e.size(1240, 900)
        await e.send('Emulation.setFocusEmulationEnabled', enabled=True)
        await asyncio.sleep(1.5)
        sash = await e.js("""(() => { const s=[...document.querySelectorAll('.monaco-sash.vertical')].map(x=>x.getBoundingClientRect()).filter(r=>r.height>300 && r.x>150 && r.x<400)[0]; return s?[s.x+2,s.y+200]:null })()""")
        if sash:
            await e.send('Input.dispatchMouseEvent', type='mouseMoved', x=sash[0], y=sash[1])
            await e.send('Input.dispatchMouseEvent', type='mousePressed', x=sash[0], y=sash[1], button='left', clickCount=1)
            for k in range(1, 11):
                await e.send('Input.dispatchMouseEvent', type='mouseMoved', x=sash[0] - (sash[0]-255)*k/10, y=sash[1], button='left'); await asyncio.sleep(0.05)
            await e.send('Input.dispatchMouseEvent', type='mouseReleased', x=255, y=sash[1], button='left', clickCount=1)
        await e.open('core.h')
        await e.palette('Terminal: Create New Terminal', 3)
        hs = await e.js("""(() => { const s=[...document.querySelectorAll('.monaco-sash.horizontal')].map(x=>x.getBoundingClientRect()).filter(r=>r.width>500 && r.y>300)[0]; return s?[s.x+300,s.y+2]:null })()""")
        if hs:
            await e.send('Input.dispatchMouseEvent', type='mouseMoved', x=hs[0], y=hs[1])
            await e.send('Input.dispatchMouseEvent', type='mousePressed', x=hs[0], y=hs[1], button='left', clickCount=1)
            for k in range(1, 11):
                await e.send('Input.dispatchMouseEvent', type='mouseMoved', x=hs[0], y=hs[1] + (640-hs[1])*k/10, button='left'); await asyncio.sleep(0.05)
            await e.send('Input.dispatchMouseEvent', type='mouseReleased', x=hs[0], y=640, button='left', clickCount=1)
        if OS == 'linux':
            await e.term_type(f'docker run -it --rm --hostname lab-linux -v {ROOT}:/home/user/sysprog-start -w /home/user/sysprog-start sp-gcc bash', 6)
        # шаг 1: core.h с CORE_API и сборка библиотеки
        shutil.copy(S12 / 'c/core.h', ROOT / 'agent/core/core.h'); await asyncio.sleep(1.5)
        await show(e, 'core.h')
        await run(e, ['cd agent/core', f'{CC} -Wall -Wextra -shared -fPIC -o {LIB} core_info.c', f'ls {LIB}'])
        await frame(e, '01-build', [('ed', '#ifdef _WIN32', '#endif'), ('ed', 'CORE_API int core_get_info'), ('tm', '-shared'), ('tq', LIB)])
        await run(e, [NM])
        await frame(e, '02-exports', [('tm', 'core_get_info')])
        # шаги 3–8: brain.py
        brain('v1_load'); await asyncio.sleep(1)
        await show(e, 'brain.py')
        await run(e, ['cd ../brain', 'python3 brain.py'], 3)
        await frame(e, '03-load', [('ed', 'ctypes.CDLL('), ('tm', '<CDLL'), ('tm', '<_FuncPtr')])
        brain('v2_struct'); await asyncio.sleep(1.5)
        await run(e, ['python3 brain.py'], 3)
        await frame(e, '04-struct', [('ed', '_fields_ = [', '    ]'), ('tm', 'sizeof 272'), ('tm', 'pid ', 'host ')])
        brain('v3_call'); await asyncio.sleep(1.5)
        await run(e, ['python3 brain.py'], 3)
        await frame(e, '05-call', [('ed', 'argtypes', 'restype'), ('ed', 'ctypes.byref(info)'), ('tm', 'pid  '), ('tm', 'host  ')])
        brain('v4_swap'); await asyncio.sleep(1.5)
        await run(e, ['python3 brain.py'], 3)
        await frame(e, '06-swap', [('ed', '("page_size"', '("cpus"'), ('tm', 'cpus  ', 'page_size')])
        brain('v5_null'); await asyncio.sleep(1.5)
        await run(e, ['python3 brain.py'], 3)
        await frame(e, '07-null', [('ed', 'core_get_info(None)'), ('tm', 'err 22')])
        brain('brain'); await asyncio.sleep(1.5)
        await e.palette('Go to Line/Column...', 0.8); await e.paste('36', 0.5); await e.key('Enter', 0.8)
        await e.palette('Terminal: Focus Terminal', 0.8)
        await run(e, ['python3 brain.py'], 3)
        await frame(e, '08-brain', [('ed', 'def get_info'), ('ed', 'raise OSError'), ('tm', '{', '}')])
        if OS == 'linux':
            await e.term_type('exit', 2)
    subprocess.run(['pkill', '-f', f'user-data-dir={cdp.PROFILE}/data'])

asyncio.run(main())
