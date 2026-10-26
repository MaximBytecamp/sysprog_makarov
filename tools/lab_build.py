"""Сборка страницы лабораторной работы из данных шагов.
Шаг: заголовок, действие и пояснения — общие или по системам (dict win/mac/linux).
Кадр: имя файла в img/<система>/ или текст места под кадр (todo)."""
import html

OS = ('win', 'mac', 'linux')


def per_os(v):
    return v if isinstance(v, dict) else {o: v for o in OS}


def block(v, render):
    """Одинаковый текст — один блок; разный — по блоку на систему с data-os."""
    d = per_os(v)
    groups = {}
    for o in OS:
        if d.get(o) is None:
            continue
        groups.setdefault(d[o], []).append(o)
    if len(groups) == 1 and len(next(iter(groups.values()))) == 3:
        return render(next(iter(groups)), None)
    return ''.join(render(val, ' '.join(oss)) for val, oss in groups.items())


def shot(s, os_):
    if s.startswith('todo:'):
        return f'<div class="shot-todo"><b>Место под кадр · {dict(win="Windows", mac="macOS", linux="Linux")[os_]}</b><p>{s[5:]}</p></div>'
    return f'<img src="img/{os_}/{s}" alt="" loading="lazy">'


def attr(o):
    return f' data-os="{o}"' if o else ''


def step(st):
    out = ['        <li>']
    out.append(block(st['do'], lambda v, o: f'<div class="lab__do"{attr(o)}><b>{v[0]}</b><span>{v[1]}</span></div>'))
    shots = per_os(st['shot'])
    for o in OS:
        out.append(f'<figure class="lab__shot shot" data-os="{o}">{shot(shots[o], o)}</figure>')
    out.append(block(st['notes'], lambda v, o: f'<div class="lab__notes"{attr(o)}><div><b>Что на кадре</b>{v[0]}</div><div><b>Что изменилось</b>{v[1]}</div></div>'))
    if st.get('q'):
        out.append(block(st['q'], lambda v, o: f'<p class="lab-q"{attr(o)}><b>В отчёт.</b> {v}</p>'))
    out.append('</li>')
    return '\n'.join(out)


def steps(lst):
    return '        <ol class="lab">\n' + '\n'.join(step(s) for s in lst) + '\n        </ol>'
