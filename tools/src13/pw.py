"""Браузер для кадров n8n: python3 pw.py <сценарий.py> — сценарий получает page и функции shot/box."""
import json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

RAW = Path(__file__).parent / 'raw'; RAW.mkdir(exist_ok=True)
MARKS = Path(__file__).parent / 'marks.json'


def run(script):
    with sync_playwright() as p:
        br = p.chromium.connect_over_cdp('http://127.0.0.1:9371')
        ctx = br.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        cdp = ctx.new_cdp_session(page)
        cdp.send('Emulation.setDeviceMetricsOverride', {'width': 1280, 'height': 800, 'deviceScaleFactor': 2, 'mobile': False})

        def shot(name, boxes=()):
            """boxes — локаторы или прямоугольники [x,y,w,h]; пишутся в marks.json."""
            time.sleep(0.8)
            rects = []
            for b in boxes:
                if isinstance(b, (list, tuple)):
                    rects.append(list(b)); continue
                bb = b.bounding_box()
                rects.append([bb['x'], bb['y'], bb['width'], bb['height']])
            page.screenshot(path=str(RAW / f'{name}.png'))
            db = json.loads(MARKS.read_text()) if MARKS.exists() else {}
            db[name] = rects; MARKS.write_text(json.dumps(db, ensure_ascii=False, indent=1))
            print('shot', name)
        exec(Path(script).read_text(), dict(page=page, shot=shot, time=time, ctx=ctx))


if __name__ == '__main__':
    run(sys.argv[1])
