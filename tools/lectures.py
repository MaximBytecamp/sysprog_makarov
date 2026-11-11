"""Конспекты глав для репозитория студента: python3 tools/lectures.py <папка lectures шаблона> 1.1 1.2 …

Конспект = ссылка на главу, разделы (заголовки h2), шпаргалка (.cheat) и итог главы. Текст для разных систем
(data-os) подписывается: «Windows: …; macOS и Linux: …»."""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://maximbytecamp.github.io/sysprog_makarov/'
CHAPTERS = {
    '1.1': ('temy/06-c-dlya-sistemnogo-programmista', 'chapter-1-1-c-for-system-programmer.md'),
    '1.2': ('temy/07-c-i-python-vmeste', 'chapter-1-2-c-and-python.md'),
    '1.3': ('temy/08-n8n-i-ollama', 'chapter-1-3-n8n-and-ollama.md'),
    '2.1': ('temy/14-spisok-processov', 'chapter-2-1-process-list.md'),
    '2.2': ('temy/16-zapusk-processa', 'chapter-2-2-process-start.md'),
    '2.3': ('temy/18-processornoe-vremya', 'chapter-2-3-cpu-time.md'),
    '2.4': ('temy/20-potoki', 'chapter-2-4-threads.md'),
}
OSNAME = {'win': 'Windows', 'mac': 'macOS', 'linux': 'Linux', 'mac linux': 'macOS и Linux', 'win mac linux': ''}


def text(fragment):
    """HTML → строка Markdown: код в обратных кавычках, варианты систем с подписями."""
    def os_span(m):
        label = OSNAME.get(m.group(1), m.group(1))
        return f' ({label}: {m.group(2)})' if label else m.group(2)
    s = re.sub(r'<span data-os="([^"]+)">((?:(?!</span>).)*)</span>', os_span, fragment, flags=re.S)
    s = re.sub(r'<code>(.*?)</code>', lambda m: '`' + re.sub(r'<[^>]+>', '', m.group(1)) + '`', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip().replace('( ', '(')


def top_spans(s):
    """Ячейки шпаргалки — верхние <span> вместе с атрибутом data-os."""
    out, depth, start = [], 0, 0
    for m in re.finditer(r'<span[^>]*>|</span>', s):
        if m.group(0).startswith('<span'):
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                out.append(s[start:m.end()])
    return out


def build(num, folder, out_dir):
    page = (ROOT / folder / 'index.html').read_text()
    title = text(re.search(r'<h1>(.*?)</h1>', page, re.S).group(1).replace('<br>', ' '))
    heads = [text(h) for h in re.findall(r'<h2 id="s\d+"><span class="sec">[^<]*</span>(.*?)</h2>', page)]
    stop = next((i for i, h in enumerate(heads) if h.startswith('Справка')), len(heads))
    cheat = re.search(r'<div class="cheat">(.*?)\n        </div>', page, re.S)
    rows = []
    if cheat:
        for block in re.findall(r'<div><b>(.*?)</b>(.*?)</div>\n', cheat.group(1) + '\n', re.S):
            cells = [text(c) for c in top_spans(block[1])]
            rows.append((text(block[0]), '; '.join(c for c in cells if c)))
    summary = text(re.search(r'<h3>Итог главы</h3>\s*<p>(.*?)</p>', page, re.S).group(1))
    md = [f'# {num} {title}', '', f'Глава справочника: [{SITE}{folder}/index.html]({SITE}{folder}/index.html)', '',
          '## Разделы', '']
    md += [f'{i}. {h}' for i, h in enumerate(heads[:stop], 1)]
    if rows:
        md += ['', '## Шпаргалка', '', '| Что | Как |', '|---|---|']
        md += [f'| {a} | {b} |' for a, b in rows]
    md += ['', '## Итог главы', '', summary, '']
    (out_dir / CHAPTERS[num][1]).write_text('\n'.join(md))
    return title


if __name__ == '__main__':
    out = Path(sys.argv[1])
    for num in sys.argv[2:]:
        print(num, build(num, CHAPTERS[num][0], out))
