"""Снимок двух окон (Терминал слева, Мониторинг справа) без фона экрана и склейка рядом."""
import Quartz, subprocess, sys
from PIL import Image
D = '/Users/makarovmn/sysprog-shots/mac/'
def wid(owner_prefix, title_part=''):
    L = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionAll, Quartz.kCGNullWindowID)
    c = [w for w in L if w.get('kCGWindowLayer') == 0 and (w.get('kCGWindowOwnerName') or '').startswith(owner_prefix)
         and title_part in (w.get('kCGWindowName') or '') and w['kCGWindowBounds']['Height'] > 100]
    c.sort(key=lambda w: (bool(w.get('kCGWindowName')), w['kCGWindowBounds']['Width'] * w['kCGWindowBounds']['Height']), reverse=True)
    return c[0]['kCGWindowNumber'] if c else None
def grab(id_, path):
    subprocess.run(['screencapture', '-x', '-o', f'-l{id_}', path])
def pair(name, extra=None):
    t, m = wid('Терминал', 'pair01'), wid('Мониторинг')
    grab(t, D + '_t.png'); grab(m, D + '_m.png')
    a, b = Image.open(D + '_t.png'), Image.open(D + '_m.png')
    H = max(a.height, b.height)
    W = Image.new('RGB', (a.width + b.width + 24, H + 24), (236, 234, 228))
    W.paste(a, (8, 12), a if a.mode == 'RGBA' else None); W.paste(b, (a.width + 16, 12), b if b.mode == 'RGBA' else None)
    if extra:
        e = Image.open(extra); W.paste(e, (W.width - e.width - 20, 60), e if e.mode == 'RGBA' else None)
    W = W.resize((W.width // 2, W.height // 2), Image.LANCZOS)
    W.save(D + name + '.png'); print(name, W.size)

def am_search(text):
    import subprocess, time
    subprocess.run(['osascript', '-e', f'''tell application "Activity Monitor" to activate
delay 0.6
set the clipboard to "{text}"
tell application "System Events" to tell process "Activity Monitor"
  key code 0 using {{command down}}
  delay 0.2
  key code 9 using {{command down}}
end tell
delay 2'''])


def bounds(id_):
    L = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionIncludingWindow, id_)
    b = L[0]['kCGWindowBounds']; return int(b['X']), int(b['Y'])

def pair3(name, title, mon='Мониторинг системы'):
    """Терминал + монитор + окно title поверх монитора на своём месте."""
    t = wid('Терминал', 'pair01'); m = wid('Мониторинг', mon); e = wid('Мониторинг', title)
    grab(t, D + '_t.png'); grab(m, D + '_m.png'); grab(e, D + '_e.png')
    a, b, c = Image.open(D + '_t.png'), Image.open(D + '_m.png'), Image.open(D + '_e.png')
    H = max(a.height, b.height)
    W = Image.new('RGB', (a.width + b.width + 24, H + 24), (236, 234, 228))
    W.paste(a, (8, 12), a); W.paste(b, (a.width + 16, 12), b)
    mx, my = bounds(m); ex, ey = bounds(e)
    W.paste(c, (a.width + 16 + (ex - mx) * 2 - 0, 12 + (ey - my) * 2), c)
    W = W.resize((W.width // 2, W.height // 2), Image.LANCZOS)
    W.save(D + name + '.png'); print(name, W.size)


def front_term_id():
    r = subprocess.run(['osascript', '-e', 'tell application "Terminal" to get id of front window'], capture_output=True, text=True)
    return int(r.stdout.strip())

def pair_ids(name, tid, mid, eid=None):
    grab(tid, D + '_t.png'); grab(mid, D + '_m.png')
    a, b = Image.open(D + '_t.png'), Image.open(D + '_m.png')
    H = max(a.height, b.height)
    W = Image.new('RGB', (a.width + b.width + 24, H + 24), (236, 234, 228))
    W.paste(a, (8, 12), a); W.paste(b, (a.width + 16, 12), b)
    if eid:
        grab(eid, D + '_e.png'); c = Image.open(D + '_e.png')
        mx, my = bounds(mid); ex, ey = bounds(eid)
        W.paste(c, (a.width + 16 + (ex - mx) * 2, 12 + (ey - my) * 2), c)
    W = W.resize((W.width // 2, W.height // 2), Image.LANCZOS)
    W.save(D + name + '.png'); print(name, W.size)


def compose(name, tid, mid, overlays=()):
    grab(tid, D + '_t.png'); grab(mid, D + '_m.png')
    a, b = Image.open(D + '_t.png'), Image.open(D + '_m.png')
    H = max(a.height, b.height)
    W = Image.new('RGB', (a.width + b.width + 24, H + 24), (236, 234, 228))
    W.paste(a, (8, 12), a); W.paste(b, (a.width + 16, 12), b)
    mx, my = bounds(mid)
    for k, eid in enumerate(overlays):
        grab(eid, D + f'_e{k}.png'); c = Image.open(D + f'_e{k}.png')
        ex, ey = bounds(eid)
        W.paste(c, (a.width + 16 + (ex - mx) * 2, 12 + (ey - my) * 2), c)
    W = W.resize((W.width // 2, W.height // 2), Image.LANCZOS)
    W.save(D + name + '.png'); print(name, W.size)

if __name__ == '__main__':
    exec(sys.argv[1])
