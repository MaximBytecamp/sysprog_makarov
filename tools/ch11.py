"""Глава 1.1 «C для системного программиста» → temy/06-c-dlya-sistemnogo-programmista/index.html.

Код программ берётся из tools/src11/posix и tools/src11/win — это те же файлы, что собраны на кадрах:
macOS 26.1 (Apple clang 17) — VS Code на Mac; Linux — VS Code на Mac, терминал в контейнере Debian 13 с gcc 14.4
(образ sp-gcc на основе gcc:14, имя машины lab-linux); Windows 11 ARM — ВМ Win11-lab, x64 Native Tools Command
Prompt, MSVC 19.44. Съёмка: src11/shoot.py (mac, linux) и ~/sysprog-shots/m1w*.txt (Windows), рамки — mark.py и winmark.py.
Числа в тексте взяты с кадров: PID 34535 (macOS), 45 (Linux), 2820 (Windows)."""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / 'src11'
OUT = ROOT / 'temy/06-c-dlya-sistemnogo-programmista/index.html'

KW = r'\b(return|if|for|while|static|const|struct|sizeof|unsigned|void|char|int|long|#include|#define|#ifndef|#endif)\b'
TYPES = r'\b(int64_t|int32_t|size_t|pid_t|DWORD|WCHAR|HANDLE|SYSTEM_INFO|BOOL)\b'


def hl(code):
    """Подсветка C: комментарии, строки, ключевые слова, типы, функции, числа."""
    out = []
    for line in code.split('\n'):
        tokens = re.split(r'("(?:[^"\\]|\\.)*"|<[a-z/._]+\.h>|\'(?:[^\'\\]|\\.)\')', line)
        res = []
        for t in tokens:
            if not t:
                continue
            if t.startswith('"') or t.startswith('<') or t.startswith("'"):
                res.append(f'<span class="s">{html.escape(t)}</span>')
                continue
            e = html.escape(t)
            e = re.sub(r'(#include|#define|#ifndef|#endif)', r'<span class="k">\1</span>', e)
            e = re.sub(TYPES, r'<span class="t">\1</span>', e)
            e = re.sub(r'(?<![#\w])(return|if|for|static|const|struct|sizeof|unsigned|void|char|int|long)\b', r'<span class="k">\1</span>', e)
            e = re.sub(r'\b([A-Za-z_]\w*)(?=\()', lambda m: m.group(1) if m.group(1) in ('if', 'for', 'sizeof', 'return') else f'<span class="f">{m.group(1)}</span>', e)
            e = re.sub(r'(?<![\w#])(\d+)\b', r'<span class="n">\1</span>', e)
            res.append(e)
        out.append(''.join(res))
    return '\n'.join(out).rstrip('\n')


def src(os_, name):
    text = (SRC / ('win' if os_ == 'win' else 'posix') / name).read_text()
    if os_ == 'linux' and name == 'errors.c':
        text = text.replace('/etc/sudoers', '/etc/shadow')
    return text


def code(name, oss=('win', 'mac linux'), note=''):
    """Файл для вставки: по блоку на группу систем с одинаковым кодом."""
    blocks = []
    for o in oss:
        first = o.split()[0]
        label = {'win': 'Windows', 'mac linux': 'macOS и Linux', 'mac': 'macOS', 'linux': 'Linux', 'win mac linux': 'все системы'}[o]
        cap = f'{name} · {label}' + (f' · {note}' if note else '')
        blocks.append(f'        <figure class="code" data-os="{o}">\n          <figcaption><span>{cap}</span></figcaption>\n'
                      f'<pre>{hl(src(first, name))}</pre>\n        </figure>')
    return '\n'.join(blocks)


def cmd(win, mac, linux, what='терминал в папке pair02'):
    """Команда сборки и запуска для каждой системы."""
    rows = []
    for o, c, where in (('win', win, 'x64 Native Tools Command Prompt'), ('mac', mac, what), ('linux', linux, what)):
        rows.append(f'        <figure class="code" data-os="{o}">\n          <figcaption><span>{where}</span></figcaption>\n<pre>{html.escape(c)}</pre>\n        </figure>')
    return '\n'.join(rows)


def shot(name, caps, alts, oss=('win', 'mac', 'linux')):
    out = []
    for o in oss:
        out.append(f'        <figure class="shot" data-os="{o}">\n          <img src="img/{o}/{name}.png" alt="{html.escape(alts[o])}" loading="lazy">\n'
                   f'          <figcaption>{caps[o]}</figcaption>\n        </figure>')
    return '\n'.join(out)


def per(**kw):
    """Абзацы по системам: per(win='…', mac='…', linux='…', maclinux='…')."""
    out = []
    for k, v in kw.items():
        o = 'mac linux' if k == 'maclinux' else k
        out.append(f'        <div data-os="{o}">{v}</div>')
    return '\n'.join(out)


def mk(n):
    return f'<span class="mk">{n}</span>'


def cells(items, cls=''):
    """Полоса ячеек памяти: [(значение, подпись, класс)]."""
    s = ''.join(f'<span class="{c}"><i>{html.escape(v)}</i><small>{html.escape(l)}</small></span>' for v, l, c in items)
    return f'<div class="bytes {cls}">{s}</div>'


def ascii_cells(text, zero=True):
    items = [(ch, f'{ord(ch):02x}', '') for ch in text]
    if zero:
        items.append(('\\0', '00', 'z'))
    return items


M = mk
HOST_MAC = ascii_cells('MacBook-Air-Maxim.local')
HOST_LIN = ascii_cells('lab-linux')
HOST_WIN = []
for ch in 'WIN11-LAB':
    HOST_WIN += [(ch, f'{ord(ch):02x}', ''), ('', '00', 'gap')]
HOST_WIN += [('\\0', '00', 'z'), ('', '00', 'z')]

S = {}

# ─────────────────────────────── §1 ───────────────────────────────
S['s1'] = f'''
        <h2 id="s1"><span class="sec">§1</span>Задача главы</h2>
        <p>В модуле 0 программа <code>hello.c</code> вызывала одну системную функцию, которая возвращает число, — номер процесса. Большинство функций системного интерфейса устроены сложнее. Они принимают адрес памяти и записывают туда результат: структуру с десятком полей, строку с именем или путь к файлу. Об ошибке они сообщают числом, а причину кладут отдельно. Для вызова таких функций нужны четыре темы языка C. Первая — сколько байт занимает каждый тип. Вторая — как функция заполняет структуру по указателю. Третья — как устроена строка в буфере. Четвёртая — где искать код ошибки.</p>
        <p>В главе эти четыре темы разобраны на маленьких программах, и из них собирается первая функция ядра агента — <code>core_get_info</code>. Она заполняет структуру <code>struct core_info</code> четырьмя сведениями о компьютере: номер процесса агента, число процессоров, размер страницы памяти и имя компьютера. В главе 1.2 эта функция войдёт в библиотеку ядра, и мозг агента на Python будет вызывать её через <code>ctypes</code>.</p>
        <figure class="scheme">
          <p class="scheme__head">Что делает функция ядра</p>
          <div class="scheme__body">
            <svg viewBox="0 0 760 210" role="img" aria-label="Схема: программа выделяет пустую структуру core_info и передаёт её адрес функции core_get_info; функция вызывает четыре системные функции и записывает их ответы в поля структуры; возвращает 0 или код ошибки">
              <rect x="10" y="40" width="210" height="130" fill="var(--acc-pale)" stroke="var(--ink)" stroke-width="3"/>
              <text x="115" y="30" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="12" font-weight="700" fill="var(--ink)">struct core_info info</text>
              <g font-family="Roboto Mono, monospace" font-size="12" fill="var(--ink)">
                <rect x="22" y="52" width="186" height="26" fill="var(--page)" stroke="var(--ink)" stroke-width="2"/><text x="30" y="70">pid</text>
                <rect x="22" y="80" width="186" height="26" fill="var(--page)" stroke="var(--ink)" stroke-width="2"/><text x="30" y="98">cpus</text>
                <rect x="22" y="108" width="186" height="26" fill="var(--page)" stroke="var(--ink)" stroke-width="2"/><text x="30" y="126">page_size</text>
                <rect x="22" y="136" width="186" height="26" fill="var(--page)" stroke="var(--ink)" stroke-width="2"/><text x="30" y="154">host[256]</text>
              </g>
              <path d="M222 70 H300" stroke="var(--ink)" stroke-width="3" fill="none"/><path d="M292 63 L302 70 L292 77" stroke="var(--ink)" stroke-width="3" fill="none"/>
              <text x="261" y="60" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="11" fill="var(--ink-soft)">&amp;info</text>
              <rect x="304" y="40" width="170" height="130" fill="var(--page)" stroke="var(--ink)" stroke-width="3"/>
              <text x="389" y="66" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="13" font-weight="700" fill="var(--ink)">core_get_info</text>
              <text x="389" y="92" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" fill="var(--ink-soft)">ядро агента, C</text>
              <text x="389" y="140" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" fill="var(--ink-soft)">вернёт 0 или</text>
              <text x="389" y="156" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" fill="var(--ink-soft)">код ошибки</text>
              <path d="M300 150 H222" stroke="var(--acc)" stroke-width="3" fill="none" stroke-dasharray="6 4"/><path d="M230 143 L220 150 L230 157" stroke="var(--acc)" stroke-width="3" fill="none"/>
              <text x="261" y="140" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" fill="var(--acc)">заполняет</text>
              <path d="M476 105 H540" stroke="var(--ng)" stroke-width="3" fill="none"/><path d="M532 98 L542 105 L532 112" stroke="var(--ng)" stroke-width="3" fill="none"/>
              <rect x="544" y="20" width="206" height="170" fill="var(--ng-pale)" stroke="var(--ink)" stroke-width="3"/>
              <text x="647" y="42" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">системные функции</text>
              <g font-family="Roboto Mono, monospace" font-size="11.5" fill="var(--ink)" data-os="mac linux">
                <text x="556" y="72">getpid()</text><text x="556" y="100">sysconf(_SC_NPROC…)</text><text x="556" y="128">sysconf(_SC_PAGESIZE)</text><text x="556" y="156">gethostname()</text>
              </g>
              <g font-family="Roboto Mono, monospace" font-size="11.5" fill="var(--ink)" data-os="win">
                <text x="556" y="72">GetCurrentProcessId()</text><text x="556" y="100">GetNativeSystemInfo()</text><text x="556" y="128">  ↳ тот же вызов</text><text x="556" y="156">GetComputerNameW()</text>
              </g>
            </svg>
          </div>
          <p class="scheme__note">Программа выделяет пустую структуру и передаёт функции её адрес. Функция вызывает системные функции и записывает ответы в поля. Сама функция возвращает только число: 0 — всё получилось, другое число — код ошибки системы.</p>
        </figure>
        <p>Такой порядок — адрес пустой структуры на входе и код ошибки на выходе — повторяет сам системный интерфейс. <span data-os="win">Функция WinAPI <code>GetNativeSystemInfo</code> заполняет структуру <code>SYSTEM_INFO</code> по адресу, <code>GetComputerNameW</code> пишет имя в переданный буфер.</span><span data-os="mac linux">Функция POSIX <code>uname</code> заполняет структуру <code>struct utsname</code> по адресу, <code>gethostname</code> пишет имя в переданный буфер.</span> Ядро агента пишется в том же стиле, поэтому его функции читаются так же, как документация системы.</p>
        <div class="why">
          <p class="why__head">Зачем это нужно в работе</p>
          <ul class="why__list">
            <li><b>Читать документацию системы.</b> Описание каждой функции WinAPI и POSIX дано объявлением на C: типы параметров, указатели, размер буфера, значение при ошибке. Без этих четырёх тем объявление не читается.</li>
            <li><b>Передавать данные между языками.</b> Мозг агента на Python читает структуру ядра через <code>ctypes</code>. Для этого он должен знать размер и порядок каждого поля, а размеры у части типов C зависят от системы.</li>
            <li><b>Не выходить за границы буфера.</b> Запись или чтение за концом буфера — частая причина падений и уязвимостей системных программ. Авария CrowdStrike из главы 0.2 началась с чтения за границей массива.</li>
            <li><b>Сообщать причину сбоя.</b> Агент работает без человека. По коду ошибки в журнале видно, что произошло: файла нет, доступ запрещён или буфер мал.</li>
          </ul>
        </div>
        <p>Все программы главы лежат в отдельной папке <code>pair02</code>: <span data-os="win"><code>C:\\syspro\\pair02</code></span><span data-os="mac linux"><code>~/syspro/pair02</code></span>, рядом с папкой <code>pair01</code> из лабораторной работы 1. Файлы ядра в конце главы переносятся в репозиторий <code>sysprog-start</code>, в папку <code>agent/core</code>. <span data-os="win">Программы собираются компилятором MSVC в окне <b>x64 Native Tools Command Prompt for VS 2022</b>, как в ЛР 1. Код набирается в VS Code.</span><span data-os="mac">Программы набираются в VS Code и собираются компилятором clang во встроенном терминале VS Code (<b>Terminal → New Terminal</b>).</span><span data-os="linux">Программы набираются в VS Code и собираются компилятором gcc во встроенном терминале VS Code (<b>Terminal → New Terminal</b>).</span></p>
        <div class="margin-note">
          <b>Как читать кадры</b>
          <p>Кадры сделаны для системы, выбранной переключателем вверху страницы. Красные рамки отмечают места, о которых идёт речь в тексте; номер рамки повторяется в тексте в красном квадрате, например {M(1)}. Номера процессов, имя компьютера и число процессоров у вас будут другими.</p>
        </div>
        <p class="bridge">Первая тема — размеры типов: от них зависит, как читать любую структуру системы.</p>
'''

# ─────────────────────────────── Шаг 1 ───────────────────────────────
SIZES_TABLE = '''        <div class="table-scroll">
          <table>
            <thead><tr><th>Тип</th><th>Windows</th><th>macOS</th><th>Linux</th><th>Что в нём хранят</th></tr></thead>
            <tbody>
              <tr><td><code>char</code></td><td class="num-cell">1</td><td class="num-cell">1</td><td class="num-cell">1</td><td>один байт: букву ASCII или часть буквы UTF-8</td></tr>
              <tr><td><code>int</code></td><td class="num-cell">4</td><td class="num-cell">4</td><td class="num-cell">4</td><td>целое число, код возврата</td></tr>
              <tr><td><code>long</code></td><td class="num-cell">4</td><td class="num-cell">8</td><td class="num-cell">8</td><td>целое число; размер зависит от системы</td></tr>
              <tr><td><code>void *</code></td><td class="num-cell">8</td><td class="num-cell">8</td><td class="num-cell">8</td><td>адрес в памяти</td></tr>
              <tr><td><code>int64_t</code></td><td class="num-cell">8</td><td class="num-cell">8</td><td class="num-cell">8</td><td>целое число ровно в 8 байт</td></tr>
              <tr><td><code>DWORD</code> / <code>pid_t</code></td><td class="num-cell">4</td><td class="num-cell">4</td><td class="num-cell">4</td><td>номер процесса и другие числа системы</td></tr>
              <tr><td><code>WCHAR</code></td><td class="num-cell">2</td><td>—</td><td>—</td><td>одна буква строки Windows в кодировке UTF-16</td></tr>
            </tbody>
          </table>
        </div>'''

S['s2'] = f'''
        <div class="part" role="separator"><span><b>1</b>Типы и структуры</span></div>
        <h2 id="s2"><span class="sec">§2</span>Шаг 1. Измерить типы</h2>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>Размер одежды «L» у разных производителей разный: у одного это 50-й российский размер, у другого 52-й. Если заказывать вещь по букве, можно ошибиться. Сантиметры у всех одинаковые, поэтому точный заказ делают по обхвату в сантиметрах.</p>
          <p class="miss">Одежду можно примерить и вернуть. Программа с неверным размером типа собирается без ошибок и при запуске читает чужие байты.</p>
        </div></div>
        <p>Каждая переменная в C занимает в памяти определённое число байт, и это число задаёт её <span class="term">тип</span>. Стандарт языка C задаёт для части типов только нижнюю границу: <code>int</code> — не меньше 2 байт, <code>long</code> — не меньше 4. Точный размер выбирают создатели компилятора и системы. Структуру, заполненную системой, читают байт за байтом. Поэтому размер каждого поля в программе должен совпадать с тем, что записала система.</p>
        <p>Размер типа в байтах возвращает оператор <code>sizeof</code>. Создаём в VS Code папку <code>pair02</code>, в ней файл <code>sizes.c</code> и вставляем код:</p>
{code('sizes.c')}
        <p>Формат <code>%zu</code> в <code>printf</code> печатает значение типа <code>size_t</code> — его возвращает <code>sizeof</code>. <span data-os="win">Кроме общих типов C, программа измеряет три типа Windows из <code>windows.h</code>. <code>DWORD</code> — число, которое возвращает <code>GetCurrentProcessId</code>. <code>WCHAR</code> — одна буква строки Windows. <code>HANDLE</code> — дескриптор объекта ядра из ЛР 1.</span><span data-os="mac linux">Тип <code>pid_t</code> из <code>sys/types.h</code> — тот, что возвращает <code>getpid</code>.</span> Собираем и запускаем:</p>
{cmd('cl /nologo /W4 sizes.c && sizes.exe', 'clang -Wall -Wextra -o sizes sizes.c && ./sizes', 'gcc -Wall -Wextra -o sizes sizes.c && ./sizes')}
        <p>Ключи <span data-os="win"><code>/W4</code></span><span data-os="mac linux"><code>-Wall -Wextra</code></span> включают предупреждения компилятора. Они понадобятся в шаге 8; включать их стоит с первой программы.</p>
{shot('01-sizes', dict(
    win=f'Сборка и запуск <code>sizes.exe</code> в командной строке MSVC. {M(1)} <code>long</code> — 4 байта, {M(2)} адрес — 8 байт, {M(3)} <code>int64_t</code> — 8 байт, {M(4)} <code>WCHAR</code> — 2 байта.',
    mac=f'VS Code: слева файл <code>sizes.c</code>, внизу терминал. {M(1)} <code>long</code> — 8 байт, {M(2)} адрес — 8 байт, {M(3)} <code>int64_t</code> — 8 байт.',
    linux=f'VS Code: слева файл <code>sizes.c</code>, внизу терминал с gcc. {M(1)} <code>long</code> — 8 байт, {M(2)} адрес — 8 байт, {M(3)} <code>int64_t</code> — 8 байт.'),
    dict(win='Командная строка MSVC: вывод sizes.exe, long 4, void * 8, int64_t 8, DWORD 4, WCHAR 2, HANDLE 8',
         mac='VS Code с файлом sizes.c и терминалом: char 1, int 4, long 8, void * 8, int64_t 8, pid_t 4',
         linux='VS Code с файлом sizes.c и терминалом gcc: char 1, int 4, long 8, void * 8, int64_t 8, pid_t 4'))}
{per(win=f'<p>Первая строка после команды — <code>sizes.c</code>: так компилятор MSVC сообщает, какой файл он собрал. Ниже — вывод программы. Строка {M(1)} отличается от macOS и Linux: в 64-битной Windows <code>long</code> занимает 4 байта. Адрес {M(2)} занимает 8 байт: программа собрана для x64, а у 64-битного процессора адрес — 64 бита. Буква строки Windows {M(4)} занимает 2 байта.</p>',
     maclinux=f'<p>Программа вывела шесть строк, по одной на тип. Строка {M(1)} отличается от Windows: в 64-битных macOS и Linux <code>long</code> занимает 8 байт, в 64-битной Windows — 4. Адрес {M(2)} занимает 8 байт: у 64-битного процессора адрес — 64 бита. Тип {M(3)} одинаков на всех системах.</p>')}
        <p>Ниже — те же числа для трёх систем рядом. Расхождение одно, в строке <code>long</code>.</p>
{SIZES_TABLE}
        <p>Расхождение в <code>long</code> записано в соглашениях о моделях данных. Windows использует модель <span class="term">LLP64</span>: в 8 байт расширены только <code>long long</code> и указатель. macOS и Linux используют модель <span class="term">LP64</span>: в 8 байт расширены <code>long</code> и указатель. Поэтому в структурах, которые передаются между системами или языками, пишут типы точного размера из <code>stdint.h</code>: <code>int32_t</code> — ровно 4 байта, <code>int64_t</code> — ровно 8. Так в ядре агента и будет сделано.</p>
        <p class="step-done"><b>Что получилось.</b>Размер типа виден оператором <code>sizeof</code>. Типы <code>char</code>, <code>int</code>, адрес и <code>int64_t</code> на трёх системах совпадают, <code>long</code> — нет. Дальше — структура, которую заполняет система.</p>
'''

# ─────────────────────────────── Шаг 2 ───────────────────────────────
S['s3'] = f'''
        <h2 id="s3"><span class="sec">§3</span>Шаг 2. Получить структуру от системы</h2>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>В МФЦ посетитель берёт пустой бланк, кладёт его в лоток окошка, и сотрудник вписывает в поля данные из базы. Посетитель не говорит сотруднику, что писать, — он только даёт бланк нужной формы. Возвращается тот же лист, но уже заполненный.</p>
          <p class="miss">Бланк из лотка забирают и потом возвращают. В C функция получает только адрес бланка и пишет прямо в память вызывающей программы, копия не создаётся.</p>
        </div></div>
        <p><span class="term">Структура</span> (<code>struct</code>) — несколько переменных разных типов под одним именем, которые лежат в памяти подряд. Каждая переменная внутри структуры называется <span class="term">полем</span>, к полю обращаются через точку: <code>u.sysname</code>. Системные функции, которые возвращают больше одного числа, обычно заполняют структуру.</p>
        <p>Через <code>return</code> функция возвращает одно значение, и системные функции отдают так код успеха или ошибки. Поэтому сведения передаются иначе: вызывающая программа сама объявляет пустую структуру и передаёт функции её адрес. <span class="term">Указатель</span> — переменная, в которой хранится адрес в памяти. Оператор <code>&amp;</code> берёт адрес переменной, а запись <code>struct utsname *</code> в объявлении функции означает «адрес структуры <code>utsname</code>». Функция пишет поля по этому адресу, и после возврата они видны в переменной вызывающей программы.</p>
{per(win='<p>В Windows так устроена функция <code>GetNativeSystemInfo</code>: она заполняет структуру <code>SYSTEM_INFO</code> — число процессоров, размер страницы памяти, архитектуру процессора. Файл <code>sysname.c</code>:</p>',
     maclinux='<p>В POSIX так устроена функция <code>uname</code>: она заполняет структуру <code>struct utsname</code> — имя системы, версию ядра, тип процессора и имя компьютера. Файл <code>sysname.c</code>:</p>')}
{code('sysname.c')}
{per(win='<p>Объявление <code>SYSTEM_INFO si;</code> выделяет память под структуру, но поля в ней пока не заданы. Вызов <code>GetNativeSystemInfo(&amp;si)</code> передаёт адрес <code>si</code>, и функция заполняет поля. Функция ничего не возвращает: получить сведения о процессоре она может всегда.</p>',
     maclinux='<p>Объявление <code>struct utsname u;</code> выделяет память под структуру, но поля в ней пока не заданы. Вызов <code>uname(&amp;u)</code> передаёт адрес <code>u</code>, и функция заполняет поля. При успехе она возвращает 0, при ошибке −1 — поэтому вызов стоит внутри <code>if</code>, а функция <code>perror</code> печатает причину ошибки.</p>')}
{cmd('cl /nologo /W4 sysname.c && sysname.exe', 'clang -Wall -Wextra -o sysname sysname.c && ./sysname', 'gcc -Wall -Wextra -o sysname sysname.c && ./sysname')}
{shot('02-uname', dict(
    win=f'{M(1)} Поля <code>SYSTEM_INFO</code> после вызова: 4 процессора, страница 4096 байт, архитектура 9. {M(2)} Вся структура занимает 48 байт.',
    mac=f'{M(1)} Объявление структуры. {M(2)} Вызов <code>uname</code> с адресом <code>&amp;u</code>. {M(3)} Поля после вызова: <code>Darwin</code>, версия ядра 25.1.0, процессор <code>arm64</code>, имя компьютера. {M(4)} Структура занимает 1280 байт.',
    linux=f'{M(1)} Объявление структуры. {M(2)} Вызов <code>uname</code> с адресом <code>&amp;u</code>. {M(3)} Поля после вызова: <code>Linux</code>, версия ядра, процессор <code>aarch64</code>, имя <code>lab-linux</code>. {M(4)} Структура занимает 390 байт.'),
    dict(win='Командная строка MSVC: processors 4, page size 4096, architecture 9, sizeof 48',
         mac='VS Code с файлом sysname.c: строки struct utsname u и uname(&u) в рамках, вывод Darwin 25.1.0 arm64, sizeof 1280',
         linux='VS Code с файлом sysname.c: строки struct utsname u и uname(&u) в рамках, вывод Linux aarch64 lab-linux, sizeof 390'))}
{per(win=f'<p>Поле <code>dwPageSize</code> {M(1)} — размер <span class="term">страницы памяти</span>: участков, которыми система выделяет память процессам. Архитектура 9 — значение <code>PROCESSOR_ARCHITECTURE_AMD64</code>, то есть x64. Кадры сняты на компьютере с процессором ARM, а программа собрана для x64. Она выполняется через эмулятор, как в ЛР 1, и функция сообщает ей архитектуру x64. Программа, собранная для ARM64, получила бы 12. На компьютере с Intel или AMD будет 9.</p>',
     mac=f'<p>Поля {M(3)} — строки: имя ядра, его версия, тип процессора и имя компьютера в сети. Размер {M(4)} показывает, как система хранит строки в этой структуре: пять полей по 256 байт. Длина каждой строки меньше 256, остаток поля не используется.</p>',
     linux=f'<p>Поля {M(3)} — строки: имя ядра, его версия, тип процессора и имя компьютера в сети. Размер {M(4)} — 390 байт: в Linux шесть полей по 65 байт, шестое — имя домена. У той же структуры в macOS другой размер, поэтому код, который копирует её байты, на другой системе прочитает не те поля.</p>')}
        <figure class="scheme">
          <p class="scheme__head">Вызов по адресу</p>
          <div class="scheme__body">
            <svg viewBox="0 0 720 170" role="img" aria-label="Схема: в памяти main лежит структура; её адрес передаётся системной функции; функция записывает поля в ту же память">
              <text x="20" y="22" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">память программы, функция main</text>
              <rect x="20" y="34" width="330" height="56" fill="var(--acc-pale)" stroke="var(--ink)" stroke-width="3"/>
              <text x="34" y="58" font-family="Roboto Mono, monospace" font-size="13" font-weight="700" fill="var(--ink)" data-os="mac linux">struct utsname u</text>
              <text x="34" y="58" font-family="Roboto Mono, monospace" font-size="13" font-weight="700" fill="var(--ink)" data-os="win">SYSTEM_INFO si</text>
              <text x="34" y="78" font-family="Inter, sans-serif" font-size="12" fill="var(--ink-soft)">после объявления поля не заданы</text>
              <path d="M350 62 H470" stroke="var(--ink)" stroke-width="3" fill="none"/><path d="M462 55 L472 62 L462 69" stroke="var(--ink)" stroke-width="3" fill="none"/>
              <text x="410" y="52" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="12" fill="var(--ink-soft)" data-os="mac linux">&amp;u</text>
              <text x="410" y="52" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="12" fill="var(--ink-soft)" data-os="win">&amp;si</text>
              <rect x="474" y="34" width="226" height="56" fill="var(--ng-pale)" stroke="var(--ink)" stroke-width="3"/>
              <text x="587" y="58" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="13" font-weight="700" fill="var(--ink)" data-os="mac linux">uname</text>
              <text x="587" y="58" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="13" font-weight="700" fill="var(--ink)" data-os="win">GetNativeSystemInfo</text>
              <text x="587" y="78" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" fill="var(--ink-soft)">системная функция</text>
              <path d="M587 92 V130 H185 V94" stroke="var(--acc)" stroke-width="3" fill="none" stroke-dasharray="7 5"/><path d="M178 102 L185 92 L192 102" stroke="var(--acc)" stroke-width="3" fill="none"/>
              <text x="386" y="152" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" fill="var(--acc)">записывает поля по полученному адресу — в ту же память</text>
            </svg>
          </div>
          <p class="scheme__note">Функция получает только адрес. Память под структуру выделила вызывающая программа, и ответ остаётся у неё.</p>
        </figure>
        <p class="step-done"><b>Что получилось.</b>Структура объявляется в вызывающей программе, системная функция получает её адрес и заполняет поля. Размер одной и той же структуры на разных системах разный. Часть полей — строки, и о них следующий шаг.</p>
'''

# ─────────────────────────────── Шаг 3 ───────────────────────────────
S['s4'] = f'''
        <div class="part" role="separator"><span><b>2</b>Строки и ошибки</span></div>
        <h2 id="s4"><span class="sec">§4</span>Шаг 3. Прочитать строку из буфера</h2>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>Ряд ячеек камеры хранения пронумерован подряд. В каждой ячейке одна буква. Где кончается слово, по ряду не видно, поэтому после последней буквы кладут пустую карточку с нулём. Кто читает слово, идёт по ячейкам, пока не встретит ноль.</p>
          <p class="miss">Ряд камеры хранения заканчивается стеной. Ряд байтов в памяти продолжается дальше, и если нуля нет, чтение идёт в чужие данные.</p>
        </div></div>
        <p><span class="term">Строка в C</span> — последовательность байтов, после которой стоит байт со значением 0. Его записывают как <code>'\\0'</code> и называют <span class="term">завершающим нулём</span>. Длину строка не хранит: функция <code>strlen</code> считает байты до нуля, <code>printf</code> с форматом <code>%s</code> печатает до нуля. Память под строку — <span class="term">буфер</span> — выделяет вызывающая программа, например массивом <code>char host[256]</code>, и передаёт функции его адрес и размер.</p>
{per(win='<p>В Windows у строк два вида. Функции с окончанием <code>A</code> работают с однобайтовой кодировкой, функции с окончанием <code>W</code> — с UTF-16, где буква занимает 2 байта (тип <code>WCHAR</code>). Внутри Windows строки хранятся в UTF-16, поэтому в курсе используются функции <code>W</code>. Ядро агента отдаёт строки в UTF-8, как macOS и Linux, и переводит их функцией <code>WideCharToMultiByte</code>.</p><p>Программа <code>hostbuf.c</code> получает имя компьютера функцией <code>GetComputerNameW</code>, печатает байты строки в UTF-16 и в UTF-8, а затем просит имя в буфер на 4 буквы:</p>',
     maclinux='<p>Программа <code>hostbuf.c</code> получает имя компьютера функцией <code>gethostname</code> в буфер на 256 байт и печатает байты строки в шестнадцатеричном виде функцией <code>dump</code>. Затем она просит то же имя в буфер на 4 байта <code>tiny</code>. Перед вызовом <code>memset</code> заполняет <code>tiny</code> буквами <code>X</code>, чтобы было видно, какие байты записала функция.</p>')}
{code('hostbuf.c')}
{cmd('cl /nologo /W4 hostbuf.c && hostbuf.exe', 'clang -Wall -Wextra -o hostbuf hostbuf.c && ./hostbuf', 'gcc -Wall -Wextra -o hostbuf hostbuf.c && ./hostbuf')}
        <div class="margin-note margin-note--warn" data-os="win">
          <b>Имя small в Windows занято</b>
          <p>Буфер в программе называется <code>tiny</code>. С именем <code>small</code> MSVC выдал ошибки C2628 и C2143. В заголовках, которые подключает <code>windows.h</code>, есть макрос <code>#define small char</code>, и компилятор видел строку <code>WCHAR char[4]</code>. Если компилятор сообщает о синтаксической ошибке в строке, где ошибки нет, причиной бывает макрос из заголовка.</p>
        </div>
{shot('03-hostbuf', dict(
    win=f'{M(1)} Имя <code>WIN11-LAB</code> в UTF-16: после каждой буквы байт <code>00</code>, в конце два нулевых байта. {M(2)} То же имя в UTF-8: 9 байт и <code>00</code>. {M(3)} Буфер на 4 буквы: ошибка 111, нужно 10.',
    mac=f'{M(1)} Буфер на 4 байта. {M(2)} Имя и его длина — 23. {M(3)} Байты имени, последний — <code>00</code>. {M(4)} Вызов с буфером <code>tiny</code> вернул 0. {M(5)} В буфере три буквы <code>Mac</code> и <code>00</code>.',
    linux=f'{M(1)} Буфер на 4 байта. {M(2)} Имя и его длина — 9. {M(3)} Байты имени, последний — <code>00</code>. {M(4)} Вызов с буфером <code>tiny</code> вернул −1, <code>errno</code> 36. {M(5)} В буфере четыре буквы <code>lab-</code>, нуля нет.'),
    dict(win='Командная строка MSVC: байты имени WIN11-LAB в UTF-16 и UTF-8, строка tiny: error 111, needed 10',
         mac='VS Code с hostbuf.c: байты имени MacBook-Air-Maxim.local, tiny rc=0 и байты 4d 61 63 00',
         linux='VS Code с hostbuf.c: байты имени lab-linux, tiny rc=-1 errno=36 File name too long и байты 6c 61 62 2d'))}
        <p>Первая часть вывода показывает, как строка лежит в памяти. На полосе ниже — те же байты по одному: сверху буква, снизу её код. Зелёная ячейка — завершающий ноль.</p>
        <div data-os="mac">{cells(HOST_MAC)}</div>
        <div data-os="linux">{cells(HOST_LIN)}</div>
        <div data-os="win">{cells(HOST_WIN)}</div>
{per(win=f'<p>В UTF-16 {M(1)} у латинской буквы второй байт нулевой (на полосе — пунктирные ячейки), а конец строки отмечен двумя нулевыми байтами — нулевой буквой <code>WCHAR</code>. Функция вернула длину 9 букв, без нуля. После перевода в UTF-8 {M(2)} буква занимает один байт, и строка выглядит так же, как в macOS и Linux.</p>',
     mac=f'<p>Длина {M(2)} — 23, а байтов {M(3)} — 24: последний байт <code>00</code> не входит в длину, но место в буфере занимает. Поэтому буфер всегда должен быть хотя бы на один байт больше самой длинной строки.</p>',
     linux=f'<p>Длина {M(2)} — 9, а байтов {M(3)} — 10: последний байт <code>00</code> не входит в длину, но место в буфере занимает. Поэтому буфер всегда должен быть хотя бы на один байт больше самой длинной строки.</p>')}
        <p>Вторая часть — буфер, в который имя не помещается. Здесь три системы ведут себя по-разному.</p>
        <div data-os="mac">{cells([('M', '4d', ''), ('a', '61', ''), ('c', '63', ''), ('\\0', '00', 'z')])}</div>
        <div data-os="linux">{cells([('l', '6c', ''), ('a', '61', ''), ('b', '62', ''), ('-', '2d', 'x')])}</div>
{per(win=f'<p>Функция <code>GetComputerNameW</code> {M(3)} вернула <code>FALSE</code>, код ошибки 111 и записала в переменную длины нужный размер — 10 букв: девять букв имени и ноль. Второй параметр функции — адрес переменной <code>tiny_len</code>: функция читает из неё размер буфера и пишет туда ответ. Программа может выделить буфер на 10 букв и вызвать функцию снова.</p>',
     mac=f'<p>macOS обрезала имя до трёх букв и поставила ноль {M(5)}, а функция вернула 0 {M(4)} — успех. Программа получила строку <code>Mac</code> и не узнала, что имя длиннее. Стандарт POSIX разрешает такое поведение: при обрезке функция может не сообщать об ошибке и не ставить ноль в конце.</p>',
     linux=f'<p>Linux вернул −1 и <code>errno</code> 36 {M(4)}, «File name too long». В буфер записаны четыре байта <code>lab-</code> {M(5)} и нуля нет (красная ячейка). Если программа не проверит код возврата и напечатает <code>tiny</code> как строку, <code>printf</code> прочитает байты за концом буфера и выведет их до первого нулевого байта в памяти.</p>')}
        <p>Из шага следуют два правила для ядра агента. Размер буфера передаётся функции вместе с адресом выражением <code>sizeof host</code>: если размер буфера изменят, вызов останется верным. Последний байт буфера после вызова принудительно делается нулём — так строка останется строкой, даже если система её обрезала.</p>
        <p class="step-done"><b>Что получилось.</b>Строка в C — байты до нуля, длина не хранится. Буфер выделяет вызывающая программа, функция получает его адрес и размер. При маленьком буфере результат зависит от системы, и узнать о проблеме можно только по коду возврата. Следующий шаг — как этот код читать.</p>
'''

# ─────────────────────────────── Шаг 4 ───────────────────────────────
S['s5'] = f'''
        <h2 id="s5"><span class="sec">§5</span>Шаг 4. Получить код ошибки</h2>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>На табло аэропорта у рейса стоит «Отменён». Причина — погода, техника или нехватка экипажа — записана в отдельной сводке у справочной. Табло отвечает только «да или нет», за причиной идут в сводку, и сделать это нужно сразу: следующая отмена её перепишет.</p>
          <p class="miss">Сводка в аэропорту хранит все отмены за день. Место для кода ошибки одно на поток программы, и следующий неудачный вызов записывает туда свой код.</p>
        </div></div>
        <p>Системные функции сообщают об ошибке в два этапа. Сначала возвращаемое значение показывает, что вызов не удался: <span data-os="win"><code>FALSE</code> или <code>INVALID_HANDLE_VALUE</code></span><span data-os="mac linux"><code>-1</code></span>. Затем номер причины берут из отдельного места: <span data-os="win">функция <code>GetLastError</code> возвращает <span class="term">код последней ошибки</span> текущего потока</span><span data-os="mac linux">переменная <code>errno</code> из <code>errno.h</code> хранит <span class="term">код последней ошибки</span> текущего потока</span>. Код читают сразу после неудачного вызова, потому что любой следующий системный вызов, даже <code>printf</code>, может его перезаписать.</p>
{per(win='<p>Программа <code>errors.c</code> открывает три файла функцией <code>CreateFileW</code>: обычный <code>win.ini</code>, несуществующий файл и <code>SAM</code> — базу учётных записей Windows, которую система держит закрытой. При неудаче программа сразу сохраняет <code>GetLastError()</code> в переменную <code>code</code>.</p>',
     mac='<p>Программа <code>errors.c</code> открывает три файла функцией <code>open</code>: <code>/etc/hosts</code>, который может читать любой пользователь, несуществующий файл и <code>/etc/sudoers</code> — настройки команды <code>sudo</code>, которые читает только администратор. При неудаче программа сразу сохраняет <code>errno</code> в переменную <code>code</code>, а функция <code>strerror</code> переводит код в текст.</p>',
     linux='<p>Программа <code>errors.c</code> открывает три файла функцией <code>open</code>: <code>/etc/hosts</code>, который может читать любой пользователь, несуществующий файл и <code>/etc/shadow</code> — хэши паролей, которые читает только администратор. При неудаче программа сразу сохраняет <code>errno</code> в переменную <code>code</code>, а функция <code>strerror</code> переводит код в текст.</p>')}
{code('errors.c', ('win', 'mac', 'linux'))}
{cmd('cl /nologo /W4 errors.c && errors.exe', 'clang -Wall -Wextra -o errors errors.c && ./errors', 'gcc -Wall -Wextra -o errors errors.c && ./errors')}
{shot('04-errors', dict(
    win=f'<code>win.ini</code> открыт, получен дескриптор. {M(1)} Несуществующий файл — ошибка 2. {M(2)} <code>SAM</code> — ошибка 5.',
    mac=f'{M(1)} Код сохраняется сразу после неудачного <code>open</code>. <code>/etc/hosts</code> открыт: дескриптор 3. {M(2)} Несуществующий файл — <code>errno</code> 2. {M(3)} <code>/etc/sudoers</code> — <code>errno</code> 13.',
    linux=f'{M(1)} Код сохраняется сразу после неудачного <code>open</code>. <code>/etc/hosts</code> открыт: дескриптор 3. {M(2)} Несуществующий файл — <code>errno</code> 2. {M(3)} <code>/etc/shadow</code> — <code>errno</code> 13.'),
    dict(win='Командная строка MSVC: win.ini handle 88, no-such-file.ini error 2, SAM error 5',
         mac='VS Code с errors.c: /etc/hosts fd=3, no-such-file errno=2 No such file or directory, /etc/sudoers errno=13 Permission denied',
         linux='VS Code с errors.c: /etc/hosts fd=3, no-such-file errno=2 No such file or directory, /etc/shadow errno=13 Permission denied'))}
{per(win=f'<p>Ошибка 2 {M(1)} — <code>ERROR_FILE_NOT_FOUND</code>, файла нет. Ошибка 5 {M(2)} — <code>ERROR_ACCESS_DENIED</code>, доступ запрещён. Текст ошибки по номеру печатает команда <code>net helpmsg</code>. Для кода 2 она выводит «Не удается найти указанный файл.», для 5 — «Отказано в доступе.». Для кода 111 из шага 3 текст — «Указано слишком длинное имя файла.». Из программы текст получают функцией <code>FormatMessageW</code>.</p>',
     maclinux=f'<p>Код 2 {M(2)} называется <code>ENOENT</code>, «No such file or directory». Код 13 {M(3)} — <code>EACCES</code>, «Permission denied»: файл есть, но читать его этому пользователю нельзя. Имена кодов объявлены в <code>errno.h</code>, и в коде сравнивают с ними: <code>if (code == ENOENT)</code>.</p>')}
        <p>Таблицы кодов у Windows и POSIX разные. Номер 2 у них совпал, а отказ в доступе — 5 в Windows и 13 в macOS и Linux. Поэтому код ошибки читают вместе с названием системы, на которой он получен.</p>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Причина</th><th>Windows, <code>GetLastError</code></th><th>macOS и Linux, <code>errno</code></th></tr></thead>
            <tbody>
              <tr><td>Файла нет</td><td><code>2</code> ERROR_FILE_NOT_FOUND</td><td><code>2</code> ENOENT</td></tr>
              <tr><td>Доступ запрещён</td><td><code>5</code> ERROR_ACCESS_DENIED</td><td><code>13</code> EACCES</td></tr>
              <tr><td>Буфер или имя слишком длинные</td><td><code>111</code> ERROR_BUFFER_OVERFLOW</td><td><code>36</code> ENAMETOOLONG в Linux, <code>63</code> в macOS</td></tr>
              <tr><td>Неверный параметр</td><td><code>87</code> ERROR_INVALID_PARAMETER</td><td><code>22</code> EINVAL</td></tr>
            </tbody>
          </table>
        </div>
        <p class="step-done"><b>Что получилось.</b>Неудачу показывает возвращаемое значение, причину — <span data-os="win"><code>GetLastError</code></span><span data-os="mac linux"><code>errno</code></span>, и её читают сразу после вызова. Теперь известно всё, что нужно для функции ядра: типы точного размера, структура по адресу, строка в буфере и код ошибки.</p>
'''

# ─────────────────────────────── Шаг 5 ───────────────────────────────
LAYOUT = cells([('pid', 'байты 0–7 · int64_t', 'w'), ('cpus', '8–11 · int32_t', 'w'), ('page_size', '12–15 · int32_t', 'w'), ('host', '16–271 · char[256]', 'w')])

S['s6'] = f'''
        <div class="part" role="separator"><span><b>3</b>Функция ядра</span></div>
        <h2 id="s6"><span class="sec">§6</span>Шаг 5. Описать свою структуру</h2>
        <p>Функции ядра понадобятся и программе на C, и мозгу агента на Python. Поэтому объявление структуры и функции выносится в отдельный <span class="term">заголовочный файл</span> <code>core.h</code>. Другие файлы подключают его строкой <code>#include "core.h"</code> — кавычки вместо угловых скобок означают, что файл ищется сначала в папке рядом с исходником. Строки <code>#ifndef CORE_H</code>, <code>#define CORE_H</code> и <code>#endif</code> не дают подключить файл дважды. Файл одинаков для трёх систем:</p>
{code('core.h', ('win mac linux',))}
        <p>Поля выбраны по шагам 1–4. Номер процесса и два числа объявлены типами точного размера, поэтому структура занимает одинаково байт на всех системах. Имя компьютера хранится в буфере на 256 байт: <code>CORE_HOST_MAX</code> задан через <code>#define</code>, и размер меняется в одном месте. Последняя строка — <span class="term">объявление функции</span>: её имя, тип результата и параметр — адрес структуры. Сама функция будет в следующем файле.</p>
        <p>Порядок полей подобран так, чтобы между ними не было пропусков. Компилятор выравнивает поля: 8-байтовое число он ставит на адрес, кратный 8. Два поля по 4 байта сразу после <code>pid</code> заполняют следующие 8 байт, и структура занимает 8 + 4 + 4 + 256 = 272 байта без пустых мест:</p>
        {LAYOUT}
        <p style="margin-top:14px">Под полосой — <span class="term">смещение</span> каждого поля: номер его первого байта от начала структуры. Программа на другом языке находит поле по смещению, поэтому раскладка не должна зависеть от системы.</p>
{shot('05-core-h', dict(
    mac=f'Файл <code>core.h</code> в VS Code. {M(1)} Структура <code>core_info</code> из четырёх полей. {M(2)} Объявление функции ядра.',
    linux=f'Файл <code>core.h</code> в VS Code. {M(1)} Структура <code>core_info</code> из четырёх полей. {M(2)} Объявление функции ядра.'),
    dict(mac='VS Code с файлом core.h: структура core_info и объявление core_get_info в рамках',
         linux='VS Code с файлом core.h: структура core_info и объявление core_get_info в рамках'), oss=('mac', 'linux'))}
        <p class="step-done"><b>Что получилось.</b>В <code>core.h</code> описано, что функция ядра отдаёт и как её вызвать. Структура занимает 272 байта на всех системах. Дальше — сама функция.</p>
'''

# ─────────────────────────────── Шаг 6 ───────────────────────────────
S['s7'] = f'''
        <h2 id="s7"><span class="sec">§7</span>Шаг 6. Написать функцию ядра</h2>
        <p>Функция <code>core_get_info</code> собирает приёмы шагов 1–4. Она получает адрес структуры, вызывает системные функции и записывает их ответы в поля. Результат функции — код ошибки: 0, если всё получилось, иначе код системы. Файл <code>core_info.c</code>:</p>
{code('core_info.c')}
        <p>Разбор по строкам.</p>
        <ul>
          <li><code>if (out == NULL)</code> — проверка адреса. <code>NULL</code> — нулевой указатель, «адреса нет». Если вызвать функцию с ним и писать в <code>out-&gt;pid</code>, программа упадёт. Функция возвращает код <span data-os="win"><code>ERROR_INVALID_PARAMETER</code> (87)</span><span data-os="mac linux"><code>EINVAL</code> (22)</span> — «неверный параметр».</li>
          <li><code><span data-os="win">ZeroMemory</span><span data-os="mac linux">memset</span>(out, 0, sizeof *out)</code> — заполняет все 272 байта структуры нулями. После объявления в полях лежит то, что раньше было в этой памяти. Без обнуления при ошибке в поле <code>host</code> остался бы мусор. <code>sizeof *out</code> — размер того, на что указывает <code>out</code>, то есть всей структуры.</li>
          <li><code>out-&gt;pid</code> — запись в поле структуры по адресу. Стрелка <code>-&gt;</code> используется, когда есть указатель на структуру: <code>out-&gt;pid</code> значит то же, что <code>(*out).pid</code>. Точка — когда есть сама структура, как <code>u.sysname</code> в шаге 2.</li>
          <li data-os="mac linux"><code>sysconf(_SC_NPROCESSORS_ONLN)</code> и <code>sysconf(_SC_PAGESIZE)</code> — функция POSIX, которая возвращает настройки системы по имени: число работающих процессоров и размер страницы. Она возвращает <code>long</code>, поэтому результат явно приводится к <code>int32_t</code>: запись <code>(int32_t)</code> перед значением показывает, что сужение типа сделано намеренно.</li>
          <li data-os="win"><code>GetNativeSystemInfo(&amp;si)</code> — структура из шага 2; из неё берутся два поля, <code>dwNumberOfProcessors</code> и <code>dwPageSize</code>. Они типа <code>DWORD</code>, поэтому при записи в поле <code>int32_t</code> стоит явное приведение <code>(int32_t)</code>.</li>
          <li data-os="mac linux"><code>gethostname(out-&gt;host, sizeof out-&gt;host)</code> — имя в буфер структуры вместе с его размером. При ошибке функция сразу возвращает <code>errno</code>. Следующая строка ставит ноль в последний байт буфера — правило из шага 3 на случай, если система обрезала имя без нуля.</li>
          <li data-os="win"><code>GetComputerNameW(name, &amp;len)</code> — имя в UTF-16 во временный буфер <code>name</code>; при ошибке функция возвращает <code>GetLastError()</code>. Затем <code>WideCharToMultiByte(CP_UTF8, …)</code> переводит имя в UTF-8 прямо в <code>out-&gt;host</code>. Параметр <code>-1</code> означает «длина — до нуля», и ноль тоже копируется.</li>
        </ul>
        <p>В функции нет <code>printf</code>. Ядро агента ничего не печатает, оно возвращает данные и код. Что с ними делать, определяет вызывающая программа: в этой главе — проверочная программа на C, в агенте — мозг на Python.</p>
{shot('06-core-info', dict(
    mac=f'Файл <code>core_info.c</code>. {M(1)} Заголовок функции: параметр — адрес структуры. {M(2)} Запись трёх числовых полей через <code>-&gt;</code>. {M(3)} Возврат кода ошибки системы.',
    linux=f'Файл <code>core_info.c</code>. {M(1)} Заголовок функции: параметр — адрес структуры. {M(2)} Запись трёх числовых полей через <code>-&gt;</code>. {M(3)} Возврат кода ошибки системы.'),
    dict(mac='VS Code с файлом core_info.c: заголовок core_get_info, строки out->pid, out->cpus, out->page_size и return errno в рамках',
         linux='VS Code с файлом core_info.c: заголовок core_get_info, строки out->pid, out->cpus, out->page_size и return errno в рамках'), oss=('mac', 'linux'))}
        <p class="step-done"><b>Что получилось.</b>Функция ядра готова: адрес на входе, поля по адресу, код ошибки на выходе. Её нужно проверить отдельной программой.</p>
'''

# ─────────────────────────────── Шаг 7 ───────────────────────────────
S['s8'] = f'''
        <h2 id="s8"><span class="sec">§8</span>Шаг 7. Проверить функцию программой</h2>
        <p>Программа <code>show_info.c</code> вызывает функцию так же, как будет вызывать мозг агента: объявляет структуру, передаёт её адрес, проверяет код и печатает поля. Для полей точного размера используются макросы формата из <code>inttypes.h</code>: <code>PRId64</code> — формат для <code>int64_t</code>, <code>PRId32</code> — для <code>int32_t</code>. На каждой системе они раскрываются в свой формат, например <code>"lld"</code> или <code>"ld"</code>.</p>
{code('show_info.c', ('win mac linux',))}
        <p>Программа собирается из двух файлов: компилятор собирает каждый, а компоновщик соединяет вызов <code>core_get_info</code> в <code>show_info.c</code> с самой функцией из <code>core_info.c</code>.</p>
{cmd('cl /nologo /W4 show_info.c core_info.c && show_info.exe', 'clang -Wall -Wextra -o show_info show_info.c core_info.c && ./show_info', 'gcc -Wall -Wextra -o show_info show_info.c core_info.c && ./show_info')}
{shot('07-info', dict(
    win=f'MSVC собрал оба файла (строки <code>show_info.c</code>, <code>core_info.c</code>, «Создание кода…»). {M(1)} Поля: PID 2820, 4 процессора, страница 4096, имя <code>WIN11-LAB</code>. {M(2)} Структура — 272 байта.',
    mac=f'{M(1)} Вызов с адресом структуры. {M(2)} Поля: PID 34535, 10 процессоров, страница 16384, имя компьютера. {M(3)} Структура — 272 байта.',
    linux=f'{M(1)} Вызов с адресом структуры. {M(2)} Поля: PID 45, 10 процессоров, страница 4096, имя <code>lab-linux</code>. {M(3)} Структура — 272 байта.'),
    dict(win='Командная строка MSVC: show_info.exe печатает pid 2820, cpus 4, page_size 4096, host WIN11-LAB, sizeof 272',
         mac='VS Code с show_info.c: вызов core_get_info(&info), вывод pid 34535, cpus 10, page_size 16384, host MacBook-Air-Maxim.local, sizeof 272',
         linux='VS Code с show_info.c: вызов core_get_info(&info), вывод pid 45, cpus 10, page_size 4096, host lab-linux, sizeof 272'))}
{per(win=f'<p>Номер процесса проверяется так же, как в ЛР 1: число совпадает с тем, что показал бы Диспетчер задач, пока программа работает. Размер {M(2)} — 272, как посчитано в шаге 5. Последняя строка — адрес структуры в памяти процесса: 16 шестнадцатеричных цифр, 8 байт.</p>',
     mac=f'<p>Размер {M(3)} — 272, как посчитано в шаге 5. Страница памяти на Mac с процессором Apple — 16384 байта, в четыре раза больше, чем в Windows и Linux на тех же процессорах ARM. Последняя строка — адрес структуры в памяти процесса; он меняется при каждом запуске.</p>',
     linux=f'<p>Размер {M(3)} — 272, как посчитано в шаге 5. Номер процесса маленький — 45: кадр снят в контейнере, где у процессов своя нумерация. На обычном компьютере с Ubuntu номер будет в тысячах, как в ЛР 1. Последняя строка — адрес структуры в памяти процесса; он меняется при каждом запуске.</p>')}
        <p class="step-done"><b>Что получилось.</b>Функция ядра работает на своей системе и отдаёт 272 байта одинаковой раскладки. Осталось проверить, что компилятор найдёт ошибку формата, если она появится.</p>
'''

# ─────────────────────────────── Шаг 8 ───────────────────────────────
S['s9'] = f'''
        <div class="part" role="separator"><span><b>4</b>Проверка и сдача</span></div>
        <h2 id="s9"><span class="sec">§9</span>Шаг 8. Найти ошибку по предупреждению</h2>
        <p>Ошибка формата в <code>printf</code> — частая ошибка при переносе кода между системами. Заменим в <code>show_info.c</code> формат номера процесса на <code>%d</code>, как пишут для обычного <code>int</code>:</p>
        <div class="code-pair">
          <figure class="code code--was" data-read>
            <figcaption><span>show_info.c, строка 13</span><span>было</span></figcaption>
<pre>    <span class="f">printf</span>(<span class="s">"pid       %"</span> PRId64 <span class="s">"\\n"</span>, info.pid);</pre>
          </figure>
          <figure class="code code--now" data-read>
            <figcaption><span>show_info.c, строка 13</span><span>стало</span></figcaption>
<pre><mark>    <span class="f">printf</span>(<span class="s">"pid       %d\\n"</span>, info.pid);</mark></pre>
          </figure>
        </div>
        <p>Собираем снова, без запуска:</p>
{cmd('cl /nologo /W4 show_info.c core_info.c', 'clang -Wall -Wextra -o show_info show_info.c core_info.c', 'gcc -Wall -Wextra -o show_info show_info.c core_info.c')}
{shot('08-warning', dict(
    win=f'{M(1)} Предупреждение C4477 для строки 13: формат <code>%d</code> требует <code>int</code>, а аргумент имеет тип <code>int64_t</code>. {M(2)} Первая из трёх подсказок: использовать <code>%lld</code>.',
    mac=f'{M(1)} Изменённая строка 13. {M(2)} Предупреждение clang: формат требует <code>int</code>, аргумент — <code>int64_t</code> (<code>long long</code>). {M(3)} Итог: одно предупреждение, программа собрана.',
    linux=f'{M(1)} Изменённая строка 13. {M(2)} Предупреждение gcc: формат <code>%d</code> рассчитан на <code>int</code>, аргумент — <code>int64_t</code> (<code>long int</code>). {M(3)} gcc показывает строку и отмечает в ней формат и аргумент.'),
    dict(win='Командная строка MSVC: warning C4477 для show_info.c строка 13 и подсказки %lld, %Id, %I64d',
         mac='VS Code: в show_info.c строка 13 с %d, в терминале warning format specifies type int but the argument has type int64_t, 1 warning generated',
         linux='VS Code: в show_info.c строка 13 с %d, в терминале warning format %d expects argument of type int, but argument 2 has type int64_t'))}
{per(win=f'<p>Сообщение {M(1)} начинается с места ошибки: файл, номер строки в скобках. Ниже {M(2)} компилятор предлагает форматы, подходящие для 8-байтового числа. Программа собрана: предупреждение не останавливает сборку.</p>',
     mac=f'<p>Сообщение {M(2)} начинается с места ошибки: файл, строка 13, позиция 30. Под ним clang повторяет строку, подчёркивает формат и аргумент и предлагает замену <code>%lld</code>. Программа собрана {M(3)}: предупреждение не останавливает сборку.</p>',
     linux=f'<p>Сообщение {M(2)} начинается с места ошибки: файл, строка 13, позиция 24. В квадратных скобках — имя проверки <code>-Wformat=</code>, её включил ключ <code>-Wall</code>. Ниже {M(3)} gcc повторяет строку и предлагает <code>%ld</code>. Программа собрана: предупреждение не останавливает сборку.</p>')}
        <p>Стандарт C называет несовпадение формата и типа аргумента неопределённым поведением. Что напечатает такая строка, зависит от компилятора и от того, как система передаёт параметры в функцию. На одной системе номер выйдет верным, на другой — другое число или сдвиг следующих аргументов. Поэтому предупреждения компилятора читают как ошибки. Возвращаем строку с <code>PRId64</code>, собираем снова — предупреждений нет.</p>
        <p class="step-done"><b>Что получилось.</b>Ключи <span data-os="win"><code>/W4</code></span><span data-os="mac linux"><code>-Wall -Wextra</code></span> находят несовпадение формата и типа. Код ядра собран без предупреждений и готов к переносу в репозиторий.</p>
'''

# ─────────────────────────────── Шаг 9 ───────────────────────────────
S['s10'] = f'''
        <h2 id="s10"><span class="sec">§10</span>Шаг 9. Положить ядро в репозиторий</h2>
        <p>Файлы ядра переносятся в репозиторий <code>sysprog-start</code>, в папку <code>agent/core</code>. Демонстрационные программы шагов 1–4 остаются в <code>pair02</code>: они не входят в агента.</p>
        <div class="filetree">
          <p class="filetree__head">sysprog-start после шага</p>
          <div class="dim"><span>agent/</span><span></span></div>
          <div class="hot"><span>&nbsp;&nbsp;core/core.h</span><span>структура и объявление функции, шаг 5</span></div>
          <div class="hot"><span>&nbsp;&nbsp;core/core_info.c</span><span>функция <code>core_get_info</code>, шаг 6</span></div>
          <div class="hot"><span>&nbsp;&nbsp;core/show_info.c</span><span>программа проверки, шаг 7</span></div>
          <div class="dim"><span>&nbsp;&nbsp;core/README.md</span><span>в таблицу дописываются три файла</span></div>
          <div class="dim"><span>&nbsp;&nbsp;brain/</span><span>мозг на Python, с главы 1.2</span></div>
        </div>
        <p>Копируем три файла в копию репозитория в Документах, открываем её в VS Code и дописываем в таблицу <code>agent/core/README.md</code> по строке на файл. Сборка из папки репозитория проверяет, что все файлы на месте:</p>
{cmd('cd /d %USERPROFILE%\\Documents\\sysprog-start\\agent\\core\ncl /nologo /W4 show_info.c core_info.c && show_info.exe', 'cd ~/Documents/sysprog-start/agent/core\nclang -Wall -Wextra -o show_info show_info.c core_info.c && ./show_info', 'cd ~/Documents/sysprog-start/agent/core\ngcc -Wall -Wextra -o show_info show_info.c core_info.c && ./show_info')}
        <p>Собранная программа в репозиторий не кладётся: <span data-os="win"><code>show_info.exe</code> и <code>.obj</code></span><span data-os="mac linux">файл <code>show_info</code></span> создаётся заново из исходников на любой системе. В панели Source Control отбираем плюсом четыре файла — три исходника и <code>README.md</code> — и делаем коммит, как в справочнике по Git:</p>
        <figure class="code">
          <figcaption><span>терминал в папке sysprog-start</span><span>то же, что плюс, Commit и Sync Changes</span></figcaption>
<pre>git add agent/core/core.h agent/core/core_info.c agent/core/show_info.c agent/core/README.md
git commit -m "core: core_get_info — сведения о системе"
git push</pre>
        </figure>
        <p class="step-done"><b>Что получилось.</b>В репозитории первая функция ядра агента. Код написан вручную; последняя часть пары — сверить с ним объяснение помощника ИИ.</p>

        <h2 id="s11"><span class="sec">§11</span>Запрос к помощнику ИИ</h2>
        <p>В режиме Р1 из главы 0.3 помощник генерирует объяснение, а код пишется вручную. Запрос к помощнику в VS Code:</p>
        <figure class="code">
          <figcaption><span>запрос помощнику</span></figcaption>
<pre>Объясни, почему в структуре core_info поля объявлены как int64_t и int32_t,
а не long и int. Структура читается из Python через ctypes на Windows, macOS и Linux.</pre>
        </figure>
        <p>Ответ сверяется с шагами 1 и 5 по списку:</p>
        <ul class="checklist">
          <li>названо, что <code>long</code> в 64-битной Windows занимает 4 байта, а в macOS и Linux — 8 (модели LLP64 и LP64);</li>
          <li>сказано, что Python должен знать точный размер и смещение каждого поля;</li>
          <li>нет утверждения, что <code>int</code> на этих системах бывает 8 байт: на кадре шага 1 он 4 байта на всех трёх;</li>
          <li>если в ответе есть код на Python, типы в нём точного размера: <code>c_int64</code>, <code>c_int32</code>.</li>
        </ul>
        <p>Если ответ расходится с кадром шага 1, проверка — запуск <code>sizes</code> на своей системе: вывод программы показывает настоящие размеры.</p>
'''

# ─────────────────────────────── Справка и конец ───────────────────────────────
S['end'] = f'''
        <div class="part" role="separator"><span><b>5</b>Справка</span></div>
        <h2 id="s12"><span class="sec">§12</span>Справка: функции и команды главы</h2>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Что нужно</th><th>Windows</th><th>macOS и Linux</th></tr></thead>
            <tbody>
              <tr><td>Номер своего процесса</td><td><code>GetCurrentProcessId()</code></td><td><code>getpid()</code></td></tr>
              <tr><td>Число процессоров, размер страницы</td><td><code>GetNativeSystemInfo(&amp;si)</code></td><td><code>sysconf(_SC_NPROCESSORS_ONLN)</code>, <code>sysconf(_SC_PAGESIZE)</code></td></tr>
              <tr><td>Имя и версия системы</td><td><code>RtlGetVersion</code></td><td><code>uname(&amp;u)</code></td></tr>
              <tr><td>Имя компьютера</td><td><code>GetComputerNameW(buf, &amp;len)</code></td><td><code>gethostname(buf, size)</code></td></tr>
              <tr><td>Строку UTF-16 в UTF-8</td><td><code>WideCharToMultiByte(CP_UTF8, …)</code></td><td>не нужно: строки уже в UTF-8</td></tr>
              <tr><td>Код последней ошибки</td><td><code>GetLastError()</code></td><td><code>errno</code></td></tr>
              <tr><td>Текст ошибки</td><td><code>FormatMessageW</code>, в командной строке <code>net helpmsg код</code></td><td><code>strerror(code)</code>, <code>perror("…")</code></td></tr>
              <tr><td>Обнулить память</td><td><code>ZeroMemory(p, n)</code></td><td><code>memset(p, 0, n)</code></td></tr>
              <tr><td>Собрать с предупреждениями</td><td><code>cl /nologo /W4 a.c b.c</code></td><td><code>clang</code> или <code>gcc -Wall -Wextra -o prog a.c b.c</code></td></tr>
            </tbody>
          </table>
        </div>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Запись в C</th><th>Что значит</th><th>Пример из главы</th></tr></thead>
            <tbody>
              <tr><td><code>sizeof x</code></td><td>размер в байтах</td><td><code>sizeof info</code> — 272</td></tr>
              <tr><td><code>&amp;x</code></td><td>адрес переменной</td><td><code>core_get_info(&amp;info)</code></td></tr>
              <tr><td><code>T *p</code></td><td>указатель — переменная с адресом значения типа T</td><td><code>struct core_info *out</code></td></tr>
              <tr><td><code>s.f</code> и <code>p-&gt;f</code></td><td>поле структуры по имени и по адресу</td><td><code>u.sysname</code>, <code>out-&gt;pid</code></td></tr>
              <tr><td><code>char buf[N]</code></td><td>буфер на N байт, строка в нём — до байта 0</td><td><code>char host[256]</code></td></tr>
              <tr><td><code>NULL</code></td><td>нулевой указатель, адреса нет</td><td><code>if (out == NULL)</code></td></tr>
              <tr><td><code>(int32_t)x</code></td><td>явное приведение к типу</td><td><code>(int32_t)sysconf(…)</code></td></tr>
              <tr><td><code>PRId64</code></td><td>формат <code>printf</code> для <code>int64_t</code></td><td><code>"%" PRId64</code></td></tr>
            </tbody>
          </table>
        </div>

        <div class="part" role="separator"><span><b>6</b>Проверка себя</span></div>
        <h2 id="s13"><span class="sec">§13</span>Частые вопросы</h2>
        <div class="myths">
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b><code>long</code> всегда 8 байт на 64-битной системе.</div>
            <div class="myth__yes"><b>На самом деле</b>В 64-битной Windows <code>long</code> — 4 байта (кадр шага 1). Для полей, которые читают другие программы, пишут <code>int32_t</code> и <code>int64_t</code>.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Функция, которая заполняет структуру, возвращает её через <code>return</code>.</div>
            <div class="myth__yes"><b>На самом деле</b>Структуру объявляет вызывающая программа и передаёт адрес. Через <code>return</code> функция отдаёт код успеха или ошибки.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Если функция получила размер буфера, строка в нём всегда закончится нулём.</div>
            <div class="myth__yes"><b>На самом деле</b><code>gethostname</code> в Linux при маленьком буфере записала <code>lab-</code> без нуля. Последний байт буфера после вызова ставят в ноль вручную.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b><code>errno</code> можно прочитать в любой момент после ошибки.</div>
            <div class="myth__yes"><b>На самом деле</b>Следующий вызов может его перезаписать. Код сохраняют в переменную сразу после неудачного вызова, как в <code>errors.c</code>.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Предупреждение компилятора можно не читать: программа же собралась.</div>
            <div class="myth__yes"><b>На самом деле</b>Предупреждение формата в шаге 8 указывает на код, который на другой системе напечатает неверное число. Ядро агента собирается без предупреждений.</div>
          </div>
        </div>

        <h2 id="s14"><span class="sec">§14</span>Проверьте себя</h2>
        <details>
          <summary>Сколько байт занимает <code>long</code> в Windows, macOS и Linux и какой тип взять для поля, которое читает Python?</summary>
          <p>4 в 64-битной Windows, 8 в macOS и Linux. Для поля, которое читает другая программа, берут тип точного размера: <code>int32_t</code> или <code>int64_t</code>.</p>
        </details>
        <details>
          <summary>Зачем функции <code>uname</code> или <code>GetNativeSystemInfo</code> передают адрес структуры <code>&amp;u</code>?</summary>
          <p>Функция должна записать поля в структуру вызывающей программы. Для этого ей нужен адрес структуры. Без <code>&amp;</code> функция получила бы копию, и изменения пропали бы после возврата.</p>
        </details>
        <details>
          <summary>Строка <code>"lab-linux"</code> — сколько байт нужно под неё в буфере?</summary>
          <p>10: девять букв и завершающий ноль. <code>strlen</code> вернёт 9.</p>
        </details>
        <details>
          <summary>Функция открытия файла вернула ошибку. Что нужно сделать до вызова <code>printf</code>?</summary>
          <p>Сохранить <span data-os="win"><code>GetLastError()</code></span><span data-os="mac linux"><code>errno</code></span> в переменную: <code>printf</code> тоже обращается к системе и может перезаписать код.</p>
        </details>
        <details>
          <summary>Почему в <code>core_get_info</code> нет <code>printf</code>?</summary>
          <p>Ядро агента отдаёт данные и код ошибки тому, кто его вызвал. Печатает, записывает в журнал или отправляет в n8n мозг агента.</p>
        </details>
        <details>
          <summary>Почему структура <code>core_info</code> занимает ровно 272 байта и пропусков в ней нет?</summary>
          <p>8 + 4 + 4 + 256. Два поля по 4 байта стоят после 8-байтового <code>pid</code> и заполняют следующие 8 байт, поэтому буфер <code>host</code> начинается со смещения 16 без выравнивающих пропусков.</p>
        </details>

        <h2 id="s15"><span class="sec">§15</span>Шпаргалка по главе</h2>
        <div class="cheat">
          <div><b>Размеры</b><span><code>sizeof x</code></span><span><code>long</code>: 4 в Windows, 8 в macOS и Linux</span><span><code>int32_t</code>, <code>int64_t</code> — точно</span></div>
          <div><b>Структура по адресу</b><span><code>struct core_info info;</code></span><span><code>core_get_info(&amp;info);</code></span><span><code>out-&gt;pid = …</code></span></div>
          <div><b>Строка в буфере</b><span>байты до <code>'\\0'</code></span><span>размер буфера — длина + 1</span><span><code>buf[sizeof buf - 1] = '\\0';</code></span></div>
          <div><b>Ошибка</b><span>возврат показывает неудачу</span><span><span data-os="win"><code>GetLastError()</code></span><span data-os="mac linux"><code>errno</code></span> — причину</span><span>сохранить сразу</span></div>
          <div><b>Сборка</b><span data-os="win"><code>cl /nologo /W4 a.c b.c</code></span><span data-os="mac"><code>clang -Wall -Wextra -o p a.c b.c</code></span><span data-os="linux"><code>gcc -Wall -Wextra -o p a.c b.c</code></span><span>предупреждения читать как ошибки</span></div>
          <div><b>Функция ядра</b><span>0 — успех, иначе код системы</span><span>нет <code>printf</code></span><span><code>agent/core</code> в репозитории</span></div>
        </div>

        <h3>Итог главы</h3>
        <p>Системные функции принимают адреса и возвращают коды, поэтому для работы с ними нужны четыре вещи языка C. Размеры типов проверяются оператором <code>sizeof</code>. У <code>long</code> размер разный в Windows и в macOS и Linux, поэтому поля, которые читают другие программы, объявляются типами точного размера. Структуру объявляет вызывающая программа, а функция заполняет её по адресу. Строка — байты до нуля в буфере, размер которого передаётся вместе с адресом. При маленьком буфере три системы ведут себя по-разному, поэтому последний байт ставят в ноль вручную. Неудачу показывает возвращаемое значение, причину — <code>GetLastError</code> или <code>errno</code>, и её сохраняют сразу. Из этого собрана первая функция ядра агента <code>core_get_info</code>. Она заполняет структуру в 272 байта с одинаковой раскладкой на трёх системах, возвращает код ошибки и ничего не печатает.</p>

        <div class="sources">
          <b>Откуда взяты факты</b>
          <ol>
            <li>Кадры и выводы программ: macOS 26.1 на Apple M-серии, Apple clang 17.0.0, VS Code 1.138; Linux — терминал VS Code в контейнере Debian 13 с gcc 14.4, ядро 7.0 (Docker Desktop), имя машины <code>lab-linux</code>; Windows 11 24H2 ARM64 в VirtualBox, MSVC 19.44 (Build Tools 2022), сборка x64.</li>
            <li>Модели данных LLP64 и LP64 и размер <code>long</code> в Windows — <a href="https://learn.microsoft.com/cpp/cpp/data-type-ranges">Microsoft Learn, Data Type Ranges</a>.</li>
            <li><code>GetNativeSystemInfo</code>, <code>SYSTEM_INFO</code> и значения <code>wProcessorArchitecture</code> — <a href="https://learn.microsoft.com/windows/win32/api/sysinfoapi/nf-sysinfoapi-getnativesysteminfo">Microsoft Learn</a>; <code>GetComputerNameW</code> и <code>ERROR_BUFFER_OVERFLOW</code> — <a href="https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-getcomputernamew">Microsoft Learn</a>.</li>
            <li><code>gethostname</code>: обрезка имени и отсутствие гарантии нуля — <a href="https://pubs.opengroup.org/onlinepubs/9799919799/functions/gethostname.html">POSIX.1-2024</a>; ошибка <code>ENAMETOOLONG</code> в glibc — <a href="https://man7.org/linux/man-pages/man2/gethostname.2.html">man 2 gethostname</a>.</li>
            <li><code>uname</code> и <code>struct utsname</code> — <a href="https://pubs.opengroup.org/onlinepubs/9799919799/functions/uname.html">POSIX.1-2024</a>; <code>errno</code> и его значение в потоке — <a href="https://pubs.opengroup.org/onlinepubs/9799919799/functions/errno.html">POSIX.1-2024</a>.</li>
            <li>Макрос <code>small</code> в <code>rpcndr.h</code> — ошибка сборки на кадре Windows (C2628, C2143) и заголовок Windows SDK.</li>
          </ol>
        </div>

        <div class="pager">
          <a href="../05-laboratornaya-1/index.html">← ЛР 1 Процесс изнутри</a>
          <a href="../../index.html">Оглавление</a>
          <a href="../07-c-i-python-vmeste/index.html">1.2 C и Python вместе →</a>
        </div>

        <div class="colophon">
          <span>Глава 1.1 · C для системного программиста · Справочник по системному программированию</span>
          <span class="author-line">Автор: Макаров Максим Николаевич</span>
        </div>
'''

CONTENTS = [('s1', 'Задача главы'), ('s2', 'Шаг 1. Измерить типы'), ('s3', 'Шаг 2. Получить структуру от системы'),
            ('s4', 'Шаг 3. Прочитать строку из буфера'), ('s5', 'Шаг 4. Получить код ошибки'), ('s6', 'Шаг 5. Описать свою структуру'),
            ('s7', 'Шаг 6. Написать функцию ядра'), ('s8', 'Шаг 7. Проверить функцию программой'), ('s9', 'Шаг 8. Найти ошибку по предупреждению'),
            ('s10', 'Шаг 9. Положить ядро в репозиторий'), ('s11', 'Запрос к помощнику ИИ'), ('s12', 'Справка: функции и команды'),
            ('s13', 'Частые вопросы'), ('s14', 'Проверьте себя'), ('s15', 'Шпаргалка по главе')]
TOC = '\n'.join(f'            <li><a href="#{a}">{t}</a></li>' for a, t in CONTENTS)

PAGE = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>1.1 C для системного программиста · Справочник по системному программированию</title>
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
          <p class="running__folio">1.1</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">1.1</span>
          <h1>C для системного<br>программиста</h1>
          <p class="lead">В главе собирается первая функция ядра агента — <code>core_get_info</code>. Она заполняет структуру сведениями о компьютере: номер процесса, число процессоров, размер страницы памяти и имя компьютера. До неё на четырёх маленьких программах разобрано, без чего не читается системный интерфейс: размеры типов, структура, которую система заполняет по адресу, строка в буфере и код ошибки. Каждый шаг — программа, сборка и кадр результата для системы, выбранной переключателем вверху страницы.</p>
        </header>

        <dl class="passport">
          <div><dt>Категория</dt><dd>Язык C</dd></div>
          <div><dt>Уровень</dt><dd>Начальный</dd></div>
          <div><dt>Что получится</dt><dd><code>core.h</code>, <code>core_info.c</code> и <code>show_info.c</code> в <code>agent/core</code></dd></div>
          <div><dt>Сколько занимает</dt><dd>Пара 2, около пятидесяти минут за компьютером</dd></div>
        </dl>

        <nav class="contents">
          <b>Порядок действий</b>
          <ol>
{TOC}
          </ol>
        </nav>
{''.join(S[k] for k in ('s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 'end'))}
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
