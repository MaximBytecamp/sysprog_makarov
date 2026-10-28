"""Съёмка главы 1.1 в VS Code по протоколу DevTools. python3 sh.py <os> <часть>"""
import asyncio, shutil, sys, json, subprocess
from pathlib import Path
import cdp
from cdp import Editor

SRC = {'mac': Path.home() / 'sysprog-stand/m1/posix', 'linux': Path.home() / 'sysprog-stand/m1/posix',
       'win': Path.home() / 'sysprog-stand/m1/win'}
RAW = Path.home() / 'sysprog-shots/m1/raw'
RAW.mkdir(exist_ok=True)


def stand(os_):
    return Path(f'/private/tmp/sp-{os_}/pair02')


def put(os_, name, text=None):
    """Положить файл главы в папку стенда (как будто его создали и вставили код)."""
    d = stand(os_)
    if text is None:
        text = (SRC[os_] / name).read_text()
        if os_ == 'linux' and name == 'errors.c':
            text = text.replace('/etc/sudoers', '/etc/shadow')
    (d / name).write_text(text)


class E(Editor):
    async def open(self, name):
        await self.key('Meta+P', 0.8)
        await self.paste(name, 0.8)
        await self.key('Enter', 1.0)

    async def term_type(self, line, wait=1.5):
        await self.key('Space', 0.1); await self.key('Backspace', 0.1)
        await self.paste(line, 0.3)
        await self.key('Enter', wait)

    async def rows(self):
        """Строки терминала: [(y, h, x0, текст)] в точках страницы."""
        return await self.js("""(() => [...document.querySelectorAll('.xterm-rows > div')].map(d => {
            const r = d.getBoundingClientRect(); const sp = [...d.querySelectorAll('span')];
            let x1 = r.x; for (const s of sp) { const q = s.getBoundingClientRect(); if (s.textContent.trim()) x1 = Math.max(x1, q.right); }
            return [r.x, r.y, x1 - r.x, r.height, d.textContent]; }))()""")

    async def lines(self):
        """Видимые строки редактора: [(x, y, w, h, номер, текст)]."""
        return await self.js("""(() => {
          const ed = [...document.querySelectorAll('.editor-instance .monaco-editor')].find(e => e.getBoundingClientRect().width > 0);
          if (!ed) return [];
          const nums = [...ed.querySelectorAll('.line-numbers')].map(n => [n.getBoundingClientRect().y, n.textContent.trim()]);
          return [...ed.querySelectorAll('.view-line')].map(l => {
            const r = l.getBoundingClientRect(); const sp = l.querySelector('span');
            const last = [...l.querySelectorAll('span span')].filter(s => s.textContent.trim()).pop();
            const first = [...l.querySelectorAll('span span')].find(s => s.textContent.trim());
            const x0 = first ? first.getBoundingClientRect().x : r.x, x1 = last ? last.getBoundingClientRect().right : r.x;
            const n = (nums.find(q => Math.abs(q[0] - r.y) < 3) || [0, ''])[1];
            return [x0, r.y, x1 - x0, r.height, n, l.textContent]; }).sort((a, b) => a[1] - b[1]); })()""")


async def setup(e, os_):
    await e.size(1240, 780)
    await e.send('Emulation.setFocusEmulationEnabled', enabled=True)
    await asyncio.sleep(2)


def launch(os_):
    cdp.launch(str(stand(os_)))
