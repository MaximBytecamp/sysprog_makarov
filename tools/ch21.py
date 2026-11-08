"""Глава 2.1 «Список процессов» → temy/14-spisok-processov/index.html.

Код: tools/src21 (core.h с struct core_proc, win|mac|linux/core_procs.c, list_procs.c, py/brain.py). core_info.c из src21
не показывается: в нём решение задания модуля 1 (uptime_s), эталон закрыт.
Кадры: ~/sysprog-shots/m21/shoot21.py mac|linux|win (macOS 26.1 — VS Code на Mac; Linux — VS Code в контейнере
sp-lab2-linux, Debian 13, gcc 14.4, Python 3.13.5; Windows — ВМ Win11-lab, MSVC 19.44 x64), рамки — m21/mark.py.
Кадр win/05-brain — снимок экрана ВМ (сеть ВМ не работает, CDP недоступен), Python 3.14 ARM64 и ядро для ARM64; рамки — src21/winmark21.py. Числа в тексте — с кадров."""
import html
from pathlib import Path

from ch11 import M, cells, hl, per, shot
from ch12 import hl_py, cmd, between

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / 'src21'
OUT = ROOT / 'temy/14-spisok-processov/index.html'


def src(name):
    return (SRC / {'win': 'win/core_procs.c', 'mac': 'mac/core_procs.c', 'linux': 'linux/core_procs.c', 'list': 'list_procs.c'}[name]).read_text()


BRAIN = (SRC / 'py/brain.py').read_text()
BRAIN_PART = '\n'.join([between(BRAIN, 'class CoreProc', ']'), '',
                        between(BRAIN, 'core.core_list_procs.argtypes', 'TOO_SMALL ='), '',
                        between(BRAIN, 'def list_procs', 'room = count.value'), '',
                        between(BRAIN, 'def parents', 'return chain')])
BRAIN_MAIN = between(BRAIN, 'if __name__')

import viz as V
import walk21
WK = walk21.build(hl, hl_py, cells, src, BRAIN_PART)


def cfile(name, os_, cap):
    return f'        <figure class="code" data-os="{os_}">\n          <figcaption><span>{cap}</span></figcaption>\n<pre>{hl(src(name))}</pre>\n        </figure>'


def todo(text):
    return f'        <div class="shot-todo" data-os="win"><b>Место под кадр · Windows</b><p>{text}</p></div>'


LIB = '<span data-os="win"><code>sentry_core.dll</code></span><span data-os="mac"><code>libsentry_core.dylib</code></span><span data-os="linux"><code>libsentry_core.so</code></span>'
LAYOUT = cells([('pid', '0 · int64_t', 'w'), ('ppid', '8 · int64_t', 'w'), ('name', '16 · char × 64', 'w')])

PIC_TREE = V.scheme('Родители и дети: часть дерева с кадра macOS',
    V.steps(V.card('pid 0', 'kernel_task', '<small>ядро macOS</small>', 'sys'), V.arrow('ppid'),
            V.card('pid 1', 'launchd', '<small>запускает программы входа</small>', 'sys'), V.arrow('ppid'),
            V.card('', 'Code', '<small>VS Code</small>', 'c'), V.arrow('ppid'),
            V.card('', 'Code Helper', '<small>процесс терминала VS Code</small>', 'c'), V.arrow('ppid'),
            V.card('', 'zsh', '<small>оболочка</small>', 'c'), V.arrow('ppid'),
            V.card('', 'Python', '<small>brain.py</small>', 'py')),
    'Стрелка идёт от родителя к ребёнку, а в записи ребёнка хранится номер родителя — <code>ppid</code>. Список детей в записи процесса не хранится: чтобы найти детей, просматривают весь список и ищут свой номер в чужих <code>ppid</code>.')

PIC_CONTRACT = V.scheme('Договор функции: места, ответ, код',
    V.steps(V.card('вызывающий', 'out[max]', '<small>массив на max мест по 80 байт</small>', 'py'), V.arrow('out, max, &amp;count'),
            V.card('ядро', 'core_list_procs', '<small>пишет не больше max строк</small>', 'c'), V.arrow('код'),
            V.card('ответ', 'count', '<small>сколько процессов найдено</small>', 'sys'))
    + V.tab(['Случай', 'В out', 'Код'], [
        ['мест хватило', 'весь список', ('0', 'is-ok')],
        ['max = 10', '10 строк', ('<span data-os="win">122</span><span data-os="mac linux">34</span>', 'is-bad')],
        ['ошибка в параметрах', 'ничего', ('<span data-os="win">87</span><span data-os="mac linux">22</span>', 'is-bad')]]),
    'Число процессов заранее неизвестно. Поэтому функция сообщает, сколько мест нужно, и вызывающий повторяет вызов с бо́льшим массивом.')

PIC_SOURCES = V.scheme('Откуда ядро берёт список',
    V.split(('Windows', V.steps(V.card('', 'CreateToolhelp32Snapshot', '<small>снимок всех процессов</small>', 'sys'), V.arrow(),
                                V.card('', 'Process32FirstW / NextW', '<small>запись за записью</small>', 'c'))),
            ('macOS', V.steps(V.card('', 'proc_listallpids', '<small>номера всех процессов</small>', 'sys'), V.arrow(),
                              V.card('', 'proc_pidinfo', '<small>родитель и имя по номеру</small>', 'c'))),
            ('Linux', V.steps(V.card('', 'opendir("/proc")', '<small>папка на каждый процесс</small>', 'sys'), V.arrow(),
                              V.card('', '/proc/N/stat', '<small>строка со сведениями</small>', 'c'))), rows=True),
    'Три системы отдают список по-разному, а наружу функция ядра отдаёт одно и то же: массив <code>struct core_proc</code> и <code>count</code>.')

PIC_ACTIONS = V.scheme('Что происходит после git push',
    V.steps(V.card('вы', 'git push', '<small>исходники ядра и мозга</small>', 'py'), V.arrow('запуск «Проверки»'),
            V.card('GitHub Actions', 'три сервера', '<small>Windows, macOS, Linux</small>', 'sys'), V.arrow('на каждом'),
            V.card('run_checks.py', 'сборка и сверка', '<small>ядро из agent/core/*.c, список против системного</small>', 'c'), V.arrow('итог'),
            V.card('Summary', 'таблица', '<small>строка 1 в «Агент-сторож»</small>', 'ok'))
    + V.tab(['Сервер', 'Результат', 'Подробности'], [
        ['Windows', ('<span data-os="win">пройдена</span><span data-os="mac linux">пропущено</span>', ''),
         '<span data-os="win">ядро 141, Win32_Process 141, общих 140, родитель совпал у 140</span><span data-os="mac linux">ядро для другой системы, Windows его не собирает</span>'],
        ['macOS', ('<span data-os="mac">пройдена</span><span data-os="win linux">пропущено</span>', ''),
         '<span data-os="mac">ядро 488, ps 488, общих 487, родитель совпал у 487</span><span data-os="win linux">ядро для другой системы, macOS его не собирает</span>'],
        ['Linux', ('<span data-os="linux">пройдена</span><span data-os="win mac">пропущено</span>', ''),
         '<span data-os="linux">ядро 169, ps 170, общих 169, родитель совпал у 169</span><span data-os="win mac">ядро для другой системы, Linux его не собирает</span>']]),
    'Строка проверки 1 в Summary каждого сервера. Числа — из настоящего запуска «Проверок» с ядром главы. Ваше ядро проходит на сервере своей системы, на двух других оно пропускается.')

PIC_FAILS = V.scheme('Если проверка 1 не пройдена',
    V.tab(['Подробности в строке', 'Что не так в ядре', 'Шаг главы'], [
        [('при max = 1 ядро вернуло 0 …', 'is-bad'), 'функция пишет за пределы <code>max</code> или не сообщает о нехватке места', 'шаг 5'],
        [('в списке ядра нет процесса проверки', 'is-bad'), 'список неполный: пропущены процессы, которые не открылись', 'шаги 2, 4'],
        [('процесс проверки: ppid = …', 'is-bad'), 'в <code>ppid</code> записан не тот номер или имя не дописано', 'шаг 2'],
        [('ядро находит не все процессы', 'is-bad'), 'цикл кончается раньше времени или счётчик растёт не для каждого процесса', 'шаги 2, 4'],
        [('ppid отличается от системного', 'is-bad'), 'поле родителя берётся не из того места', 'шаг 2']]),
    'Проверка запускает ваше ядро так же, как шаг 5 и шаг 4: сначала с одним местом, потом с запасом, и сверяет список с программой системы.')

S = []

S.append(f'''
        <h2 id="s1"><span class="sec">§1</span>Задача главы</h2>
        <p>В ЛР 4 вы смотрели дерево процессов в программе системы: у каждого процесса есть родитель, тот процесс, который его запустил. Агенту нужен тот же список в своём коде: с него начинаются проверки модуля 2. Агент ищет процесс, который загружает процессор, растёт в памяти или запущен не тем родителем. В главе ядро агента получает функцию <code>core_list_procs</code>, которая отдаёт список процессов системы, а мозг агента по этому списку находит цепочку своих родителей.</p>
        <p><span class="term">PID</span> (process identifier) — номер процесса, который система выдаёт при запуске. Пока процесс работает, номер не меняется; после завершения номер может достаться новому процессу. <span class="term">PPID</span> (parent PID) — номер родителя. Родитель записан в каждом процессе, а список детей — нет: детей находят, просматривая весь список.</p>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>В анкете сотрудника есть строка «руководитель: табельный номер такой-то». Чтобы нарисовать структуру отдела, берут все анкеты и раскладывают их по номерам руководителей. Анкеты руководителя для этого не нужны: в ней нет списка подчинённых.</p>
          <p class="miss">Табельный номер уволенного не дают новому сотруднику. Номер завершённого процесса система может отдать новому, поэтому записанный родитель иногда оказывается чужим процессом.</p>
        </div></div>
{PIC_TREE}
        <div class="why">
          <p class="why__head">Зачем это нужно в работе</p>
          <ul class="why__list">
            <li><b>Видеть, что запущено.</b> Список процессов — основа диспетчера задач, антивируса и системы наблюдения. Каждая из них начинает со списка, а потом спрашивает о каждом процессе подробности.</li>
            <li><b>Находить, кто что запустил.</b> Командная оболочка, которую запустил текстовый редактор или браузер, — частый признак заражения: человек запускает её из меню или из терминала. Такой вывод делают по цепочке родителей.</li>
            <li><b>Работать с буфером неизвестного размера.</b> Число процессов заранее неизвестно. Договор «дай место — получи число, сколько нужно» встречается в WinAPI и POSIX постоянно.</li>
          </ul>
        </div>
        <p>Глава продолжает репозиторий <code>sysprog-start</code> после задания модуля 1: в <code>agent/core</code> лежат <code>core.h</code> с полем <code>uptime_s</code> и <code>core_info.c</code>, в <code>agent/brain</code> — <code>brain.py</code>. <span data-os="win">Команды выполняются во встроенном терминале VS Code. VS Code запускается из окна <b>x64 Native Tools Command Prompt for VS 2022</b>, как в главе 1.2. Тогда в его терминале доступен <code>cl</code>, а Python — 64-битный для x64.</span><span data-os="mac linux">Команды выполняются во встроенном терминале VS Code, начиная с корня репозитория.</span></p>
        <div class="margin-note margin-note--warn">
          <b>Если задание модуля 1 не сделано</b>
          <p>Структура <code>core_info</code> в этой главе — 280 байт, с полем <code>uptime_s</code> из задания. Если задание не сделано, начните с него: <a href="../11-zadanie-modulya-1/index.html">задание модуля 1</a>, в его начале есть код глав 1.1–1.3 для своей системы. Новые файлы этой главы от <code>uptime_s</code> не зависят, их можно делать и с ядром из главы 1.2, если убрать <code>uptime_s</code> из <code>core.h</code> и <code>brain.py</code>.</p>
        </div>
        <p class="bridge">Ядро отдаёт список массивом структур, поэтому первая часть начинается с описания одной строки списка в <code>core.h</code>.</p>
''')

CORE_WAS = '''<span class="k">struct</span> core_info {
    <span class="c">…</span>
    <span class="t">int64_t</span> uptime_s;
};

CORE_API <span class="k">int</span> <span class="f">core_get_info</span>(<span class="k">struct</span> core_info *out);'''
CORE_NOW = '''<mark><span class="k">#define</span> CORE_NAME_MAX <span class="n">64</span></mark>
<span class="c">…</span>
<span class="k">struct</span> core_info {
    <span class="c">…</span>
    <span class="t">int64_t</span> uptime_s;
};
<mark>
<span class="k">struct</span> core_proc {
    <span class="t">int64_t</span> pid;
    <span class="t">int64_t</span> ppid;
    <span class="k">char</span>    name[CORE_NAME_MAX];
};</mark>

CORE_API <span class="k">int</span> <span class="f">core_get_info</span>(<span class="k">struct</span> core_info *out);
<mark>CORE_API <span class="k">int</span> <span class="f">core_list_procs</span>(<span class="k">struct</span> core_proc *out, <span class="t">int32_t</span> max, <span class="t">int32_t</span> *count);</mark>'''

S.append(f'''
        <div class="part" role="separator"><span><b>1</b>Ядро: список процессов</span></div>
        <h2 id="s2"><span class="sec">§2</span>Шаг 1. Описать процесс в core.h</h2>
        <p>Одна строка списка — три поля: номер процесса, номер родителя и имя. Номера хранятся в <code>int64_t</code>. В Windows номер процесса — 32-битное <code>DWORD</code>, в macOS и Linux — <code>pid_t</code> (тоже 32 бита). Поле на 8 байт вмещает номер любой из трёх систем, и между полями не появляются пропуски для выравнивания. Имя — массив из 64 байт в UTF-8. В <code>core.h</code> добавляются размер имени, структура и объявление функции:</p>
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
        <p>Строка <code>#define CORE_NAME_MAX 64</code> ставится рядом с <code>CORE_HOST_MAX</code>. Поля идут подряд без пропусков, размер структуры — 8 + 8 + 64 = 80 байт:</p>
        {LAYOUT}
        <p>Функция принимает три параметра:</p>
        <ul class="words">
          <li><code>out</code> — адрес массива, куда ядро пишет строки списка;</li>
          <li><code>max</code> — сколько мест в массиве: ядро не пишет за его конец;</li>
          <li><code>count</code> — адрес числа, куда ядро запишет, сколько процессов нашло. Если мест не хватило, это число говорит, сколько их нужно.</li>
        </ul>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>Секретарю дают бланк на 10 строк и просят переписать всех посетителей за день. Посетителей было 14: секретарь заполняет 10 строк, а внизу пишет «всего 14, нужен бланк побольше».</p>
          <p class="miss">Секретарь может дописать строку на полях. Функция на C за край массива писать не должна: там чужая память.</p>
        </div></div>
{PIC_CONTRACT}
{shot('01-core-h', dict(
    win=f'{M(1)} Структура процесса — три поля. {M(2)} Объявление функции ядра.',
    mac=f'{M(1)} Структура процесса — три поля. {M(2)} Объявление функции ядра.',
    linux=f'{M(1)} Структура процесса — три поля. {M(2)} Объявление функции ядра.'),
    dict(win='VS Code с core.h: struct core_proc и объявление core_list_procs в рамках', mac='VS Code с core.h: struct core_proc и объявление core_list_procs в рамках',
         linux='VS Code с core.h: struct core_proc и объявление core_list_procs в рамках'))}
        <p class="step-done"><b>Что получилось.</b>В <code>core.h</code> описана строка списка на 80 байт и договор функции. Теперь её нужно написать для своей системы.</p>
''')

S.append(f'''
        <h2 id="s3"><span class="sec">§3</span>Шаг 2. Написать core_procs.c</h2>
        <p>Функция списка — в новом файле <code>agent/core/core_procs.c</code>: у каждой части ядра свой файл, и <code>core_info.c</code> не меняется. Каждая система отдаёт список своим способом:</p>
{PIC_SOURCES}
{cfile('win', 'win', 'agent/core/core_procs.c · Windows')}
{cfile('mac', 'mac', 'agent/core/core_procs.c · macOS')}
{cfile('linux', 'linux', 'agent/core/core_procs.c · Linux')}
{WK['win']}
{WK['mac']}
{WK['linux']}
        <p>Во всех трёх файлах одинаковы проверка параметров, счётчик <code>found</code> вне условия и ответ в конце: так в коде выполняется договор из шага 1. Различается только то, как система отдаёт сведения о процессах.</p>
        <p class="step-done"><b>Что получилось.</b>Функция <code>core_list_procs</code> написана для своей системы. Проверим её программой на C, прежде чем вызывать из Python.</p>
''')

S.append(f'''
        <h2 id="s4"><span class="sec">§4</span>Шаг 3. Проверить ядро программой на C</h2>
        <p>Программа проверки <code>agent/core/list_procs.c</code> одна для трёх систем: она вызывает функцию ядра и печатает список.</p>
{cfile('list', 'win mac linux', 'agent/core/list_procs.c · все системы')}
{WK['list']}
        <p>Собираем программу из двух файлов и пишем список в файл <code>procs.txt</code>: в терминале сотни строк не уместятся. Последняя строка файла — итог:</p>
{cmd('cd agent\\core\ncl /nologo /W4 list_procs.c core_procs.c\nlist_procs.exe > procs.txt\nfindstr processes procs.txt',
     'cd agent/core\nclang -Wall -Wextra -o list_procs list_procs.c core_procs.c\n./list_procs > procs.txt\ntail -1 procs.txt',
     'cd agent/core\ngcc -Wall -Wextra -o list_procs list_procs.c core_procs.c\n./list_procs > procs.txt\ntail -1 procs.txt',
     'терминал VS Code')}
        <p>Знак <code>&gt;</code> направляет вывод программы в файл вместо терминала. Открываем <code>procs.txt</code> в VS Code.</p>
{shot('02-list', dict(
    win=f'{M(1)} Строка самой программы: <code>list_procs.exe</code>, номер 5900, родитель 5976 — <code>cmd.exe</code> терминала. {M(2)} Итог: 131 процесс, запись — 80 байт.',
    mac=f'{M(1)} Строка самой программы: номер 4979, родитель 4503 — <code>zsh</code> терминала. {M(2)} Итог: 499 процессов, запись — 80 байт.',
    linux=f'{M(1)} Строка самой программы: номер 305, родитель 229 — <code>bash</code> терминала. {M(2)} Итог: 17 процессов, запись — 80 байт.'),
    dict(win='procs.txt в VS Code: строка list_procs.exe 5900 5976, в терминале processes 131, sizeof 80',
         mac='procs.txt в VS Code: строка 4979 4503 list_procs, в терминале processes 499, sizeof 80',
         linux='procs.txt в VS Code: строка 305 229 list_procs, в терминале processes 17, sizeof 80'))}
        <p>Программа нашла в списке сама себя {M(1)}: в момент вызова она тоже процесс. Её родитель — оболочка терминала, из которой её запустили. Размер записи {M(2)} совпал с раскладкой шага 1.</p>
{per(win='<p>Имена в Windows — полные имена файлов с <code>.exe</code>. Первые две строки файла — особые процессы с номерами 0 и 4: <code>[System Process]</code> (бездействие системы) и <code>System</code> (потоки ядра).</p>',
     mac='<p>Имена в macOS обрезаны до 15 символов: в строке 3 имя <code>Yandex Helper (</code> оборвано на скобке, а <code>mdworker_shared</code> — ровно 15. Так хранит имя ядро macOS (<code>MAXCOMLEN</code> = 16 байт с нулём). Процесс 0 — <code>kernel_task</code>, само ядро, процесс 1 — <code>launchd</code>.</p>',
     linux='<p>Кадр снят в контейнере Docker: в нём видны только его 17 процессов, а процесс 1 — <code>sleep</code>, команда запуска контейнера. На обычном Linux процесс 1 — <code>systemd</code>, процессов сотни. Имена обрезаны до 15 символов: так хранит имя ядро Linux (<code>TASK_COMM_LEN</code> = 16 байт с нулём).</p>')}
        <p class="step-done"><b>Что получилось.</b>Ядро отдаёт список, и в нём есть сама программа с верным родителем. Осталось сверить число процессов с программой системы.</p>
''')

S.append(f'''
        <h2 id="s5"><span class="sec">§5</span>Шаг 4. Сверить с программой системы</h2>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>Двое по очереди пересчитывают людей в зале, где идёт перерыв. Счёт расходится на несколько человек: кто-то вышел, кто-то вошёл, а каждый счётчик сам стоит в зале.</p>
          <p class="miss">Людей в зале можно попросить замереть. Процессы во время подсчёта продолжают запускаться и завершаться.</p>
        </div></div>
        <p>Ядро должно находить столько же процессов, сколько находит системная программа. В ЛР 4 это была программа с окном, здесь удобнее командная: <span data-os="win"><code>tasklist</code></span><span data-os="mac linux"><code>ps</code></span>. Печатаем итог ядра и число строк вывода системной программы:</p>
{cmd('findstr processes procs.txt\nfor /f %n in (\'tasklist /NH ^| find /c /v ""\') do @echo tasklist: %n',
     'tail -1 procs.txt\necho "ps: $(ps -A -o pid= | wc -l)"', 'tail -1 procs.txt\necho "ps: $(ps -A -o pid= | wc -l)"', 'терминал VS Code')}
{per(win='<p><code>tasklist /NH</code> печатает процессы без заголовка, <code>find /c /v ""</code> считает строки. <code>for /f … do @echo</code> берёт число из вывода и печатает его с подписью.</p>',
     maclinux='<p><code>ps -A</code> печатает все процессы, <code>-o pid=</code> оставляет в строке только номер без заголовка, <code>wc -l</code> считает строки. <code>$(…)</code> подставляет вывод команды в текст <code>echo</code>.</p>')}
{shot('03-compare', dict(
    win=f'{M(1)} Ядро: 131 процесс. {M(2)} <code>tasklist</code>: 135.',
    mac=f'{M(1)} Ядро: 499 процессов. {M(2)} <code>ps</code>: 485.',
    linux=f'{M(1)} Ядро: 17 процессов. {M(2)} <code>ps</code>: 19.'),
    dict(win='терминал: processes 131, tasklist: 135', mac='терминал: processes 499, ps: 485', linux='терминал: processes 17, ps: 19'))}
        <p>Числа близки, но не равны. Две программы считают процессы в разные моменты, и каждая попадает в свой счёт вместе со своей командой.</p>
{per(win='<p>Список ядра снят в шаге 3, а <code>tasklist</code> запущен позже. Кроме того, в момент подсчёта работают <code>tasklist.exe</code>, <code>find.exe</code> и отдельный <code>cmd.exe</code>, который запускает <code>for /f</code>: их нет в <code>procs.txt</code>. Отсюда разница в 4 процесса.</p>',
     mac='<p>Список ядра снят в шаге 3, а <code>ps</code> запущен позже. В macOS за это время число процессов меняется заметно: короткие процессы вроде <code>mdworker_shared</code> и <code>sleep</code> постоянно появляются и завершаются. При проверке на том же Mac счёт <code>ps</code> раз в секунду за 12 секунд вырос с 548 до 568. Если запустить <code>./list_procs | tail -1</code> и <code>ps</code> сразу друг за другом, числа совпадают с точностью до самих программ. Ядро находит <code>list_procs</code> и процесс 0, а <code>ps</code> — себя.</p>',
     linux='<p>В момент подсчёта работают <code>ps</code>, <code>wc</code> и копия оболочки, которую создаёт <code>$(…)</code>, а <code>list_procs</code> уже завершился: три процесса вместо одного, разница — 2.</p>')}
        <p>Точного совпадения в работающей системе не бывает, поэтому числа сравнивают с допуском. Надёжнее искать в списке ядра процессы, которые точно работают: оболочку терминала и саму программу.</p>
        <p class="step-done"><b>Что получилось.</b>Ядро находит те же процессы, что системная программа. Последняя проверка ядра — ответ, когда мест мало.</p>
''')

S.append(f'''
        <h2 id="s6"><span class="sec">§6</span>Шаг 5. Дать ядру мало места</h2>
        <p>Параметр командной строки задаёт 10 мест вместо 4096. Процессов больше, и ядро должно ответить кодом «мест не хватило» и числом, сколько мест нужно:</p>
{cmd('list_procs.exe 10\necho %errorlevel%', './list_procs 10\necho $?', './list_procs 10\necho $?', 'терминал VS Code')}
        <p><span data-os="win"><code>%errorlevel%</code></span><span data-os="mac linux"><code>$?</code></span> — код завершения последней программы.</p>
{shot('04-small', dict(
    win=f'{M(1)} Код 122, нужно 132 места, было 10.',
    mac=f'{M(1)} Код 34, нужно 483 места, было 10.',
    linux=f'{M(1)} Код 34, нужно 17 мест, было 10.'),
    dict(win='list_procs.exe 10: core_list_procs: error 122, need 132 places, have 10; errorlevel 1',
         mac='./list_procs 10: core_list_procs: error 34, need 483 places, have 10; код 1',
         linux='./list_procs 10: core_list_procs: error 34, need 17 places, have 10; код 1'))}
{per(win='<p>Код 122 — <code>ERROR_INSUFFICIENT_BUFFER</code>, «область данных, переданная системному вызову, слишком мала». Этим кодом многие функции WinAPI сообщают, что переданный им буфер мал.</p>',
     maclinux='<p>Код 34 — <code>ERANGE</code>, «Result too large»: результат не помещается в отведённое место. Его же возвращает, например, <code>getcwd</code>, когда путь длиннее буфера.</p>')}
        <p>Число нужных мест — то, ради чего функция считает процессы до конца. Без него вызывающему пришлось бы угадывать размер и повторять вызов вслепую. Программа на C на этом завершается кодом 1, а мозг агента повторит вызов с нужным местом.</p>
        <p class="step-done"><b>Что получилось.</b>Ядро соблюдает договор: при нехватке места оно не выходит за массив и сообщает, сколько мест нужно. Можно подключать функцию к мозгу.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>2</b>Мозг: цепочка родителей</span></div>
        <h2 id="s7"><span class="sec">§7</span>Шаг 6. Вызвать список из Python</h2>
        <p>Библиотека ядра теперь собирается из двух файлов: <code>core_info.c</code> и <code>core_procs.c</code>. Программа <code>list_procs.c</code> в библиотеку не входит: в ней <code>main</code>.</p>
{cmd('cl /nologo /W4 /LD core_info.c core_procs.c /Fe:sentry_core.dll',
     'clang -Wall -Wextra -shared -fPIC -o libsentry_core.dylib core_info.c core_procs.c',
     'gcc -Wall -Wextra -shared -fPIC -o libsentry_core.so core_info.c core_procs.c', 'терминал VS Code, папка agent/core')}
        <p>В <code>brain.py</code> добавляются класс <code>CoreProc</code>, типы новой функции и две функции Python. Класс ставится после <code>CoreInfo</code>, типы — после типов <code>core_get_info</code>, функции — после <code>get_info</code>. Кроме того, в начало файла добавляется <code>import errno</code>, а функция <code>error_text</code> из задания модуля 1 остаётся как была:</p>
        <figure class="code">
          <figcaption><span>agent/brain/brain.py · новые части</span></figcaption>
<pre>{hl_py(BRAIN_PART)}</pre>
        </figure>
{WK['brain']}
        <p>В конце файла сообщение <code>agent_started</code> получает два новых поля — число процессов и имена цепочки родителей от самого <code>brain.py</code> вверх:</p>
        <figure class="code">
          <figcaption><span>agent/brain/brain.py · запуск</span></figcaption>
<pre>{hl_py(BRAIN_MAIN)}</pre>
        </figure>
        <p>Запускаем из папки <code>agent/brain</code>:</p>
{cmd('cd ..\\brain\npython brain.py', 'cd ../brain\npython3 brain.py', 'cd ../brain\npython3 brain.py', 'терминал VS Code')}
{shot('05-brain', dict(
    win=f'{M(1)} Запуск <code>python brain.py</code>. {M(2)} 118 процессов. {M(3)} Цепочка родителей: <code>python.exe</code> → <code>cmd.exe</code> → <code>Code.exe</code> → <code>Code.exe</code> → <code>cmd.exe</code> → <code>explorer.exe</code>. Кадр снят Python для ARM64 с ядром, собранным для ARM64: на компьютере с процессором x64 вывод такой же.',
    mac=f'{M(1)} Функция <code>list_procs</code> с повтором. {M(2)} 491 процесс. {M(3)} Цепочка родителей: <code>Python</code> → <code>zsh</code> → <code>Code Helper</code> → <code>Code</code> → <code>launchd</code> → <code>kernel_task</code>.',
    linux=f'{M(1)} Функция <code>list_procs</code> с повтором. {M(2)} 17 процессов. {M(3)} Цепочка родителей: <code>python3</code> → <code>bash</code> → <code>code</code> → <code>code</code> → <code>sleep</code>.'),
    dict(win='терминал VS Code: python brain.py, вывод procs 118 и parents python.exe, cmd.exe, Code.exe, Code.exe, cmd.exe, explorer.exe',
         mac='VS Code с brain.py: def list_procs в рамке, вывод procs 491 и parents Python, zsh, Code Helper, Code, launchd, kernel_task',
         linux='VS Code с brain.py: def list_procs в рамке, вывод procs 17 и parents python3, bash, code, code, sleep'))}
{per(win='<p>На кадре 118 процессов, и 256 мест хватило с первого вызова. Если процессов больше 256, первый вызов возвращает «мест не хватило», второй — весь список.</p>',
     mac='<p>Процессов больше 256, поэтому первый вызов вернул «мест не хватило», а второй — весь список.</p>',
     linux='<p>В контейнере 17 процессов, и 256 мест хватило с первого вызова. На обычном Linux процессов сотни, и сработает повтор.</p>')}
        <p>Цепочка {M(3)} читается снизу вверх как путь запуска: система запустила VS Code, VS Code — оболочку терминала, оболочка — Python.</p>
{per(mac='<p>Цепочка доходит до процесса 0 <code>kernel_task</code>: у него <code>ppid</code> тоже 0, и функция <code>parents</code> останавливается.</p>',
     linux='<p>Цепочка кончается на процессе 1 <code>sleep</code>: его родитель 0 в списке отсутствует, потому что процесса 0 в <code>/proc</code> нет.</p>',
     win='<p>В Windows цепочка часто обрывается раньше: родитель записан номером, а сам родитель мог давно завершиться. На кадре цепочка кончается на <code>explorer.exe</code>: при входе в систему его запускает процесс <code>userinit.exe</code> и сразу завершается, поэтому родителя Проводника в списке нет. Второй <code>cmd.exe</code> в цепочке — окно, из которого запущен VS Code.</p>')}
        <p class="step-done"><b>Что получилось.</b>Мозг агента получает полный список процессов, сколько бы их ни было, и находит цепочку процессов, которые его запустили.</p>
''')

S.append(f'''
        <h2 id="s8"><span class="sec">§8</span>Шаг 7. Отправить в репозиторий</h2>
        <p>В репозиторий уходят исходники: <code>core.h</code>, <code>core_procs.c</code>, <code>list_procs.c</code> и <code>brain.py</code>. Собранные файлы и <code>procs.txt</code> в него не входят: библиотеку и программу каждый собирает у себя, а список процессов у каждого свой. В <code>agent/core/README.md</code> дописываем строку о <code>core_procs.c</code> и сборке библиотеки из двух файлов.</p>
        <figure class="code">
          <figcaption><span>терминал в папке sysprog-start</span><span>то же, что плюс, Commit и Sync Changes</span></figcaption>
<pre>git add agent/core/core.h agent/core/core_procs.c agent/core/list_procs.c agent/core/README.md agent/brain/brain.py
git commit -m "core: core_list_procs — список процессов, brain: цепочка родителей"
git push</pre>
        </figure>
        <p>Перед <code>git add</code> посмотрите <code>git status</code>: если в списке есть <span data-os="win"><code>list_procs.exe</code></span><span data-os="mac linux"><code>list_procs</code></span> или <code>procs.txt</code>, допишите их в <code>.gitignore</code>.</p>
        <p>С этой пары в отчёте «Проверок» работает первая проверка агента-сторожа: список процессов ядра совпадает с системным. Схема ниже показывает, что запускается после <code>git push</code> и где искать результат: вкладка <b>Actions</b> → <b>Проверки</b> → последний запуск → <b>Summary</b>, таблица «Агент-сторож».</p>
{PIC_ACTIONS}
        <p>Верхняя часть схемы — путь отправки: GitHub запускает проверки на трёх серверах, и на каждом <code>run_checks.py</code> собирает библиотеку из ваших файлов <code>agent/core/*.c</code>. Нижняя таблица — строка проверки 1 с каждого сервера. На сервере вашей системы стоит «пройдена», и в подробностях четыре числа: сколько процессов нашло ядро, сколько показала программа системы, сколько номеров есть в обоих списках и у скольких из них родитель совпал. Ядро и системная программа запускаются друг за другом, и за доли секунды один-два процесса успевают завершиться или появиться, поэтому числа могут отличаться на единицу. Проверка допускает разницу до 5 процессов или до 10%. На двух других серверах стоит «пропущено»: <span data-os="win"><code>core_procs.c</code> с <code>windows.h</code> там не собирается</span><span data-os="mac"><code>core_procs.c</code> с <code>libproc.h</code> собирается только в macOS</span><span data-os="linux"><code>core_procs.c</code> читает <code>/proc</code>, а он есть только в Linux</span>, и это не ошибка.</p>
        <p>Если в строке стоит «не пройдена», подробности подсказывают, где искать ошибку:</p>
{PIC_FAILS}
        <p>Левая колонка — начало текста из подробностей, средняя — что обычно неверно в коде, правая — шаг главы, который это показывает у вас на компьютере. Исправленный файл отправляется ещё одним коммитом, и проверки запускаются снова.</p>
        <p class="step-done"><b>Что получилось.</b>Ядро и мозг с новым списком процессов в репозитории, а проверка 1 агента-сторожа пройдена на сервере вашей системы. Последняя часть — что проверять в коде, если такую функцию пишет помощник ИИ.</p>

        <h2 id="s9"><span class="sec">§9</span>Запрос к помощнику ИИ</h2>
        <p>Функцию списка процессов помощник ИИ пишет быстро, но в ней легко пропустить договор о месте. Запрос в режиме Р1 из главы 0.3:</p>
        <figure class="code">
          <figcaption><span>запрос помощнику</span></figcaption>
<pre>Вот core.h. Напиши core_list_procs для <span data-os="win">Windows</span><span data-os="mac">macOS</span><span data-os="linux">Linux</span>: функция заполняет out не больше чем max строками,
в *count пишет число процессов, при нехватке места возвращает код ошибки.</pre>
        </figure>
        <ul class="checklist">
          <li>функция не пишет в <code>out</code> больше <code>max</code> строк — проверка <code>if (found &lt; max)</code> стоит перед записью;</li>
          <li>счётчик растёт и после того, как место кончилось, иначе <code>count</code> не скажет, сколько мест нужно;</li>
          <li><span data-os="win">снимок закрывается <code>CloseHandle</code> на всех путях, в том числе при ошибке <code>Process32FirstW</code>;</span><span data-os="mac">массив для <code>proc_listallpids</code> передаётся размером в байтах, а результат — число номеров;</span><span data-os="linux">закрывающая скобка имени ищется с конца строки, и папка закрывается <code>closedir</code>;</span></li>
          <li>шаг 5 даёт код <span data-os="win">122</span><span data-os="mac linux">34</span> и число нужных мест, шаг 4 — число процессов рядом с системной программой.</li>
        </ul>
        <p>Первые три пункта проверяются чтением кода, последний — запуском.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>3</b>Справка</span></div>
        <h2 id="s10"><span class="sec">§10</span>Справка: функции и команды</h2>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Что нужно</th><th>Windows</th><th>macOS</th><th>Linux</th></tr></thead>
            <tbody>
              <tr><td>Все процессы</td><td><code>CreateToolhelp32Snapshot</code>, <code>Process32FirstW</code>, <code>Process32NextW</code></td><td><code>proc_listallpids</code></td><td><code>opendir("/proc")</code>, <code>readdir</code></td></tr>
              <tr><td>Родитель и имя</td><td>поля <code>th32ParentProcessID</code>, <code>szExeFile</code></td><td><code>proc_pidinfo(…, PROC_PIDT_SHORTBSDINFO, …)</code></td><td>файл <code>/proc/N/stat</code></td></tr>
              <tr><td>Длина имени</td><td>полное имя файла</td><td>15 символов</td><td>15 символов</td></tr>
              <tr><td>«Мест не хватило»</td><td>122 <code>ERROR_INSUFFICIENT_BUFFER</code></td><td colspan="2">34 <code>ERANGE</code></td></tr>
              <tr><td>Число процессов командой</td><td><code>tasklist /NH | find /c /v ""</code></td><td colspan="2"><code>ps -A -o pid= | wc -l</code></td></tr>
              <tr><td>Собрать библиотеку</td><td><code>cl /LD core_info.c core_procs.c /Fe:sentry_core.dll</code></td><td><code>clang -shared -fPIC … core_info.c core_procs.c</code></td><td><code>gcc -shared -fPIC … core_info.c core_procs.c</code></td></tr>
            </tbody>
          </table>
        </div>

        <div class="part" role="separator"><span><b>4</b>Проверка себя</span></div>
        <h2 id="s11"><span class="sec">§11</span>Частые вопросы</h2>
        <div class="myths">
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>В записи процесса хранится список его детей.</div>
            <div class="myth__yes"><b>На самом деле</b>Хранится только номер родителя. Детей находят по всему списку — так строят дерево ЛР 4 и программы системы.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Число процессов у ядра и у системной программы должно совпасть точно.</div>
            <div class="myth__yes"><b>На самом деле</b>Процессы появляются и завершаются каждую секунду, а каждая программа попадает в свой счёт. В шаге 4 числа разошлись на 2–14.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Если места мало, функция вернёт часть списка без ошибки.</div>
            <div class="myth__yes"><b>На самом деле</b>Она вернёт часть списка и код ошибки, а в <code>count</code> — сколько мест нужно. Код нельзя пропускать: иначе агент не узнает, что список неполный.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Номер родителя всегда указывает на настоящего родителя.</div>
            <div class="myth__yes"><b>На самом деле</b>Родитель мог завершиться, а его номер — достаться другому процессу. Поэтому <code>parents</code> ограничивает цепочку 64 шагами.</div>
          </div>
        </div>

        <h2 id="s12"><span class="sec">§12</span>Проверьте себя</h2>
        <details>
          <summary>Какого размера <code>struct core_proc</code> и почему номера в ней по 8 байт?</summary>
          <p>80 байт: 8 + 8 + 64. Поле на 8 байт вмещает номер процесса любой из трёх систем. Пропусков для выравнивания нет, поэтому раскладка одна на всех системах и совпадает с описанием в Python.</p>
        </details>
        <details>
          <summary>Зачем функция считает процессы и после того, как место в массиве кончилось?</summary>
          <p>Чтобы записать в <code>count</code> число нужных мест. По нему мозг агента сразу повторяет вызов с массивом нужного размера.</p>
        </details>
        <details>
          <summary>Что вернёт <code>core_list_procs</code>, если передать <code>max</code> = 10, а процессов 17?</summary>
          <p>Первые 10 строк в <code>out</code>, <code>count</code> = 17 и код <span data-os="win">122</span><span data-os="mac linux">34</span>.</p>
        </details>
        <details>
          <summary>Почему имя процесса в macOS и Linux бывает обрезано, а в Windows — нет?</summary>
          <p>Ядра macOS и Linux хранят короткое имя процесса в 16 байтах с нулём, то есть до 15 символов. В Windows из снимка приходит полное имя файла программы.</p>
        </details>
        <details>
          <summary>Почему в Linux закрывающую скобку имени ищут с конца строки?</summary>
          <p>Имя процесса может содержать пробелы и скобки. Всё между первой «(» и последней «)» — имя, а числа после него читаются уже без ошибок.</p>
        </details>
        <details>
          <summary>Где кончается цепочка родителей и почему?</summary>
          <p>Когда номера родителя нет в списке (родитель завершился или это процесс 1 в контейнере), когда процесс сам себе родитель (процесс 0) или после 64 шагов.</p>
        </details>

        <h2 id="s13"><span class="sec">§13</span>Шпаргалка по главе</h2>
        <div class="cheat">
          <div><b>Строка списка</b><span><code>struct core_proc</code>: <code>pid</code>, <code>ppid</code>, <code>name[64]</code></span><span>80 байт</span></div>
          <div><b>Договор</b><span><code>core_list_procs(out, max, &amp;count)</code></span><span>не больше <code>max</code> строк, в <code>count</code> — сколько найдено</span></div>
          <div><b>Мест мало</b><span data-os="win">122 <code>ERROR_INSUFFICIENT_BUFFER</code></span><span data-os="mac linux">34 <code>ERANGE</code></span><span>повторить с <code>count</code> + запас</span></div>
          <div><b>Источник</b><span data-os="win"><code>CreateToolhelp32Snapshot</code> + <code>Process32NextW</code></span><span data-os="mac"><code>proc_listallpids</code> + <code>proc_pidinfo</code></span><span data-os="linux"><code>/proc</code> + <code>/proc/N/stat</code></span></div>
          <div><b>Сверка</b><span data-os="win"><code>tasklist</code></span><span data-os="mac linux"><code>ps -A</code></span><span>близко, но не точно</span></div>
          <div><b>Мозг</b><span><code>list_procs()</code> — список словарей</span><span><code>parents(procs, os.getpid())</code> — цепочка</span></div>
        </div>

        <h3>Итог главы</h3>
        <p>Ядро агента получило функцию <code>core_list_procs</code>: она заполняет массив строками «номер, родитель, имя» по 80 байт и пишет в <code>count</code>, сколько процессов нашла. Windows отдаёт список снимком Tool Help, macOS — номерами из <code>proc_listallpids</code> и сведениями <code>proc_pidinfo</code>, Linux — папками <code>/proc</code> и файлами <code>stat</code>. Наружу функция на всех системах отдаёт одно и то же. Программа <code>list_procs.c</code> показала три вещи. Ядро находит само себя с верным родителем. Число процессов близко к числу системной программы. При 10 местах приходит код <span data-os="win">122</span><span data-os="mac linux">34</span> и число нужных мест. Мозг агента повторяет вызов с нужным местом и по номерам родителей строит цепочку от <code>brain.py</code> вверх до процесса, с которого начинается система.</p>

        <div class="sources">
          <b>Откуда взяты факты</b>
          <ol>
            <li>Кадры и выводы: macOS 26.1, Apple clang 17.0.0, Python 3.12.12; Linux — контейнер Debian 13, gcc 14.4, Python 3.13.5; Windows 11 ARM64 в VirtualBox, MSVC 19.44 (x64), Python 3.14.0 для x64; кадр шага 6 — Python 3.14.0 для ARM64 и ядро, собранное для ARM64; VS Code 1.144.</li>
            <li><code>CreateToolhelp32Snapshot</code>, <code>Process32FirstW</code>, <code>PROCESSENTRY32W</code> — <a href="https://learn.microsoft.com/windows/win32/toolhelp/taking-a-snapshot-and-viewing-processes">Microsoft Learn, Taking a Snapshot and Viewing Processes</a>; коды 87 и 122 — <a href="https://learn.microsoft.com/windows/win32/debug/system-error-codes--0-499-">System Error Codes</a>.</li>
            <li><code>proc_listallpids</code>, <code>proc_pidinfo</code>, <code>struct proc_bsdshortinfo</code>, <code>MAXCOMLEN</code> — заголовки <code>libproc.h</code>, <code>sys/proc_info.h</code>, <code>sys/param.h</code> из SDK macOS.</li>
            <li>Формат <code>/proc/PID/stat</code> и длина имени 16 байт — <a href="https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html">man 5 proc_pid_stat</a>.</li>
            <li><code>ERANGE</code> и <code>EINVAL</code> — <a href="https://man7.org/linux/man-pages/man3/errno.3.html">man 3 errno</a>.</li>
          </ol>
        </div>

        <div class="pager">
          <a href="../13-laboratornaya-4/index.html">← ЛР 4 Дерево процессов</a>
          <a href="../../index.html">Оглавление</a>
        </div>

        <div class="colophon">
          <span>Глава 2.1 · Список процессов · Справочник по системному программированию</span>
          <span class="author-line">Автор: Макаров Максим Николаевич</span>
        </div>
''')

CONTENTS = [('s1', 'Задача главы'), ('s2', 'Шаг 1. Описать процесс в core.h'), ('s3', 'Шаг 2. Написать core_procs.c'),
            ('s4', 'Шаг 3. Проверить ядро программой на C'), ('s5', 'Шаг 4. Сверить с программой системы'),
            ('s6', 'Шаг 5. Дать ядру мало места'), ('s7', 'Шаг 6. Вызвать список из Python'), ('s8', 'Шаг 7. Отправить в репозиторий'),
            ('s9', 'Запрос к помощнику ИИ'), ('s10', 'Справка: функции и команды'), ('s11', 'Частые вопросы'),
            ('s12', 'Проверьте себя'), ('s13', 'Шпаргалка по главе')]
TOC = '\n'.join(f'            <li><a href="#{a}">{t}</a></li>' for a, t in CONTENTS)

PAGE = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>2.1 Список процессов · Справочник по системному программированию</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,600;0,7..72,700;1,7..72,400&family=Pixelify+Sans:wght@500;600;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css">
</head>
<body>
  <div class="book">
    <div class="book__body">
      <div class="spine"><span>Модуль 2 · Процессы, потоки и память</span></div>

      <main class="leaf">
        <div class="running">
          <p class="eyebrow"><a href="../../index.html" style="text-decoration:none;color:inherit">Справочник по системному программированию</a> · модуль 2 · процессы</p>
          <p class="running__folio">2.1</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">2.1</span>
          <h1>Список процессов</h1>
          <p class="lead">В главе ядро агента получает функцию <code>core_list_procs</code>: она отдаёт список всех процессов системы — номер, номер родителя и имя. Разобрано, как список берётся в Windows, macOS и Linux, как функция работает с массивом неизвестного заранее размера и как проверить её числами системной программы. В конце мозг агента находит цепочку своих родителей.</p>
        </header>

        <dl class="passport">
          <div><dt>Категория</dt><dd>Процессы</dd></div>
          <div><dt>Уровень</dt><dd>Начальный</dd></div>
          <div><dt>Что получится</dt><dd><code>agent/core/core_procs.c</code>, <code>list_procs.c</code>, новый <code>brain.py</code></dd></div>
          <div><dt>Сколько занимает</dt><dd>Пара 4, около сорока пяти минут за компьютером</dd></div>
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
