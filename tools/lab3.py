"""Лабораторная работа 3 «Библиотеки программы» → temy/10-laboratornaya-3/index.html.

Кадры — встроенный терминал VS Code по протоколу DevTools (~/sysprog-shots/lab3/shoot3.py mac|linux|win, рамки mark.py):
macOS 26 (Apple clang 17, Python 3.9.6 из Command Line Tools), Linux — VS Code для Linux в контейнере sp-lab2-linux
(Debian, gcc 14, Python 3.13.5), Windows — ВМ Win11-lab (MSVC 19.44 x64, Python 3.14.0 ARM64). Числа в тексте — с этих кадров."""
from pathlib import Path
from lab_build import steps
import snaps
from ch11 import hl
import walk_labs

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'temy/10-laboratornaya-3/index.html'
CODE = (Path(__file__).parent / 'src_lab3/src/libs.c').read_text()


def mk(n):
    return f'<span class="mk">{n}</span>'


S = []

# ─────────────── Часть 1. Библиотеки файла ───────────────
S.append(dict(
    do={'win': ('Соберите и запустите программу', 'Откройте папку <code>03-libraries</code> в VS Code командой <code>code .</code> из <b>x64 Native Tools Command Prompt</b>, откройте встроенный терминал (<b>Terminal → New Terminal</b>, оболочка <b>Command Prompt</b>) и выполните <code>cl /nologo libs.c && libs.exe</code>.'),
        'mac': ('Соберите и запустите программу', 'Откройте папку <code>03-libraries</code> в VS Code, затем встроенный терминал: <b>Terminal → New Terminal</b>. Выполните <code>clang -o libs libs.c && ./libs</code>.'),
        'linux': ('Соберите и запустите программу', 'Откройте папку <code>03-libraries</code> в VS Code, затем встроенный терминал: <b>Terminal → New Terminal</b>. Выполните <code>gcc -o libs libs.c -lm && ./libs</code>.')},
    shot='01-build.png',
    notes={'win': ('<p>' + mk(1) + ' — строка <code>#include &lt;math.h&gt;</code>: объявление функции <code>sqrt</code>. ' + mk(2) + ' — команда сборки и запуска. ' + mk(3) + ' — вывод: <code>libs.exe: sqrt(2) = 1.414214</code>.</p>',
                   '<p>Программа вызвала функцию <code>sqrt</code>, которую сама не содержит: её написали создатели библиотеки C. В Explorer появились <code>libs.exe</code> и промежуточный файл <code>libs.obj</code>.</p>'),
           'mac': ('<p>' + mk(1) + ' — строка <code>#include &lt;math.h&gt;</code>: объявление функции <code>sqrt</code>. ' + mk(2) + ' — команда сборки и запуска. ' + mk(3) + ' — вывод: <code>./libs: sqrt(2) = 1.414214</code>.</p>',
                   '<p>Программа вызвала функцию <code>sqrt</code>, которую сама не содержит: её написали создатели библиотеки C. В Explorer появился файл <code>libs</code>.</p>'),
           'linux': ('<p>' + mk(1) + ' — строка <code>#include &lt;math.h&gt;</code>: объявление функции <code>sqrt</code>. ' + mk(2) + ' — команда сборки и запуска с ключом <code>-lm</code>. ' + mk(3) + ' — вывод: <code>./libs: sqrt(2) = 1.414214</code>.</p>',
                     '<p>Программа вызвала функцию <code>sqrt</code>, которую сама не содержит. В Linux математические функции лежат в отдельной библиотеке <code>libm</code>, и ключ <code>-lm</code> просит компоновщик подключить её. Без него gcc остановится с ошибкой <code>undefined reference to `sqrt\'</code>: заголовок <code>math.h</code> только объявляет функцию, сама она в библиотеке.</p>')},
    q='что напечатала программа.'))

S.append(dict(
    do={'win': ('Посмотрите, какие библиотеки нужны файлу', 'Выполните <code>dumpbin /nologo /dependents libs.exe | findstr /i .dll</code>. Программа <code>dumpbin</code> входит в Build Tools; <code>findstr</code> оставляет только строки с <code>.dll</code>.'),
        'mac': ('Посмотрите, какие библиотеки нужны файлу', 'Выполните <code>otool -L libs</code>. Программа <code>otool</code> входит в Command Line Tools.'),
        'linux': ('Посмотрите, какие библиотеки нужны файлу', 'Выполните <code>ldd libs</code>.')},
    shot='02-deps.png',
    notes={'win': ('<p>' + mk(1) + ' — команда. ' + mk(2) + ' — единственная библиотека: <code>KERNEL32.dll</code>.</p>',
                   '<p>Файлу <code>libs.exe</code> нужна одна системная библиотека Windows. Функция <code>sqrt</code> и <code>printf</code> в списке не видны: MSVC по умолчанию копирует нужные части библиотеки C прямо в <code>.exe</code> — это <span class="term">статическая компоновка</span>. Файл стал больше, зато на другом компьютере ему ничего не нужно, кроме Windows.</p>'),
           'mac': ('<p>' + mk(1) + ' — команда. ' + mk(2) + ' — имя файла. ' + mk(3) + ' — единственная библиотека: <code>/usr/lib/libSystem.B.dylib</code>.</p>',
                   '<p>В macOS функции C, математика и системные вызовы собраны в одну библиотеку <code>libSystem</code>, поэтому в списке одна строка. Её загружает каждая программа macOS. Это <span class="term">динамическая компоновка</span>: в самом файле <code>libs</code> функции <code>sqrt</code> нет, есть только запись «взять её из libSystem при запуске».</p>'),
           'linux': ('<p>' + mk(1) + ' — команда. ' + mk(2) + ' — <code>libm.so.6</code>, математика, подключённая ключом <code>-lm</code>. ' + mk(3) + ' — <code>libc.so.6</code>, библиотека C: <code>printf</code> и системные вызовы.</p>',
                     '<p>Справа от стрелки — где система нашла файл библиотеки. <code>linux-vdso.so.1</code> — небольшой кусок ядра, который оно само кладёт в каждый процесс, файла на диске у него нет. <code>ld-linux-aarch64.so.1</code> — <span class="term">загрузчик</span>: он при запуске находит и загружает остальные библиотеки. Это <span class="term">динамическая компоновка</span>: в самом файле <code>libs</code> функции <code>sqrt</code> нет, есть только запись «взять её из libm».</p>')},
    q='сколько библиотек в списке и как называется библиотека C на своей системе.'))

S.append(dict(
    do={'win': ('Посмотрите библиотеки Python', 'Разверните панель терминала кнопкой <b>Maximize Panel Size</b> справа над терминалом и скройте боковую панель: <kbd>Ctrl</kbd>+<kbd>B</kbd>. Выполните команду ниже: она узнаёт у Python путь к <code>python.exe</code> и передаёт его <code>dumpbin</code>.<br><code>for /f "delims=" %p in (\'python -c "import sys; print(sys.executable)"\') do dumpbin /nologo /dependents "%p" | findstr /i .dll</code>'),
        'mac': ('Посмотрите библиотеки Python', 'Разверните панель терминала кнопкой <b>Maximize Panel Size</b> и скройте боковую панель: <kbd>⌘</kbd>+<kbd>B</kbd>. Выполните <code>otool -L "$(python3 -c \'import sys; print(sys.executable)\')"</code> — путь к интерпретатору подставит сам Python.'),
        'linux': ('Посмотрите библиотеки Python', 'Разверните панель терминала кнопкой <b>Maximize Panel Size</b> и скройте боковую панель: <kbd>Ctrl</kbd>+<kbd>B</kbd>. Выполните <code>ldd "$(which python3)"</code>.')},
    shot='03-python-deps.png',
    notes={'win': ('<p>' + mk(1) + ' — <code>python314.dll</code>: здесь весь интерпретатор. ' + mk(2) + ' — <code>KERNEL32.dll</code>. Между ними — <code>VCRUNTIME140.dll</code> и пять библиотек <code>api-ms-win-crt-…</code>, библиотека C Windows.</p>',
                   '<p>Файл <code>python.exe</code> — маленькая обёртка: он загружает <code>python314.dll</code>, а та делает всю работу. Python собран с <b>динамической</b> библиотекой C, поэтому она в списке, а у <code>libs.exe</code> — нет. Путь к Python — <code>C:\\Program Files\\Python314-arm64</code>: на кадре Python для ARM64.</p>'),
           'mac': ('<p>' + mk(1) + ' — <code>@executable_path/../Python3</code>: библиотека с интерпретатором, путь отсчитывается от самого файла. ' + mk(2) + ' — <code>libSystem.B.dylib</code>.</p>',
                   '<p>Файл <code>python3</code> из Command Line Tools — обёртка, весь интерпретатор лежит в библиотеке <code>Python3</code>. Список выведен дважды, для <code>x86_64</code> и для <code>arm64</code>: файл <span class="term">универсальный</span>, в нём программы для двух процессоров. Python с python.org устроен так же, но путь и версия другие.</p>'),
           'linux': ('<p>' + mk(1) + ' — <code>libz.so.1</code>, сжатие данных. ' + mk(2) + ' — <code>libc.so.6</code>. Между ними <code>libm.so.6</code> и <code>libexpat.so.1</code> — разбор XML.</p>',
                     '<p>У Python библиотек больше, чем у <code>libs</code>: интерпретатору нужны сжатие, разбор XML, математика. Это библиотеки, которые нужны <b>при запуске</b>. Остальные Python загружает позже, когда программа их попросит, — это видно в части 2.</p>')}))

# ─────────────── Часть 2. Библиотеки процесса ───────────────
S.append(dict(
    do=('Запустите Python и узнайте номер процесса', 'В том же терминале выполните <code>' + 'python' + '</code><span data-os="mac linux"><code>3</code></span>. В интерпретаторе наберите <code>import os</code> и <code>os.getpid()</code>.'),
    shot='04-pid.png',
    notes={'win': ('<p>' + mk(1) + ' — вызов <code>os.getpid()</code>. ' + mk(2) + ' — номер процесса Python. Выше — версия: Python 3.14.0 для ARM64.</p>',
                   '<p>Терминал теперь занят интерпретатором: приглашение <code>&gt;&gt;&gt;</code> ждёт команду Python. Процесс работает и ждёт ввода, как <code>hello</code> в ЛР 1. Номер понадобится во втором терминале.</p>'),
           'mac': ('<p>' + mk(1) + ' — вызов <code>os.getpid()</code>. ' + mk(2) + ' — номер процесса Python. Выше — версия: Python 3.9.6 из Command Line Tools.</p>',
                   '<p>Терминал теперь занят интерпретатором: приглашение <code>&gt;&gt;&gt;</code> ждёт команду Python. Процесс работает и ждёт ввода, как <code>hello</code> в ЛР 1. Номер понадобится во втором терминале.</p>'),
           'linux': ('<p>' + mk(1) + ' — вызов <code>os.getpid()</code>. ' + mk(2) + ' — номер процесса Python. Выше — версия: Python 3.13.5.</p>',
                     '<p>Терминал теперь занят интерпретатором: приглашение <code>&gt;&gt;&gt;</code> ждёт команду Python. Процесс работает и ждёт ввода, как <code>hello</code> в ЛР 1. Номер понадобится во втором терминале.</p>')},
    q='номер процесса Python.'))

S.append(dict(
    do={'win': ('Посчитайте библиотеки процесса', 'Нажмите кнопку <b>Split Terminal</b> над терминалом: справа откроется второй. В нём запишите номер в переменную: <code>set P=номер</code>. Затем выполните две команды: <code>powershell -c "(Get-Process -Id %P%).Modules.Count"</code> — сколько модулей загружено в процесс, и <code>tasklist /m winsqlite3.dll /fi "PID eq %P%"</code> — есть ли среди них <code>winsqlite3.dll</code>.'),
        'mac': ('Посчитайте библиотеки процесса', 'Нажмите кнопку <b>Split Terminal</b> над терминалом: справа откроется второй. В нём запишите номер в переменную: <code>P=номер</code>. Затем выполните две команды: <code>vmmap $P | grep -o \'/[^ ]*\\.dylib\' | sort -u | wc -l</code> — сколько библиотек в памяти процесса, и <code>vmmap $P | grep -o \'/[^ ]*pcap[^ ]*\' | sort -u</code> — есть ли среди них <code>libpcap</code>.'),
        'linux': ('Посчитайте библиотеки процесса', 'Нажмите кнопку <b>Split Terminal</b> над терминалом: справа откроется второй. В нём запишите номер в переменную: <code>P=номер</code>. Затем выполните две команды: <code>grep -o \'/[^ ]*\\.so[^ ]*\' /proc/$P/maps | sort -u | wc -l</code> — сколько библиотек в памяти процесса, и <code>grep -o \'/[^ ]*sqlite[^ ]*\' /proc/$P/maps | sort -u</code> — есть ли среди них <code>libsqlite3</code>.')},
    shot='05-before.png',
    notes={'win': ('<p>' + mk(1) + ' — номер процесса в переменной <code>P</code>. ' + mk(2) + ' — 29 модулей: <code>python.exe</code> и библиотеки. ' + mk(3) + ' — поиск <code>winsqlite3.dll</code>: «Задачи, отвечающие заданным критериям, отсутствуют».</p>',
                   '<p>В процессе 29 модулей, <code>winsqlite3.dll</code> среди них нет. Это библиотека базы данных SQLite, она входит в Windows и лежит в <code>C:\\Windows\\System32</code>. Лежать на диске и быть загруженной в процесс — разные вещи.</p>'),
           'mac': ('<p>' + mk(1) + ' — номер процесса в переменной <code>P</code>. ' + mk(2) + ' — 171 библиотека в памяти процесса. ' + mk(3) + ' — поиск <code>libpcap</code>: команда ничего не вывела.</p>',
                   '<p>Программа <code>vmmap</code> печатает карту памяти процесса, а <code>grep</code> и <code>sort -u</code> оставляют из неё неповторяющиеся пути к <code>.dylib</code>. 171 — так много, потому что Python из Command Line Tools подключает системные фреймворки macOS, а они тянут свои библиотеки. <code>libpcap</code> — библиотека захвата сетевых пакетов, ей пользуется Wireshark в ЛР 14. В процессе её пока нет.</p>'),
           'linux': ('<p>' + mk(1) + ' — номер процесса в переменной <code>P</code>. ' + mk(2) + ' — 11 библиотек в памяти процесса. ' + mk(3) + ' — поиск <code>sqlite</code>: команда ничего не вывела.</p>',
                     '<p>Файл <code>/proc/$P/maps</code> — карта памяти процесса, её отдаёт ядро; так же её показывал Системный монитор в ЛР 1. <code>grep</code> и <code>sort -u</code> оставляют неповторяющиеся пути к <code>.so</code>. Библиотеки SQLite <code>libsqlite3</code> в процессе нет, хотя файл есть на диске.</p>')},
    q='сколько библиотек в процессе до загрузки.'))

S.append(dict(
    do={'win': ('Загрузите библиотеку и вызовите её функцию', 'Вернитесь в левый терминал с Python и наберите по строке: <code>import ctypes</code>, <code>lib = ctypes.CDLL("winsqlite3.dll")</code>, <code>lib.sqlite3_libversion.restype = ctypes.c_char_p</code>, <code>lib.sqlite3_libversion()</code>.'),
        'mac': ('Загрузите библиотеку и вызовите её функцию', 'Вернитесь в левый терминал с Python и наберите по строке: <code>import ctypes</code>, <code>lib = ctypes.CDLL("libpcap.dylib")</code>, <code>lib.pcap_lib_version.restype = ctypes.c_char_p</code>, <code>lib.pcap_lib_version()</code>.'),
        'linux': ('Загрузите библиотеку и вызовите её функцию', 'Вернитесь в левый терминал с Python и наберите по строке: <code>import ctypes</code>, <code>lib = ctypes.CDLL("libsqlite3.so.0")</code>, <code>lib.sqlite3_libversion.restype = ctypes.c_char_p</code>, <code>lib.sqlite3_libversion()</code>.')},
    shot='06-load.png',
    notes={'win': ('<p>' + mk(1) + ' — загрузка <code>winsqlite3.dll</code>. ' + mk(2) + ' — вызов функции <code>sqlite3_libversion</code>. ' + mk(3) + ' — ответ: <code>b\'3.43.2\'</code>, версия SQLite в этой Windows.</p>',
                   '<p>Python загрузил библиотеку из <code>System32</code> и вызвал функцию на C. <code>restype = ctypes.c_char_p</code> говорит Python, что функция возвращает адрес строки C, — без этой строки он принял бы адрес за число. Буква <code>b</code> перед кавычками — байты, как в главе 1.2.</p>'),
           'mac': ('<p>' + mk(1) + ' — загрузка <code>libpcap.dylib</code>. ' + mk(2) + ' — вызов функции <code>pcap_lib_version</code>. ' + mk(3) + ' — ответ: <code>b\'libpcap version 1.10.1\'</code>.</p>',
                   '<p>Python загрузил библиотеку и вызвал функцию на C. <code>restype = ctypes.c_char_p</code> говорит Python, что функция возвращает адрес строки C, — без этой строки он принял бы адрес за число. Буква <code>b</code> перед кавычками — байты, как в главе 1.2.</p>'),
           'linux': ('<p>' + mk(1) + ' — загрузка <code>libsqlite3.so.0</code>. ' + mk(2) + ' — вызов функции <code>sqlite3_libversion</code>. ' + mk(3) + ' — ответ: <code>b\'3.46.1\'</code>, версия SQLite.</p>',
                     '<p>Python загрузил библиотеку и вызвал функцию на C. <code>restype = ctypes.c_char_p</code> говорит Python, что функция возвращает адрес строки C, — без этой строки он принял бы адрес за число. Буква <code>b</code> перед кавычками — байты, как в главе 1.2.</p>')},
    q='что вернула функция библиотеки.'))

S.append(dict(
    do=('Снова посчитайте библиотеки процесса', 'Перейдите в правый терминал и повторите обе команды шага 5: стрелкой <kbd>↑</kbd> можно вызвать их из истории.'),
    shot='07-after.png',
    notes={'win': ('<p>' + mk(1) + ' — теперь 30 модулей. ' + mk(2) + ' — <code>tasklist</code> нашёл процесс: <code>python.exe</code> с тем же номером, модуль <code>winsqlite3.dll</code>.</p>',
                   '<p>Модулей стало на один больше: <code>ctypes.CDLL</code> загрузил <code>winsqlite3.dll</code> в работающий процесс. Перезапускать программу не понадобилось. Так в главе 1.2 мозг агента загрузит библиотеку ядра <code>sentry_core.dll</code>.</p>'),
           'mac': ('<p>' + mk(1) + ' — теперь 173 библиотеки. ' + mk(2) + ' — найдена <code>/usr/lib/libpcap.A.dylib</code>.</p>',
                   '<p>Библиотек стало на две больше: <code>libpcap</code> и <code>libffi</code> — через неё <code>ctypes</code> вызывает функции C, она загрузилась командой <code>import ctypes</code>. Имя файла — <code>libpcap.A.dylib</code>: <code>libpcap.dylib</code> из команды — короткое имя, которое ведёт к нему. Перезапускать программу не понадобилось. Так в главе 1.2 мозг агента загрузит библиотеку ядра <code>libsentry_core.dylib</code>.</p>'),
           'linux': ('<p>' + mk(1) + ' — теперь 14 библиотек. ' + mk(2) + ' — найдена <code>/usr/lib/aarch64-linux-gnu/libsqlite3.so.0.8.6</code>.</p>',
                     '<p>Библиотек стало на три больше: <code>libsqlite3</code>, модуль Python <code>_ctypes</code> из <code>import ctypes</code> и библиотека <code>libffi</code>, через которую <code>ctypes</code> вызывает функции C. Имя файла длиннее, чем в команде: <code>libsqlite3.so.0</code> — короткое имя, которое ведёт к файлу с полной версией. Перезапускать программу не понадобилось. Так в главе 1.2 мозг агента загрузит библиотеку ядра <code>libsentry_core.so</code>.</p>')},
    q='сколько библиотек стало и какой файл библиотеки нашёлся.'))

LAB = steps(S, '03-libraries')

HTML = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>Лабораторная работа 3. Библиотеки программы · Справочник по системному программированию</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,600;0,7..72,700;1,7..72,400&family=Pixelify+Sans:wght@500;600;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css">
</head>
<body>
  <div class="book">
    <div class="book__body">
      <div class="spine"><span>Модуль 1 · Лабораторная работа 3</span></div>

      <main class="leaf">
        <div class="running">
          <p class="eyebrow"><a href="../../index.html" style="text-decoration:none;color:inherit">Справочник по системному программированию</a> · модуль 1 · лабораторная работа</p>
          <p class="running__folio">ЛР 3</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">ЛР 3</span>
          <h1>Библиотеки<br>программы</h1>
          <p class="lead">Программа почти никогда не работает одна: функции <code>printf</code>, <code>sqrt</code> и системные вызовы лежат в библиотеках системы. В первой части видно, какие библиотеки записаны в файле программы. Во второй — как работающий процесс Python загружает новую библиотеку по запросу и вызывает её функцию. Так в главе 1.2 мозг агента на Python загрузит ядро агента на C.</p>
        </header>

        <dl class="passport">
          <div><dt>Пара</dt><dd>3, первая половина; перед главой 1.2</dd></div>
          <div><dt>Время</dt><dd>30–35 минут</dd></div>
          <div><dt>Программы</dt><dd>VS Code, <span data-os="win">dumpbin, PowerShell, tasklist</span><span data-os="mac">otool, vmmap</span><span data-os="linux">ldd, карта памяти /proc</span>, Python</dd></div>
          <div><dt>Сдать</dt><dd><code>libs.c</code>, <code>report.md</code> и 7 снимков в <code>screenshots/</code> в папке <code>labs/03-libraries</code> репозитория <code>sysprog-start</code></dd></div>
        </dl>

        <nav class="contents">
          <b>В этой работе</b>
          <ol>
            <li><a href="#s1">Подготовка</a></li>
            <li><a href="#s2">Два способа подключить библиотеку</a></li>
            <li><a href="#s3">Часть 1. Библиотеки файла</a></li>
            <li><a href="#s4">Часть 2. Библиотеки процесса</a></li>
            <li><a href="#s5">Что получилось</a></li>
            <li><a href="#s6">Отчёт</a></li>
            <li><a href="#s7">Проверьте себя</a></li>
          </ol>
        </nav>

        <h2 id="s1"><span class="sec">§1</span>Подготовка</h2>

        <p>Нужны VS Code, компилятор и Python из ЛР 1. Создайте в репозитории <code>sysprog-start</code> папку <code>labs/03-libraries</code> и в ней файл <code>libs.c</code>. Программа печатает квадратный корень из числа: <code>argc</code> — сколько слов в команде запуска, без аргументов это 1, значит корень из 2. Число берётся из <code>argc</code>, а не пишется прямо в коде, чтобы компилятор не посчитал корень заранее и программе действительно понадобилась функция <code>sqrt</code>.</p>

        <figure class="code"><figcaption><span>labs/03-libraries/libs.c</span></figcaption><pre>{hl(CODE)}</pre></figure>

{walk_labs.libs_c(hl(CODE))}

        <p data-os="win">Компилятор <code>cl</code> и <code>dumpbin</code> находятся, только если VS Code запущен из <b>x64 Native Tools Command Prompt</b> командой <code>code .</code>. Встроенный терминал переключите на <b>Command Prompt</b>: команды работы написаны для него.</p>

        <div class="margin-note">
          <b>Как читать шаг</b>
          <p>Вверху шага — действие. Ниже — кадр экрана после действия; красные рамки отмечают места, о которых идёт речь, номера рамок повторяются в тексте. Слева под кадром — что на нём видно, справа — что изменилось. Строка «В отчёт» — что записать в <code>report.md</code>. Номера процессов и числа библиотек у вас будут другими.</p>
        </div>

        <h2 id="s2"><span class="sec">§2</span>Два способа подключить библиотеку</h2>

        <p><span class="term">Библиотека</span> — файл с готовыми функциями, которые вызывают другие программы. Подключить её к программе можно двумя способами.</p>

        <div class="table-scroll">
          <table>
            <thead><tr><th></th><th>Статическая компоновка</th><th>Динамическая компоновка</th></tr></thead>
            <tbody>
              <tr><td>Что происходит</td><td>компоновщик копирует нужные функции прямо в файл программы</td><td>в файле только запись «взять функцию из такой-то библиотеки»; её загружает система при запуске</td></tr>
              <tr><td>Сравнение</td><td>рецепт, переписанный в свою тетрадь целиком</td><td>в тетради ссылка: «соус — см. книгу на полке, с. 40»</td></tr>
              <tr><td>Файл библиотеки</td><td><span data-os="win"><code>.lib</code></span><span data-os="mac linux"><code>.a</code></span></td><td><span data-os="win"><code>.dll</code></span><span data-os="mac"><code>.dylib</code></span><span data-os="linux"><code>.so</code></span></td></tr>
              <tr><td>Плюс</td><td>программе ничего не нужно на чужом компьютере</td><td>файл меньше; обновили библиотеку — исправились все программы</td></tr>
              <tr><td>Минус</td><td>ошибку в библиотеке надо исправлять пересборкой каждой программы</td><td>нет библиотеки или не та версия — программа не запустится</td></tr>
            </tbody>
          </table>
        </div>

        <p>Есть и третий путь — загрузить библиотеку уже во время работы, по имени, когда она понадобилась. Так делает <code>ctypes</code> во второй части, и так мозг агента загружает ядро.</p>

        <h2 id="s3"><span class="sec">§3</span>Часть 1. Библиотеки файла</h2>

        <p>В первой части программа собирается, и по её файлу видно, какие библиотеки ей нужны. Затем то же — для интерпретатора Python.</p>

{LAB}

        <h2 id="s5"><span class="sec">§5</span>Что получилось</h2>

        <div class="table-scroll">
          <table>
            <thead><tr><th></th><th>Windows</th><th>macOS</th><th>Linux</th></tr></thead>
            <tbody>
              <tr><td>Чем смотреть библиотеки файла</td><td><code>dumpbin /dependents</code></td><td><code>otool -L</code></td><td><code>ldd</code></td></tr>
              <tr><td>Библиотеки <code>libs</code></td><td><code>KERNEL32.dll</code> — библиотека C внутри файла</td><td><code>libSystem.B.dylib</code></td><td><code>libm.so.6</code>, <code>libc.so.6</code></td></tr>
              <tr><td>Где весь Python</td><td><code>python314.dll</code></td><td>библиотека <code>Python3</code></td><td>в самом <code>python3</code></td></tr>
              <tr><td>Чем смотреть библиотеки процесса</td><td>PowerShell, <code>tasklist /m</code></td><td><code>vmmap</code></td><td><code>/proc/PID/maps</code></td></tr>
              <tr><td>До и после <code>ctypes.CDLL</code></td><td>29 → 30</td><td>171 → 173</td><td>11 → 14</td></tr>
            </tbody>
          </table>
        </div>

        <p>Библиотеку можно увидеть в двух местах: в файле — список того, что загрузится при запуске, и в процессе — то, что загружено сейчас. Второй список длиннее, и он растёт, пока программа работает.</p>

        <h2 id="s6"><span class="sec">§6</span>Отчёт</h2>

        <p>Бланк — в <code>labs/03-libraries/report.md</code>. Замените каждый пропуск <code>___</code> данными со своего экрана. Рядом положите <code>libs.c</code>; собранную программу не добавляйте. Коммит — <code>labs 03: библиотеки, отчёт</code>. После отправки GitHub Actions соберёт <code>libs.c</code> и проверит строку <code>sqrt(2) = 1.414214</code>.</p>

        <pre class="report"># ЛР 3. Библиотеки программы

Система: <span class="blank">___</span>

## Библиотеки файла
Программа напечатала: <span class="blank">___</span>
Команда для списка библиотек файла: <span class="blank">___</span>
Библиотеки libs: <span class="blank">___</span>
Почему в списке нет отдельной математической библиотеки (или почему она есть): <span class="blank">___</span>
Где лежит интерпретатор Python (файл или библиотека): <span class="blank">___</span>

## Библиотеки процесса
PID Python: <span class="blank">___</span>
Библиотек в процессе до ctypes.CDLL: <span class="blank">___</span>, после: <span class="blank">___</span>
Загруженная библиотека и её полный путь: <span class="blank">___</span>
Функция вернула: <span class="blank">___</span>

Не получилось: <span class="blank">___</span>

{snaps.report_pre('03-libraries')}</pre>

{snaps.page_block('03-libraries')}

        <h2 id="s7"><span class="sec">§7</span>Проверьте себя</h2>

        <details>
          <summary>Почему в Windows у libs.exe одна библиотека, а у python.exe — восемь?</summary>
          <p>MSVC по умолчанию собирает программу со статической библиотекой C: <code>printf</code> и <code>sqrt</code> скопированы в <code>libs.exe</code>. Python собран с динамической библиотекой C — <code>VCRUNTIME140.dll</code> и <code>api-ms-win-crt-…</code> — и весь интерпретатор вынесен в <code>python314.dll</code>.</p>
        </details>
        <details>
          <summary>Зачем в Linux ключ -lm?</summary>
          <p>Математические функции в Linux лежат в отдельной библиотеке <code>libm</code>, и компоновщик подключает её только по просьбе: <code>-l</code> значит «подключить библиотеку», <code>m</code> — её имя без <code>lib</code>. Заголовок <code>math.h</code> только объявляет <code>sqrt</code>.</p>
        </details>
        <details>
          <summary>Почему библиотека есть на диске, но её нет в процессе?</summary>
          <p>Процесс загружает только то, что записано в его файле, и то, что он сам попросил во время работы. Остальные библиотеки системы лежат на диске и в память этого процесса не попадают.</p>
        </details>
        <details>
          <summary>Что будет, если в ctypes.CDLL написать имя несуществующей библиотеки?</summary>
          <p>Python сообщит об ошибке: <code>OSError</code> в macOS и Linux, <code>FileNotFoundError</code> в Windows, с текстом, что файл не найден. Программа на C с отсутствующей библиотекой в списке зависимостей не запустилась бы вовсе — ошибку выдал бы загрузчик системы.</p>
        </details>

        <div class="pager">
          <a href="../06-c-dlya-sistemnogo-programmista/index.html">← 1.1 C для системного программиста</a>
          <a href="../../index.html">Оглавление</a>
          <a href="../07-c-i-python-vmeste/index.html">1.2 C и Python вместе →</a>
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
marker = '        <li>\n<div class="lab__do"><b>Запустите Python и узнайте номер процесса'
part2 = ('        </ol>\n\n        <h2 id="s4"><span class="sec">§4</span>Часть 2. Библиотеки процесса</h2>\n\n'
         '        <p>Во второй части в работающий процесс Python загружается библиотека, которой в нём не было, и вызывается её функция. Второй терминал показывает список библиотек процесса до и после.</p>\n\n'
         '        <ol class="lab" start="4" style="counter-reset: lab 3">\n')
assert marker in HTML, 'нет шага 4'
HTML = HTML.replace(marker, part2 + marker, 1)
OUT.write_text(HTML)
print('ok', OUT)
