"""Лабораторная работа 9 «Разбор падения» → temy/22-laboratornaya-9/index.html.

Кадры: macOS и Linux — VS Code с развёрнутым терминалом (~/sysprog-shots/m9/shoot9.py: macOS — clang 17, Linux — контейнер
sp-lab2-linux, gcc 14 и libasan), рамки m9/mark.py. Windows — ВМ Win11-lab ARM64 (MSVC без AddressSanitizer: /fsanitize=address
для ARM64 нет, x64-сборка под эмуляцией падает), рамки m9/winmark9.py; вывод AddressSanitizer для Windows — запуск на windows-latest x64
в GitHub Actions (src_lab9/win_asan_log.txt). Программы — tools/src_lab9 (crash.c, ctypes_crash.py). Числа — с кадров (MODUL-2.md)."""
import html
from pathlib import Path
from ch11 import hl
from ch12 import hl_py
from lab_build import steps
import snaps
import viz as V

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / 'src_lab9'
OUT = ROOT / 'temy/22-laboratornaya-9/index.html'
LAB = '09-crash'


def mk(n):
    return f'<span class="mk">{n}</span>'


def file(name, py=False):
    code = (SRC / name).read_text()
    return (f'        <figure class="code"><figcaption><span>labs/{LAB}/{name}</span></figcaption>\n'
            f'<pre>{hl_py(code) if py else hl(code)}</pre>\n        </figure>')


def win_asan():
    lines = (SRC / 'win_asan_log.txt').read_text(encoding='utf-8').splitlines()
    keep = [l for l in lines if l.startswith(('==', 'WRITE of', 'READ of', 'freed by', 'SUMMARY'))
            or ('crash.c:' in l and ('heap_overflow' in l or 'use_after_free' in l))]
    keep = [l.replace('D:\\a\\sysprog-win-shots\\sysprog-win-shots\\l9\\', '')[:150] for l in keep if not l.startswith('=====')]
    return ('        <figure class="code" data-os="win"><figcaption><span>вывод crash_asan.exe heap и uaf · Windows x64, GitHub Actions</span>'
            '<span>строки отчётов, остальное опущено</span></figcaption>\n<pre>' + html.escape('\n'.join(keep)) + '</pre>\n        </figure>')


CC = {'win': 'cl /nologo /Zi /W4 crash.c', 'mac': 'clang -g -O0 -Wall -Wextra -o crash crash.c', 'linux': 'gcc -g -O0 -Wall -Wextra -o crash crash.c'}
ASAN = {'win': 'cl /nologo /Zi /fsanitize=address crash.c /Fe:crash_asan.exe', 'mac': 'clang -g -O0 -fsanitize=address -o crash_asan crash.c',
        'linux': 'gcc -g -O0 -fsanitize=address -o crash_asan crash.c'}

PIC_STRUCT = V.scheme('Как пятая запись портит соседнюю переменную',
    V.tab(['', 'data[0]', 'data[1]', 'data[2]', 'data[3]', 'limit'], [
        ['до цикла', '0', '0', '0', '0', '100'],
        ['после i ≤ 4', '7', '7', '7', '7', ('7', 'is-bad')]]),
    'Поля структуры лежат подряд, по 4 байта. Места у массива на 4 числа; запись <code>data[4]</code> попадает в следующие 4 байта — в <code>limit</code>.')

PIC_KINDS = V.scheme('Три ошибки памяти: что видно без проверки и с AddressSanitizer',
    V.tab(['Ошибка', 'Без проверки', 'С AddressSanitizer'], [
        ['запись по адресу 0', ('процесс убит системой', 'is-bad'), 'то же'],
        ['запись за границу', ('работает, данные испорчены', 'is-bad'), ('отчёт и остановка', 'is-ok')],
        ['чтение после free', ('работает, печатает мусор', 'is-bad'), ('отчёт и остановка', 'is-ok')]]),
    'Розовое — ошибка без сообщения об ошибке или смерть процесса. AddressSanitizer — проверка памяти, которую компилятор встраивает в программу.')

PIC_CODES = V.scheme('Как система сообщает о падении',
    V.tab(['', 'Windows', 'macOS', 'Linux'], [
        ['код завершения', '−1073741819 = 0xC0000005, «нарушение доступа»', '139 = 128 + 11, сигнал SIGSEGV', '139 = 128 + 11, сигнал SIGSEGV'],
        ['сообщение', 'нет', '<code>zsh: segmentation fault</code>', '<code>Segmentation fault</code>'],
        ['запись о падении', 'журнал «Приложение», событие 1000', 'отчёт <code>~/Library/Logs/DiagnosticReports/*.ips</code>', '—']]),
    'SIGSEGV — сигнал «нарушение сегментации»: процесс обратился к памяти, которой у него нет. 0xC0000005 — то же в Windows.')

SIMPLE_NULL = V.simple('Что происходит при записи по адресу 0',
    '          <p>Память процесса — длинный коридор с дверями-страницами. Самая первая дверь, с номером 0, заколочена специально: туда ходят только по ошибке, когда указатель забыли заполнить. Процесс пытается войти — процессор поднимает тревогу, система приходит и выводит процесс из здания.</p>\n'
    '          <p>Код 139 — это «выведен за попытку войти в чужую дверь»: 128 значит «убит сигналом», 11 — номер сигнала SIGSEGV. В Windows то же называется кодом 0xC0000005.</p>',
    V.steps(V.card('программа', '<code>*p = 42</code>', '<small>p = NULL, адрес 0</small>', 'c'), V.arrow(),
            V.card('процессор', 'страницы 0 нет', '<small>тревога</small>', 'sys'), V.arrow(),
            V.card('система', 'убивает процесс', '<small>код 139 / 0xC0000005</small>', 'sys')),
    '<b>Что есть что.</b> Заколоченная дверь — нулевая страница, которую система не отдаёт ни одному процессу. Тревога — исключение процессора, вывод из здания — сигнал SIGSEGV.')

SIMPLE_SILENT = V.simple('Почему запись за границу не падает',
    '          <p>Комод с четырьмя ящиками для носков, а под ним — ящик с деньгами. Пятую пару носков засунули «в пятый ящик» — а пятого нет, следующий — ящик с деньгами. Носки легли поверх денег, и никто не закричал: ящик-то существует, дверь открыта.</p>\n'
    '          <p>Система ловит только попытку войти в чужую дверь. Соседняя переменная — своя память процесса, и запись туда разрешена. Поэтому программа работает дальше с испорченным <code>limit</code> = 7 — и узнают об этом, когда что-то сломается гораздо позже.</p>',
    '', '<b>Что есть что.</b> Ящики для носков — <code>data[0..3]</code>, ящик с деньгами — <code>limit</code>, пятая пара — <code>data[4] = 7</code>.')

SIMPLE_ASAN = V.simple('Как AddressSanitizer находит ошибку',
    '          <p>AddressSanitizer обтягивает каждый выданный кусок памяти красной лентой — по краям оставляет запретные байты. Перед каждой записью и чтением программа сверяется с картой лент. Наступил на ленту — программа останавливается и печатает, какой байт тронут, в какой строке и где этот кусок был выдан.</p>\n'
    '          <p>Освобождённую память он какое-то время держит под лентой «освобождено» и никому не выдаёт. Кто полез туда после <code>free</code> — попался тоже, и в отчёте видно и строку обращения, и строку <code>free</code>.</p>',
    V.steps(V.card('malloc(16)', '16 байт и ленты по краям', '', 'c'), V.arrow('запись data[4]'),
            V.card('проверка', 'байт под лентой', '', 'sys'), V.arrow(),
            V.card('отчёт', 'heap-buffer-overflow', '<small>crash.c:24</small>', 'py')),
    '<b>Что есть что.</b> Лента — «красная зона» (redzone), карта лент — теневая память ASan, отчёт — строки <code>ERROR: AddressSanitizer</code>.')

S = []

S.append(dict(
    do={o: ('Уроните программу', f'В папке <code>labs/{LAB}</code> соберите программу: <code>{CC[o]}</code>. Выполните <code>{"crash.exe null" if o == "win" else "./crash null"}</code>: функция <code>null_write</code> записывает число по пустому указателю. Затем <code>{"echo %errorlevel%" if o == "win" else "echo $?"}</code> — код завершения.') for o in ('win', 'mac', 'linux')},
    shot={'win': '01-null.png', 'mac': '01-null.png', 'linux': '01-null.png'},
    notes={'win': (f'<p>{mk(1)} — программа напечатала адрес <code>0000000000000000</code>, строки <code>not reached</code> нет; код завершения −1073741819.</p>',
                   '<p>Сообщения о падении командная строка не печатает, оно видно только по коду. −1073741819 — это 0xC0000005, «нарушение доступа»: процесс обратился к памяти, которой у него нет.</p>'),
           'mac': (f'<p>{mk(1)} — <code>writing to address 0x0</code>, затем <code>zsh: segmentation fault ./crash null</code> и код 139.</p>',
                   '<p>Система убила процесс сигналом SIGSEGV, номер 11. Оболочка сообщила об этом и записала код 128 + 11 = 139.</p>'),
           'linux': (f'<p>Выше — предупреждение gcc: <code>pointer \'name\' used after \'free\'</code> в строке 33 — оно пригодится в шаге 5. {mk(1)} — <code>writing to address (nil)</code>, <code>Segmentation fault</code>, код 139.</p>',
                     '<p>Система убила процесс сигналом SIGSEGV, номер 11, а оболочка записала код 128 + 11 = 139.</p>')},
    q='что напечатала программа и код завершения.'))

S.append(dict(
    do={'win': ('Уроните Python и найдите запись о падении', 'Выполните <code>python ctypes_crash.py</code>: программа через <code>ctypes</code> пишет 8 байт по адресу 0. Затем выполните<br><code>powershell -c "Get-WinEvent -FilterHashtable @{LogName=\'Application\';Id=1000} -MaxEvents 1 | Select -Expand Message"</code><br>— последнее событие 1000 «Сбой приложения» из журнала Windows.'),
        'mac': ('Уроните Python и найдите запись о падении', 'Выполните <code>python3 ctypes_crash.py 2&gt;&amp;1 | head -6</code>: программа через <code>ctypes</code> пишет 8 байт по адресу 0, <code>head -6</code> оставляет начало сообщения. Затем выполните<br><code>grep -o \'"exception"[^}]*}\' $(ls -t ~/Library/Logs/DiagnosticReports/crash-* | head -1)</code><br>— причина из последнего отчёта о падении программы <code>crash</code>.'),
        'linux': ('Уроните Python', 'Выполните <code>python3 ctypes_crash.py 2&gt;&amp;1 | head -6</code>: программа через <code>ctypes</code> пишет 8 байт по адресу 0, <code>head -6</code> оставляет начало сообщения.')},
    shot={'win': '02-python.png', 'mac': '02-python.png', 'linux': '02-python.png'},
    notes={'win': (f'<p>{mk(1)} — стек Python от <code>faulthandler</code>: строка 6 в <code>save</code>, строка 11. {mk(2)} — <code>OSError: exception: access violation writing 0x0000000000000000</code>. {mk(3)} — событие журнала: сбойное приложение <code>crash.exe</code>, код исключения <code>0xc0000005</code>.</p>',
                   '<p>В Windows Python пережил ошибку: <code>ctypes</code> перехватил нарушение доступа и превратил его в исключение <code>OSError</code>, которое можно поймать в <code>try</code>. А падение <code>crash.exe</code> из шага 1 Windows записала в журнал «Приложение» с тем же кодом 0xC0000005.</p>'),
           'mac': (f'<p>{mk(1)} — <code>Fatal Python error: Segmentation fault</code> и стек Python: строка 6 в <code>save</code>, строка 11. {mk(2)} — из отчёта: <code>"type":"EXC_BAD_ACCESS","signal":"SIGSEGV","subtype":"KERN_INVALID_ADDRESS at 0x0000000000000000"</code>.</p>',
                   '<p>Python упал так же, как программа на C, но <code>faulthandler</code> успел напечатать, в какой строке Python это случилось. macOS после каждого падения пишет отчёт: причина — неверный адрес 0.</p>'),
           'linux': (f'<p>{mk(1)} — <code>Fatal Python error: Segmentation fault</code> и стек Python: строка 6 в <code>save</code>, строка 11 в <code>&lt;module&gt;</code>.</p>',
                     '<p>Python упал так же, как программа на C: ошибка внутри <code>ctypes</code> убивает весь процесс. <code>faulthandler.enable()</code> успел напечатать, на какой строке Python это случилось, — без него было бы только <code>Segmentation fault</code>.</p>')},
    q='что напечатал Python и где система записала падение.'))

S.append(dict(
    do={o: ('Запишите за границу массива', f'Выполните <code>{"crash.exe overflow" if o == "win" else "./crash overflow"}</code> и снова посмотрите код завершения. Функция <code>overflow</code> пишет пять чисел в массив на четыре.') for o in ('win', 'mac', 'linux')},
    shot={'win': '03-overflow.png', 'mac': '03-overflow.png', 'linux': '03-overflow.png'},
    notes={o: (f'<p>{mk(1)} — <code>limit before: 100</code>, <code>limit after: 7</code>. {mk(2)} — код завершения 0.</p>',
               '<p>Программа не упала и сообщила об успехе. При этом переменная <code>limit</code>, которую никто не трогал, стала 7. Это хуже падения: ошибка тихо испортила данные.</p>') for o in ('win', 'mac', 'linux')},
    q='значение limit до и после и код завершения.'))

S.append(dict(
    do={'win': ('Включите AddressSanitizer', 'Выполните <code>crash.exe heap</code>: функция <code>heap_overflow</code> пишет пять чисел в память, выделенную <code>malloc</code> на четыре. Затем соберите программу с проверкой: <code>cl /nologo /Zi /fsanitize=address crash.c /Fe:crash_asan.exe</code> и выполните <code>crash_asan.exe heap</code>. Ключ <code>/fsanitize=address</code> работает на компьютерах с x64; на ARM компилятор Microsoft его пропускает с предупреждением D9002 — тогда смотрите вывод ниже, после хода работы.'),
        'mac': ('Включите AddressSanitizer', f'Выполните <code>./crash heap</code>: функция <code>heap_overflow</code> пишет пять чисел в память, выделенную <code>malloc</code> на четыре. Затем соберите программу с проверкой: <code>{ASAN["mac"]}</code> и выполните <code>./crash_asan heap 2&gt;&amp;1 | head -8</code>.'),
        'linux': ('Включите AddressSanitizer', f'Выполните <code>./crash heap</code>: функция <code>heap_overflow</code> пишет пять чисел в память, выделенную <code>malloc</code> на четыре. Затем соберите программу с проверкой: <code>{ASAN["linux"]}</code> и выполните <code>./crash_asan heap 2&gt;&amp;1 | head -8</code>.')},
    shot={'win': '04-heap.png', 'mac': '04-heap.png', 'linux': '04-heap.png'},
    notes={'win': (f'<p>Кадр — компьютер с ARM, проверки нет. {mk(1)} — <code>wrote 5 numbers into room for 4</code>: программа не заметила ошибки. На x64 <code>crash_asan.exe heap</code> печатает <code>ERROR: AddressSanitizer: heap-buffer-overflow</code>, <code>WRITE of size 4</code> и строку <code>crash.c:24</code> — вывод ниже, после хода работы.</p>',
                   '<p>Без проверки запись за границу кучи проходит молча, как в шаге 3. AddressSanitizer останавливает программу на первой же лишней записи и называет строку.</p>'),
           'mac': (f'<p>{mk(1)} — без проверки: <code>wrote 5 numbers into room for 4</code>. {mk(2)} — с проверкой: <code>ERROR: AddressSanitizer: heap-buffer-overflow</code>, <code>WRITE of size 4</code>, <code>in heap_overflow crash.c:24</code>.</p>',
                   '<p>Без проверки ошибка прошла молча. С проверкой программа остановилась на лишней записи: 4 байта, строка 24 — <code>data[i] = 7</code> при <code>i = 4</code>. Ниже в полном выводе: адрес находится «0 bytes after 16-byte region» — сразу за 16 байтами, которые выдал <code>malloc</code>.</p>'),
           'linux': (f'<p>{mk(1)} — без проверки: <code>wrote 5 numbers into room for 4</code>. {mk(2)} — с проверкой: <code>ERROR: AddressSanitizer: heap-buffer-overflow</code>, <code>WRITE of size 4</code>, <code>in heap_overflow …/crash.c:24</code>.</p>',
                     '<p>Без проверки ошибка прошла молча. С проверкой программа остановилась на лишней записи: 4 байта, строка 24 — <code>data[i] = 7</code> при <code>i = 4</code>.</p>')},
    q='что напечатала программа без проверки и с AddressSanitizer, какую строку он назвал.'))

S.append(dict(
    do={'win': ('Найдите чтение освобождённой памяти', 'Выполните <code>crash.exe uaf</code>: функция <code>use_after_free</code> освобождает строку и потом печатает её. На x64 выполните также <code>crash_asan.exe uaf</code>.'),
        'mac': ('Найдите чтение освобождённой памяти', 'Выполните<br><code>./crash_asan uaf 2&gt;&amp;1 | grep -E "ERROR|in use_after_free|freed by|in main" | head -6</code><br>Функция <code>use_after_free</code> освобождает строку и потом печатает её; <code>grep</code> оставляет главные строки отчёта.'),
        'linux': ('Найдите чтение освобождённой памяти', 'Выполните<br><code>./crash_asan uaf 2&gt;&amp;1 | grep -E "ERROR|in use_after_free|freed by|in main" | head -6</code><br>Функция <code>use_after_free</code> освобождает строку и потом печатает её; <code>grep</code> оставляет главные строки отчёта.')},
    shot={'win': '04-heap.png', 'mac': '05-uaf.png', 'linux': '05-uaf.png'},
    notes={'win': (f'<p>Тот же кадр. {mk(2)} — без проверки: <code>name after free: name after free: name af</code> — вместо <code>agent</code> напечатан мусор. На x64 AddressSanitizer печатает <code>heap-use-after-free</code>, обращение в <code>crash.c:33</code> и освобождение в <code>crash.c:32</code>.</p>',
                   '<p>Освобождённую память куча уже отдала под другие данные — под текст самого <code>printf</code>. Программа не упала и напечатала чужое.</p>'),
           'mac': (f'<p>{mk(1)} — <code>ERROR: AddressSanitizer: heap-use-after-free</code>. {mk(2)} — <code>freed by thread T0 here</code>: память освобождена в <code>use_after_free crash.c:32</code>; выше — обращение в <code>crash.c:33</code>.</p>',
                   '<p>Отчёт называет обе строки: где память освободили (32, <code>free(name)</code>) и где к ней обратились (33, <code>printf</code>). По ним ошибка находится без отладчика.</p>'),
           'linux': (f'<p>{mk(1)} — <code>ERROR: AddressSanitizer: heap-use-after-free</code>; ниже — обращение в <code>crash.c:33</code>. {mk(2)} — освобождено в <code>use_after_free …/crash.c:32</code>.</p>',
                     '<p>Отчёт называет обе строки: где память освободили (32) и где к ней обратились (33). Ту же ошибку gcc заметил ещё при сборке в шаге 1 — предупреждение <code>-Wuse-after-free</code>. Компилятор видит такие ошибки не всегда, проверка при запуске — надёжнее.</p>')},
    q='какой вид ошибки назвал AddressSanitizer и какие две строки.'))

S.append(dict(
    do={'win': ('Исправьте и проверьте', 'Выполните <code>powershell -c "(gc crash.c) -replace \'i &lt;= 4\',\'i &lt; 4\' | sc crash_fixed.c"</code>: в копии оба цикла идут до <code>i &lt; 4</code>. Затем <code>fc crash.c crash_fixed.c</code>, соберите <code>cl /nologo /Zi /W4 crash_fixed.c</code> и выполните <code>crash_fixed.exe heap</code> и <code>crash_fixed.exe overflow</code>.'),
        'mac': ('Исправьте и проверьте', "Выполните <code>sed 's/i &lt;= 4/i &lt; 4/g' crash.c &gt; crash_fixed.c</code>: в копии оба цикла идут до <code>i &lt; 4</code>. Затем <code>diff crash.c crash_fixed.c</code>, соберите копию с проверкой: <code>clang -g -O0 -fsanitize=address -o crash_fixed crash_fixed.c</code> и выполните <code>./crash_fixed heap</code> и <code>./crash_fixed overflow</code>."),
        'linux': ('Исправьте и проверьте', "Выполните <code>sed 's/i &lt;= 4/i &lt; 4/g' crash.c &gt; crash_fixed.c</code>: в копии оба цикла идут до <code>i &lt; 4</code>. Затем <code>diff crash.c crash_fixed.c</code>, соберите копию с проверкой: <code>gcc -g -O0 -fsanitize=address -o crash_fixed crash_fixed.c</code> и выполните <code>./crash_fixed heap</code> и <code>./crash_fixed overflow</code>.")},
    shot={'win': '06-fixed.png', 'mac': '06-fixed.png', 'linux': '06-fixed.png'},
    notes={o: (f'<p>{mk(1)} — разница файлов: <code>i &lt;= 4</code> заменено на <code>i &lt; 4</code>. {mk(2)} — <code>wrote 4 numbers into room for 4</code>. {mk(3)} — <code>limit before: 100</code>, <code>limit after: 100</code>.</p>',
               ('<p>Исправленная программа пишет четыре числа и не трогает <code>limit</code>.' + (' Собрана с AddressSanitizer — и он молчит: лишних записей больше нет.' if o != 'win' else ' На x64 соберите её ещё и с <code>/fsanitize=address</code>: проверка должна промолчать.') + ' Так проверяют любое исправление: тот же запуск с проверкой, и отчёта нет.</p>')) for o in ('win', 'mac', 'linux')},
    q='что изменилось в коде и что напечатала исправленная программа.'))

STEPS = steps(S, LAB)

HTML = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>Лабораторная работа 9. Разбор падения · Справочник по системному программированию</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,600;0,7..72,700;1,7..72,400&family=Pixelify+Sans:wght@500;600;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css">
</head>
<body>
  <div class="book">
    <div class="book__body">
      <div class="spine"><span>Модуль 2 · Лабораторная работа 9</span></div>

      <main class="leaf">
        <div class="running">
          <p class="eyebrow"><a href="../../index.html" style="text-decoration:none;color:inherit">Справочник по системному программированию</a> · модуль 2 · лабораторная работа</p>
          <p class="running__folio">ЛР 9</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">ЛР 9</span>
          <h1>Разбор<br>падения</h1>
          <p class="lead">Программа на C с тремя ошибками памяти: одна убивает процесс, две другие проходят молча и портят данные. В работе видно, как система сообщает о падении и где его записывает, почему Python падает вместе с кодом на C, который вызывает, и как AddressSanitizer превращает молчаливую ошибку в отчёт с номером строки.</p>
        </header>

        <dl class="passport">
          <div><dt>Пара</dt><dd>9</dd></div>
          <div><dt>Время</dt><dd>35–40 минут</dd></div>
          <div><dt>Программы</dt><dd><span data-os="win">MSVC (<code>cl</code>), PowerShell</span><span data-os="mac">clang, Терминал</span><span data-os="linux">gcc, терминал</span>, Python, AddressSanitizer</dd></div>
          <div><dt>Сдать</dt><dd><code>report.md</code> и {len(snaps.SNAPS[LAB])} снимка в <code>screenshots/</code> в папке <code>labs/{LAB}</code> репозитория <code>sysprog-start</code></dd></div>
        </dl>

        <nav class="contents">
          <b>В этой работе</b>
          <ol>
            <li><a href="#s1">Подготовка</a></li>
            <li><a href="#s2">Три ошибки памяти</a></li>
            <li><a href="#s3">Ход работы</a></li>
            <li><a href="#s4">Что получилось</a></li>
            <li><a href="#s5">Отчёт</a></li>
            <li><a href="#s6">Проверьте себя</a></li>
          </ol>
        </nav>

        <h2 id="s1"><span class="sec">§1</span>Подготовка</h2>

        <p>Нужны компилятор C из модуля 1 и Python. <span data-os="win">AddressSanitizer входит в MSVC и включается ключом <code>/fsanitize=address</code> на компьютерах с x64. На компьютере с ARM этот ключ компилятор пропускает, и проверку в шагах 4–5 заменяет вывод с x64 в конце хода работы.</span><span data-os="mac">AddressSanitizer входит в clang из Command Line Tools.</span><span data-os="linux">AddressSanitizer входит в gcc; если сборка с <code>-fsanitize=address</code> пишет, что нет <code>libasan</code>, поставьте её: <code>sudo apt install libasan8</code>.</span> В шаблоне в папке <code>labs/{LAB}</code> лежат бланк, папка <code>screenshots/</code> и две программы. Главная — <code>crash.c</code>:</p>
{file('crash.c')}
        <p>Четыре функции, по одной на ошибку, выбираются словом в командной строке. <code>null_write</code> пишет по пустому указателю. <code>overflow</code> пишет пять чисел в массив <code>data</code> на четыре, а за массивом в той же структуре лежит <code>limit</code>. <code>heap_overflow</code> делает то же с памятью из <code>malloc</code>. <code>use_after_free</code> освобождает строку и печатает её. Вторая программа, <code>ctypes_crash.py</code>, пишет по адресу 0 из Python через <code>ctypes</code>:</p>
{file('ctypes_crash.py', py=True)}
        <p><code>faulthandler.enable()</code> велит Python при падении напечатать, на какой строке Python он был.</p>

        <div class="margin-note">
          <b>Как читать шаг</b>
          <p>Вверху шага — действие. Ниже — кадр экрана после действия; красные рамки отмечают места, о которых идёт речь. Слева под кадром — что на нём видно, справа — что изменилось. Строка «В отчёт» — что записать в <code>report.md</code>. Адреса в отчётах у вас будут другими, а номера строк — те же.</p>
        </div>

        <h2 id="s2"><span class="sec">§2</span>Три ошибки памяти</h2>

        <p>Процесс может работать только с той памятью, которую ему выдала система. Попытка обратиться к памяти, которой у процесса нет, — например, по адресу 0, — <span class="term">падение</span>: процессор останавливает команду, и система завершает процесс. Но большинство ошибок памяти падения не вызывают: запись за границу массива попадает в соседнюю переменную того же процесса, и это разрешено.</p>
{PIC_STRUCT}
        <p>Слева — четыре ячейки массива, справа — <code>limit</code>. После цикла с условием <code>i &lt;= 4</code> пятая семёрка лежит там, где было 100. Такие ошибки ловит <span class="term">AddressSanitizer</span> — проверка, которую компилятор встраивает в программу по ключу <code>-fsanitize=address</code>: перед каждым обращением к памяти программа проверяет, своё ли это место. Что видно с проверкой и без неё:</p>
{PIC_KINDS}
        <p>Первая строка — шаги 1–2, вторая — шаги 3–4, третья — шаг 5. Шаг 6 показывает, как проверка подтверждает исправление.</p>
{SIMPLE_NULL}

        <h2 id="s3"><span class="sec">§3</span>Ход работы</h2>

{STEPS}
{win_asan()}
{SIMPLE_SILENT}
{SIMPLE_ASAN}

        <h2 id="s4"><span class="sec">§4</span>Что получилось</h2>

{PIC_CODES}
        <div class="table-scroll">
          <table>
            <thead><tr><th>Шаг</th><th>Windows</th><th>macOS</th><th>Linux</th></tr></thead>
            <tbody>
              <tr><td>Запись по адресу 0</td><td>код −1073741819, событие 1000 в журнале</td><td>139, отчёт EXC_BAD_ACCESS</td><td>139, Segmentation fault</td></tr>
              <tr><td>То же из Python</td><td>исключение OSError, Python жив</td><td colspan="2">Fatal Python error, процесс убит</td></tr>
              <tr><td>Запись за границу, без проверки</td><td colspan="3">limit 100 → 7, код 0; «wrote 5 numbers into room for 4»</td></tr>
              <tr><td>С AddressSanitizer</td><td>x64: heap-buffer-overflow, crash.c:24</td><td colspan="2">heap-buffer-overflow, crash.c:24</td></tr>
              <tr><td>Чтение после free</td><td>без проверки — мусор; x64: heap-use-after-free, 33 и 32</td><td colspan="2">heap-use-after-free, обращение 33, освобождение 32</td></tr>
              <tr><td>После исправления</td><td colspan="3">wrote 4 numbers, limit 100, отчётов нет</td></tr>
            </tbody>
          </table>
        </div>

        <p>Из трёх ошибок только одна дала знать о себе сама — падением с кодом 139 или 0xC0000005. Две другие программа пережила, вернула код 0 и испортила данные. AddressSanitizer превращает их в отчёт с видом ошибки и номером строки, поэтому программы на C, особенно те, что вызываются из Python через <code>ctypes</code>, проверяют сборкой с <code>-fsanitize=address</code> — и после исправления запускают тот же опыт ещё раз.</p>

        <h2 id="s5"><span class="sec">§5</span>Отчёт</h2>

        <p>Бланк — в <code>labs/{LAB}/report.md</code>. Замените каждый пропуск <code>___</code> данными со своего экрана, снимки положите в <code>screenshots/</code>. Коммит — <code>labs 09: разбор падения, отчёт</code>.</p>

        <pre class="report"># ЛР 9. Разбор падения

Система: <span class="blank">___</span>
Компилятор: <span class="blank">___</span>

## Падение
crash null: что напечатано и код завершения: <span class="blank">___</span>
ctypes_crash.py: что напечатал Python: <span class="blank">___</span>
Где система записала падение: <span class="blank">___</span>

## Молчаливые ошибки
crash overflow: limit до и после, код: <span class="blank">___</span>
crash heap без проверки: <span class="blank">___</span>
AddressSanitizer для heap: вид ошибки и строка: <span class="blank">___</span>
AddressSanitizer для uaf: вид ошибки и две строки: <span class="blank">___</span>

## Исправление
Что изменено и что напечатала исправленная программа: <span class="blank">___</span>

Не получилось: <span class="blank">___</span>

{snaps.report_pre(LAB)}</pre>

{snaps.page_block(LAB)}

        <h2 id="s6"><span class="sec">§6</span>Проверьте себя</h2>

        <details>
          <summary>Почему код завершения после падения — 139?</summary>
          <p>Процесс убит сигналом SIGSEGV с номером 11, а оболочка записывает такой код как 128 + номер сигнала.</p>
        </details>
        <details>
          <summary>Почему запись за границу массива в шаге 3 не уронила программу?</summary>
          <p>Пятое число попало в соседнюю переменную <code>limit</code> — это своя память процесса, и система её не охраняет. Падение бывает только при обращении к памяти, которой у процесса нет.</p>
        </details>
        <details>
          <summary>Что сообщает AddressSanitizer в отчёте?</summary>
          <p>Вид ошибки (heap-buffer-overflow, heap-use-after-free), размер обращения, строку, где оно произошло, и строку, где память выделили или освободили.</p>
        </details>
        <details>
          <summary>Почему ошибка в коде на C роняет программу на Python?</summary>
          <p>Через <code>ctypes</code> функция на C работает внутри процесса Python. Если она обращается к чужой памяти, система убивает весь процесс. В Windows <code>ctypes</code> перехватывает нарушение доступа и поднимает <code>OSError</code>, но данные к этому моменту могли быть уже испорчены.</p>
        </details>
        <details>
          <summary>Как проверить, что ошибка исправлена?</summary>
          <p>Собрать исправленную программу с AddressSanitizer и повторить тот же запуск: отчёта нет, и результат правильный.</p>
        </details>

        <div class="pager">
          <a href="../21-laboratornaya-8/index.html">← ЛР 8 Карта памяти</a>
          <a href="../../index.html">Оглавление</a>
        </div>

        <div class="colophon">
          <span>Справочник по системному программированию</span>
          <span class="author-line">© Макаров Максим Николаевич</span>
        </div>
      </main>
    </div>
  </div>
  <script src="../../book.js"></script>
</body>
</html>
'''
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(HTML)
print('ok', OUT)
