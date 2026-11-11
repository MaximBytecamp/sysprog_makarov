"""Глава 2.4 «Потоки» → temy/20-potoki/index.html.

Код: tools/src24 (core.h с core_proc_threads, win|mac|linux/core_threads.c, count_threads.c, race.c, py/brain.py);
core_cpu.c — из src23, core_spawn.c и core_info.c — из src22.
Кадры: ~/sysprog-shots/m24 — macOS и Linux снимает shoot24.py (VS Code через протокол отладки, рамки mark.py),
Windows — экран ВМ Win11-lab 800×600 (win24.py, файлы с ISO m24.iso, ядро ARM64), рамки winmark24.py.
Числа в тексте — с кадров (MODUL-2.md)."""
from pathlib import Path

from ch11 import M, hl, per, shot
from ch12 import hl_py, cmd, between
import viz as V
import walk24

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / 'src24'
OUT = ROOT / 'temy/20-potoki/index.html'


def src(name):
    return (SRC / {'win': 'win/core_threads.c', 'mac': 'mac/core_threads.c', 'linux': 'linux/core_threads.c',
                   'count': 'count_threads.c', 'race': 'race.c'}[name]).read_text()


BRAIN = (SRC / 'py/brain.py').read_text()
BRAIN_PART = '\n'.join([between(BRAIN, 'core.core_proc_threads.argtypes', 'core.core_proc_threads.restype'), '',
                        between(BRAIN, 'def proc_threads', 'return count.value'), '',
                        between(BRAIN, 'def most_threads', 'return sorted')])
BRAIN_MAIN = between(BRAIN, 'if __name__')
WK = walk24.build(hl, hl_py, src, BRAIN_PART)


def cfile(name, os_, cap):
    return f'        <figure class="code" data-os="{os_}">\n          <figcaption><span>{cap}</span></figcaption>\n<pre>{hl(src(name))}</pre>\n        </figure>'


NO_PROC = '<span data-os="win">87</span><span data-os="mac">3</span><span data-os="linux">2</span>'
CALL = '<span data-os="win">снимок Toolhelp32</span><span data-os="mac">proc_pidinfo</span><span data-os="linux">/proc/PID/stat</span>'

PIC_FLOW = V.scheme('Путь вопроса «сколько потоков»',
    V.steps(V.card('мозг', '<code>proc_threads(pid)</code>', '<small>номер процесса</small>', 'py'), V.arrow('pid'),
            V.card('ядро агента', '<code>core_proc_threads</code>', f'<small>{CALL}</small>', 'c'), V.arrow('запрос'),
            V.card('система', 'запись о процессе', '<small>сколько потоков сейчас</small>', 'sys'), V.arrow('число'),
            V.card('мозг', '<code>most_threads()</code>', '<small>у кого потоков больше всего</small>', 'py')),
    'Бирюзовые карточки — Python, янтарная — ядро на C, серая — система. Ответ — одно целое число, переводить единицы не нужно.')

PIC_SRC = V.scheme('Где система хранит число потоков процесса',
    V.tab(['Система', 'Откуда', 'Поле', 'Нет процесса'], [
        ['Windows', 'снимок <code>TH32CS_SNAPPROCESS</code>', '<code>cntThreads</code>', '87'],
        ['macOS', '<code>proc_pidinfo(PROC_PIDTASKINFO)</code>', '<code>pti_threadnum</code>', '3'],
        ['Linux', '<code>/proc/PID/stat</code>', 'поле 20 <code>num_threads</code>', '2']]),
    'macOS и Linux берут число из тех же источников, что процессорное время в главе 2.3, Windows — из того же снимка, что список процессов в главе 2.1.')

PIC_LIFE = V.scheme('Сколько потоков у count_threads в каждый момент',
    V.steps(V.card('start', '1 поток', '<small>только главный</small>', 'sys'), V.arrow('создать × 4'),
            V.card('running', '5 потоков', '<small>главный и четыре рабочих</small>', 'c'), V.arrow('join × 4'),
            V.card('joined', '1 поток', '<small>рабочие завершены</small>', 'sys')),
    'Числа одинаковы на трёх системах — так на кадрах шага 3.')

PIC_RACE = V.scheme('Как два потока теряют одну прибавку',
    V.tab(['Шаг', 'Поток A', 'Поток B', 'counter в памяти'], [
        ['1', 'прочитал 41', '', '41'],
        ['2', '', 'прочитал 41', '41'],
        ['3', 'прибавил, записал 42', '', ('42', 'is-ok')],
        ['4', '', 'прибавил, записал 42', ('42', 'is-bad')]]),
    '<code>counter++</code> — три действия: прочитать, прибавить, записать. Между ними другой поток успевает прочитать старое значение. Две прибавки — а счётчик вырос на одну.')

PIC_AI = V.scheme('Один и тот же счётчик: атомарная прибавка и counter++',
    V.tab(['Система', 'race.c — ADD', 'ai_race.c — counter++, запуск 1', 'запуск 2'], [
        ['Windows', ('4 000 000', 'is-ok'), ('1 307 579', 'is-bad'), ('3 058 075', 'is-bad')],
        ['macOS', ('4 000 000', 'is-ok'), ('1 050 345', 'is-bad'), ('1 159 969', 'is-bad')],
        ['Linux', ('4 000 000', 'is-ok'), ('1 822 571', 'is-bad'), ('1 316 327', 'is-bad')]]),
    'Числа — с кадров. Ожидается 4 000 000; у счётчика с <code>volatile</code> результат каждый раз другой.')

OS_CARD = '<span data-os="win">запись в снимке процессов</span><span data-os="mac">структура <code>proc_taskinfo</code></span><span data-os="linux">файл <code>/proc/PID/stat</code></span>'
OS_FIELD = '<span data-os="win"><code>cntThreads</code></span><span data-os="mac"><code>pti_threadnum</code></span><span data-os="linux">поле 20</span>'
OS_NEW = '<span data-os="win"><code>CreateThread</code></span><span data-os="mac linux"><code>pthread_create</code></span>'
OS_JOIN = '<span data-os="win"><code>WaitForMultipleObjects</code></span><span data-os="mac linux"><code>pthread_join</code></span>'
OS_ADD = '<span data-os="win"><code>InterlockedIncrement64</code></span><span data-os="mac linux"><code>__atomic_fetch_add</code></span>'

SIMPLE_COUNT = V.simple('Как функция узнаёт число потоков',
    '          <p>Считать потоки самим не нужно: система и так ведёт учёт. На каждый процесс у неё заведена карточка, и там написано, сколько у процесса потоков прямо сейчас. Функция идёт к этой карточке и переписывает цифру.</p>\n'
    '          <p>Так же работает отдел кадров. На вопрос «сколько человек в бригаде номер 1212?» сотрудник открывает папку бригады и читает: «пять». Пересчитывать людей по головам никто не бегает.</p>',
    V.steps(V.card('мозг', '«сколько потоков у 1212?»', '<small>вызывает proc_threads</small>', 'py'), V.arrow(),
            V.card('ядро агента', 'идёт в отдел кадров', '<small>вызов системы</small>', 'c'), V.arrow(),
            V.card('система', 'открывает карточку 1212', f'<small>{OS_CARD}</small>', 'sys'), V.arrow(),
            V.card('мозг', 'получает «5»', '<small>число, без перевода единиц</small>', 'py')),
    f'<b>Что есть что.</b> Отдел кадров — система. Папка бригады — {OS_CARD}. Строка «сколько человек» — {OS_FIELD}. Номер бригады — <code>pid</code>.')

SIMPLE_LIFE = V.simple('Что делает count_threads',
    '          <p><code>main</code> — бригадир. В начале смены он один: 1 поток. Потом он нанимает четырёх рабочих и каждому даёт одно задание — поспать секунду. Пока рабочие на смене, людей пятеро: 5 потоков.</p>\n'
    '          <p>Домой бригадир не уходит, пока каждый рабочий не отчитается. Все отчитались и ушли — бригадир снова один: 1 поток. Если бы он не ждал отчётов и не отпускал людей, рабочие так и числились бы на смене — это и есть утечка потоков.</p>',
    V.steps(V.card('start', 'бригадир один', '<small>1 поток</small>', 'sys'), V.arrow('нанял 4'),
            V.card('running', 'бригадир и 4 рабочих', '<small>5 потоков</small>', 'c'), V.arrow('ждёт отчёта'),
            V.card('joined', 'рабочие ушли', '<small>снова 1 поток</small>', 'sys')),
    f'<b>Что есть что.</b> Бригадир — главный поток. Нанять рабочего — {OS_NEW}. Задание — функция <code>worker</code>. Дождаться отчёта — {OS_JOIN}.')

SIMPLE_RACE = V.simple('Почему теряются прибавки',
    '          <p>На доске написано число. Четыре человека должны каждый миллион раз сделать «+1». <code>counter++</code> — это три движения: подойти и посмотреть число, прибавить в уме, стереть и написать новое.</p>\n'
    '          <p>Если двое подошли почти одновременно, оба увидели 41, оба прибавили в уме и оба написали 42. Сделано две прибавки, а число выросло на одну. <code>volatile</code> — это правило «смотри на доску, а не вспоминай»: смотрят честно, но подойти вдвоём всё ещё можно. Атомарная прибавка — счётчик-кликер: нажал кнопку, число выросло, и нажать «посередине» чужого нажатия нельзя.</p>',
    V.steps(V.card('поток A', 'смотрит: 41', '', 'c'), V.arrow(),
            V.card('поток B', 'смотрит: 41', '', 'sys'), V.arrow(),
            V.card('поток A', 'пишет 42', '', 'c'), V.arrow(),
            V.card('поток B', 'пишет 42', '<small>вместо 43 на доске 42</small>', 'sys')),
    f'<b>Что есть что.</b> Доска — переменная <code>counter</code> в памяти. Посмотреть — чтение, написать — запись. Кликер — {OS_ADD}.')


def more(title, body):
    """Свёрнутый блок «Подробнее»: разборы, справка и вопросы не мешают читать главу с первого взгляда."""
    return f'''        <details class="more">
          <summary>{title}</summary>
{body}
        </details>'''


GIST = f'''        <section class="gist" aria-label="Суть главы">
          <p class="gist__head">Суть за две минуты</p>
          <div class="gist__cards">
            <div><b data-n="1">Поток — рабочий в бригаде</b><p>Процесс — бригада, потоки — её рабочие. Они делают дело одновременно и пользуются одним общим складом — памятью процесса.</p><p>Бригадир есть всегда: это главный поток, с него начинается <code>main</code>.</p></div>
            <div><b data-n="2">Считать людей не нужно</b><p>Система, как отдел кадров, держит на каждый процесс карточку, и там написано, сколько в нём потоков. Наша функция просто читает эту цифру.</p><p>Рабочих наняли и не отпустили — цифра растёт. Это утечка потоков.</p></div>
            <div><b data-n="3">Общая доска — ловушка</b><p>Четверо по миллиону раз пишут «+1» на одной доске. Двое смотрят одновременно, оба видят 41, оба пишут 42 — одна прибавка пропала.</p><p>Итог вместо 4 000 000 — от 1 до 3 млн. Спасает «кликер» — атомарная прибавка.</p></div>
          </div>
          <p class="gist__do"><b>За пару:</b>функция <code>core_proc_threads</code> → программа, у которой видно 1 → 5 → 1 поток → мозг находит самые многопоточные процессы → гонка в коде от помощника ИИ.</p>
        </section>'''

S = []

S.append(f'''
        <h2 id="s1"><span class="sec">§1</span>Задача главы</h2>
        <p>В ЛР 7 потоки процесса считали мониторы: <span data-os="win">Монитор ресурсов и PowerShell</span><span data-os="mac">Мониторинг системы и <code>ps -M</code></span><span data-os="linux"><code>top</code></span>. В этой главе ядро агента получает функцию <code>core_proc_threads</code>: она возвращает число потоков процесса по его номеру. Чтобы её проверить, программа на C сама запускает потоки — функцией <span data-os="win"><code>CreateThread</code></span><span data-os="mac linux"><code>pthread_create</code></span>. Мозг находит процессы, у которых потоков больше всего.</p>
        <p>Напомним, из чего состоит агент. <b>Ядро</b> на C — «руки»: достаёт числа у системы. <b>Мозг</b> на Python — «голова»: решает, что с этими числами делать. Сегодня руки учатся доставать новое число, а голова — им пользоваться.</p>
        <p>Путь вопроса от мозга до системы и обратно:</p>
{PIC_FLOW}
        <p>Путь короче, чем в главе 2.3: система отдаёт готовое число, ядру остаётся его передать. <span class="term">Поток</span> — ход выполнения кода внутри процесса, как в ЛР 7.</p>
        <div class="why">
          <p class="why__head">Зачем это нужно в работе</p>
          <ul class="why__list">
            <li><b>Найти утечку.</b> Число потоков растёт и не падает — служба запускает потоки и забывает завершать.</li>
            <li><b>Понять загрузку.</b> 400% в ЛР 7 — это четыре занятых потока.</li>
            <li><b>Поймать гонку.</b> Ошибки потоков не видны с одного запуска — их ловит проверка итога.</li>
          </ul>
        </div>
        <p>Глава продолжает репозиторий <code>sysprog-start</code> после главы 2.3: в <code>agent/core</code> лежат <code>core.h</code>, <code>core_info.c</code>, <code>core_procs.c</code>, <code>core_spawn.c</code> и <code>core_cpu.c</code>, в <code>agent/brain</code> — <code>brain.py</code> с подсчётом загрузки. <span data-os="win">Команды выполняются во встроенном терминале VS Code, запущенного из окна <b>x64 Native Tools Command Prompt for VS 2022</b>.</span><span data-os="mac linux">Команды выполняются во встроенном терминале VS Code в папке <code>agent/core</code>.</span></p>
        <p class="bridge">Первая часть начинается с объявления новой функции в <code>core.h</code>.</p>
''')

CORE_WAS = '''CORE_API <span class="k">int</span> <span class="f">core_proc_cpu</span>(<span class="t">int64_t</span> pid, <span class="k">struct</span> core_cpu *out);'''
CORE_NOW = '''CORE_API <span class="k">int</span> <span class="f">core_proc_cpu</span>(<span class="t">int64_t</span> pid, <span class="k">struct</span> core_cpu *out);
<mark>CORE_API <span class="k">int</span> <span class="f">core_proc_threads</span>(<span class="t">int64_t</span> pid, <span class="t">int32_t</span> *count);</mark>'''

S.append(f'''
        <div class="part" role="separator"><span><b>1</b>Ядро: число потоков</span></div>
        <h2 id="s2"><span class="sec">§2</span>Шаг 1. Объявить функцию в core.h</h2>
        <p class="purpose"><b>Зачем этот шаг</b><code>core.h</code> — меню ядра: список того, что оно умеет. Мозг на Python может позвать только то, что записано в меню. Добавляем туда пункт «сколько потоков у процесса».</p>
        <p>Ответ функции — одно число, поэтому новая структура не нужна: ядро запишет число потоков по адресу <code>count</code>. Тип — <code>int32_t</code>: потоков у процесса бывают тысячи, но не миллиарды.</p>
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
        <p>Договор тот же, что у <code>core_proc_cpu</code>: 0 — число записано, иначе код ошибки системы. Процесса нет — {NO_PROC}, ошибка в параметрах — <span data-os="win">87</span><span data-os="mac linux">22</span>.</p>
{shot('01-core-h', dict(
    win=f'{M(1)} Объявление новой функции.', mac=f'{M(1)} Объявление новой функции.', linux=f'{M(1)} Объявление новой функции.'),
    dict(win='VS Code с core.h: объявление core_proc_threads в рамке', mac='VS Code с core.h: объявление core_proc_threads в рамке',
         linux='VS Code с core.h: объявление core_proc_threads в рамке'))}
        <p class="step-done"><b>Что получилось.</b>В <code>core.h</code> объявлена функция числа потоков. Теперь её нужно написать для своей системы.</p>
''')

S.append(f'''
        <h2 id="s3"><span class="sec">§3</span>Шаг 2. Написать core_threads.c</h2>
        <p class="purpose"><b>Зачем этот шаг</b>Пункт в меню есть, а того, кто его готовит, ещё нет. Пишем, как ядро добывает ответ у системы — у каждой системы по-своему.</p>
        <p>Функция — в новом файле <code>agent/core/core_threads.c</code>. Число потоков каждая система уже хранит в записи о процессе, и источники знакомы по прошлым главам:</p>
{PIC_SRC}
        <p>В каждой строке таблицы — откуда взять число и в каком поле оно лежит. Последний столбец — ответ, когда процесса нет: коды те же, что у <code>core_proc_cpu</code>. Поэтому файл короче <code>core_cpu.c</code>: найти процесс, взять поле, вернуть.</p>
{cfile('win', 'win', 'agent/core/core_threads.c · Windows')}
{cfile('mac', 'mac', 'agent/core/core_threads.c · macOS')}
{cfile('linux', 'linux', 'agent/core/core_threads.c · Linux')}
{SIMPLE_COUNT}
{more('Разбор core_threads.c по строкам', WK['win'] + chr(10) + WK['mac'] + chr(10) + WK['linux'])}
        <p class="step-done"><b>Что получилось.</b>Функция написана для своей системы. Чтобы проверить её, нужен процесс, у которого число потоков меняется на глазах.</p>
''')

S.append(f'''
        <h2 id="s4"><span class="sec">§4</span>Шаг 3. Запустить потоки из C</h2>
        <p class="purpose"><b>Зачем этот шаг</b>Функции пока нельзя верить на слово. Проверяем её на процессе, про который ответ известен заранее: сами запускаем 4 потока и смотрим, покажет ли она 1 → 5 → 1.</p>
        <p>Программа <code>agent/core/count_threads.c</code> сама меняет число своих потоков. Она спрашивает ядро о своём процессе трижды: до запуска потоков, пока четыре потока работают и после того, как все они завершились.</p>
{cfile('count', 'win mac linux', 'agent/core/count_threads.c · все системы')}
{more('Разбор count_threads.c по строкам', WK['count'])}
        <p>Собираем программу из двух файлов<span data-os="linux">; ключ <code>-pthread</code> подключает библиотеку потоков</span>:</p>
{cmd('cl /nologo /W4 count_threads.c core_threads.c\ncount_threads.exe',
     'clang -Wall -Wextra -o count_threads count_threads.c core_threads.c\n./count_threads',
     'gcc -Wall -Wextra -pthread -o count_threads count_threads.c core_threads.c\n./count_threads', 'терминал VS Code в agent/core')}
{shot('02-count', dict(
    win=f'{M(1)} До запуска — 1 поток. {M(2)} Во время работы — 5. {M(3)} После ожидания — снова 1.',
    mac=f'{M(1)} До запуска — 1 поток. {M(2)} Во время работы — 5. {M(3)} После ожидания — снова 1.',
    linux=f'{M(1)} До запуска — 1 поток. {M(2)} Во время работы — 5. {M(3)} После ожидания — снова 1.'),
    dict(win='терминал: start 1 threads, running 5 threads, joined 1 threads', mac='терминал: start 1 threads, running 5 threads, joined 1 threads',
         linux='терминал: start 1 threads, running 5 threads, joined 1 threads'))}
        <p>Три числа складываются в картину жизни процесса:</p>
{PIC_LIFE}
        <p>Главный поток есть всегда, рабочие появляются при создании и исчезают после ожидания. Если бы программа не дождалась потоков и не освободила их, число не вернулось бы к единице: так выглядит утечка потоков.</p>
{SIMPLE_LIFE}
        <p class="step-done"><b>Что получилось.</b>Ядро видит, как у процесса появляются и исчезают потоки. Можно подключать функцию к мозгу.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>2</b>Мозг: у кого больше всего потоков</span></div>
        <h2 id="s5"><span class="sec">§5</span>Шаг 4. Число потоков в Python</h2>
        <p class="purpose"><b>Зачем этот шаг</b>Ради этого всё и делали: агент-сторож должен замечать процессы с подозрительно большим числом потоков. Даём мозгу эту возможность.</p>
        <p>Библиотека ядра теперь собирается из пяти файлов:</p>
{cmd('cl /nologo /W4 /LD core_info.c core_procs.c core_spawn.c core_cpu.c core_threads.c /Fe:sentry_core.dll',
     'clang -Wall -Wextra -shared -fPIC -o libsentry_core.dylib core_info.c core_procs.c core_spawn.c core_cpu.c core_threads.c',
     'gcc -Wall -Wextra -shared -fPIC -o libsentry_core.so core_info.c core_procs.c core_spawn.c core_cpu.c core_threads.c', 'терминал VS Code в agent/core')}
        <p>В <code>brain.py</code> добавляются типы новой функции после типов <code>core_proc_cpu</code> и функции <code>proc_threads</code> и <code>most_threads</code> после <code>cpu_load</code>:</p>
        <figure class="code">
          <figcaption><span>agent/brain/brain.py · новые части</span></figcaption>
<pre>{hl_py(BRAIN_PART)}</pre>
        </figure>
{more('Разбор новых частей brain.py по строкам', WK['brain'])}
        <p>Блок запуска меняется: мозг запускает ребёнка — Python с четырьмя потоками, каждый спит 3 секунды. Через секунду, пока потоки живы, мозг спрашивает число потоков ребёнка и ищет три самых многопоточных процесса:</p>
        <figure class="code">
          <figcaption><span>agent/brain/brain.py · блок запуска</span></figcaption>
<pre>{hl_py(BRAIN_MAIN)}</pre>
        </figure>
{cmd('cd ..\\brain\npython brain.py', 'cd ../brain\npython3 brain.py', 'cd ../brain\npython3 brain.py', 'терминал VS Code')}
{shot('03-brain', dict(
    win=f'{M(1)} У ребёнка 8 потоков. {M(2)} Больше всего потоков у <code>System</code> — 162, у <code>Code.exe</code> — 59, у <code>msedgewebview2.exe</code> — 51.',
    mac=f'{M(1)} У ребёнка 5 потоков. {M(2)} Больше всего потоков у <code>Telegram</code> — 104, у <code>Code</code> и <code>Yandex</code> — по 59.',
    linux=f'{M(1)} У ребёнка 5 потоков. {M(2)} Больше всего потоков у процессов VS Code <code>code</code> — 39, 21 и 21.'),
    dict(win='терминал: child_threads 8, most_threads System 162, Code.exe 59, msedgewebview2.exe 51',
         mac='терминал: child_threads 5, most_threads Telegram 104, Code 59, Yandex 59',
         linux='терминал: child_threads 5, most_threads code 39, code 21, code 21'))}
        <p><span data-os="mac linux">Пять потоков ребёнка — четыре спящих и главный, как в ЛР 7.</span><span data-os="win">Восемь потоков ребёнка — четыре спящих, главный и три служебных потока, которые Python держит в Windows, как в ЛР 7.</span> Первые места в списке занимают <span data-os="win">ядро системы <code>System</code> и программы с встроенным браузером</span><span data-os="mac">мессенджер, редактор и браузер</span><span data-os="linux">процессы VS Code — в контейнере других программ нет</span>: у больших программ десятки потоков. Тревожный признак — число, которое растёт и не падает.</p>
        <p class="step-done"><b>Что получилось.</b>Мозг знает число потоков любого доступного процесса и находит самые многопоточные. Осталось отправить работу в репозиторий.</p>
''')

S.append(f'''
        <h2 id="s6"><span class="sec">§6</span>Шаг 5. Отправить в репозиторий</h2>
        <p class="purpose"><b>Зачем этот шаг</b>Работа должна попасть на GitHub: там её автоматически собирают и проверяют «Проверки».</p>
        <p>В репозиторий уходят исходники: <code>core.h</code>, <code>core_threads.c</code>, <code>count_threads.c</code> и <code>brain.py</code>. В <code>agent/core/README.md</code> дописываем строку о <code>core_threads.c</code> и сборке библиотеки из пяти файлов.</p>
        <figure class="code">
          <figcaption><span>терминал в папке sysprog-start</span><span>то же, что плюс, Commit и Sync Changes</span></figcaption>
<pre>git add agent/core/core.h agent/core/core_threads.c agent/core/count_threads.c agent/core/README.md agent/brain/brain.py
git commit -m "core: core_proc_threads — число потоков, brain: proc_threads и most_threads"
git push</pre>
        </figure>
        <p>Перед <code>git add</code> посмотрите <code>git status</code>: собранную <span data-os="win"><code>count_threads.exe</code> и файлы <code>.obj</code>, <code>.lib</code>, <code>.exp</code></span><span data-os="mac linux"><code>count_threads</code></span> допишите в <code>.gitignore</code>, если их там нет. Новой проверки в этой паре нет: «Проверки» собирают библиотеку с <code>core_threads.c</code> и прогоняют проверки 1 и 2.</p>
        <p class="step-done"><b>Что получилось.</b>Ядро и мозг с числом потоков в репозитории. Последняя часть — ошибка, которую помощник ИИ допускает в коде с потоками.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>3</b>Код от помощника ИИ</span></div>
        <h2 id="s7"><span class="sec">§7</span>Запрос к помощнику ИИ</h2>
        <p class="purpose"><b>Зачем этот шаг</b>Код с потоками вы чаще всего будете получать от ИИ. Здесь — его самая частая ошибка: с одного запуска её не видно. Учимся её узнавать и ловить.</p>
        <p>Код с потоками помощник пишет быстро, и он даже работает. Ошибка прячется в общей переменной, которую меняют сразу несколько потоков. Запрос в режиме Р2 из главы 0.3:</p>
        <figure class="code">
          <figcaption><span>запрос помощнику</span></figcaption>
<pre>Напиши на C для <span data-os="win">Windows</span><span data-os="mac">macOS</span><span data-os="linux">Linux</span> программу: 4 потока по миллиону раз
увеличивают общий счётчик, в конце напечатать его значение.</pre>
        </figure>
        <p>Частый ответ — <code>volatile long long counter</code> и <code>counter++</code> в цикле. <code>volatile</code> заставляет каждый раз читать переменную из памяти — помощник ставит его, «чтобы потоки видели изменения». Но <code>counter++</code> — три действия: прочитать, прибавить, записать. Между ними вклинивается другой поток:</p>
{PIC_RACE}
        <p>Читаем сверху вниз: оба потока прочитали 41, оба записали 42 — одна прибавка пропала. Это <span class="term">гонка</span>: итог зависит от того, кто успел первым. <code>volatile</code> её не лечит. Лечит <span class="term">атомарная прибавка</span> — процессор делает все три действия за один неделимый шаг. Так написан <code>race.c</code>:</p>
{cfile('race', 'win mac linux', 'agent/core/race.c · все системы')}
{more('Разбор race.c по строкам', WK['race'])}
        <p>Вариант помощника получается из <code>race.c</code> заменой двух строк. Собираем оба и запускаем вариант помощника дважды:</p>
{cmd('powershell -c "(gc race.c) -replace \'static long long counter\',\'static volatile long long counter\' -replace \'ADD\\(&counter\\);\',\'counter++;\' | sc ai_race.c"\ncl /nologo /W4 race.c\ncl /nologo /W4 ai_race.c\nfc race.c ai_race.c\nrace.exe\nai_race.exe\nai_race.exe',
     "sed 's/static long long counter/static volatile long long counter/; s/ADD(&counter);/counter++;/' race.c > ai_race.c\nclang -Wall -Wextra -o race race.c\nclang -Wall -Wextra -o ai_race ai_race.c\ndiff race.c ai_race.c\n./race\n./ai_race\n./ai_race",
     "sed 's/static long long counter/static volatile long long counter/; s/ADD(&counter);/counter++;/' race.c > ai_race.c\ngcc -Wall -Wextra -pthread -o race race.c\ngcc -Wall -Wextra -pthread -o ai_race ai_race.c\ndiff race.c ai_race.c\n./race\n./ai_race\n./ai_race", 'терминал VS Code в agent/core')}
{shot('04-race', dict(
    win=f'{M(1)} Вторая разница файлов: <code>ADD(&amp;counter)</code> и <code>counter++</code>; первая, со словом <code>volatile</code>, уехала вверх. {M(2)} <code>race.exe</code>: 4 000 000. {M(3)} <code>ai_race.exe</code>: 1 307 579 и 3 058 075.',
    mac=f'{M(1)} Файлы отличаются двумя строками: <code>volatile</code> и <code>counter++</code>. {M(2)} <code>race</code>: 4 000 000. {M(3)} <code>ai_race</code>: 1 050 345 и 1 159 969.',
    linux=f'{M(1)} Файлы отличаются двумя строками: <code>volatile</code> и <code>counter++</code>. {M(2)} <code>race</code>: 4 000 000. {M(3)} <code>ai_race</code>: 1 822 571 и 1 316 327.'),
    dict(win='терминал: fc, race 4000000, ai_race 1307579 и 3058075', mac='терминал: diff, race 4000000, ai_race 1050345 и 1159969',
         linux='терминал: diff, race 4000000, ai_race 1822571 и 1316327'))}
        <p>Результаты трёх систем рядом:</p>
{PIC_AI}
        <p>Атомарная прибавка — ровно 4 000 000 везде. <code>counter++</code> теряет от четверти до трёх четвертей прибавок, и каждый запуск — новое число. Компилятор молчит, а на одном ядре ошибки не видно вовсе: её находят уже на сервере.</p>
{SIMPLE_RACE}
        <ul class="checklist">
          <li>каждая переменная, которую меняют несколько потоков, меняется атомарной операцией или под замком: <span data-os="win"><code>InterlockedIncrement64</code>, <code>SRWLOCK</code></span><span data-os="mac linux"><code>__atomic_fetch_add</code>, <code>pthread_mutex_t</code></span>;</li>
          <li><code>volatile</code> не считается защитой от гонки;</li>
          <li>каждый запущенный поток дожидаются: <span data-os="win"><code>WaitForMultipleObjects</code> и <code>CloseHandle</code></span><span data-os="mac linux"><code>pthread_join</code></span>;</li>
          <li>программа проверки сверяет итог с ожидаемым и запускается несколько раз на компьютере с несколькими ядрами.</li>
        </ul>
        <p>Первые три пункта проверяются чтением кода, последний — запуском.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>4</b>Справка</span></div>
        <h2 id="s8"><span class="sec">§8</span>Справка: функции и команды</h2>
        <details class="more">
          <summary>Таблица функций трёх систем</summary>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Что нужно</th><th>Windows</th><th>macOS и Linux</th></tr></thead>
            <tbody>
              <tr><td>Число потоков процесса</td><td>снимок Toolhelp32, <code>cntThreads</code></td><td><code>pti_threadnum</code> / поле 20 <code>/proc/PID/stat</code></td></tr>
              <tr><td>Запустить поток</td><td><code>CreateThread</code></td><td><code>pthread_create</code></td></tr>
              <tr><td>Функция потока</td><td><code>DWORD WINAPI f(LPVOID)</code></td><td><code>void *f(void *)</code></td></tr>
              <tr><td>Дождаться потоков</td><td><code>WaitForMultipleObjects</code>, затем <code>CloseHandle</code></td><td><code>pthread_join</code></td></tr>
              <tr><td>Атомарная прибавка</td><td><code>InterlockedIncrement64</code></td><td><code>__atomic_fetch_add</code></td></tr>
              <tr><td>Номер своего процесса</td><td><code>GetCurrentProcessId</code></td><td><code>getpid</code></td></tr>
              <tr><td>Собрать программу с потоками</td><td><code>cl</code> без ключей</td><td>macOS — без ключей, Linux — <code>gcc -pthread</code></td></tr>
            </tbody>
          </table>
        </div>
        </details>

        <div class="part" role="separator"><span><b>5</b>Проверка себя</span></div>
        <h2 id="s9"><span class="sec">§9</span>Частые вопросы</h2>
        <details class="more">
          <summary>Четыре частых заблуждения о потоках</summary>
        <div class="myths">
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b><code>volatile</code> делает переменную безопасной для потоков.</div>
            <div class="myth__yes"><b>На самом деле</b><code>volatile</code> только запрещает компилятору держать копию в регистре. <code>counter++</code> остаётся тремя действиями, и на кадрах из 4 000 000 прибавок дошло от 1 050 345 до 3 058 075.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Если программа один раз дала верный ответ, гонки в ней нет.</div>
            <div class="myth__yes"><b>На самом деле</b>Итог гонки зависит от того, как система раздала ядра. На одном ядре ошибка может не проявиться ни разу. На сервере с многими ядрами она проявляется почти при каждом запуске.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Много потоков у процесса — признак ошибки.</div>
            <div class="myth__yes"><b>На самом деле</b>У больших программ десятки и сотни потоков. Признак утечки — число, которое растёт и не возвращается назад.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>У программы на Python без потоков ровно один поток.</div>
            <div class="myth__yes"><b>На самом деле</b>Сам интерпретатор и библиотеки запускают свои потоки: Python в Windows на кадре держит три служебных.</div>
          </div>
        </div>
        </details>

        <h2 id="s10"><span class="sec">§10</span>Проверьте себя</h2>
        <details>
          <summary>Почему у <code>core_proc_threads</code> нет своей структуры?</summary>
          <p>Ответ — одно целое число. Его записывают по адресу <code>count</code>, как <code>count</code> у <code>core_list_procs</code> в главе 2.1.</p>
        </details>
        <details>
          <summary>Сколько потоков покажет <code>count_threads</code> во время работы и почему?</summary>
          <p>Пять: главный поток и четыре рабочих. До их запуска и после ожидания — один.</p>
        </details>
        <details>
          <summary>Что будет, если не вызвать <span data-os="win"><code>WaitForMultipleObjects</code></span><span data-os="mac linux"><code>pthread_join</code></span>?</summary>
          <p><code>main</code> завершится раньше рабочих потоков, и процесс закончится вместе с ними. В программе, которая работает долго, незавершённые и не освобождённые потоки копятся — это утечка.</p>
        </details>
        <details>
          <summary>Почему <code>counter++</code> из четырёх потоков теряет прибавки?</summary>
          <p>Это чтение, сложение и запись. Два потока читают одно и то же значение, каждый прибавляет единицу и записывает — одна прибавка пропадает.</p>
        </details>
        <details>
          <summary>Чем атомарная прибавка отличается от <code>counter++</code>?</summary>
          <p>Процессор выполняет чтение, сложение и запись как одно неделимое действие, и другой поток не может вклиниться посередине.</p>
        </details>

        <h2 id="s11"><span class="sec">§11</span>Шпаргалка по главе</h2>
        <div class="cheat">
          <div><b>Число потоков</b><span><code>core_proc_threads(pid, &amp;count)</code></span><span data-os="win"><code>cntThreads</code></span><span data-os="mac"><code>pti_threadnum</code></span><span data-os="linux">поле 20 <code>stat</code></span></div>
          <div><b>Запуск потока</b><span data-os="win"><code>CreateThread</code> → дескриптор</span><span data-os="mac linux"><code>pthread_create(&amp;t, NULL, f, arg)</code></span><span data-os="win"><code>WaitForMultipleObjects</code>, <code>CloseHandle</code></span><span data-os="mac linux"><code>pthread_join</code></span></div>
          <div><b>Жизнь потоков</b><span>1 → 5 → 1</span><span>главный есть всегда</span></div>
          <div><b>Мозг</b><span><code>proc_threads(pid)</code> — число или <code>None</code></span><span><code>most_threads(3)</code> — самые многопоточные</span></div>
          <div><b>Гонка</b><span><code>counter++</code> из потоков теряет прибавки</span><span>атомарная операция или замок</span></div>
        </div>

        <h3>Итог главы</h3>
        <ul>
          <li>Число потоков система хранит сама — <code>core_proc_threads</code> его только читает.</li>
          <li>Потоки запустили и дождались: 1 → 5 → 1. Не дождаться — утечка.</li>
          <li>Мозг нашёл у ребёнка <span data-os="win">8</span><span data-os="mac linux">5</span> потоков и три самых многопоточных процесса.</li>
          <li>Общую переменную из потоков меняют только атомарно или под замком: <code>counter++</code> с <code>volatile</code> теряет прибавки.</li>
        </ul>

        <details class="more sources">
          <summary>Откуда взяты факты</summary>
          <ol>
            <li>Кадры и выводы: macOS 26.1, Apple clang 17, Python 3.9 из Command Line Tools; Linux — контейнер Debian 13, gcc 14.4, Python 3.13; Windows 11 ARM64 в VirtualBox, MSVC 19.44 (программы собраны для ARM64), Python 3.14 для ARM64.</li>
            <li><code>CreateToolhelp32Snapshot</code>, <code>PROCESSENTRY32W.cntThreads</code>, <code>CreateThread</code>, <code>WaitForMultipleObjects</code>, <code>InterlockedIncrement64</code> — <a href="https://learn.microsoft.com/windows/win32/api/tlhelp32/ns-tlhelp32-processentry32w">Microsoft Learn, PROCESSENTRY32W</a> и соседние страницы.</li>
            <li><code>proc_taskinfo.pti_threadnum</code> — заголовок <code>sys/proc_info.h</code> SDK macOS; <code>pthread_create</code>, <code>pthread_join</code> — <a href="https://man7.org/linux/man-pages/man3/pthread_create.3.html">man 3 pthread_create</a>.</li>
            <li>Поле 20 <code>num_threads</code> — <a href="https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html">man 5 proc_pid_stat</a>; <code>__atomic_fetch_add</code> — <a href="https://gcc.gnu.org/onlinedocs/gcc/_005f_005fatomic-Builtins.html">GCC, __atomic Builtins</a>.</li>
          </ol>
        </details>

        <div class="pager">
          <a href="../19-laboratornaya-7/index.html">← ЛР 7 Потоки Python и GIL</a>
          <a href="../../index.html">Оглавление</a>
          <a href="../21-laboratornaya-8/index.html">ЛР 8 Карта памяти →</a>
        </div>

        <div class="colophon">
          <span>Глава 2.4 · Потоки · Справочник по системному программированию</span>
          <span class="author-line">Автор: Макаров Максим Николаевич</span>
        </div>
''')

CONTENTS = [('s1', 'Задача главы'), ('s2', 'Шаг 1. Объявить функцию в core.h'), ('s3', 'Шаг 2. Написать core_threads.c'),
            ('s4', 'Шаг 3. Запустить потоки из C'), ('s5', 'Шаг 4. Число потоков в Python'), ('s6', 'Шаг 5. Отправить в репозиторий'),
            ('s7', 'Запрос к помощнику ИИ'), ('s8', 'Справка: функции и команды'), ('s9', 'Частые вопросы'), ('s10', 'Проверьте себя'),
            ('s11', 'Шпаргалка по главе')]
TOC = '\n'.join(f'            <li><a href="#{a}">{t}</a></li>' for a, t in CONTENTS)
LEAD = ('Агент учится считать потоки процесса, а программа на C сама запускает потоки и дожидается их. '
        'В конце — гонка: четыре потока теряют до трёх четвертей общих прибавок.')

PAGE = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>2.4 Потоки · Справочник по системному программированию</title>
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
          <p class="running__folio">2.4</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">2.4</span>
          <h1>Потоки</h1>
          <p class="lead">{LEAD}</p>
        </header>

        <dl class="passport">
          <div><dt>Категория</dt><dd>Процессы</dd></div>
          <div><dt>Уровень</dt><dd>Начальный</dd></div>
          <div><dt>Что получится</dt><dd><code>agent/core/core_threads.c</code>, <code>count_threads.c</code>, новый <code>brain.py</code></dd></div>
          <div><dt>Сколько занимает</dt><dd>Пара 7, около сорока пяти минут за компьютером</dd></div>
        </dl>

{GIST}

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
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(PAGE)
    print('ok', OUT, len(PAGE))
