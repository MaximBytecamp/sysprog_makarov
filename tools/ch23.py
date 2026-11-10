"""Глава 2.3 «Процессорное время» → temy/18-processornoe-vremya/index.html.

Код: tools/src23 (core.h со struct core_cpu, win|mac|linux/core_cpu.c, cpu_top.c, py/brain.py); core_spawn.c — из tools/src22.
Кадры: ~/sysprog-shots/m23 — macOS и Linux снимает shoot23.py (VS Code через протокол отладки, рамки mark.py),
Windows — экран ВМ Win11-lab 800×600 (win23.py, файлы с ISO m23.iso, ядро ARM64), рамки winmark23.py.
Числа в тексте — с кадров (MODUL-2.md)."""
from pathlib import Path

from ch11 import M, cells, hl, per, shot
from ch12 import hl_py, cmd, between
import viz as V
import walk23

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / 'src23'
OUT = ROOT / 'temy/18-processornoe-vremya/index.html'


def src(name):
    return (SRC / {'win': 'win/core_cpu.c', 'mac': 'mac/core_cpu.c', 'linux': 'linux/core_cpu.c', 'top': 'cpu_top.c'}[name]).read_text()


BRAIN = (SRC / 'py/brain.py').read_text()
BRAIN_PART = '\n'.join([between(BRAIN, 'class CoreCpu', ']'), '',
                        between(BRAIN, 'core.core_proc_cpu.argtypes', 'core.core_proc_cpu.restype'), '',
                        between(BRAIN, 'def proc_cpu', 'return cpu.user_us'), '',
                        between(BRAIN, 'def cpu_load', 'return sorted')])
BRAIN_MAIN = between(BRAIN, 'if __name__')
WK = walk23.build(hl, hl_py, src, BRAIN_PART)


def cfile(name, os_, cap):
    return f'        <figure class="code" data-os="{os_}">\n          <figcaption><span>{cap}</span></figcaption>\n<pre>{hl(src(name))}</pre>\n        </figure>'


NO_PROC = '<span data-os="win">87</span><span data-os="mac">3</span><span data-os="linux">2</span>'
CALL = '<span data-os="win">GetProcessTimes</span><span data-os="mac">proc_pidinfo</span><span data-os="linux">/proc/PID/stat</span>'
LAYOUT = cells([('user_us', '0 · int64_t', 'w'), ('kernel_us', '8 · int64_t', 'w')])

PIC_FLOW = V.scheme('Путь замера: от мозга до процентов',
    V.steps(V.card('мозг', '<code>proc_cpu(pid)</code>', '<small>номер процесса</small>', 'py'), V.arrow('pid'),
            V.card('ядро агента', '<code>core_proc_cpu</code>', f'<small><code>{CALL}</code></small>', 'c'), V.arrow('счётчик'),
            V.card('система', 'время процесса', '<small>в своих единицах</small>', 'sys'), V.arrow('× / ÷'),
            V.card('ядро агента', 'микросекунды', '<small>user_us, kernel_us</small>', 'c'))
    + V.steps(V.card('мозг', 'снимок 1', '<small>время всех процессов</small>', 'py'), V.arrow('пауза 1 с'),
              V.card('мозг', 'снимок 2', '<small>то же ещё раз</small>', 'py'), V.arrow('разница'),
              V.card('мозг', '<code>cpu_load()</code>', '<small>проценты, самые занятые первыми</small>', 'py')),
    'Верхняя строка — один замер одного процесса, нижняя — как мозг из двух снимков получает загрузку. Бирюзовые карточки — Python, янтарные — ядро на C, серые — система.')

PIC_CONTRACT = V.scheme('Договор core_proc_cpu: что приходит в ответ',
    V.tab(['Случай', 'Код', 'Что в ответе'], [
        ['процесс прочитан', ('0', 'is-ok'), '<code>user_us</code> и <code>kernel_us</code> в микросекундах'],
        ['процесса нет', (NO_PROC, 'is-bad'), 'ничего'],
        ['процесс чужой', ('<span data-os="win">5</span><span data-os="mac">1</span><span data-os="linux">0</span>', 'is-bad'),
         '<span data-os="win mac">ничего: прав не хватает</span><span data-os="linux">в Linux время любого процесса читается</span>'],
        ['ошибка в параметрах', ('<span data-os="win">87</span><span data-os="mac linux">22</span>', 'is-bad'), 'ничего']]),
    'Ноль в колонке «Код» — успех. Номера ошибок — системные: <span data-os="win"><code>ERROR_INVALID_PARAMETER</code> 87 и <code>ERROR_ACCESS_DENIED</code> 5</span><span data-os="mac"><code>ESRCH</code> 3, <code>EPERM</code> 1, <code>EINVAL</code> 22</span><span data-os="linux"><code>ENOENT</code> 2 — нет файла <code>/proc/PID/stat</code>, <code>EINVAL</code> 22</span>.')

PIC_UNITS = V.scheme('В чём система считает время и как перевести в микросекунды',
    V.tab(['Система', 'Что отдаёт', 'Единица', 'В микросекунды'], [
        ['Windows', '<code>FILETIME</code>', '100 нс', '÷ 10'],
        ['macOS', '<code>pti_total_*</code>', 'тик Mach: 41,7 нс на Apple, 1 нс на Intel', '× numer ÷ denom ÷ 1000'],
        ['Linux', 'поля 14, 15 <code>stat</code>', 'тик часов: 10 мс', '× 1 000 000 ÷ 100']]),
    'Единица у каждой системы своя, и ни одна не равна микросекунде. Ошибка в переводе не мешает программе работать: числа выходят в несколько раз больше или меньше настоящих.')

PIC_STEP = V.scheme('Два замера нагрузки с паузой в секунду',
    V.tab(['Система', 'user_us, замер 1', 'user_us, замер 2', 'Прирост за 1 с', 'Шаг счёта'], [
        ['Windows', '265 625', '1 250 000', '984 375 = 98%', '15 625 мкс'],
        ['macOS', '280 351', '1 274 554', '995 944 = 99%', 'доли мкс'],
        ['Linux', '270 000', '1 280 000', '1 010 000 = 101%', '10 000 мкс']]),
    'Числа — с кадров шага 3. В приросте учтено и время ядра системы; у Windows и Linux оно за секунду не изменилось.')

PIC_AI = V.scheme('Одна строка — другая загрузка',
    V.tab(['Система', 'Строка в ядре главы', 'Строка в коде помощника', 'Ядро главы', 'Код помощника'], [
        ['Windows', '<code>QuadPart / 10</code>', '<code>QuadPart / 10000</code>', ('95%', 'is-ok'), ('0%', 'is-bad')],
        ['macOS', '<code>* tb.numer / tb.denom / 1000</code>', '<code>/ 1000</code>', ('99%', 'is-ok'), ('2%', 'is-bad')],
        ['Linux', '<code>hz = sysconf(_SC_CLK_TCK)</code>', '<code>hz = 1000</code>', ('100%', 'is-ok'), ('10%', 'is-bad')]]),
    'Числа — с кадров: одна и та же нагрузка, замер <code>cpu_top</code> с ядром главы и с ядром, где изменена одна строка.')

PIC_CHECK = V.scheme('Что запускает и с чем сравнивает проверка 2',
    V.tab(['Процесс', 'Что делает', 'Условие'], [
        ['нагрузка', 'пустой цикл 7 с', ('от 80 до 120%', 'is-ok')],
        ['спящий процесс', '<code>time.sleep(7)</code>', ('не больше 10%', 'is-ok')],
        ['номер 2147483646', 'процесса нет', ('код ошибки, не 0', 'is-bad')]]),
    'Замер — два вызова <code>core_proc_cpu</code> с паузой 3 секунды; проценты — от одного ядра.')

S = []

S.append(f'''
        <h2 id="s1"><span class="sec">§1</span>Задача главы</h2>
        <p>В ЛР 6 загрузку процессора считали вручную: дважды смотрели процессорное время процесса и делили прирост на паузу. В этой главе то же делает агент. Ядро получает функцию <code>core_proc_cpu</code>: она читает процессорное время процесса по его номеру и возвращает его в микросекундах. Мозг вызывает её для всех процессов дважды с паузой в секунду и находит те, что загружают процессор.</p>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>У трактора есть счётчик моточасов: сколько часов работал двигатель за всю жизнь машины. Чтобы узнать, насколько трактор был занят сегодня, механик записывает показание утром и вечером и вычитает одно из другого.</p>
          <p class="miss">У трактора один двигатель и один счётчик. Процесс может работать на нескольких ядрах сразу, и за секунду его время иногда вырастает больше чем на секунду.</p>
        </div></div>
        <p>Схема показывает путь замера целиком: верхняя строка — один процесс, нижняя — загрузка из двух снимков.</p>
{PIC_FLOW}
        <p>В верхней строке ядро агента берёт у системы счётчик процесса и переводит его в микросекунды. <span class="term">Процессорное время</span> — сколько времени ядра процессора выполняли код процесса за всю его жизнь. Система хранит его двумя числами: время в коде самой программы и время в ядре системы, когда оно работало по просьбе процесса, например читало файл. Нижняя строка — работа мозга: два снимка и разница между ними. Сам счётчик загрузку не показывает, её даёт только прирост за известную паузу.</p>
        <div class="why">
          <p class="why__head">Зачем это нужно в работе</p>
          <ul class="why__list">
            <li><b>Находить виновника.</b> Когда сервер «тормозит», первый вопрос — какой процесс занял процессор. Агент отвечает списком самых занятых процессов.</li>
            <li><b>Различать «работает» и «завис в цикле».</b> Процесс, который должен ждать запросов, а держит ядро на 100%, почти наверняка крутит бесконечный цикл.</li>
            <li><b>Считать честно.</b> Мониторы показывают проценты в разных шкалах, как было видно в ЛР 6. Агент считает загрузку сам по одной формуле, и 100% у него — всегда одно ядро.</li>
          </ul>
        </div>
        <p>Глава продолжает репозиторий <code>sysprog-start</code> после главы 2.2: в <code>agent/core</code> лежат <code>core.h</code>, <code>core_info.c</code>, <code>core_procs.c</code> и <code>core_spawn.c</code>, в <code>agent/brain</code> — <code>brain.py</code> с запуском процессов. <span data-os="win">Команды выполняются во встроенном терминале VS Code, запущенного из окна <b>x64 Native Tools Command Prompt for VS 2022</b>, как в главе 2.2.</span><span data-os="mac linux">Команды выполняются во встроенном терминале VS Code в папке <code>agent/core</code>.</span></p>
        <p class="bridge">Ответ ядра — два числа, поэтому первая часть начинается с их описания в <code>core.h</code>.</p>
''')

CORE_WAS = '''<span class="k">struct</span> core_child {
    <span class="c">…</span>
};

CORE_API <span class="k">int</span> <span class="f">core_spawn</span>(<span class="k">char</span> *<span class="k">const</span> argv[], <span class="k">struct</span> core_child *out);
CORE_API <span class="k">int</span> <span class="f">core_wait</span>(<span class="k">struct</span> core_child *child, <span class="t">int32_t</span> timeout_ms, <span class="t">int32_t</span> *exit_code);'''
CORE_NOW = '''<span class="k">struct</span> core_child {
    <span class="c">…</span>
};
<mark>
<span class="k">struct</span> core_cpu {
    <span class="t">int64_t</span> user_us;
    <span class="t">int64_t</span> kernel_us;
};</mark>

CORE_API <span class="k">int</span> <span class="f">core_spawn</span>(<span class="k">char</span> *<span class="k">const</span> argv[], <span class="k">struct</span> core_child *out);
CORE_API <span class="k">int</span> <span class="f">core_wait</span>(<span class="k">struct</span> core_child *child, <span class="t">int32_t</span> timeout_ms, <span class="t">int32_t</span> *exit_code);
<mark>CORE_API <span class="k">int</span> <span class="f">core_proc_cpu</span>(<span class="t">int64_t</span> pid, <span class="k">struct</span> core_cpu *out);</mark>'''

S.append(f'''
        <div class="part" role="separator"><span><b>1</b>Ядро: время процесса</span></div>
        <h2 id="s2"><span class="sec">§2</span>Шаг 1. Описать время процесса в core.h</h2>
        <p>Ядро отвечает двумя числами: <code>user_us</code> — сколько микросекунд процесс выполнял свой код, <code>kernel_us</code> — сколько микросекунд ядро системы работало по его просьбам. Микросекунда — миллионная доля секунды. Единица одна для трёх систем: мозг складывает и вычитает числа, не зная, откуда они пришли. Оба поля — <code>int64_t</code>: в 8 байт помещается почти 300 тысяч лет в микросекундах.</p>
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
        <p>Структура занимает 16 байт, поля идут подряд:</p>
        {LAYOUT}
        <p>У функции два параметра: <code>pid</code> — номер процесса, <code>out</code> — куда записать ответ. Как остальные функции ядра, она возвращает 0 при успехе и код ошибки системы при неудаче. Все случаи — в таблице:</p>
{PIC_CONTRACT}
        <p>Первая строка — обычный ответ. Вторая и третья случаются постоянно: в списке процессов из главы 2.1 сотни номеров, часть из них завершается раньше замера, часть принадлежит системе. <span data-os="win mac">Чужие процессы <span data-os="win">Windows</span><span data-os="mac">macOS</span> не даёт читать обычному пользователю.</span><span data-os="linux">Linux показывает время любого процесса, поэтому кода «процесс чужой» у этой функции в Linux нет.</span></p>
{shot('01-core-h', dict(
    win=f'{M(1)} Структура времени процесса — два поля. {M(2)} Объявление новой функции.',
    mac=f'{M(1)} Структура времени процесса — два поля. {M(2)} Объявление новой функции.',
    linux=f'{M(1)} Структура времени процесса — два поля. {M(2)} Объявление новой функции.'),
    dict(win='VS Code с core.h: struct core_cpu и объявление core_proc_cpu в рамках', mac='VS Code с core.h: struct core_cpu и объявление core_proc_cpu в рамках',
         linux='VS Code с core.h: struct core_cpu и объявление core_proc_cpu в рамках'))}
        <p class="step-done"><b>Что получилось.</b>В <code>core.h</code> описаны структура на 16 байт и договор функции. Теперь её нужно написать для своей системы.</p>
''')

S.append(f'''
        <h2 id="s3"><span class="sec">§3</span>Шаг 2. Написать core_cpu.c</h2>
        <p>Функция — в новом файле <code>agent/core/core_cpu.c</code>, у каждой системы свой. Время процесса каждая система отдаёт в своих единицах, и функция переводит их в микросекунды:</p>
{PIC_UNITS}
        <p>В каждой строке таблицы — путь от числа системы к микросекундам. Windows считает отрезки по 100 нс, и перевод — деление на 10. macOS считает тики Mach, их длину сообщает сама система дробью <code>numer / denom</code>. Linux считает тики часов ядра, их число в секунде даёт <code>sysconf</code>. Из этого следует правило: единицу нельзя угадывать, её берут из документации или у самой системы.</p>
{cfile('win', 'win', 'agent/core/core_cpu.c · Windows')}
{cfile('mac', 'mac', 'agent/core/core_cpu.c · macOS')}
{cfile('linux', 'linux', 'agent/core/core_cpu.c · Linux')}
{WK['win']}
{WK['mac']}
{WK['linux']}
        <p>Во всех трёх файлах одинаковы проверка параметров и ответ: 0 или код ошибки системы, время — в микросекундах. Различаются вызов системы и единица, в которой она считает время.</p>
        <p class="step-done"><b>Что получилось.</b>Функция чтения времени написана для своей системы. Проверим её программой на C на настоящей нагрузке.</p>
''')

S.append(f'''
        <h2 id="s4"><span class="sec">§4</span>Шаг 3. Проверить ядро на нагрузке</h2>
        <p>Программа <code>agent/core/cpu_top.c</code> одна для трёх систем. Она запускает нагрузку — Python с пустым циклом, как в ЛР 6, — замеряет её время дважды с паузой в секунду и печатает загрузку. Запускает нагрузку <code>core_spawn</code> из главы 2.2.</p>
{cfile('top', 'win mac linux', 'agent/core/cpu_top.c · все системы')}
{WK['top']}
        <p>Собираем программу из трёх файлов и запускаем без параметров:</p>
{cmd('cl /nologo /W4 cpu_top.c core_cpu.c core_spawn.c\ncpu_top.exe',
     'clang -Wall -Wextra -o cpu_top cpu_top.c core_cpu.c core_spawn.c\n./cpu_top',
     'gcc -Wall -Wextra -o cpu_top cpu_top.c core_cpu.c core_spawn.c\n./cpu_top', 'терминал VS Code в agent/core')}
{shot('02-cpu-top', dict(
    win=f'{M(1)} Два замера процесса 3636: время программы 265 625 и 1 250 000 мкс. {M(2)} Прирост 984 375 мкс за секунду — 98%.',
    mac=f'{M(1)} Два замера процесса 45564: время программы 280 351 и 1 274 554 мкс. {M(2)} Прирост 995 944 мкс за секунду — 99%.',
    linux=f'{M(1)} Два замера процесса 321: время программы 270 000 и 1 280 000 мкс. {M(2)} Прирост 1 010 000 мкс за секунду — 101%.'),
    dict(win='терминал: pid 3636 user 265625 и 1250000 us, load 984375 us = 98%', mac='терминал: pid 45564 user 280351 и 1274554 us, load 995944 us = 99%',
         linux='терминал: pid 321 user 270000 и 1280000 us, load 1010000 us = 101%'))}
        <p>За секунду паузы нагрузка получила почти секунду процессорного времени: она занимала одно ядро целиком, как в ЛР 6. Числа трёх систем рядом:</p>
{PIC_STEP}
        <p>По последнему столбцу видно, что система считает время шагами. <span data-os="win">В Windows все числа кратны 15 625 мкс — это 1/64 секунды, шаг системного таймера.</span><span data-os="mac">В macOS числа идут без округления: тики Mach короче микросекунды.</span><span data-os="linux">В Linux все числа кратны 10 000 мкс — один тик часов ядра.</span> Поэтому загрузка за одну секунду может выйти чуть больше 100% или чуть меньше: в Linux лишний тик дал 101%. Чем длиннее пауза между замерами, тем меньше эта погрешность.</p>
        <p class="step-done"><b>Что получилось.</b>Ядро читает время работающего процесса, и загрузка нагрузки близка к 100%. Осталось проверить отказы: процесса нет и процесс чужой.</p>
''')

S.append(f'''
        <h2 id="s5"><span class="sec">§5</span>Шаг 4. Процесса нет и процесс чужой</h2>
        <p>Номер 2147483646 — на единицу меньше самого большого 32-битного числа со знаком. Процесса с таким номером нет ни в одной системе: в Windows номера процессов кратны 4, а в macOS и Linux так далеко не доходят. <span data-os="win">Номер 4 в Windows — процесс System, ядро системы.</span><span data-os="mac linux">Номер 1 — первый процесс системы: <span data-os="mac"><code>launchd</code>, он работает от имени администратора.</span><span data-os="linux">в обычной Linux — <code>systemd</code>, в контейнере этого кадра — <code>sleep</code>, которым контейнер запущен.</span></span> После каждого запуска печатается код завершения <code>cpu_top</code>:</p>
{cmd('cpu_top.exe 2147483646\necho %errorlevel%\ncpu_top.exe 4\necho %errorlevel%',
     './cpu_top 2147483646\necho $?\n./cpu_top 1\necho $?',
     './cpu_top 2147483646\necho $?\n./cpu_top 1\necho $?', 'терминал VS Code в agent/core')}
{shot('03-errors', dict(
    win=f'{M(1)} Процесса нет: код 87. {M(2)} Процесс System: код 5.',
    mac=f'{M(1)} Процесса нет: код 3. {M(2)} Процесс 1: код 1.',
    linux=f'{M(1)} Процесса нет: код 2. {M(2)} Процесс 1 прочитан: 10 000 мкс в своём коде и 10 000 мкс в ядре системы, код завершения 0.'),
    dict(win='терминал: core_proc_cpu: error 87, core_proc_cpu: error 5', mac='терминал: core_proc_cpu: error 3, core_proc_cpu: error 1',
         linux='терминал: core_proc_cpu: error 2, pid 1: user 10000 us, kernel 10000 us'))}
{per(win='<p>87 — <code>ERROR_INVALID_PARAMETER</code>: <code>OpenProcess</code> так отвечает на номер, которого нет. 5 — <code>ERROR_ACCESS_DENIED</code>: даже самое узкое право <code>PROCESS_QUERY_LIMITED_INFORMATION</code> к процессу System обычному пользователю не дают.</p>',
     mac='<p>3 — <code>ESRCH</code>, «No such process». 1 — <code>EPERM</code>, «Operation not permitted»: <code>launchd</code> принадлежит администратору, и сведения о нём обычному пользователю закрыты.</p>',
     linux='<p>2 — <code>ENOENT</code>: нет папки <code>/proc/2147483646</code>, а значит и файла <code>stat</code> в ней. Процесс 1 прочитан: файл <code>/proc/PID/stat</code> открыт для чтения всем пользователям.</p>')}
        <p>Отказы ядро возвращает кодом, и <code>cpu_top</code> завершается с кодом 1. Для агента это обычная ситуация: в списке процессов всегда есть завершившиеся и чужие, и мозг должен их пропускать.</p>
        <p class="step-done"><b>Что получилось.</b>Ядро различает три исхода: время прочитано, процесса нет, процесс недоступен. Можно подключать функцию к мозгу.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>2</b>Мозг: загрузка всех процессов</span></div>
        <h2 id="s6"><span class="sec">§6</span>Шаг 5. Посчитать загрузку в Python</h2>
        <p>Библиотека ядра теперь собирается из четырёх файлов. Программа <code>cpu_top.c</code> в неё не входит: в ней <code>main</code>.</p>
{cmd('cl /nologo /W4 /LD core_info.c core_procs.c core_spawn.c core_cpu.c /Fe:sentry_core.dll',
     'clang -Wall -Wextra -shared -fPIC -o libsentry_core.dylib core_info.c core_procs.c core_spawn.c core_cpu.c',
     'gcc -Wall -Wextra -shared -fPIC -o libsentry_core.so core_info.c core_procs.c core_spawn.c core_cpu.c', 'терминал VS Code в agent/core')}
        <p>В <code>brain.py</code> добавляются класс <code>CoreCpu</code> после <code>CoreProc</code>, типы новой функции после типов <code>core_wait</code> и функции <code>proc_cpu</code> и <code>cpu_load</code> после <code>wait</code>:</p>
        <figure class="code">
          <figcaption><span>agent/brain/brain.py · новые части</span></figcaption>
<pre>{hl_py(BRAIN_PART)}</pre>
        </figure>
{WK['brain']}
        <p>Блок запуска в конце файла меняется: мозг запускает нагрузку — второй Python с пустым циклом на 3 секунды. Пока она работает, мозг считает загрузку всех процессов за секунду, берёт три самых занятых и кладёт их в сообщение под ключом <code>top</code>:</p>
        <figure class="code">
          <figcaption><span>agent/brain/brain.py · блок запуска</span></figcaption>
<pre>{hl_py(BRAIN_MAIN)}</pre>
        </figure>
        <p><code>cpu_load(1.0)[:3]</code> — срез: первые три элемента отсортированного списка. <code>wait(child, 5000)</code> забирает код нагрузки, чтобы она не осталась зомби.</p>
{cmd('cd ..\\brain\npython brain.py', 'cd ../brain\npython3 brain.py', 'cd ../brain\npython3 brain.py', 'терминал VS Code')}
{shot('04-brain', dict(
    win=f'{M(1)} Нагрузка — процесс 296. {M(2)} Первым в списке стоит он: <code>python.exe</code>, 100%. Дальше <code>Taskmgr.exe</code> и <code>Code.exe</code>, по 2%.',
    mac=f'{M(1)} Нагрузка — процесс 46413. {M(2)} Первым в списке стоит он: <code>python3.9</code>, 99%. Дальше <code>Telegram</code> — 27% и <code>incy</code> — 7%.',
    linux=f'{M(1)} Нагрузка — процесс 503. {M(2)} Первым в списке стоит он: <code>python3</code>, 99%. Дальше VS Code — 1% и <code>sleep</code> — 0%.'),
    dict(win='терминал: JSON с child 296 и списком top: python.exe 100, Taskmgr.exe 2, Code.exe 2',
         mac='терминал: JSON с child 46413 и списком top: python3.9 99, Telegram 27, incy 7',
         linux='терминал: JSON с child 503 и списком top: python3 99, code 1, sleep 0'))}
        <p>Мозг нашёл нагрузку сам: из сотен процессов первым оказался тот, номер которого совпадает с <code>child</code>. Остальные строки — обычная жизнь системы: <span data-os="win">Диспетчер задач и VS Code</span><span data-os="mac">мессенджер и другие программы</span><span data-os="linux">сам VS Code и процесс 1 контейнера</span> занимают проценты, но не ядро целиком. Проценты считаются от одного ядра, как в <code>top</code>: процесс с несколькими потоками может показать больше 100%.</p>
        <p class="step-done"><b>Что получилось.</b>Мозг считает загрузку каждого процесса и находит самый занятый. Осталось отправить работу в репозиторий.</p>
''')

S.append(f'''
        <h2 id="s7"><span class="sec">§7</span>Шаг 6. Отправить в репозиторий</h2>
        <p>В репозиторий уходят исходники: <code>core.h</code>, <code>core_cpu.c</code>, <code>cpu_top.c</code> и <code>brain.py</code>. В <code>agent/core/README.md</code> дописываем строку о <code>core_cpu.c</code> и сборке библиотеки из четырёх файлов.</p>
        <figure class="code">
          <figcaption><span>терминал в папке sysprog-start</span><span>то же, что плюс, Commit и Sync Changes</span></figcaption>
<pre>git add agent/core/core.h agent/core/core_cpu.c agent/core/cpu_top.c agent/core/README.md agent/brain/brain.py
git commit -m "core: core_proc_cpu — процессорное время, brain: proc_cpu и cpu_load"
git push</pre>
        </figure>
        <p>Перед <code>git add</code> посмотрите <code>git status</code>: собранную <span data-os="win"><code>cpu_top.exe</code> и файлы <code>.obj</code>, <code>.lib</code>, <code>.exp</code></span><span data-os="mac linux"><code>cpu_top</code></span> допишите в <code>.gitignore</code>, если их там нет.</p>
        <p>После отправки «Проверки» собирают библиотеку из всех файлов <code>agent/core/*.c</code> без <code>main</code> и запускают проверку 2. Она запускает два процесса Python: нагрузку с пустым циклом и спящий процесс. Через секунду она замеряет их время функцией <code>core_proc_cpu</code>, ещё через 3 секунды — снова. Проверка пройдена, если у нагрузки вышло от 80 до 120%, у спящего — не больше 10%, а для номера 2147483646 функция вернула код ошибки.</p>
{PIC_CHECK}
        <p>Каждая строка проверяет свою ошибку. Нагрузка ловит ошибку в единицах: при ней загрузка выходит меньше 80% или больше 120%. Спящий процесс ловит обратную ошибку — когда функция возвращает время, которое растёт само, например время с запуска процесса. Последняя строка проверяет, что для несуществующего процесса функция возвращает код ошибки.</p>
        <p class="step-done"><b>Что получилось.</b>Ядро и мозг с замером процессорного времени в репозитории. Последняя часть — что проверять, если такую функцию пишет помощник ИИ.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>3</b>Код от помощника ИИ</span></div>
        <h2 id="s8"><span class="sec">§8</span>Запрос к помощнику ИИ</h2>
        <p>Функцию чтения времени помощник ИИ пишет быстро, и она работает: компилируется, возвращает 0, числа растут. Ошибка сидит в единицах: число, которое отдала система, переведено в микросекунды не тем множителем. Запрос в режиме Р2 из главы 0.3, когда код целиком пишет помощник:</p>
        <figure class="code">
          <figcaption><span>запрос помощнику</span></figcaption>
<pre>Вот core.h. Напиши core_proc_cpu для <span data-os="win">Windows</span><span data-os="mac">macOS</span><span data-os="linux">Linux</span>: по номеру процесса вернуть
время в пользовательском режиме и в ядре в микросекундах.</pre>
        </figure>
        <p>Такую ошибку видно только на нагрузке с известной загрузкой. Для опыта сделаем копию <code>core_cpu.c</code> с одной изменённой строкой — так, как ошибается код от помощника — и соберём с ней <code>cpu_top</code>:</p>
{cmd('powershell -c "(gc core_cpu.c) -replace \'/ 10\\)\', \'/ 10000)\' | sc ai_cpu.c"\nfc core_cpu.c ai_cpu.c\ncl /nologo /W4 cpu_top.c ai_cpu.c core_spawn.c /Fe:cpu_top_ai.exe\ncpu_top.exe | find "load"\ncpu_top_ai.exe | find "load"',
     "sed 's/ \\* tb.numer \\/ tb.denom//' core_cpu.c > ai_cpu.c\ndiff core_cpu.c ai_cpu.c\nclang -Wall -Wextra -o cpu_top_ai cpu_top.c ai_cpu.c core_spawn.c\n./cpu_top | tail -1\n./cpu_top_ai | tail -1",
     "sed 's/sysconf(_SC_CLK_TCK)/1000/' core_cpu.c > ai_cpu.c\ndiff core_cpu.c ai_cpu.c\ngcc -Wall -Wextra -o cpu_top_ai cpu_top.c ai_cpu.c core_spawn.c\n./cpu_top | tail -1\n./cpu_top_ai | tail -1", 'терминал VS Code в agent/core')}
{per(win='<p>PowerShell читает файл (<code>gc</code>), заменяет <code>/ 10)</code> на <code>/ 10000)</code> и записывает результат (<code>sc</code>). <code>fc</code> сравнивает два файла и печатает различия, <code>find "load"</code> оставляет из вывода только строку с загрузкой.</p>',
     maclinux='<p><code>sed</code> заменяет текст в каждой строке файла, <code>diff</code> печатает различия двух файлов: строки со знаком <code>&lt;</code> — из первого файла, со знаком <code>&gt;</code> — из второго. <code>tail -1</code> оставляет из вывода последнюю строку.</p>')}
{shot('05-units', dict(
    win=f'{M(1)} Файлы отличаются одной строкой: <code>/ 10</code> и <code>/ 10000</code>. {M(2)} Ядро главы: 953 125 мкс за секунду, 95%. {M(3)} Ядро с ошибкой: 1000 мкс, 0%.',
    mac=f'{M(1)} Файлы отличаются двумя строками: из них убрано <code>* tb.numer / tb.denom</code>. {M(2)} Ядро главы: 999 176 мкс за секунду, 99%. {M(3)} Ядро с ошибкой: 24 097 мкс, 2%.',
    linux=f'{M(1)} Файлы отличаются одной строкой: <code>sysconf(_SC_CLK_TCK)</code> и <code>1000</code>. {M(2)} Ядро главы: 1 000 000 мкс за секунду, 100%. {M(3)} Ядро с ошибкой: 100 000 мкс, 10%.'),
    dict(win='терминал: fc с разницей / 10 и / 10000, load 95% и load 0%', mac='терминал: diff без tb.numer / tb.denom, load 99% и load 2%',
         linux='терминал: diff hz = sysconf и hz = 1000, load 100% и load 10%'))}
        <p>Результаты трёх систем сведены в таблицу:</p>
{PIC_AI}
        <p>Нагрузка одна и та же, а загрузка отличается в десятки раз. <span data-os="win">Деление на 10 000 переводит 100 нс в миллисекунды, а поле называется <code>user_us</code>: числа выходят в 1000 раз меньше настоящих.</span><span data-os="mac">Без дроби <code>numer / denom</code> тики считаются наносекундами. На Mac с процессором Intel это верно, поэтому такой код часто встречается в примерах. На процессорах Apple тик длиннее в 125/3 раза, и числа выходят в 41,7 раза меньше.</span><span data-os="linux">Код с <code>hz = 1000</code> считает тик миллисекундой, а он длится 10 мс: числа выходят в 10 раз меньше.</span> Компилятор на такую ошибку не предупреждает, проверка кода возврата её тоже пропускает: функция возвращает 0, и время растёт. Её ловит проверка 2, потому что у нагрузки известная загрузка — около 100%. Подсказка в её отчёте при такой ошибке — «проверьте единицы времени».</p>
        <ul class="checklist">
          <li>единица времени взята из документации или у системы: <span data-os="win">100 нс у <code>FILETIME</code></span><span data-os="mac">дробь из <code>mach_timebase_info</code></span><span data-os="linux">число тиков в секунде из <code>sysconf(_SC_CLK_TCK)</code></span>;</li>
          <li>перевод в микросекунды записан одной формулой, и по ней видно, что умножение стоит раньше деления;</li>
          <li><span data-os="win">дескриптор процесса закрывается на всех путях, и при ошибке тоже;</span><span data-os="mac">ответ <code>proc_pidinfo</code> сравнивается с размером структуры;</span><span data-os="linux">конец имени процесса ищется по последней скобке, функцией <code>strrchr</code>;</span></li>
          <li><code>cpu_top</code> на нагрузке показывает около 100%, а проверка 2 пройдена.</li>
        </ul>
        <p>Первые три пункта проверяются чтением кода, последний — запуском.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>4</b>Справка</span></div>
        <h2 id="s9"><span class="sec">§9</span>Справка: функции и команды</h2>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Что нужно</th><th>Windows</th><th>macOS</th><th>Linux</th></tr></thead>
            <tbody>
              <tr><td>Время процесса</td><td><code>OpenProcess</code> + <code>GetProcessTimes</code></td><td><code>proc_pidinfo(PROC_PIDTASKINFO)</code></td><td>файл <code>/proc/PID/stat</code>, поля 14 и 15</td></tr>
              <tr><td>Единица</td><td>100 нс</td><td>тик Mach, длина — <code>mach_timebase_info</code></td><td>тик часов ядра, 1/<code>sysconf(_SC_CLK_TCK)</code> с</td></tr>
              <tr><td>Шаг счёта на кадрах</td><td>15 625 мкс</td><td>доли мкс</td><td>10 000 мкс</td></tr>
              <tr><td>Процесса нет</td><td>87 <code>ERROR_INVALID_PARAMETER</code></td><td>3 <code>ESRCH</code></td><td>2 <code>ENOENT</code></td></tr>
              <tr><td>Процесс чужой</td><td>5 <code>ERROR_ACCESS_DENIED</code></td><td>1 <code>EPERM</code></td><td>читается</td></tr>
              <tr><td>Загрузка</td><td colspan="3">(время₂ − время₁) ÷ пауза × 100%; 100% — одно ядро целиком</td></tr>
              <tr><td>Собрать библиотеку</td><td><code>cl /LD core_info.c core_procs.c core_spawn.c core_cpu.c</code></td><td><code>clang -shared -fPIC …</code></td><td><code>gcc -shared -fPIC …</code></td></tr>
            </tbody>
          </table>
        </div>

        <div class="part" role="separator"><span><b>5</b>Проверка себя</span></div>
        <h2 id="s10"><span class="sec">§10</span>Частые вопросы</h2>
        <div class="myths">
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Система хранит загрузку процесса в процентах, её достаточно прочитать.</div>
            <div class="myth__yes"><b>На самом деле</b>Система хранит только счётчик процессорного времени за всю жизнь процесса. Проценты мониторы и агент считают сами по двум замерам.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Загрузка процесса не бывает больше 100%.</div>
            <div class="myth__yes"><b>На самом деле</b>100% — одно ядро. Процесс с несколькими потоками на нескольких ядрах за секунду получает больше секунды времени. Даже у одного потока бывает 101% из-за шага счёта, как в Linux на кадре шага 3.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Если функция вернула 0 и время растёт, она написана верно.</div>
            <div class="myth__yes"><b>На самом деле</b>Ошибка в единицах даёт растущие числа, но в 10, 41 или 1000 раз меньше настоящих. Видно её только на нагрузке с известной загрузкой.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Процесс, который не удалось прочитать, — ошибка агента.</div>
            <div class="myth__yes"><b>На самом деле</b>В списке всегда есть процессы, которые завершились между замерами или принадлежат системе. Мозг пропускает их и считает остальные.</div>
          </div>
        </div>

        <h2 id="s11"><span class="sec">§11</span>Проверьте себя</h2>
        <details>
          <summary>Что хранят поля <code>user_us</code> и <code>kernel_us</code>?</summary>
          <p>Сколько микросекунд процесс выполнял свой код и сколько микросекунд ядро системы работало по его просьбам, за всю жизнь процесса.</p>
        </details>
        <details>
          <summary>Почему загрузку нельзя получить одним вызовом <code>core_proc_cpu</code>?</summary>
          <p>Один вызов даёт время с запуска процесса. Загрузка — прирост времени за известную паузу, поэтому нужны два замера и разница между ними.</p>
        </details>
        <details>
          <summary>Как перевести время системы в микросекунды на вашей системе?</summary>
          <p><span data-os="win">Число <code>FILETIME</code> в отрезках по 100 нс разделить на 10.</span><span data-os="mac">Тики Mach умножить на <code>numer</code>, разделить на <code>denom</code> из <code>mach_timebase_info</code> — это наносекунды — и разделить на 1000.</span><span data-os="linux">Тики умножить на 1 000 000 и разделить на <code>sysconf(_SC_CLK_TCK)</code>, обычно 100.</span></p>
        </details>
        <details>
          <summary>Почему в Linux нагрузка за секунду может показать 101%?</summary>
          <p>Время считается тиками по 10 мс. Если за паузу счётчик прибавил 101 тик вместо 100, прирост выходит 1 010 000 мкс. Чем длиннее пауза, тем меньше такая погрешность.</p>
        </details>
        <details>
          <summary>Зачем <code>proc_cpu</code> в мозге возвращает <code>None</code> при ошибке?</summary>
          <p>Среди сотен процессов всегда есть завершившиеся и чужие. Исключение остановило бы весь подсчёт, а <code>None</code> позволяет пропустить такой процесс и посчитать остальные.</p>
        </details>
        <details>
          <summary>Как заметить ошибку в единицах времени?</summary>
          <p>Запустить нагрузку с известной загрузкой — пустой цикл — и замерить её. Должно выйти около 100%. 0, 2 или 10% значат, что перевод в микросекунды сделан не тем множителем.</p>
        </details>

        <h2 id="s12"><span class="sec">§12</span>Шпаргалка по главе</h2>
        <div class="cheat">
          <div><b>Время процесса</b><span><code>struct core_cpu</code>: <code>user_us</code>, <code>kernel_us</code></span><span>16 байт</span></div>
          <div><b>Замер</b><span><code>core_proc_cpu(pid, &amp;cpu)</code></span><span data-os="win"><code>GetProcessTimes</code>, ÷ 10</span><span data-os="mac"><code>proc_pidinfo</code>, × numer ÷ denom ÷ 1000</span><span data-os="linux"><code>/proc/PID/stat</code>, × 10⁶ ÷ hz</span></div>
          <div><b>Загрузка</b><span>(время₂ − время₁) ÷ пауза</span><span>100% — одно ядро</span></div>
          <div><b>Коды</b><span>нет процесса — {NO_PROC}</span><span data-os="win">чужой — 5</span><span data-os="mac">чужой — 1</span><span data-os="linux">чужой читается</span></div>
          <div><b>Мозг</b><span><code>proc_cpu(pid)</code> — мкс или <code>None</code></span><span><code>cpu_load(1.0)</code> — список по убыванию</span></div>
          <div><b>Ошибка ИИ</b><span>не та единица времени</span><span>ловит нагрузка с известной загрузкой</span></div>
        </div>

        <h3>Итог главы</h3>
        <p>Ядро агента получило функцию <code>core_proc_cpu</code>: по номеру процесса она возвращает его процессорное время в микросекундах. <span data-os="win">В Windows время берётся из <code>GetProcessTimes</code> в отрезках по 100 нс.</span><span data-os="mac">В macOS время берётся из <code>proc_pidinfo</code> в тиках Mach и переводится дробью <code>mach_timebase_info</code>.</span><span data-os="linux">В Linux время берётся из полей 14 и 15 файла <code>/proc/PID/stat</code> в тиках по 10 мс.</span> Программа <code>cpu_top.c</code> показала, что нагрузка за секунду получает почти секунду времени, а для несуществующего и чужого процесса ядро возвращает код ошибки. Мозг из двух снимков посчитал загрузку всех процессов и первым нашёл нагрузку. Копия ядра с одной изменённой строкой показала ошибку в единицах: та же нагрузка выглядит загруженной на <span data-os="win">0%</span><span data-os="mac">2%</span><span data-os="linux">10%</span>, и заметить это можно только на нагрузке с известной загрузкой.</p>

        <div class="sources">
          <b>Откуда взяты факты</b>
          <ol>
            <li>Кадры и выводы: macOS 26.1, Apple clang 17, Python 3.9 из Command Line Tools; Linux — контейнер Debian 13, gcc 14.4, Python 3.13; Windows 11 ARM64 в VirtualBox, MSVC 19.44 (ядро и программы собраны для ARM64), Python 3.14 для ARM64; VS Code 1.144.</li>
            <li><code>GetProcessTimes</code>, <code>FILETIME</code>, <code>OpenProcess</code>, <code>PROCESS_QUERY_LIMITED_INFORMATION</code> — <a href="https://learn.microsoft.com/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes">Microsoft Learn, GetProcessTimes</a>; коды 5 и 87 — <a href="https://learn.microsoft.com/windows/win32/debug/system-error-codes--0-499-">System Error Codes</a>.</li>
            <li><code>proc_pidinfo</code>, <code>struct proc_taskinfo</code> — заголовки <code>libproc.h</code> и <code>sys/proc_info.h</code> SDK macOS; <code>mach_timebase_info</code> — <a href="https://developer.apple.com/documentation/driverkit/mach_timebase_info_data_t">Apple Developer, mach_timebase_info_data_t</a>.</li>
            <li>Поля <code>/proc/PID/stat</code>, <code>utime</code> и <code>stime</code> в тиках <code>sysconf(_SC_CLK_TCK)</code> — <a href="https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html">man 5 proc_pid_stat</a>.</li>
          </ol>
        </div>

        <div class="pager">
          <a href="../17-laboratornaya-6/index.html">← ЛР 6 Кто загружает процессор</a>
          <a href="../../index.html">Оглавление</a>
        </div>

        <div class="colophon">
          <span>Глава 2.3 · Процессорное время · Справочник по системному программированию</span>
          <span class="author-line">Автор: Макаров Максим Николаевич</span>
        </div>
''')

CONTENTS = [('s1', 'Задача главы'), ('s2', 'Шаг 1. Описать время процесса в core.h'), ('s3', 'Шаг 2. Написать core_cpu.c'),
            ('s4', 'Шаг 3. Проверить ядро на нагрузке'), ('s5', 'Шаг 4. Процесса нет и процесс чужой'),
            ('s6', 'Шаг 5. Посчитать загрузку в Python'), ('s7', 'Шаг 6. Отправить в репозиторий'), ('s8', 'Запрос к помощнику ИИ'),
            ('s9', 'Справка: функции и команды'), ('s10', 'Частые вопросы'), ('s11', 'Проверьте себя'), ('s12', 'Шпаргалка по главе')]
TOC = '\n'.join(f'            <li><a href="#{a}">{t}</a></li>' for a, t in CONTENTS)

PAGE = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>2.3 Процессорное время · Справочник по системному программированию</title>
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
          <p class="running__folio">2.3</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">2.3</span>
          <h1>Процессорное время</h1>
          <p class="lead">В главе ядро агента получает функцию <code>core_proc_cpu</code>: она читает процессорное время процесса и возвращает его в микросекундах. Разобрано, в каких единицах время считают Windows, macOS и Linux, как их перевести, что отвечает система про несуществующий и чужой процесс и почему загрузка — это прирост времени за паузу. В конце мозг агента находит самый занятый процесс, а копия ядра с одной изменённой строкой показывает ошибку в единицах, которую не видит компилятор.</p>
        </header>

        <dl class="passport">
          <div><dt>Категория</dt><dd>Процессы</dd></div>
          <div><dt>Уровень</dt><dd>Начальный</dd></div>
          <div><dt>Что получится</dt><dd><code>agent/core/core_cpu.c</code>, <code>cpu_top.c</code>, новый <code>brain.py</code></dd></div>
          <div><dt>Сколько занимает</dt><dd>Пара 6, около сорока пяти минут за компьютером</dd></div>
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
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(PAGE)
    print('ok', OUT, len(PAGE))
