"""Общие функции съёмки ЛР 2 в VS Code по протоколу DevTools (основа — ~/sysprog-shots/m1)."""
import asyncio, json, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / 'sysprog-shots/m1'))
import cdp
cdp.KEYS.update({'F5': ('F5', 'F5', 116), 'F9': ('F9', 'F9', 120), 'F10': ('F10', 'F10', 121), 'F11': ('F11', 'F11', 122)})
from sh import E

HERE = Path(__file__).parent
RAW = HERE / 'raw'


def profile(name, port, settings_extra=None):
    cdp.PROFILE = f'/private/tmp/vsc-{name}'
    cdp.PORT = port
    P = Path(cdp.PROFILE)
    shutil.rmtree(P / 'data', ignore_errors=True)
    (P / 'data/User').mkdir(parents=True)
    s = json.loads((HERE / 'settings.json').read_text())
    s.update(settings_extra or {})
    (P / 'data/User/settings.json').write_text(json.dumps(s, ensure_ascii=False, indent=1))


async def goto(e, line):
    await e.key('Ctrl+G', 0.6)
    await e.paste(str(line), 0.4)
    await e.key('Enter', 0.6)
