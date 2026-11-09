"""Глава 2.2 «Запуск процесса» → temy/16-zapusk-processa/index.html.

Код: tools/src22 (core.h с struct core_child, win/core_spawn.c, posix/core_spawn.c, run_child.c, leak.c, py/brain.py).
Кадры: ~/sysprog-shots/m22 — macOS и Linux снимает shoot22.py (VS Code через протокол отладки, рамки mark.py),
Windows — экран ВМ Win11-lab 800×600 (сети в ВМ нет, файлы с ISO m22.iso, ядро собрано для ARM64), рамки winmark22.py.
Числа в тексте — с кадров (MODUL-2.md)."""
import html
from pathlib import Path

from ch11 import M, cells, hl, per, shot
from ch12 import hl_py, cmd, between
import viz as V
import walk22

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / 'src22'
OUT = ROOT / 'temy/16-zapusk-processa/index.html'


def src(name):
    return (SRC / {'win': 'win/core_spawn.c', 'posix': 'posix/core_spawn.c', 'run': 'run_child.c', 'leak': 'leak.c'}[name]).read_text()


BRAIN = (SRC / 'py/brain.py').read_text()
BRAIN_PART = '\n'.join([between(BRAIN, 'class CoreChild', ']'), '',
                        between(BRAIN, 'core.core_spawn.argtypes', 'core.core_wait.restype'), '',
                        between(BRAIN, 'def spawn', 'return child'), '',
                        between(BRAIN, 'def wait', 'return code.value')])
BRAIN_MAIN = between(BRAIN, 'if __name__')
WK = walk22.build(hl, hl_py, src, BRAIN_PART)


def cfile(name, os_, cap):
    return f'        <figure class="code" data-os="{os_}">\n          <figcaption><span>{cap}</span></figcaption>\n<pre>{hl(src(name))}</pre>\n        </figure>'


LIB = '<span data-os="win"><code>sentry_core.dll</code></span><span data-os="mac"><code>libsentry_core.dylib</code></span><span data-os="linux"><code>libsentry_core.so</code></span>'
TIMEOUT = '<span data-os="win">258</span><span data-os="mac">60</span><span data-os="linux">110</span>'
LAYOUT = cells([('pid', '0 · int64_t', 'w'), ('handle', '8 · int64_t', 'w')])

PIC_FLOW = V.scheme('Путь запуска: от мозга до кода завершения',
    V.steps(V.card('мозг', '<code>spawn([…])</code>', '<small>список: программа и аргументы</small>', 'py'), V.arrow('argv'),
            V.card('ядро агента', '<code>core_spawn</code>', '<small><span data-os="win">CreateProcessW</span><span data-os="mac linux">posix_spawnp</span></small>', 'c'), V.arrow('системный вызов'),
            V.card('система', 'новый процесс', '<small>номер, память, программа</small>', 'sys'), V.arrow('работает'),
            V.card('ребёнок', 'завершается', '<small>оставляет код, например 3</small>', 'py'))
    + V.steps(V.card('ребёнок', 'код 3', '<small>хранится в системе</small>', 'sys'), V.arrow('забирает'),
              V.card('ядро агента', '<code>core_wait</code>', '<small><span data-os="win">WaitForSingleObject, GetExitCodeProcess</span><span data-os="mac linux">waitpid</span></small>', 'c'), V.arrow('code'),
              V.card('мозг', '<code>wait(child)</code>', '<small>возвращает 3</small>', 'py')),
    'Верхняя строка — запуск, нижняя — путь кода завершения обратно к мозгу. Бирюзовые карточки — Python, янтарные — ядро на C, серые — система.')

PIC_CONTRACT = V.scheme('Договор функций: что приходит в ответ',
    V.tab(['Случай', 'Функция', 'Код', 'Что в ответе'], [
        ['программа запущена', '<code>core_spawn</code>', ('0', 'is-ok'), '<code>child.pid</code>, <span data-os="win"><code>child.handle</code></span><span data-os="mac linux"><code>handle</code> = 0</span>'],
        ['программы нет', '<code>core_spawn</code>', ('2', 'is-bad'), 'ничего'],
        ['ребёнок завершился', '<code>core_wait</code>', ('0', 'is-ok'), 'код завершения в <code>exit_code</code>'],
        ['время вышло', '<code>core_wait</code>', (TIMEOUT, 'is-bad'), 'ребёнок работает, ждать можно снова'],
        ['ошибка в параметрах', 'обе', ('<span data-os="win">87</span><span data-os="mac linux">22</span>', 'is-bad'), 'ничего']]),
    'Ноль в колонке «Код» — успех. Код 2 одинаков на трёх системах: <span data-os="win"><code>ERROR_FILE_NOT_FOUND</code></span><span data-os="mac linux"><code>ENOENT</code></span>, «нет такого файла».')

PIC_TWO = V.scheme('Чем держат запущенный процесс',
    V.split(('Windows', V.steps(V.card('', 'CreateProcessW', '<small>ответ: номер и два дескриптора</small>', 'sys'), V.arrow(),
                                V.card('', 'дескриптор потока', '<small>сразу CloseHandle</small>', 'c'), V.arrow(),
                                V.card('', 'дескриптор процесса', '<small>держать до core_wait</small>', 'c'))),
            ('macOS и Linux', V.steps(V.card('', 'posix_spawnp', '<small>ответ: номер процесса</small>', 'sys'), V.arrow(),
                                      V.card('', 'номер процесса', '<small>по нему waitpid</small>', 'c'), V.arrow(),
                                      V.card('', 'waitpid', '<small>забирает код и удаляет запись</small>', 'c'))), rows=True),
    'В обоих случаях запись о завершившемся процессе живёт, пока родитель её не освободит: в Windows — закрытием дескриптора процесса, в macOS и Linux — вызовом <code>waitpid</code>.')

PIC_LEAK = V.scheme('Что остаётся после 20 запусков без core_wait',
    V.tab(['Система', 'До', 'После', 'Что накопилось'], [
        ['Windows, ядро главы', '44 дескриптора', ('72', 'is-bad'), '20 дескрипторов процессов и 8 других'],
        ['Windows, без <code>CloseHandle(pi.hThread)</code>', '44 дескриптора', ('92', 'is-bad'), 'ещё 20 дескрипторов потоков'],
        ['macOS', '0 зомби', ('20', 'is-bad'), '20 записей о завершившихся детях'],
        ['Linux', '0 зомби', ('20', 'is-bad'), '20 записей о завершившихся детях']]),
    'Числа — из запусков <code>leak.c</code> на кадре: Windows 11 в ВМ, macOS 26, Linux в контейнере.')

S = []

S.append(f'''
        <h2 id="s1"><span class="sec">§1</span>Задача главы</h2>
        <p>В ЛР 5 было видно, как родитель запускает программу: просит ядро системы создать процесс, ждёт его завершения и забирает код. В этой главе то же делает ядро агента. Оно получает две функции: <code>core_spawn</code> запускает программу по списку аргументов, <code>core_wait</code> ждёт её завершения и возвращает код. Мозг агента запускает через них программу на Python, находит её в списке процессов из главы 2.1 и получает её код.</p>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>Начальник смены отдаёт заказ в цех: что сделать и из чего. Цех выдаёт номер заказа, а когда заказ готов, сообщает итог: «сделано» или «брак, причина такая-то». Начальник спрашивает о заказе по номеру столько раз, сколько нужно, пока не заберёт итог.</p>
          <p class="miss">Цех не хранит готовые заказы вечно. Процесс тоже: его запись остаётся в системе, пока родитель не заберёт код, и родитель обязан это сделать.</p>
        </div></div>
        <p>Схема показывает путь запуска целиком: мозг передаёт список аргументов ядру агента, ядро агента — системе, а код завершения возвращается тем же путём.</p>
{PIC_FLOW}
        <p>По верхней строке видно, что сам мозг процессы не создаёт: он передаёт список строк функции на C, а та вызывает <span data-os="win"><code>CreateProcessW</code></span><span data-os="mac linux"><code>posix_spawnp</code></span>. Нижняя строка — обратный путь: код 3, который оставил ребёнок, хранится в системе, пока <code>core_wait</code> его не заберёт и не отдаст мозгу. <span class="term">Код завершения</span> — число, которое процесс оставляет при завершении: 0 — успех, остальные числа — ошибки, смысл которых задаёт программа.</p>
        <div class="why">
          <p class="why__head">Зачем это нужно в работе</p>
          <ul class="why__list">
            <li><b>Запускать проверки.</b> Агенты наблюдения запускают системные программы и разбирают их вывод и код. Код завершения — самый короткий ответ «получилось или нет».</li>
            <li><b>Не терять завершившиеся процессы.</b> Программа, которая запускает детей и не забирает их коды, копит в системе записи о них. За сутки работы службы их набираются тысячи.</li>
            <li><b>Ограничивать время.</b> Зависшая программа не должна останавливать агента, поэтому ожидание идёт с пределом времени.</li>
          </ul>
        </div>
        <p>Глава продолжает репозиторий <code>sysprog-start</code> после главы 2.1: в <code>agent/core</code> лежат <code>core.h</code>, <code>core_info.c</code> и <code>core_procs.c</code>, в <code>agent/brain</code> — <code>brain.py</code> со списком процессов. <span data-os="win">Команды выполняются во встроенном терминале VS Code, запущенного из окна <b>x64 Native Tools Command Prompt for VS 2022</b>, как в главах 1.2 и 2.1.</span><span data-os="mac linux">Команды выполняются во встроенном терминале VS Code в папке <code>agent/core</code>.</span></p>
        <p class="bridge">Ядро отвечает о запущенном процессе структурой, поэтому первая часть начинается с её описания в <code>core.h</code>.</p>
''')

CORE_WAS = '''<span class="k">struct</span> core_proc {
    <span class="c">…</span>
};

CORE_API <span class="k">int</span> <span class="f">core_get_info</span>(<span class="k">struct</span> core_info *out);
CORE_API <span class="k">int</span> <span class="f">core_list_procs</span>(<span class="k">struct</span> core_proc *out, <span class="t">int32_t</span> max, <span class="t">int32_t</span> *count);'''
CORE_NOW = '''<span class="k">struct</span> core_proc {
    <span class="c">…</span>
};
<mark>
<span class="k">struct</span> core_child {
    <span class="t">int64_t</span> pid;
    <span class="t">int64_t</span> handle;
};</mark>

CORE_API <span class="k">int</span> <span class="f">core_get_info</span>(<span class="k">struct</span> core_info *out);
CORE_API <span class="k">int</span> <span class="f">core_list_procs</span>(<span class="k">struct</span> core_proc *out, <span class="t">int32_t</span> max, <span class="t">int32_t</span> *count);
<mark>CORE_API <span class="k">int</span> <span class="f">core_spawn</span>(<span class="k">char</span> *<span class="k">const</span> argv[], <span class="k">struct</span> core_child *out);
CORE_API <span class="k">int</span> <span class="f">core_wait</span>(<span class="k">struct</span> core_child *child, <span class="t">int32_t</span> timeout_ms, <span class="t">int32_t</span> *exit_code);</mark>'''

S.append(f'''
        <div class="part" role="separator"><span><b>1</b>Ядро: запуск и ожидание</span></div>
        <h2 id="s2"><span class="sec">§2</span>Шаг 1. Описать запущенный процесс в core.h</h2>
        <p>О запущенном процессе ядро агента запоминает две вещи: номер процесса и <span class="term">дескриптор</span> — номер, по которому Windows даёт работать с объектом системы, например с процессом. В macOS и Linux к процессу обращаются по его номеру, и поле дескриптора там остаётся нулём. Оба поля — <code>int64_t</code>: в номер процесса и в дескриптор Windows помещается 8 байт.</p>
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
        <p>Параметры функций:</p>
        <ul class="words">
          <li><code>argv</code> — список строк: имя программы и её аргументы, в конце <code>NULL</code>. Так же устроен <code>argv</code> в <code>main</code> любой программы на C;</li>
          <li><code>out</code> — куда <code>core_spawn</code> запишет номер и дескриптор нового процесса;</li>
          <li><code>timeout_ms</code> — сколько миллисекунд ждать; −1 — ждать сколько потребуется;</li>
          <li><code>exit_code</code> — куда <code>core_wait</code> запишет код завершения.</li>
        </ul>
        <p>Обе функции, как <code>core_list_procs</code>, возвращают 0 при успехе и код ошибки системы при неудаче. Все случаи — в таблице:</p>
{PIC_CONTRACT}
        <p>Строки таблицы идут в порядке жизни процесса: запуск, ожидание, завершение. Особая строка — «время вышло»: это ошибка ожидания, а сам процесс жив, и его можно ждать снова. Код этой ошибки на трёх системах разный, а «программы нет» везде — 2, как в ЛР 5.</p>
{shot('01-core-h', dict(
    win=f'{M(1)} Структура запущенного процесса — два поля. {M(2)} Объявления двух новых функций.',
    mac=f'{M(1)} Структура запущенного процесса — два поля. {M(2)} Объявления двух новых функций.',
    linux=f'{M(1)} Структура запущенного процесса — два поля. {M(2)} Объявления двух новых функций.'),
    dict(win='VS Code с core.h: struct core_child и объявления core_spawn и core_wait в рамках', mac='VS Code с core.h: struct core_child и объявления core_spawn и core_wait в рамках',
         linux='VS Code с core.h: struct core_child и объявления core_spawn и core_wait в рамках'))}
        <p class="step-done"><b>Что получилось.</b>В <code>core.h</code> описаны структура на 16 байт и договор двух функций. Теперь их нужно написать для своей системы.</p>
''')

S.append(f'''
        <h2 id="s3"><span class="sec">§3</span>Шаг 2. Написать core_spawn.c</h2>
        <p>Обе функции — в новом файле <code>agent/core/core_spawn.c</code>. Для macOS и Linux файл один: <code>posix_spawnp</code> и <code>waitpid</code> есть в обеих системах. Windows отвечает на запуск иначе, и от этого зависит, как ядро держит процесс:</p>
{PIC_TWO}
        <p>Верхняя ветка — Windows: <code>CreateProcessW</code> возвращает номер процесса и два дескриптора, потока и процесса. Дескриптор потока ядру агента не нужен и закрывается сразу, дескриптор процесса хранится до <code>core_wait</code>. Нижняя ветка — macOS и Linux: в ответ приходит только номер, и по нему <code>waitpid</code> забирает код. Последняя карточка каждой ветки — шаг, без которого система не освобождает запись о процессе. В части 3 видно, что бывает, если этот шаг пропустить.</p>
{cfile('win', 'win', 'agent/core/core_spawn.c · Windows')}
{cfile('posix', 'mac linux', 'agent/core/core_spawn.c · macOS и Linux')}
{WK['win']}
{WK['posix']}
        <p>В обоих файлах одинаковы проверка параметров и ответ: 0 или код ошибки системы. Различается, как система запускает процесс и как сообщает о его завершении: <span data-os="win">Windows будит ожидающий поток, когда процесс завершился</span><span data-os="mac linux">ядро агента само спрашивает систему каждые 10 мс</span>.</p>
        <p class="step-done"><b>Что получилось.</b>Функции запуска и ожидания написаны для своей системы. Проверим их программой на C, прежде чем вызывать из Python.</p>
''')

S.append(f'''
        <h2 id="s4"><span class="sec">§4</span>Шаг 3. Проверить ядро программой на C</h2>
        <p>Программа <code>agent/core/run_child.c</code> одна для трёх систем: она берёт из командной строки время ожидания и запускаемую программу, вызывает обе функции ядра и печатает результат.</p>
{cfile('run', 'win mac linux', 'agent/core/run_child.c · все системы')}
{WK['run']}
        <p>Собираем программу из двух файлов и запускаем вторую оболочку, которая сразу завершается с кодом 7:</p>
{cmd('cl /nologo /W4 run_child.c core_spawn.c\nrun_child.exe 5000 cmd /c exit 7',
     'clang -Wall -Wextra -o run_child run_child.c core_spawn.c\n./run_child 5000 sh -c "exit 7"',
     'gcc -Wall -Wextra -o run_child run_child.c core_spawn.c\n./run_child 5000 sh -c "exit 7"', 'терминал VS Code в agent/core')}
{per(win='<p>Строки компоновщика «Создается библиотека run_child.lib и объект run_child.exp» появляются, потому что функции ядра помечены <code>CORE_API</code>, то есть <code>__declspec(dllexport)</code>. Для программы <code>.exe</code> эти файлы не нужны, их можно удалить.</p>')}
{shot('02-run', dict(
    win=f'{M(1)} Процесс запущен, номер 8952. {M(2)} Он завершился с кодом 7.',
    mac=f'{M(1)} Процесс запущен, номер 88026. {M(2)} Он завершился с кодом 7.',
    linux=f'{M(1)} Процесс запущен, номер 308. {M(2)} Он завершился с кодом 7.'),
    dict(win='терминал: started pid 8952, pid 8952 exited, code 7', mac='терминал: started pid 88026, pid 88026 exited, code 7',
         linux='терминал: started pid 308, pid 308 exited, code 7'))}
        <p>Строка {M(1)} напечатана сразу после <code>core_spawn</code>: процесс уже создан и получил номер. Строка {M(2)} — после <code>core_wait</code>: ребёнок завершился, и его код 7 дошёл до программы на C. Это та же цепочка, что в шаге 3 ЛР 5, только родитель теперь — ядро агента.</p>
        <p class="step-done"><b>Что получилось.</b>Ядро запускает программу и получает её код. Осталось проверить два отказа: ребёнок работает дольше отведённого времени, и программы нет.</p>
''')

S.append(f'''
        <h2 id="s5"><span class="sec">§5</span>Шаг 4. Время вышло и программы нет</h2>
        <p>Первая команда запускает ребёнка, который работает около 2 секунд, и даёт ему 300 мс. Вторая запускает программу <code>nosuch</code>, которой нет. После каждой печатается код завершения <code>run_child</code>:</p>
{cmd('run_child.exe 300 cmd /c "ping -n 3 127.0.0.1 >nul"\necho %errorlevel%\nrun_child.exe 1000 nosuch\necho %errorlevel%',
     './run_child 300 sleep 2\necho $?\n./run_child 1000 nosuch\necho $?',
     './run_child 300 sleep 2\necho $?\n./run_child 1000 nosuch\necho $?', 'терминал VS Code в agent/core')}
{per(win='<p><code>ping -n 3</code> трижды проверяет связь с этим же компьютером с паузой в секунду, <code>&gt;nul</code> убирает его вывод. Аргумент с пробелами взят в кавычки, и <code>core_spawn</code> передаёт его тоже в кавычках.</p>',
     maclinux='<p><code>sleep 2</code> ждёт 2 секунды и ничего не делает.</p>')}
{shot('03-errors', dict(
    win=f'{M(1)} Время вышло: код 258, процесс 4664 работает. {M(2)} Программы нет: код 2.',
    mac=f'{M(1)} Время вышло: код 60, процесс 88235 работает. {M(2)} Программы нет: код 2.',
    linux=f'{M(1)} Время вышло: код 110, процесс 348 работает. {M(2)} Программы нет: код 2.'),
    dict(win='терминал: core_wait: error 258, pid 4664 still running; core_spawn: error 2', mac='терминал: core_wait: error 60, pid 88235 still running; core_spawn: error 2',
         linux='терминал: core_wait: error 110, pid 348 still running; core_spawn: error 2'))}
{per(win='<p>258 — <code>WAIT_TIMEOUT</code>: <code>WaitForSingleObject</code> не дождался процесса. 2 — <code>ERROR_FILE_NOT_FOUND</code>: <code>CreateProcessW</code> не нашла <code>nosuch.exe</code> ни в одной папке поиска.</p>',
     mac='<p>60 — <code>ETIMEDOUT</code> в macOS, «Operation timed out». 2 — <code>ENOENT</code>: <code>posix_spawnp</code> не нашла <code>nosuch</code> ни в одной папке <code>PATH</code>.</p>',
     linux='<p>110 — <code>ETIMEDOUT</code> в Linux, «Connection timed out»: у одной и той же ошибки в двух системах разные номера. 2 — <code>ENOENT</code>: <code>posix_spawnp</code> не нашла <code>nosuch</code> ни в одной папке <code>PATH</code>.</p>')}
        <p>После отказа ожидания процесс продолжает работать: <code>run_child</code> завершилась, а ребёнок ещё секунду-две работает сам и становится сиротой, как в ЛР 4. Во втором случае процесса не было вовсе, поэтому печатать нечего, кроме кода. Обе программы завершились с кодом 1: так <code>run_child</code> сообщает о любой ошибке.</p>
        <p class="step-done"><b>Что получилось.</b>Ядро различает три исхода: код ребёнка, «время вышло» и «программы нет». Можно подключать функции к мозгу.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>2</b>Мозг: запуск из Python</span></div>
        <h2 id="s6"><span class="sec">§6</span>Шаг 5. Запустить процесс из Python</h2>
        <p>Библиотека ядра теперь собирается из трёх файлов. Программа <code>run_child.c</code> в неё не входит: в ней <code>main</code>.</p>
{cmd('cl /nologo /W4 /LD core_info.c core_procs.c core_spawn.c /Fe:sentry_core.dll',
     'clang -Wall -Wextra -shared -fPIC -o libsentry_core.dylib core_info.c core_procs.c core_spawn.c',
     'gcc -Wall -Wextra -shared -fPIC -o libsentry_core.so core_info.c core_procs.c core_spawn.c', 'терминал VS Code в agent/core')}
        <p>В <code>brain.py</code> добавляются класс <code>CoreChild</code> после <code>CoreProc</code>, типы новых функций после типов <code>core_list_procs</code> и функции <code>spawn</code> и <code>wait</code> после <code>parents</code>:</p>
        <figure class="code">
          <figcaption><span>agent/brain/brain.py · новые части</span></figcaption>
<pre>{hl_py(BRAIN_PART)}</pre>
        </figure>
{WK['brain']}
        <p>Блок запуска в конце файла меняется: мозг запускает ребёнка — второй Python, который ждёт секунду и завершается с кодом 3. Пока ребёнок работает, мозг берёт список процессов и строит цепочку родителей уже от ребёнка, а затем ждёт его код не дольше 5 секунд:</p>
        <figure class="code">
          <figcaption><span>agent/brain/brain.py · блок запуска</span></figcaption>
<pre>{hl_py(BRAIN_MAIN)}</pre>
        </figure>
        <p><code>sys.executable</code> — полный путь к интерпретатору Python, который выполняет <code>brain.py</code>: ребёнок запускается тем же Python. <code>raise SystemExit(3)</code> завершает программу с кодом 3.</p>
{cmd('cd ..\\brain\npython brain.py', 'cd ../brain\npython3 brain.py', 'cd ../brain\npython3 brain.py', 'терминал VS Code')}
{shot('04-brain', dict(
    win=f'{M(1)} Ребёнок — процесс 4448, его код 3. {M(2)} Цепочка родителей ребёнка: <code>python.exe</code> ребёнка, <code>python.exe</code> мозга, <code>cmd.exe</code> терминала, два <code>Code.exe</code>, <code>cmd.exe</code> и <code>explorer.exe</code>.',
    mac=f'{M(1)} Функции <code>spawn</code> и <code>wait</code>. {M(2)} Ребёнок — процесс 88861, его код 3. {M(3)} Цепочка родителей ребёнка: <code>python3.9</code> ребёнка, <code>Python</code> мозга, <code>zsh</code>, VS Code, <code>launchd</code>, <code>kernel_task</code>.',
    linux=f'{M(1)} Функции <code>spawn</code> и <code>wait</code>. {M(2)} Ребёнок — процесс 484, его код 3. {M(3)} Цепочка родителей ребёнка: два <code>python3</code>, <code>bash</code>, два процесса VS Code и <code>sleep</code> — процесс 1 контейнера.'),
    dict(win='терминал: JSON с child 4448, child_code 3 и цепочкой parents', mac='brain.py с функциями spawn и wait, в терминале child 88861, child_code 3 и цепочка parents',
         linux='brain.py с функциями spawn и wait, в терминале child 484, child_code 3 и цепочка parents'))}
        <p>Первые два имени цепочки — ребёнок и сам мозг: ребёнка запустило ядро агента, загруженное в процесс мозга, поэтому родитель ребёнка — процесс Python с <code>brain.py</code>. Дальше идёт та же цепочка, что в главе 2.1: терминал, VS Code и процессы системы.</p>
{per(mac='<p>Имена ребёнка и мозга разные: команда <code>python3</code> в этом терминале — короткий запускатель, который запускает интерпретатор <code>Python</code>. <code>sys.executable</code> указывает на сам интерпретатор <code>python3.9</code>, его и запускает ядро агента.</p>')}
        <p class="step-done"><b>Что получилось.</b>Мозг запускает программу через ядро, находит её в списке процессов своим ребёнком и получает её код. Осталось отправить работу в репозиторий.</p>
''')

S.append(f'''
        <h2 id="s7"><span class="sec">§7</span>Шаг 6. Отправить в репозиторий</h2>
        <p>В репозиторий уходят исходники: <code>core.h</code>, <code>core_spawn.c</code>, <code>run_child.c</code> и <code>brain.py</code>. В <code>agent/core/README.md</code> дописываем строку о <code>core_spawn.c</code> и сборке библиотеки из трёх файлов.</p>
        <figure class="code">
          <figcaption><span>терминал в папке sysprog-start</span><span>то же, что плюс, Commit и Sync Changes</span></figcaption>
<pre>git add agent/core/core.h agent/core/core_spawn.c agent/core/run_child.c agent/core/README.md agent/brain/brain.py
git commit -m "core: core_spawn и core_wait — запуск процесса, brain: spawn и wait"
git push</pre>
        </figure>
        <p>Перед <code>git add</code> посмотрите <code>git status</code>: если в списке есть собранная <span data-os="win"><code>run_child.exe</code> или <code>run_child.lib</code></span><span data-os="mac linux"><code>run_child</code></span>, допишите её в <code>.gitignore</code>. После отправки «Проверки» собирают библиотеку из всех файлов <code>agent/core/*.c</code> без <code>main</code>, теперь вместе с <code>core_spawn.c</code>, и проверка 1 из главы 2.1 проходит на новой библиотеке.</p>
        <p class="step-done"><b>Что получилось.</b>Ядро и мозг с запуском процессов в репозитории. Последняя часть — что проверять, если код запуска пишет помощник ИИ.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>3</b>Код от помощника ИИ</span></div>
        <h2 id="s8"><span class="sec">§8</span>Запрос к помощнику ИИ</h2>
        <p>Код запуска процесса помощник ИИ пишет быстро и обычно рабочий: программа запускается, код приходит. Ошибка проявляется через много запусков: система копит записи о процессах, которые никто не освободил. Запрос в режиме Р2 из главы 0.3, когда код целиком пишет помощник:</p>
        <figure class="code">
          <figcaption><span>запрос помощнику</span></figcaption>
<pre>Вот core.h. Напиши core_spawn и core_wait для <span data-os="win">Windows</span><span data-os="mac">macOS</span><span data-os="linux">Linux</span>: запустить программу по argv,
вернуть номер процесса, дождаться завершения с пределом времени и вернуть код завершения.</pre>
        </figure>
        <p>Проверить такой код помогает программа <code>leak.c</code>: она 20 раз запускает короткую программу через <code>core_spawn</code> и ни разу не вызывает <code>core_wait</code>. До и после запусков она печатает, сколько у неё <span data-os="win">открытых дескрипторов — функция <code>GetProcessHandleCount</code></span><span data-os="mac linux">детей-зомби. <span class="term">Зомби</span> — завершившийся процесс, код которого родитель ещё не забрал: от процесса осталась только запись в системе с номером и кодом. Программа считает их по выводу <code>ps</code>: у зомби в столбце состояния буква <code>Z</code></span>.</p>
{cfile('leak', 'win mac linux', 'agent/core/leak.c · все системы')}
{cmd('cl /nologo /W4 leak.c core_spawn.c\nleak.exe',
     'clang -Wall -Wextra -o leak leak.c core_spawn.c\n./leak', 'gcc -Wall -Wextra -o leak leak.c core_spawn.c\n./leak', 'терминал VS Code в agent/core')}
{per(win='<p>Для сравнения собрана вторая программа, <code>leak_ai.exe</code>, с ядром, где пропущена строка <code>CloseHandle(pi.hThread)</code> — частая ошибка в коде от помощника. Файл <code>ai_spawn.c</code> получен из <code>core_spawn.c</code> командой <code>findstr /v /c:"CloseHandle(pi.hThread)" core_spawn.c &gt; ai_spawn.c</code>: <code>findstr /v</code> оставляет все строки, кроме найденной.</p>')}
{shot('05-leak', dict(
    win=f'{M(1)} Ядро главы: было 44 дескриптора, стало 72. {M(2)} Ядро без <code>CloseHandle(pi.hThread)</code>: было 44, стало 92.',
    mac=f'{M(1)} 20 запусков без <code>core_wait</code>. {M(2)} Зомби: было 0, стало 20.',
    linux=f'{M(1)} 20 запусков без <code>core_wait</code>. {M(2)} Зомби: было 0, стало 20.'),
    dict(win='терминал: leak.exe handles 44 и 72, leak_ai.exe handles 44 и 92', mac='leak.c с циклом core_spawn, в терминале zombies 0 и zombies 20',
         linux='leak.c с циклом core_spawn, в терминале zombies 0 и zombies 20'))}
        <p>Числа с кадров всех трёх систем сведены в таблицу:</p>
{PIC_LEAK}
        <p>Каждый запуск без ожидания оставляет в системе след. <span data-os="win">В Windows это открытый дескриптор процесса: 20 запусков — 20 дескрипторов процессов. Ещё 8 дескрипторов программа открыла по ходу работы для своих нужд. Если ядро вдобавок не закрывает дескриптор потока, на каждый запуск остаётся два дескриптора, и рост вдвое больше: 48 против 28.</span><span data-os="mac linux">В macOS и Linux это зомби: ребёнок завершился, а запись о нём остаётся до вызова <code>waitpid</code>. 20 запусков — 20 зомби.</span> Записи исчезают, только когда завершается сам родитель. Агент работает неделями, поэтому у него они копятся без конца.</p>
        <ul class="checklist">
          <li><span data-os="win">после <code>CreateProcessW</code> дескриптор потока закрывается, а дескриптор процесса — после того, как код прочитан;</span><span data-os="mac linux">после <code>posix_spawnp</code> на каждом пути кода есть <code>waitpid</code>, иначе ребёнок станет зомби;</span></li>
          <li>ожидание идёт с пределом времени, и «время вышло» возвращается отдельным кодом, отличным от нуля;</li>
          <li>код ребёнка разбирается: <span data-os="win"><code>GetExitCodeProcess</code> после <code>WaitForSingleObject</code></span><span data-os="mac linux">через <code>WIFEXITED</code> и <code>WEXITSTATUS</code>: в числе <code>status</code> код упакован вместе с другими сведениями</span>;</li>
          <li><code>leak.c</code> после 20 запусков с <code>core_wait</code> показывает то же число, что до них.</li>
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
              <tr><td>Запустить программу</td><td><code>CreateProcessW</code></td><td colspan="2"><code>posix_spawnp</code> (под ним копия процесса и <code>execve</code>)</td></tr>
              <tr><td>Чем держат процесс</td><td>дескриптор процесса</td><td colspan="2">номер процесса</td></tr>
              <tr><td>Дождаться</td><td><code>WaitForSingleObject</code></td><td colspan="2"><code>waitpid</code>, с <code>WNOHANG</code> — без ожидания</td></tr>
              <tr><td>Код завершения</td><td><code>GetExitCodeProcess</code></td><td colspan="2"><code>WIFEXITED</code>, <code>WEXITSTATUS</code>; сигнал — <code>128 + WTERMSIG</code></td></tr>
              <tr><td>Освободить запись</td><td><code>CloseHandle</code> дескриптора процесса</td><td colspan="2"><code>waitpid</code></td></tr>
              <tr><td>«Время вышло»</td><td>258 <code>WAIT_TIMEOUT</code></td><td>60 <code>ETIMEDOUT</code></td><td>110 <code>ETIMEDOUT</code></td></tr>
              <tr><td>«Программы нет»</td><td>2 <code>ERROR_FILE_NOT_FOUND</code></td><td colspan="2">2 <code>ENOENT</code></td></tr>
              <tr><td>Собрать библиотеку</td><td><code>cl /LD core_info.c core_procs.c core_spawn.c</code></td><td><code>clang -shared -fPIC …</code></td><td><code>gcc -shared -fPIC …</code></td></tr>
            </tbody>
          </table>
        </div>

        <div class="part" role="separator"><span><b>5</b>Проверка себя</span></div>
        <h2 id="s10"><span class="sec">§10</span>Частые вопросы</h2>
        <div class="myths">
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Завершившийся процесс исчезает из системы сразу.</div>
            <div class="myth__yes"><b>На самом деле</b>Запись о нём с кодом завершения остаётся, пока родитель её не освободит: закроет дескриптор в Windows или вызовет <code>waitpid</code> в macOS и Linux. В шаге <code>leak.c</code> таких записей набралось 20.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Если время ожидания вышло, ребёнок завершён.</div>
            <div class="myth__yes"><b>На самом деле</b>Ребёнок продолжает работать. В шаге 4 <code>run_child</code> завершилась, а процесс с <span data-os="win"><code>ping</code></span><span data-os="mac linux"><code>sleep</code></span> работал дальше.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Код ошибки «время вышло» одинаков на всех системах.</div>
            <div class="myth__yes"><b>На самом деле</b>258 в Windows, 60 в macOS, 110 в Linux. Одинаков на трёх системах только код 2, «нет такого файла».</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Чтобы запустить программу, ей передают одну строку команды.</div>
            <div class="myth__yes"><b>На самом деле</b>В macOS и Linux программа получает список аргументов. В Windows — одну строку, и ядро агента склеивает её из списка, беря в кавычки аргументы с пробелами.</div>
          </div>
        </div>

        <h2 id="s11"><span class="sec">§11</span>Проверьте себя</h2>
        <details>
          <summary>Какого размера <code>struct core_child</code> и что в её полях на каждой системе?</summary>
          <p>16 байт: номер процесса и дескриптор, по 8 байт. В Windows <code>handle</code> — дескриптор процесса от <code>CreateProcessW</code>, в macOS и Linux — 0.</p>
        </details>
        <details>
          <summary>Почему в Windows дескриптор потока закрывают сразу после запуска, а дескриптор процесса — нет?</summary>
          <p>Поток ядру агента не нужен. Дескриптор процесса нужен <code>core_wait</code>: по нему ждут процесс и читают код завершения. Его закрывают после того, как код прочитан.</p>
        </details>
        <details>
          <summary>Что делает флаг <code>WNOHANG</code> в <code>waitpid</code>?</summary>
          <p>Вызов отвечает сразу: номер ребёнка, если он завершился, или 0, если ещё работает. Поэтому <code>core_wait</code> может ждать с пределом времени, спрашивая каждые 10 мс.</p>
        </details>
        <details>
          <summary>Что вернёт <code>core_wait</code>, если ребёнка убили сигналом 9?</summary>
          <p>0, а в <code>exit_code</code> — 137: процесс завершён сигналом, и ядро агента записывает <code>128 + 9</code>, как оболочки. Проверка — <code>run_child 2000 sh -c 'kill -9 $$'</code> в macOS или Linux.</p>
        </details>
        <details>
          <summary>Что такое зомби и как его убрать?</summary>
          <p>Завершившийся процесс, код которого родитель не забрал. Убирает его родитель вызовом <code>waitpid</code>. Если родитель завершился, зомби достаётся новому родителю, и тот его забирает.</p>
        </details>
        <details>
          <summary>Почему первые два имени в цепочке родителей ребёнка — Python?</summary>
          <p>Ребёнок — второй Python, а запустило его ядро агента, загруженное в процесс мозга. Ядро работает внутри Python, поэтому родитель ребёнка — процесс Python с <code>brain.py</code>.</p>
        </details>

        <h2 id="s12"><span class="sec">§12</span>Шпаргалка по главе</h2>
        <div class="cheat">
          <div><b>Запущенный процесс</b><span><code>struct core_child</code>: <code>pid</code>, <code>handle</code></span><span>16 байт</span></div>
          <div><b>Запуск</b><span><code>core_spawn(argv, &amp;child)</code></span><span data-os="win"><code>CreateProcessW</code>, поток закрыть сразу</span><span data-os="mac linux"><code>posix_spawnp</code></span></div>
          <div><b>Ожидание</b><span><code>core_wait(&amp;child, ms, &amp;code)</code></span><span data-os="win"><code>WaitForSingleObject</code> + <code>GetExitCodeProcess</code></span><span data-os="mac linux"><code>waitpid</code> с <code>WNOHANG</code></span></div>
          <div><b>Коды</b><span>нет программы — 2</span><span>время вышло — {TIMEOUT}</span></div>
          <div><b>Мозг</b><span><code>spawn([…])</code> — процесс</span><span><code>wait(child, 5000)</code> — код</span></div>
          <div><b>Утечка</b><span>запуск без ожидания</span><span data-os="win">открытые дескрипторы</span><span data-os="mac linux">зомби</span></div>
        </div>

        <h3>Итог главы</h3>
        <p>Ядро агента получило две функции. <code>core_spawn</code> запускает программу по списку аргументов: в Windows — <code>CreateProcessW</code> по командной строке, склеенной из списка, в macOS и Linux — <code>posix_spawnp</code>. <code>core_wait</code> ждёт ребёнка с пределом времени и возвращает его код: в Windows через дескриптор процесса, в macOS и Linux через <code>waitpid</code>. Программа <code>run_child.c</code> показала три исхода: код 7, «время вышло» с кодом {TIMEOUT} и «программы нет» с кодом 2. Мозг запустил второй Python, увидел его своим ребёнком в списке процессов и получил код 3. Программа <code>leak.c</code> показала, что запуск без ожидания оставляет в системе след: <span data-os="win">20 дескрипторов процессов, а без <code>CloseHandle(pi.hThread)</code> — ещё 20 дескрипторов потоков</span><span data-os="mac linux">20 зомби</span>.</p>

        <div class="sources">
          <b>Откуда взяты факты</b>
          <ol>
            <li>Кадры и выводы: macOS 26.1, Apple clang 17, Python 3.9 из Command Line Tools; Linux — контейнер Debian 13, gcc 14.4, Python 3.13; Windows 11 ARM64 в VirtualBox, MSVC 19.44 (ядро и программы собраны для ARM64), Python 3.14 для ARM64; VS Code 1.144. Код также проверен на windows-latest в GitHub Actions (x64).</li>
            <li><code>CreateProcessW</code>, порядок поиска программы, <code>PROCESS_INFORMATION</code> — <a href="https://learn.microsoft.com/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw">Microsoft Learn, CreateProcessW</a>; <code>WaitForSingleObject</code>, <code>GetExitCodeProcess</code>, <code>GetProcessHandleCount</code> — Microsoft Learn; коды 2, 87, 258 — <a href="https://learn.microsoft.com/windows/win32/debug/system-error-codes--0-499-">System Error Codes</a>.</li>
            <li><code>posix_spawnp</code> — <a href="https://man7.org/linux/man-pages/man3/posix_spawn.3.html">man 3 posix_spawn</a>; <code>waitpid</code>, <code>WNOHANG</code>, <code>WIFEXITED</code>, зомби — <a href="https://man7.org/linux/man-pages/man2/wait.2.html">man 2 wait</a>.</li>
            <li><code>ETIMEDOUT</code> 60 и 110 — <code>sys/errno.h</code> SDK macOS и <a href="https://man7.org/linux/man-pages/man3/errno.3.html">man 3 errno</a>.</li>
          </ol>
        </div>

        <div class="pager">
          <a href="../15-laboratornaya-5/index.html">← ЛР 5 Рождение процесса</a>
          <a href="../../index.html">Оглавление</a>
        </div>

        <div class="colophon">
          <span>Глава 2.2 · Запуск процесса · Справочник по системному программированию</span>
          <span class="author-line">Автор: Макаров Максим Николаевич</span>
        </div>
''')

CONTENTS = [('s1', 'Задача главы'), ('s2', 'Шаг 1. Описать запущенный процесс в core.h'), ('s3', 'Шаг 2. Написать core_spawn.c'),
            ('s4', 'Шаг 3. Проверить ядро программой на C'), ('s5', 'Шаг 4. Время вышло и программы нет'),
            ('s6', 'Шаг 5. Запустить процесс из Python'), ('s7', 'Шаг 6. Отправить в репозиторий'), ('s8', 'Запрос к помощнику ИИ'),
            ('s9', 'Справка: функции и команды'), ('s10', 'Частые вопросы'), ('s11', 'Проверьте себя'), ('s12', 'Шпаргалка по главе')]
TOC = '\n'.join(f'            <li><a href="#{a}">{t}</a></li>' for a, t in CONTENTS)

PAGE = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>2.2 Запуск процесса · Справочник по системному программированию</title>
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
          <p class="running__folio">2.2</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">2.2</span>
          <h1>Запуск процесса</h1>
          <p class="lead">В главе ядро агента получает функции <code>core_spawn</code> и <code>core_wait</code>: первая запускает программу, вторая ждёт её завершения и возвращает код. Разобрано, как запуск устроен в Windows и в macOS и Linux, чем ядро держит запущенный процесс, что делать, когда время вышло или программы нет, и что остаётся в системе, если код не забрать. В конце мозг агента запускает программу и находит её своим ребёнком в списке процессов.</p>
        </header>

        <dl class="passport">
          <div><dt>Категория</dt><dd>Процессы</dd></div>
          <div><dt>Уровень</dt><dd>Начальный</dd></div>
          <div><dt>Что получится</dt><dd><code>agent/core/core_spawn.c</code>, <code>run_child.c</code>, новый <code>brain.py</code></dd></div>
          <div><dt>Сколько занимает</dt><dd>Пара 5, около сорока пяти минут за компьютером</dd></div>
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
