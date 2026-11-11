"""Картинки данных из блоков части 11 styles.css: этапы со стрелками, полосы памяти, стопка вызовов, бланк, таблица.

Функции возвращают HTML. Полосы байтов строит cells() из ch11 — здесь только раскладка вокруг них."""


def scheme(title, body, note='', os_=''):
    """Рамка .scheme на всю ширину текста: заголовок, картинка, подпись."""
    attr = f' data-os="{os_}"' if os_ else ''
    note_html = f'\n          <p class="scheme__note">{note}</p>' if note else ''
    return f'''        <figure class="scheme"{attr}>
          <p class="scheme__head">{title}</p>
          <div class="scheme__body">
{body}
          </div>{note_html}
        </figure>'''


def card(label, title, body='', kind=''):
    cls = f'vcard is-{kind}' if kind else 'vcard'
    head = f'<h5>{label}</h5>' if label else ''
    tit = f'<b>{title}</b>' if title else ''
    return f'<div class="{cls}">{head}{tit}{body}</div>'


def arrow(text='', back=False):
    cls = 'varr is-back' if back else 'varr'
    return f'<div class="{cls}">{text}</div>'


def steps(*items):
    """Этапы: card, arrow, card, …"""
    return '<div class="vsteps">' + ''.join(items) + '</div>'


def mem(rows):
    """Полосы памяти строками: [(подпись, пояснение, html полосы)]."""
    out = ''.join(f'<b>{a}{f"<small>{b}</small>" if b else ""}</b>{c}' for a, b, c in rows)
    return f'<div class="vmem">{out}</div>'


def frame(name, note, body, top=False):
    cls = 'vframe is-top' if top else 'vframe'
    return f'<div class="{cls}"><b>{name}<small>{note}</small></b>{body}</div>'


def stack(*frames):
    return '<div class="vstack">' + ''.join(frames) + '</div>'


def kv(rows):
    return '<div class="vkv">' + ''.join(f'<div><span>{a}</span><span>{b}</span></div>' for a, b in rows) + '</div>'


def proc(items):
    """Модули процесса: [(имя, пояснение, новый?)]."""
    return '<div class="vproc">' + ''.join(
        f'<span{" class=\"is-new\"" if new else ""}>{n}{f"<small>{s}</small>" if s else ""}</span>' for n, s, new in items) + '</div>'


def tab(head, rows):
    """Таблица значений: head — заголовки, rows — [[ячейка | (ячейка, класс)]] или (строка, класс строки)."""
    th = ''.join(f'<th>{h}</th>' for h in head)
    body = []
    for r in rows:
        rcls = ''
        if isinstance(r, tuple) and len(r) == 2 and isinstance(r[0], list):
            r, rcls = r
        tds = ''.join(f'<td class="{c[1]}">{c[0]}</td>' if isinstance(c, tuple) else f'<td>{c}</td>' for c in r)
        body.append(f'<tr{f" class=\"{rcls}\"" if rcls else ""}>{tds}</tr>')
    return f'<table class="vtab"><thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table>'


def split(*cols, rows=False):
    """Колонки рядом: [(заголовок, html)]; rows=True — те же части одна под другой."""
    return f'<div class="vsplit{" is-rows" if rows else ""}">' + ''.join(f'<div><h6>{h}</h6>{b}</div>' for h, b in cols) + '</div>'


def simple(title, text, strip='', map_=''):
    """Раскрывающийся блок «По-простому»: text — абзацы разговорным языком, strip — раскадровка (steps), map_ — «что есть что» в коде."""
    m = f'<p class="simple__map">{map_}</p>' if map_ else ''
    return f'''        <details class="simple">
          <summary>{title}</summary>
{text}
{strip}
          {m}
        </details>'''
