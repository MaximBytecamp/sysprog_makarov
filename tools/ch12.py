"""Глава 1.2 «C и Python вместе: библиотека и ctypes» → temy/07-c-i-python-vmeste/index.html.

Код: tools/src12/c (core.h с CORE_API, core_info.c из 1.1) и tools/src12/py (версии brain.py по шагам, make_py.py).
Кадры: macOS и Linux — ~/sysprog-shots/m1/shoot12.py (VS Code, терминал; Linux — контейнер sp-gcc, Python 3.13.5),
Windows — ВМ Win11-lab, MSVC 19.44 x64 и Python 3.14.0 x64 (C:\\Py314x64); кадр WinError 193 — Python 3.14 ARM64.
Рамки: mark12.py и winmark12.py. Числа в тексте — с кадров."""
import html
import re
from pathlib import Path

from ch11 import M, cells, hl, per, shot

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / 'src12'
OUT = ROOT / 'temy/07-c-i-python-vmeste/index.html'

PY_KW = r'\b(import|from|class|def|return|if|else|for|in|raise|not|and|or|None|True|False)\b'


def hl_py(code):
    out = []
    for line in code.rstrip('\n').split('\n'):
        parts = re.split(r'("""[^"]*"""|f?"(?:[^"\\]|\\.)*"|#.*$)', line)
        res = []
        for t in parts:
            if not t:
                continue
            if t.startswith('#'):
                res.append(f'<span class="c">{html.escape(t)}</span>')
            elif t.startswith('"') or t.startswith('f"'):
                res.append(f'<span class="s">{html.escape(t)}</span>')
            else:
                e = html.escape(t)
                e = re.sub(PY_KW, r'<span class="k">\1</span>', e)
                e = re.sub(r'\b([A-Za-z_]\w*)(?=\()', lambda m: f'<span class="f">{m.group(1)}</span>', e)
                e = re.sub(r'(?<![\w.])(\d+)\b', r'<span class="n">\1</span>', e)
                res.append(e)
        out.append(''.join(res))
    return '\n'.join(out)


def pyfile(cap, code, attr=''):
    return f'        <figure class="code"{attr}>\n          <figcaption><span>{cap}</span></figcaption>\n<pre>{hl_py(code)}</pre>\n        </figure>'


def cmd(win, mac, linux, where='терминал'):
    rows = []
    for o, c, w in (('win', win, 'x64 Native Tools Command Prompt'), ('mac', mac, where), ('linux', linux, where)):
        rows.append(f'        <figure class="code" data-os="{o}">\n          <figcaption><span>{w}</span></figcaption>\n<pre>{html.escape(c)}</pre>\n        </figure>')
    return '\n'.join(rows)


def py(name):
    return (SRC / 'py' / f'{name}.py').read_text()


def between(text, start, end=None):
    """Фрагмент версии brain.py: от строки с start до строки с end включительно (или до конца)."""
    lines = text.rstrip('\n').split('\n')
    i = next(k for k, l in enumerate(lines) if start in l)
    j = len(lines) - 1 if end is None else next(k for k in range(i, len(lines)) if end in lines[k])
    return '\n'.join(lines[i:j + 1])


V1, V2, V3, V4, V5, BRAIN = (py(n) for n in ('v1_load', 'v2_struct', 'v3_call', 'v4_swap', 'v5_null', 'brain'))
LIB = '<span data-os="win"><code>sentry_core.dll</code></span><span data-os="mac"><code>libsentry_core.dylib</code></span><span data-os="linux"><code>libsentry_core.so</code></span>'
PYRUN = '<span data-os="win"><code>python brain.py</code></span><span data-os="mac linux"><code>python3 brain.py</code></span>'
LAYOUT = cells([('pid', '0 · c_int64', 'w'), ('cpus', '8 · c_int32', 'w'), ('page_size', '12 · c_int32', 'w'), ('host', '16 · c_char × 256', 'w')])

S = []

S.append(f'''
        <h2 id="s1"><span class="sec">§1</span>Задача главы</h2>
        <p>Глава 1.1 закончилась функцией ядра <code>core_get_info</code> и программой на C, которая её вызывает. Агенту нужно, чтобы ту же функцию вызывала программа на Python — мозг агента. На Python пишутся решения агента, отправка сообщений в n8n и работа с моделями ИИ. Системные функции остаются в ядре на C. Чтобы соединить два языка, ядро собирается в динамическую библиотеку, а Python загружает её модулем <code>ctypes</code> из стандартной библиотеки.</p>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>К дрели подходят насадки разных производителей: сверло, бита, венчик для краски. Насадку вставляют в патрон, когда она нужна, и дрель вращает её своим мотором. Насадка подходит, если её хвостовик совпадает по форме и размеру с патроном.</p>
          <p class="miss">Неподходящая насадка в патрон не войдёт. Несовпадение структуры в C и Python загрузке не мешает: числа читаются, но из чужих байтов.</p>
        </div></div>
        <p><span class="term">Динамическая библиотека</span> — файл с готовым машинным кодом функций, который загружается в процесс программы во время её работы. <span data-os="win">В Windows такой файл называется DLL и имеет расширение <code>.dll</code>, как <code>kernel32.dll</code> из ЛР 1.</span><span data-os="mac">В macOS у такого файла расширение <code>.dylib</code>, как у <code>libSystem.B.dylib</code> из ЛР 1.</span><span data-os="linux">В Linux у такого файла расширение <code>.so</code> (shared object), как у <code>libc.so.6</code> из ЛР 1.</span> Своей функции <code>main</code> у библиотеки нет: её функции вызывает программа, которая её загрузила.</p>
        <p><span class="term">ctypes</span> — модуль Python, который загружает динамическую библиотеку и вызывает её функции. Он переводит значения Python в типы C и обратно: целое число Python — в <code>int64_t</code>, класс с полями — в структуру. Как устроены типы C, ctypes заранее не определяет: их описывают в коде на Python, и это описание должно совпасть с <code>core.h</code> до байта.</p>
        <figure class="scheme">
          <p class="scheme__head">Ядро и мозг в одном процессе</p>
          <div class="scheme__body">
            <svg viewBox="0 0 740 220" role="img" aria-label="Схема: процесс Python; внутри интерпретатор с brain.py и загруженная библиотека ядра; brain.py вызывает core_get_info через ctypes, библиотека вызывает системные функции">
              <rect x="10" y="20" width="520" height="185" fill="var(--paper)" stroke="var(--ink)" stroke-width="3" stroke-dasharray="8 5"/>
              <text x="24" y="42" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">один процесс: python</text>
              <rect x="30" y="60" width="200" height="120" fill="var(--acc-pale)" stroke="var(--ink)" stroke-width="3"/>
              <text x="130" y="88" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="13" font-weight="700" fill="var(--ink)">brain.py</text>
              <text x="130" y="110" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" fill="var(--ink-soft)">интерпретатор Python</text>
              <text x="130" y="150" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="11.5" fill="var(--ink)">class CoreInfo</text>
              <text x="130" y="166" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="11.5" fill="var(--ink)">ctypes.CDLL(…)</text>
              <path d="M232 105 H306" stroke="var(--ink)" stroke-width="3" fill="none"/><path d="M298 98 L308 105 L298 112" stroke="var(--ink)" stroke-width="3" fill="none"/>
              <text x="269" y="96" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="11" fill="var(--ink-soft)">ctypes</text>
              <path d="M306 145 H232" stroke="var(--acc)" stroke-width="3" fill="none" stroke-dasharray="6 4"/><path d="M240 138 L230 145 L240 152" stroke="var(--acc)" stroke-width="3" fill="none"/>
              <text x="269" y="166" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" fill="var(--acc)">272 байта</text>
              <rect x="310" y="60" width="200" height="120" fill="var(--ng-pale)" stroke="var(--ink)" stroke-width="3"/>
              <text x="410" y="88" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="12" font-weight="700" fill="var(--ink)" data-os="win">sentry_core.dll</text>
              <text x="410" y="88" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="12" font-weight="700" fill="var(--ink)" data-os="mac">libsentry_core.dylib</text>
              <text x="410" y="88" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="12" font-weight="700" fill="var(--ink)" data-os="linux">libsentry_core.so</text>
              <text x="410" y="110" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" fill="var(--ink-soft)">ядро агента, машинный код</text>
              <text x="410" y="158" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="11.5" fill="var(--ink)">core_get_info()</text>
              <path d="M512 120 H590" stroke="var(--ng)" stroke-width="3" fill="none"/><path d="M582 113 L592 120 L582 127" stroke="var(--ng)" stroke-width="3" fill="none"/>
              <rect x="594" y="70" width="136" height="100" fill="var(--page)" stroke="var(--ink)" stroke-width="3"/>
              <text x="662" y="112" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">системные</text>
              <text x="662" y="130" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">функции</text>
            </svg>
          </div>
          <p class="scheme__note">Пунктирная рамка — один процесс. Библиотека ядра загружается в процесс Python, и её код выполняется там же, где <code>brain.py</code>. Сплошная стрелка — вызов функции, пунктирная — 272 байта структуры, которые функция заполнила.</p>
        </figure>
        <div class="why">
          <p class="why__head">Зачем это нужно в работе</p>
          <ul class="why__list">
            <li><b>Писать каждую часть на подходящем языке.</b> Системные вызовы и быстрый код — на C, сценарии, сеть и ИИ — на Python. Так устроены numpy, драйверы баз данных и библиотеки машинного обучения: снаружи Python, внутри C.</li>
            <li><b>Вызывать системные функции из Python.</b> Модуль <code>ctypes</code> загружает и системные библиотеки: <span data-os="win"><code>kernel32.dll</code></span><span data-os="mac linux">библиотеку C системы</span>. Так в главе 0.1 Python получал номер процесса без кода на C.</li>
            <li><b>Находить ошибки на стыке языков.</b> Несовпадение описания структуры в Python и в C не вызывает ошибки или предупреждения. Его находят только сверкой размеров и смещений.</li>
          </ul>
        </div>
        <p>Глава продолжает репозиторий <code>sysprog-start</code> из шага 9 главы 1.1: в <code>agent/core</code> лежат <code>core.h</code>, <code>core_info.c</code> и <code>show_info.c</code>, папка <code>agent/brain</code> пуста. Репозиторий открыт в VS Code. <span data-os="win">Команды выполняются в окне <b>x64 Native Tools Command Prompt for VS 2022</b>; Python в нём должен быть 64-битным для x64, как и компилятор.</span><span data-os="mac linux">Команды выполняются во встроенном терминале VS Code из корня репозитория.</span></p>
        <p class="bridge">Python загружает только динамическую библиотеку, поэтому первая часть — собрать её из того же <code>core_info.c</code>.</p>
''')

CORE_WAS = '''<span class="k">#include</span> <span class="s">&lt;stdint.h&gt;</span>

<span class="k">#define</span> CORE_HOST_MAX <span class="n">256</span>
<span class="c">…</span>
<span class="k">int</span> <span class="f">core_get_info</span>(<span class="k">struct</span> core_info *out);'''
CORE_NOW = '''<span class="k">#include</span> <span class="s">&lt;stdint.h&gt;</span>
<mark>
<span class="k">#ifdef</span> _WIN32
<span class="k">#define</span> CORE_API __declspec(dllexport)
<span class="k">#else</span>
<span class="k">#define</span> CORE_API
<span class="k">#endif</span></mark>

<span class="k">#define</span> CORE_HOST_MAX <span class="n">256</span>
<span class="c">…</span>
<mark>CORE_API</mark> <span class="k">int</span> <span class="f">core_get_info</span>(<span class="k">struct</span> core_info *out);'''

S.append(f'''
        <div class="part" role="separator"><span><b>1</b>Библиотека ядра</span></div>
        <h2 id="s2"><span class="sec">§2</span>Шаг 1. Собрать библиотеку</h2>
        <p>Программа на C из главы 1.1 собиралась в исполняемый файл, где <code>main</code> вызывает <code>core_get_info</code>. Библиотека собирается из одного <code>core_info.c</code>, без <code>main</code>. Чтобы другая программа могла найти функцию в готовом файле, функция должна попасть в <span class="term">таблицу экспорта</span> — список имён и адресов функций, которые библиотека отдаёт наружу. <span data-os="win">MSVC кладёт туда только функции, отмеченные <code>__declspec(dllexport)</code>.</span><span data-os="mac linux">clang и gcc кладут туда все функции, кроме объявленных <code>static</code>, поэтому отметка не нужна.</span></p>
        <p>Код ядра собирается на трёх системах, поэтому отметку прячут за макросом <code>CORE_API</code>. В Windows он раскрывается в <code>__declspec(dllexport)</code>, в macOS и Linux — в пустое место. В <code>core.h</code> добавляются пять строк и одно слово перед объявлением функции:</p>
        <div class="code-pair">
          <figure class="code code--was" data-read>
            <figcaption><span>agent/core/core.h</span><span>было</span></figcaption>
<pre>{CORE_WAS}</pre>
          </figure>
          <figure class="code code--now" data-read>
            <figcaption><span>agent/core/core.h</span><span>стало</span></figcaption>
<pre>{CORE_NOW}</pre>
          </figure>
        </div>
        <p>Макрос <code>_WIN32</code> компилятор MSVC задаёт сам, поэтому <code>#ifdef _WIN32</code> выбирает ветку Windows без настройки. Файл <code>core_info.c</code> не меняется. Из папки <code>agent/core</code> собираем библиотеку:</p>
{cmd('cd agent\\core\ncl /nologo /W4 /LD core_info.c /Fe:sentry_core.dll\ndir /b sentry_core.*', 'cd agent/core\nclang -Wall -Wextra -shared -fPIC -o libsentry_core.dylib core_info.c\nls libsentry_core.dylib', 'cd agent/core\ngcc -Wall -Wextra -shared -fPIC -o libsentry_core.so core_info.c\nls libsentry_core.so')}
{per(win='<p>Ключ <code>/LD</code> собирает DLL вместо <code>.exe</code>, <code>/Fe:</code> задаёт имя файла.</p>',
     maclinux='<p>Ключ <code>-shared</code> собирает динамическую библиотеку вместо исполняемого файла. Ключ <code>-fPIC</code> делает код независимым от адреса: библиотека может загрузиться в любое место памяти процесса. Имя по соглашению начинается с <code>lib</code>.</p>')}
{shot('01-build', dict(
    win=f'{M(1)} Компоновщик создал вместе с DLL файлы <code>sentry_core.lib</code> и <code>sentry_core.exp</code>. {M(2)} Сама библиотека.',
    mac=f'{M(1)} Макрос <code>CORE_API</code>. {M(2)} Отметка перед объявлением функции. {M(3)} Сборка библиотеки — без сообщений. {M(4)} Файл <code>libsentry_core.dylib</code> появился, он виден и в панели слева.',
    linux=f'{M(1)} Макрос <code>CORE_API</code>. {M(2)} Отметка перед объявлением функции. {M(3)} Сборка библиотеки — без сообщений. {M(4)} Файл <code>libsentry_core.so</code> появился, он виден и в панели слева.'),
    dict(win='Командная строка MSVC: cl /LD собирает sentry_core.dll, рядом sentry_core.exp и sentry_core.lib',
         mac='VS Code с core.h: блок CORE_API и объявление функции в рамках, в терминале сборка clang -shared и файл libsentry_core.dylib',
         linux='VS Code с core.h: блок CORE_API и объявление функции в рамках, в терминале сборка gcc -shared и файл libsentry_core.so'))}
{per(win=f'<p>Строка {M(1)} — сообщение компоновщика: «Создается библиотека sentry_core.lib и объект sentry_core.exp». Файл <code>.lib</code> нужен программам на C, которые подключают DLL при сборке; Python его не использует. В папке три файла {M(2)}, и все три исключены в <code>.gitignore</code> шаблона: библиотека собирается из исходников на каждом компьютере.</p>',
     maclinux=f'<p>Сборка {M(3)} прошла без предупреждений, и в папке {M(4)} появился файл библиотеки. Шаблон репозитория уже исключает его в <code>.gitignore</code>: библиотека собирается из исходников на каждом компьютере.</p>')}
        <p class="step-done"><b>Что получилось.</b>Ядро собрано в библиотеку {LIB}. Перед загрузкой в Python стоит проверить, что функция в ней видна по имени.</p>
''')

S.append(f'''
        <h2 id="s3"><span class="sec">§3</span>Шаг 2. Проверить таблицу экспорта</h2>
        <p>Таблицу экспорта печатает служебная программа: <span data-os="win"><code>dumpbin</code> из набора MSVC</span><span data-os="mac"><code>nm</code> из инструментов разработчика Xcode</span><span data-os="linux"><code>nm</code> из пакета binutils</span>. По ней видно, найдёт ли Python функцию по имени.</p>
{cmd('dumpbin /nologo /exports sentry_core.dll', 'nm -gU libsentry_core.dylib', 'nm -D --defined-only libsentry_core.so')}
{per(win='<p>Ключ <code>/exports</code> печатает только таблицу экспорта.</p>', mac='<p>Ключ <code>-g</code> оставляет только внешние имена, <code>-U</code> убирает имена, которые библиотека берёт из других библиотек.</p>', linux='<p>Ключ <code>-D</code> читает таблицу динамических имён, <code>--defined-only</code> убирает имена, которые библиотека берёт из других библиотек.</p>')}
{shot('02-exports', dict(
    win=f'{M(1)} В библиотеке одна функция и одно имя. {M(2)} Номер 1, адрес внутри файла <code>00001000</code>, имя <code>core_get_info</code>.',
    mac=f'{M(1)} Строка <code>_core_get_info</code> с буквой <code>T</code>.',
    linux=f'{M(1)} Строка <code>core_get_info</code> с буквой <code>T</code>.'),
    dict(win='dumpbin /exports: number of functions 1, строка 1 0 00001000 core_get_info',
         mac='VS Code, терминал: nm -gU печатает адрес, T и _core_get_info', linux='VS Code, терминал: nm -D печатает адрес, T и core_get_info'))}
{per(win=f'<p>Строки {M(1)} показывают, что экспортирована одна функция. В строке {M(2)} имя совпадает с именем в коде: для функций C компилятор MSVC в 64-битной сборке имя не меняет. Если убрать <code>CORE_API</code> из <code>core.h</code> и собрать заново, функций в таблице не будет, и Python не найдёт <code>core_get_info</code>.</p>',
     mac=f'<p>Буква <code>T</code> {M(1)} означает, что имя относится к коду (секция text) и определено в этой библиотеке. Перед именем стоит подчёркивание: так macOS записывает имена функций C. При вызове из Python подчёркивание не пишут: при поиске имени его добавляет загрузчик macOS.</p>',
     linux=f'<p>Буква <code>T</code> {M(1)} означает, что имя относится к коду (секция text) и определено в этой библиотеке. Имя совпадает с именем в коде, под ним Python и найдёт функцию.</p>')}
        <p class="step-done"><b>Что получилось.</b>Функция <code>core_get_info</code> есть в таблице экспорта. Библиотеку можно загружать из Python.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>2</b>Вызов из Python</span></div>
        <h2 id="s4"><span class="sec">§4</span>Шаг 3. Загрузить библиотеку</h2>
        <p>Создаём файл <code>agent/brain/brain.py</code>. В первой версии он только загружает библиотеку и печатает, что получилось:</p>
{pyfile('agent/brain/brain.py · шаг 3', V1)}
        <p>Разбор по строкам.</p>
        <ul>
          <li><code>Path(__file__).resolve().parent.parent / "core"</code> — путь к папке ядра от места, где лежит сам <code>brain.py</code>: на уровень вверх из <code>brain</code> и в <code>core</code>. Так скрипт находит библиотеку, из какой бы папки его ни запустили.</li>
          <li><code>sys.platform</code> — строка с названием системы: <code>win32</code>, <code>darwin</code> (macOS) или <code>linux</code>. По ней выбирается имя файла библиотеки; для Linux имя берётся по умолчанию из <code>.get</code>.</li>
          <li><code>ctypes.CDLL(путь)</code> — загружает библиотеку в процесс и возвращает объект, через который доступны её функции. <code>CDLL</code> вызывает функции по обычному соглашению C. Путь передаётся строкой, поэтому <code>Path</code> обёрнут в <code>str</code>.</li>
          <li><code>core.core_get_info</code> — функция ищется в таблице экспорта при первом обращении к имени. Если имени нет, Python сообщит <code>AttributeError</code>.</li>
        </ul>
        <p>Запускаем из папки <code>agent/brain</code>:</p>
{cmd('cd ..\\brain\npython brain.py', 'cd ../brain\npython3 brain.py', 'cd ../brain\npython3 brain.py')}
{shot('03-load', dict(
    win=f'{M(1)} Объект библиотеки: полный путь к <code>sentry_core.dll</code> и её адрес в процессе (handle). {M(2)} Объект функции.',
    mac=f'{M(1)} Строка загрузки. {M(2)} Объект библиотеки: путь и адрес в процессе. {M(3)} Объект функции <code>_FuncPtr</code>.',
    linux=f'{M(1)} Строка загрузки. {M(2)} Объект библиотеки: путь и адрес в процессе. {M(3)} Объект функции <code>_FuncPtr</code>.'),
    dict(win='python brain.py печатает CDLL с путём к sentry_core.dll и handle, затем _FuncPtr object',
         mac='VS Code с brain.py: строка ctypes.CDLL в рамке, вывод CDLL libsentry_core.dylib handle и _FuncPtr object',
         linux='VS Code с brain.py: строка ctypes.CDLL в рамке, вывод CDLL libsentry_core.so handle и _FuncPtr object'))}
        <p>Число после слова <code>handle</code> — адрес, по которому библиотека загружена в память процесса Python. Объект функции <code>_FuncPtr</code> хранит адрес функции внутри библиотеки. Сколько у функции параметров и какого они типа, в объекте функции пока не записано.</p>
        <div class="margin-note margin-note--warn" data-os="win">
          <b>Python и библиотека одной архитектуры</b>
          <p>Процесс выполняет код одной архитектуры, поэтому 64-битный Python для x64 загружает только DLL для x64. Кадры главы сняты на компьютере с процессором ARM, где установлен и Python для ARM64. Если запустить <code>brain.py</code> им, загрузка падает:</p>
          <figure class="shot" style="margin:10px 0"><img src="img/win/09-arm.png" alt="python для ARM64 печатает OSError: [WinError 193] %1 не является приложением Win32 в строке ctypes.CDLL" loading="lazy"><figcaption>{M(1)} Python для ARM64. {M(2)} Ошибка в строке загрузки. {M(3)} <code>WinError 193</code> — файл не подходит процессу.</figcaption></figure>
          <p>Код 193 — <code>ERROR_BAD_EXE_FORMAT</code>. Архитектуру Python показывает <code>python -c "import platform; print(platform.machine())"</code>: для окна x64 Native Tools нужен ответ <code>AMD64</code>.</p>
        </div>
        <p class="step-done"><b>Что получилось.</b>Библиотека загружена в процесс Python, функция найдена по имени. Чтобы её вызвать, Python должен знать, как устроена структура <code>core_info</code>.</p>
''')

S.append(f'''
        <h2 id="s5"><span class="sec">§5</span>Шаг 4. Описать структуру в Python</h2>
        <p>Структура описывается классом, унаследованным от <code>ctypes.Structure</code>. Его атрибут <code>_fields_</code> — список пар «имя поля — тип ctypes» в том же порядке, что в <code>core.h</code>. По этому списку ctypes сам считает размер и смещения, применяя те же правила выравнивания, что компилятор C. Каждому типу C из <code>core.h</code> соответствует тип ctypes:</p>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Поле</th><th>Тип в <code>core.h</code></th><th>Тип ctypes</th><th>Байт</th></tr></thead>
            <tbody>
              <tr><td><code>pid</code></td><td><code>int64_t</code></td><td><code>ctypes.c_int64</code></td><td class="num-cell">8</td></tr>
              <tr><td><code>cpus</code></td><td><code>int32_t</code></td><td><code>ctypes.c_int32</code></td><td class="num-cell">4</td></tr>
              <tr><td><code>page_size</code></td><td><code>int32_t</code></td><td><code>ctypes.c_int32</code></td><td class="num-cell">4</td></tr>
              <tr><td><code>host</code></td><td><code>char[256]</code></td><td><code>ctypes.c_char * 256</code></td><td class="num-cell">256</td></tr>
            </tbody>
          </table>
        </div>
        <p>Запись <code>ctypes.c_char * 256</code> — массив из 256 элементов типа <code>c_char</code>, как <code>char host[256]</code> в C. Во второй версии <code>brain.py</code> после путей появляется класс, а вместо загрузки — проверка размера и смещений:</p>
{pyfile('agent/brain/brain.py · шаг 4 · после строки LIB_NAME', between(V2, 'class CoreInfo'))}
        <p>У каждого поля класса есть атрибуты <code>offset</code> — смещение от начала структуры — и <code>size</code> — размер в байтах. Функция <code>getattr(CoreInfo, name)</code> берёт поле по имени-строке из <code>_fields_</code>. Запускаем {PYRUN}:</p>
{shot('04-struct', dict(
    win=f'{M(1)} Размер структуры — 272 байта. {M(2)} Смещения 0, 8, 12, 16 и размеры полей.',
    mac=f'{M(1)} Описание полей в <code>_fields_</code>. {M(2)} Размер — 272. {M(3)} Смещения 0, 8, 12, 16 и размеры полей.',
    linux=f'{M(1)} Описание полей в <code>_fields_</code>. {M(2)} Размер — 272. {M(3)} Смещения 0, 8, 12, 16 и размеры полей.'),
    dict(win='python brain.py: sizeof 272, pid offset 0 size 8, cpus 8 4, page_size 12 4, host 16 256',
         mac='VS Code с brain.py: _fields_ в рамке, вывод sizeof 272 и смещения полей', linux='VS Code с brain.py: _fields_ в рамке, вывод sizeof 272 и смещения полей'))}
        <p>Числа совпали с раскладкой из шага 5 главы 1.1, которую посчитал компилятор C:</p>
        {LAYOUT}
        <p>Совпадение размера и смещений — единственная проверка, что описание в Python верное. Сами ctypes и компилятор её не делают: класс <code>CoreInfo</code> с <code>core.h</code> автоматически не сравнивается.</p>
        <p class="step-done"><b>Что получилось.</b>Класс <code>CoreInfo</code> описывает те же 272 байта, что <code>struct core_info</code>. Можно вызывать функцию.</p>
''')

S.append(f'''
        <h2 id="s6"><span class="sec">§6</span>Шаг 5. Вызвать функцию ядра</h2>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>Перед звонком в справочную записывают, что спросить и в каком виде ждать ответ: номер телефона или адрес. Без такой записи легко назвать не тот документ и не понять ответ.</p>
          <p class="miss">Оператор переспросит, если вопрос непонятен. Функция на C параметр не проверяет: она прочитает переданные байты как адрес структуры.</p>
        </div></div>
        <p>У функции на C в библиотеке нет сведений о типах параметров: в таблице экспорта только имя и адрес. Поэтому типы задают в Python двумя атрибутами объекта функции. <code>argtypes</code> — список типов параметров: один параметр, указатель на <code>CoreInfo</code>, записывается как <code>ctypes.POINTER(CoreInfo)</code>. <code>restype</code> — тип результата, <code>ctypes.c_int</code>. Если передать значение другого типа, ctypes не вызывает функцию и поднимает исключение <code>ArgumentError</code>.</p>
        <p>Третья версия <code>brain.py</code> загружает библиотеку, задаёт типы и вызывает функцию. Её начало до класса включительно такое же, как в шаге 4, и добавлен <code>import os</code>:</p>
{pyfile('agent/brain/brain.py · шаг 5 · после класса CoreInfo', between(V3, 'core = ctypes.CDLL'))}
        <p><code>CoreInfo()</code> создаёт структуру в памяти Python, все 272 байта — нули. <code>ctypes.byref(info)</code> передаёт её адрес, как <code>&amp;info</code> в C. Функция <code>os.getpid()</code> печатает номер процесса Python для сравнения. Запускаем {PYRUN}:</p>
{shot('05-call', dict(
    win=f'{M(1)} Номер процесса из ядра — 4656, <code>os.getpid()</code> — тоже 4656. {M(2)} Имя компьютера пришло строкой байтов <code>b\'WIN11-LAB\'</code>.',
    mac=f'{M(1)} Типы параметра и результата. {M(2)} Вызов с адресом структуры. {M(3)} Номер процесса из ядра совпал с <code>os.getpid()</code>. {M(4)} Имя пришло строкой байтов <code>b\'…\'</code>.',
    linux=f'{M(1)} Типы параметра и результата. {M(2)} Вызов с адресом структуры. {M(3)} Номер процесса из ядра совпал с <code>os.getpid()</code>. {M(4)} Имя пришло строкой байтов <code>b\'lab-linux\'</code>.'),
    dict(win='python brain.py: err 0, pid 4656 os.getpid 4656, cpus 4, page_size 4096, host b WIN11-LAB',
         mac='VS Code с brain.py: argtypes и restype, вызов с byref в рамках; вывод err 0, pid равен os.getpid, host b MacBook-Air-Maxim.local',
         linux='VS Code с brain.py: argtypes и restype, вызов с byref в рамках; вывод err 0, pid равен os.getpid, host b lab-linux'))}
        <p>Функция вернула 0, поля заполнены. Номер процесса из ядра совпал с номером процесса Python: <code>getpid</code> внутри библиотеки вернул номер того процесса, в который библиотека загружена. Это то, что показывает схема в §1, — ядро и мозг работают в одном процессе.</p>
        <p>Поле <code>host</code> ctypes вернул как <code>bytes</code> — последовательность байтов до первого нуля, на что указывает буква <code>b</code> перед кавычками. Строкой Python оно станет после <code>.decode("utf-8")</code>: ядро в главе 1.1 отдаёт имя в UTF-8 на всех трёх системах.</p>
        <p class="step-done"><b>Что получилось.</b>Python вызвал функцию ядра на C и прочитал все четыре поля. Следующая часть — что происходит, когда описание на стыке языков неверное.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>3</b>Ошибки на стыке языков</span></div>
        <h2 id="s7"><span class="sec">§7</span>Шаг 6. Поменять поля местами</h2>
        <p>Первая ошибка на стыке языков — описание полей, которое не совпадает с C. Для опыта переставим в <code>_fields_</code> два поля по 4 байта. Размер структуры от этого не меняется:</p>
        <div class="code-pair">
          <figure class="code code--was" data-read>
            <figcaption><span>agent/brain/brain.py</span><span>было</span></figcaption>
<pre>{hl_py(between(V3, '("cpus"', '("page_size"'))}</pre>
          </figure>
          <figure class="code code--now" data-read>
            <figcaption><span>agent/brain/brain.py</span><span>стало</span></figcaption>
<pre><mark>{hl_py(between(V4, '("page_size"', '("cpus"'))}</mark></pre>
          </figure>
        </div>
{shot('06-swap', dict(
    win=f'{M(1)} <code>cpus</code> — 4096, <code>page_size</code> — 4. Ошибки нет, <code>err</code> равен 0.',
    mac=f'{M(1)} Переставленные поля. {M(2)} <code>cpus</code> — 16384, <code>page_size</code> — 10. Ошибки нет, <code>err</code> равен 0.',
    linux=f'{M(1)} Переставленные поля. {M(2)} <code>cpus</code> — 4096, <code>page_size</code> — 10. Ошибки нет, <code>err</code> равен 0.'),
    dict(win='python brain.py после перестановки: cpus 4096, page_size 4', mac='VS Code: переставленные поля в _fields_, вывод cpus 16384 и page_size 10',
         linux='VS Code: переставленные поля в _fields_, вывод cpus 4096 и page_size 10'))}
        <p>Числа поменялись местами, а сообщений об ошибке не было. Функция на C записала число процессоров в байты 8–11, а размер страницы — в байты 12–15, как задано в <code>core.h</code>. Python прочитал байты 8–11 под именем <code>page_size</code>, потому что так написано в его описании. ctypes читает поля по смещениям из <code>_fields_</code>. Что записал C, он не проверяет.</p>
        <p>Здесь ошибку видно сразу: тысяч процессоров на компьютере не бывает. Если бы поменялись два поля одного смысла, например два счётчика, неверные числа ушли бы дальше в тревоги агента. Поэтому описание в Python сверяют с <code>core.h</code> по таблице шага 4 при каждой правке структуры. Возвращаем порядок полей.</p>
        <p class="step-done"><b>Что получилось.</b>Несовпадение описания полей не даёт ошибки: значения читаются из чужих байтов. Вторая ошибка на стыке — неверный адрес.</p>
''')

S.append(f'''
        <h2 id="s8"><span class="sec">§8</span>Шаг 7. Передать пустой адрес</h2>
        <p>В Python пустому указателю <code>NULL</code> соответствует <code>None</code>. ctypes разрешает передать <code>None</code> туда, где ждут указатель, поэтому такой вызов пройдёт проверку <code>argtypes</code>. В главе 1.1 функция ядра начинается с проверки <code>if (out == NULL)</code> — теперь видно, зачем она. Пятая версия вместо структуры передаёт <code>None</code> и печатает код с текстом:</p>
{pyfile('agent/brain/brain.py · шаг 7 · после строки restype', between(V5, 'err = core.core_get_info(None)'))}
        <p>Текст ошибки по коду в macOS и Linux возвращает <code>os.strerror</code>, в Windows — <code>ctypes.FormatError</code>: это вызов <code>FormatMessageW</code> из шага 4 главы 1.1, обёрнутый в ctypes.</p>
{shot('07-null', dict(
    win=f'{M(1)} Код 87 и текст «Параметр задан неверно.».',
    mac=f'{M(1)} Вызов с <code>None</code>. {M(2)} Код 22 — <code>EINVAL</code>, «Invalid argument».',
    linux=f'{M(1)} Вызов с <code>None</code>. {M(2)} Код 22 — <code>EINVAL</code>, «Invalid argument».'),
    dict(win='python brain.py: err 87 Параметр задан неверно.', mac='VS Code: вызов core_get_info(None), вывод err 22 Invalid argument',
         linux='VS Code: вызов core_get_info(None), вывод err 22 Invalid argument'))}
        <p>Функция вернула код ошибки, и процесс продолжил работу. Без проверки в ядре функция стала бы записывать нули по нулевому адресу.</p>
{per(win='<p>В Windows ctypes перехватывает такое обращение к памяти и поднимает в Python исключение <code>OSError</code> с текстом «access violation». Процесс продолжает работу, но что успела испортить функция до сбоя, неизвестно.</p>',
     maclinux='<p>Если убрать из <code>core_info.c</code> строки с <code>NULL</code> и пересобрать библиотеку, <code>python3 brain.py</code> завершается без вывода с кодом 139. Это 128 плюс 11 — номер сигнала <code>SIGSEGV</code>. Python не успевает поднять исключение: система завершает весь процесс, потому что ядро и мозг работают в одном процессе.</p>')}
        <p>Поэтому ядро проверяет всё, что ему передают, и отвечает кодом ошибки.</p>
        <p class="step-done"><b>Что получилось.</b>Ядро возвращает код на неверный адрес, и Python получает его текст. Осталось собрать окончательный <code>brain.py</code>, который превращает код ошибки в исключение.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>4</b>Мозг агента</span></div>
        <h2 id="s9"><span class="sec">§9</span>Шаг 8. Собрать brain.py</h2>
        <p>Окончательная версия собирает шаги 3–7 в функцию <code>get_info</code>. Она возвращает словарь Python, а при коде ошибки поднимает исключение <code>OSError</code> с кодом и текстом — так же поступают функции Python для работы с файлами. При запуске скрипт печатает первое сообщение агента в формате JSON:</p>
{pyfile('agent/brain/brain.py · окончательная версия', BRAIN)}
        <ul>
          <li><code>error_text</code> — текст ошибки по коду, отдельно для Windows и для macOS и Linux.</li>
          <li><code>raise OSError(err, error_text(err))</code> — код ядра становится исключением. Тот, кто вызывает <code>get_info</code>, обрабатывает его через <code>try</code>/<code>except OSError</code>.</li>
          <li><code>info.host.decode("utf-8")</code> — имя из байтов в строку Python.</li>
          <li><code>if __name__ == "__main__":</code> — блок выполняется, только когда <code>brain.py</code> запущен как программа. Если его подключат командой <code>import</code>, сообщение не печатается.</li>
          <li><code>**get_info()</code> — поля словаря вставляются в сообщение рядом с <code>event</code> и <code>os</code>.</li>
        </ul>
{shot('08-brain', dict(
    win=f'{M(1)} Сообщение <code>agent_started</code> в JSON: система <code>win32</code>, номер процесса, 4 процессора, страница 4096, имя <code>WIN11-LAB</code>.',
    mac=f'{M(1)} Функция <code>get_info</code>. {M(2)} Код ошибки становится исключением. {M(3)} Сообщение <code>agent_started</code> в JSON с системой <code>darwin</code>.',
    linux=f'{M(1)} Функция <code>get_info</code>. {M(2)} Код ошибки становится исключением. {M(3)} Сообщение <code>agent_started</code> в JSON: <code>linux</code>, номер процесса 28, 10 процессоров, страница 4096, <code>lab-linux</code>.'),
    dict(win='python brain.py печатает JSON agent_started с os win32, cpus 4, page_size 4096, host WIN11-LAB',
         mac='VS Code с brain.py: def get_info и raise OSError в рамках, вывод JSON agent_started darwin',
         linux='VS Code с brain.py: def get_info и raise OSError в рамках, вывод JSON agent_started linux'))}
        <p>Сообщение готово к отправке: в формате JSON его принимает сценарий n8n. Файл <code>brain.py</code> и изменённый <code>core.h</code> отправляем в репозиторий; в <code>agent/brain/README.md</code> дописываем строку о <code>brain.py</code>, в <code>agent/core/README.md</code> — о сборке библиотеки:</p>
        <figure class="code">
          <figcaption><span>терминал в папке sysprog-start</span><span>то же, что плюс, Commit и Sync Changes</span></figcaption>
<pre>git add agent/core/core.h agent/core/README.md agent/brain/brain.py agent/brain/README.md
git commit -m "brain: brain.py вызывает core_get_info через ctypes"
git push</pre>
        </figure>
        <p>Файл библиотеки в список не входит: его исключает <code>.gitignore</code>, и <code>git status</code> его не показывает.</p>
        <p class="step-done"><b>Что получилось.</b>Мозг агента на Python вызывает ядро на C и печатает сведения о системе в JSON. Последняя часть — проверка описания структуры, которое сгенерирует помощник ИИ.</p>

        <h2 id="s10"><span class="sec">§10</span>Запрос к помощнику ИИ</h2>
        <p>Описание структуры для ctypes — частый запрос к помощнику ИИ: его можно сгенерировать по <code>core.h</code>. В режиме Р1 из главы 0.3 ответ сверяется с кодом и кадрами. Запрос:</p>
        <figure class="code">
          <figcaption><span>запрос помощнику</span></figcaption>
<pre>Вот файл core.h. Напиши для него класс ctypes.Structure и задай argtypes и restype
для функции core_get_info. Библиотека загружается на Windows, macOS и Linux.</pre>
        </figure>
        <ul class="checklist">
          <li>типы полей точного размера: <code>c_int64</code>, <code>c_int32</code>; <code>c_long</code> в 64-битной Windows — 4 байта, как <code>long</code> в C;</li>
          <li>порядок полей как в <code>core.h</code>, массив — <code>c_char * 256</code>;</li>
          <li><code>argtypes</code> — <code>[ctypes.POINTER(CoreInfo)]</code>, <code>restype</code> — <code>ctypes.c_int</code>;</li>
          <li>сгенерированный класс проходит проверку шага 4: <code>sizeof</code> — 272, смещения 0, 8, 12, 16.</li>
        </ul>
        <p>Последний пункт проверяется запуском: в шаге 6 неверное описание не дало ни одной ошибки.</p>
''')

S.append('''
        <div class="part" role="separator"><span><b>5</b>Справка</span></div>
        <h2 id="s11"><span class="sec">§11</span>Справка: команды и ctypes</h2>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Что нужно</th><th>Windows</th><th>macOS</th><th>Linux</th></tr></thead>
            <tbody>
              <tr><td>Собрать библиотеку</td><td><code>cl /LD a.c /Fe:x.dll</code></td><td><code>clang -shared -fPIC -o libx.dylib a.c</code></td><td><code>gcc -shared -fPIC -o libx.so a.c</code></td></tr>
              <tr><td>Отметить функцию для экспорта</td><td><code>__declspec(dllexport)</code></td><td>не нужно</td><td>не нужно</td></tr>
              <tr><td>Таблица экспорта</td><td><code>dumpbin /exports x.dll</code></td><td><code>nm -gU libx.dylib</code></td><td><code>nm -D --defined-only libx.so</code></td></tr>
              <tr><td>Архитектура Python</td><td colspan="3"><code>python -c "import platform; print(platform.machine())"</code></td></tr>
            </tbody>
          </table>
        </div>
        <div class="table-scroll">
          <table>
            <thead><tr><th>В C</th><th>В ctypes</th></tr></thead>
            <tbody>
              <tr><td><code>int</code>, <code>int32_t</code>, <code>int64_t</code></td><td><code>c_int</code>, <code>c_int32</code>, <code>c_int64</code></td></tr>
              <tr><td><code>char buf[N]</code></td><td><code>c_char * N</code>, значение — <code>bytes</code></td></tr>
              <tr><td><code>struct x { … }</code></td><td>класс от <code>ctypes.Structure</code> с <code>_fields_</code></td></tr>
              <tr><td><code>struct x *</code> в объявлении</td><td><code>ctypes.POINTER(X)</code> в <code>argtypes</code></td></tr>
              <tr><td><code>&amp;info</code> при вызове</td><td><code>ctypes.byref(info)</code></td></tr>
              <tr><td><code>NULL</code></td><td><code>None</code></td></tr>
              <tr><td><code>sizeof(struct x)</code>, смещение поля</td><td><code>ctypes.sizeof(X)</code>, <code>X.поле.offset</code></td></tr>
              <tr><td>текст ошибки</td><td><code>os.strerror(code)</code>; в Windows <code>ctypes.FormatError(code)</code></td></tr>
            </tbody>
          </table>
        </div>

        <div class="part" role="separator"><span><b>6</b>Проверка себя</span></div>
        <h2 id="s12"><span class="sec">§12</span>Частые вопросы</h2>
        <div class="myths">
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>ctypes читает из библиотеки, какие параметры у функции и какие поля у структуры.</div>
            <div class="myth__yes"><b>На самом деле</b>В таблице экспорта только имя и адрес. Типы задаются в Python: <code>_fields_</code>, <code>argtypes</code>, <code>restype</code>.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Если поля описаны неверно, Python сообщит об ошибке.</div>
            <div class="myth__yes"><b>На самом деле</b>В шаге 6 переставленные поля дали неверные числа без ошибки. Проверка — сверка размера и смещений с <code>core.h</code>.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Библиотека ядра работает отдельной программой рядом с Python.</div>
            <div class="myth__yes"><b>На самом деле</b>Она загружается в процесс Python: номер процесса из ядра совпал с <code>os.getpid()</code>. Падение в ядре завершает и Python.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Файл библиотеки нужно положить в репозиторий.</div>
            <div class="myth__yes"><b>На самом деле</b>Библиотека собирается из исходников под систему и архитектуру компьютера. В репозитории — <code>core.h</code> и <code>core_info.c</code>, файлы <code>.dll</code>, <code>.dylib</code>, <code>.so</code> исключены в <code>.gitignore</code>.</div>
          </div>
        </div>

        <h2 id="s13"><span class="sec">§13</span>Проверьте себя</h2>
        <details>
          <summary>Почему в Windows функцию нужно отметить <code>__declspec(dllexport)</code>, а в macOS и Linux — нет?</summary>
          <p>MSVC кладёт в таблицу экспорта DLL только отмеченные функции. clang и gcc экспортируют все функции, кроме <code>static</code>. Макрос <code>CORE_API</code> даёт отметку только при сборке в Windows.</p>
        </details>
        <details>
          <summary>Какой командой проверить, что функция попала в библиотеку?</summary>
          <p><code>dumpbin /exports</code> в Windows, <code>nm -gU</code> в macOS, <code>nm -D --defined-only</code> в Linux. В выводе должно быть имя <code>core_get_info</code>.</p>
        </details>
        <details>
          <summary>Чему равны <code>ctypes.sizeof(CoreInfo)</code> и смещение поля <code>host</code>, если описание верное?</summary>
          <p>272 и 16 — столько же, сколько у <code>struct core_info</code> в C.</p>
        </details>
        <details>
          <summary>Зачем задавать <code>argtypes</code>, если вызов работает и без них?</summary>
          <p>С <code>argtypes</code> ctypes проверяет тип каждого параметра и откажется передать, например, число вместо указателя. Без них значение уходит в функцию как есть, и C прочитает его как адрес.</p>
        </details>
        <details>
          <summary>Почему поле <code>host</code> приходит как <code>b'lab-linux'</code> и что с ним делать?</summary>
          <p>Массив <code>c_char</code> ctypes отдаёт как <code>bytes</code> до первого нуля. Строкой Python оно становится после <code>.decode("utf-8")</code>.</p>
        </details>
        <details>
          <summary>Что означает <code>OSError: [WinError 193]</code> при загрузке DLL?</summary>
          <p>Архитектура DLL не совпадает с архитектурой Python, например DLL для x64 и Python для ARM64. Библиотеку собирают компилятором той же архитектуры, что и Python.</p>
        </details>

        <h2 id="s14"><span class="sec">§14</span>Шпаргалка по главе</h2>
        <div class="cheat">
          <div><b>Библиотека</b><span data-os="win"><code>cl /LD core_info.c /Fe:sentry_core.dll</code></span><span data-os="mac"><code>clang -shared -fPIC -o libsentry_core.dylib core_info.c</code></span><span data-os="linux"><code>gcc -shared -fPIC -o libsentry_core.so core_info.c</code></span><span>в Windows — <code>CORE_API</code></span></div>
          <div><b>Экспорт</b><span data-os="win"><code>dumpbin /exports sentry_core.dll</code></span><span data-os="mac"><code>nm -gU libsentry_core.dylib</code></span><span data-os="linux"><code>nm -D --defined-only libsentry_core.so</code></span></div>
          <div><b>Загрузка</b><span><code>core = ctypes.CDLL(str(путь))</code></span><span>архитектура Python = архитектура библиотеки</span></div>
          <div><b>Структура</b><span><code>class CoreInfo(ctypes.Structure)</code></span><span><code>_fields_</code> в порядке <code>core.h</code></span><span><code>ctypes.sizeof</code> = 272</span></div>
          <div><b>Вызов</b><span><code>argtypes = [ctypes.POINTER(CoreInfo)]</code></span><span><code>restype = ctypes.c_int</code></span><span><code>core.core_get_info(ctypes.byref(info))</code></span></div>
          <div><b>Ошибка</b><span>код ≠ 0 → <code>raise OSError(код, текст)</code></span><span><code>None</code> = <code>NULL</code></span></div>
        </div>

        <h3>Итог главы</h3>
        <p>Ядро агента собрано в динамическую библиотеку из того же <code>core_info.c</code>. В Windows функция отмечена <code>__declspec(dllexport)</code> через макрос <code>CORE_API</code>, в macOS и Linux она экспортируется без отметки, и таблица экспорта это показывает. Python загружает библиотеку модулем <code>ctypes</code> в свой процесс, поэтому архитектура библиотеки и Python должна совпадать. Структура описана классом с <code>_fields_</code>, типы параметров — в <code>argtypes</code> и <code>restype</code>, адрес передаётся через <code>byref</code>. Описание в Python ничем не сверяется с <code>core.h</code>: переставленные поля дали неверные числа без ошибки, поэтому размер и смещения проверяются запуском. Пустой адрес ядро отклоняет кодом ошибки, и <code>brain.py</code> превращает этот код в <code>OSError</code>. Итог — <code>brain.py</code>, который печатает сообщение <code>agent_started</code> в JSON.</p>

        <div class="sources">
          <b>Откуда взяты факты</b>
          <ol>
            <li>Кадры и выводы: macOS 26.1, Apple clang 17.0.0, Python 3.12.12; Linux — контейнер Debian 13, gcc 14.4, Python 3.13.5; Windows 11 ARM64 в VirtualBox, MSVC 19.44 (x64), Python 3.14.0 для x64 и для ARM64; VS Code 1.138.</li>
            <li>ctypes: <code>CDLL</code>, <code>Structure</code>, <code>_fields_</code>, <code>argtypes</code>, <code>restype</code>, <code>byref</code>, <code>FormatError</code> — <a href="https://docs.python.org/3/library/ctypes.html">документация Python, ctypes</a>.</li>
            <li><code>__declspec(dllexport)</code> и экспорт из DLL — <a href="https://learn.microsoft.com/cpp/build/exporting-from-a-dll-using-declspec-dllexport">Microsoft Learn</a>; ключ <code>/LD</code> — <a href="https://learn.microsoft.com/cpp/build/reference/md-mt-ld-use-run-time-library">Microsoft Learn</a>; <code>dumpbin /exports</code> — <a href="https://learn.microsoft.com/cpp/build/reference/exports">Microsoft Learn</a>.</li>
            <li>Код 193 <code>ERROR_BAD_EXE_FORMAT</code> — <a href="https://learn.microsoft.com/windows/win32/debug/system-error-codes--0-499-">Microsoft Learn, System Error Codes</a>.</li>
            <li>Ключи <code>-shared</code> и <code>-fPIC</code> — <a href="https://gcc.gnu.org/onlinedocs/gcc/Link-Options.html">документация GCC</a>; <code>nm</code> — <a href="https://sourceware.org/binutils/docs/binutils/nm.html">документация binutils</a>.</li>
          </ol>
        </div>

        <div class="pager">
          <a href="../06-c-dlya-sistemnogo-programmista/index.html">← 1.1 C для системного программиста</a>
          <a href="../../index.html">Оглавление</a>
        </div>

        <div class="colophon">
          <span>Глава 1.2 · C и Python вместе · Справочник по системному программированию</span>
          <span class="author-line">Автор: Макаров Максим Николаевич</span>
        </div>
''')

CONTENTS = [('s1', 'Задача главы'), ('s2', 'Шаг 1. Собрать библиотеку'), ('s3', 'Шаг 2. Проверить таблицу экспорта'),
            ('s4', 'Шаг 3. Загрузить библиотеку'), ('s5', 'Шаг 4. Описать структуру в Python'), ('s6', 'Шаг 5. Вызвать функцию ядра'),
            ('s7', 'Шаг 6. Поменять поля местами'), ('s8', 'Шаг 7. Передать пустой адрес'), ('s9', 'Шаг 8. Собрать brain.py'),
            ('s10', 'Запрос к помощнику ИИ'), ('s11', 'Справка: команды и ctypes'), ('s12', 'Частые вопросы'),
            ('s13', 'Проверьте себя'), ('s14', 'Шпаргалка по главе')]
TOC = '\n'.join(f'            <li><a href="#{a}">{t}</a></li>' for a, t in CONTENTS)

PAGE = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>1.2 C и Python вместе: библиотека и ctypes · Справочник по системному программированию</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,600;0,7..72,700;1,7..72,400&family=Pixelify+Sans:wght@500;600;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css">
</head>
<body>
  <div class="book">
    <div class="book__body">
      <div class="spine"><span>Модуль 1 · Рабочее место: C, Python и ИИ</span></div>

      <main class="leaf">
        <div class="running">
          <p class="eyebrow"><a href="../../index.html" style="text-decoration:none;color:inherit">Справочник по системному программированию</a> · модуль 1 · рабочее место</p>
          <p class="running__folio">1.2</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">1.2</span>
          <h1>C и Python вместе:<br>библиотека и ctypes</h1>
          <p class="lead">В главе функция ядра <code>core_get_info</code> из главы 1.1 собирается в динамическую библиотеку, и её вызывает программа на Python — мозг агента <code>brain.py</code>. Разобрано, как функция попадает в таблицу экспорта, как Python загружает библиотеку модулем <code>ctypes</code>, описывает структуру и передаёт её адрес. Две ошибки на стыке языков показаны на настоящем запуске: переставленные поля и пустой адрес. В конце <code>brain.py</code> печатает первое сообщение агента в JSON.</p>
        </header>

        <dl class="passport">
          <div><dt>Категория</dt><dd>C и Python</dd></div>
          <div><dt>Уровень</dt><dd>Начальный</dd></div>
          <div><dt>Что получится</dt><dd>Библиотека ядра и <code>agent/brain/brain.py</code></dd></div>
          <div><dt>Сколько занимает</dt><dd>Пара 3, около сорока пяти минут за компьютером</dd></div>
        </dl>

        <nav class="contents">
          <b>Порядок действий</b>
          <ol>
{TOC}
          </ol>
        </nav>
{''.join(S)}
      </main>
    </div>
  </div>
  <script src="../../book.js"></script>
</body>
</html>
'''

if __name__ == '__main__':
    OUT.write_text(PAGE)
    print('ok', OUT, len(PAGE))
