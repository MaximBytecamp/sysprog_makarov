"""Блок «Если файлов прошлых глав нет» для глав 1.2, 1.3 и задания модуля 1.

Глава опирается на файлы, которые студент создал раньше. Если глава пропущена или репозиторий создан заново,
блок даёт полный код этих файлов для своей системы и команду сборки. Код берётся из тех же исходников,
что и в главах (tools/src11, src12, src13), поэтому совпадает с ними."""
import html
from pathlib import Path

T = Path(__file__).resolve().parent
BUILD = {
    'win': ('x64 Native Tools Command Prompt', 'cd agent\\core\ncl /nologo /W4 /LD core_info.c /Fe:sentry_core.dll'),
    'mac': ('терминал в папке sysprog-start', 'cd agent/core\nclang -Wall -Wextra -shared -fPIC -o libsentry_core.dylib core_info.c'),
    'linux': ('терминал в папке sysprog-start', 'cd agent/core\ngcc -Wall -Wextra -shared -fPIC -o libsentry_core.so core_info.c'),
}


def fig(path, code, os_=None, note=''):
    attr = f' data-os="{os_}"' if os_ else ''
    cap = f'<span>{path}</span>' + (f'<span>{note}</span>' if note else '')
    return f'          <figure class="code"{attr}>\n            <figcaption>{cap}</figcaption>\n<pre>{code}</pre>\n          </figure>'


def block(for_, hl, hl_py):
    """for_: '1.2' — нужны файлы главы 1.1; '1.3' — файлы глав 1.1–1.2; 'z1' — файлы глав 1.1–1.3."""
    if for_ == '1.2':
        title = 'Если файлов главы 1.1 нет'
        intro = ('Глава 1.2 начинается с файлов ядра из главы 1.1. Если глава пропущена или репозиторий создан заново, '
                 'создайте в <code>agent/core</code> два файла с кодом ниже — для своей системы — и продолжайте с шага 1.')
        core_h = (T / 'src11/posix/core.h').read_text()
        info = {'win': (T / 'src11/win/core_info.c').read_text(), 'posix': (T / 'src11/posix/core_info.c').read_text()}
        brain, build, src = None, False, 'из главы 1.1, шаги 5–6'
    else:
        prev = '1.1–1.2' if for_ == '1.3' else '1.1–1.3'
        title = f'Если файлов глав {prev} нет'
        intro = (f'{"Глава 1.3" if for_ == "1.3" else "Задание"} начинается с ядра и мозга агента из глав {prev}. '
                 'Если главы пропущены или репозиторий создан заново, создайте файлы ниже для своей системы, '
                 'соберите библиотеку и проверьте запуском <code>brain.py</code>: он должен напечатать JSON <code>agent_started</code>.')
        core_h = (T / 'src12/c/core.h').read_text()
        info = {'win': (T / 'src12/c/core_info_win.c').read_text(), 'posix': (T / 'src12/c/core_info.c').read_text()}
        brain = (T / ('src12/py/brain.py' if for_ == '1.3' else 'src13/brain.py')).read_text()
        build, src = True, 'из глав 1.1–1.2' if for_ == '1.3' else 'из глав 1.1–1.3'
    parts = [fig('agent/core/core.h', hl(core_h).rstrip('\n'), note=src),
             fig('agent/core/core_info.c', hl(info['win']).rstrip('\n'), 'win', 'Windows'),
             fig('agent/core/core_info.c', hl(info['posix']).rstrip('\n'), 'mac linux', 'macOS и Linux')]
    if brain:
        parts.append(fig('agent/brain/brain.py', hl_py(brain).rstrip('\n'), note='все системы'))
    if build:
        for o, (where, c) in BUILD.items():
            parts.append(fig(where, html.escape(c), o, 'сборка библиотеки'))
    body = '\n'.join(parts)
    return f'''        <details class="catchup">
          <summary>{title}</summary>
          <p>{intro}</p>
{body}
        </details>'''
