"""Лабораторная работа 8 «Карта памяти» → temy/21-laboratornaya-8/index.html.

Кадры: Linux — ВМ Ubuntu 24.04 Live (Python 3.14.10 из uv, ps и pmap), Windows — ВМ Win11-lab (Python 3.14 ARM64, Get-Process
и VMMap vmmap64a.exe с ISO win/l8.iso), macOS — MacBook Air (Python 3.14.6, ps и vmmap). Программы — tools/src_lab8 (mem.py, leak.py).
Сырые кадры — ~/sysprog-shots/raw/lab8, рамки — tools/src_lab8/mark8.py. Числа — с кадров (MODUL-2.md). Номера процессов
в шагах macOS различаются: кадры 1–2 сняты в другом запуске."""
from pathlib import Path
from ch12 import hl_py
from lab_build import steps
import snaps
import viz as V

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / 'src_lab8'
OUT = ROOT / 'temy/21-laboratornaya-8/index.html'
LAB = '08-memory-map'


def mk(n):
    return f'<span class="mk">{n}</span>'


def pyfile(name):
    return (f'        <figure class="code"><figcaption><span>labs/{LAB}/{name}</span></figcaption>\n'
            f'<pre>{hl_py((SRC / name).read_text())}</pre>\n        </figure>')


SIZE_WIN = 'powershell -c "Get-Process python | ft Id,WorkingSet64,PrivateMemorySize64,VirtualMemorySize64"'
SIZE_MAC = "ps -o pid,vsz,rss,comm -p $!; vmmap -summary $! | grep 'Physical footprint:'"
SIZE_LIN = 'ps -o pid,vsz,rss,comm -p $!'
MAP_MAC = "vmmap -summary $! | grep -E 'VIRTUAL|REGION TYPE|MALLOC_SMALL  |MALLOC_TINY|^Stack |VM_ALLOCATE|^__TEXT|^__DATA  |^TOTAL '"

PIC_TWO = V.scheme('Две цифры памяти процесса',
    V.split(('Виртуальная — обещано', V.kv([('что это', 'адреса, которые система выдала процессу'), ('стоит', 'почти ничего'),
                                              ('растёт', 'когда процесс просит память')])),
            ('Резидентная — занято', V.kv([('что это', 'страницы, которые лежат в оперативной памяти'), ('стоит', 'настоящие мегабайты'),
                                            ('растёт', 'когда процесс пишет в страницу')]))),
    'Страница — кусок памяти, которым система её раздаёт: 4 КБ в Windows и Linux, 16 КБ в macOS на процессорах Apple.')

PIC_NAMES = V.scheme('Как эти цифры называют программы',
    V.tab(['', 'Виртуальная', 'Резидентная (занятая)'], [
        ['Linux, <code>ps</code>', '<code>VSZ</code>', '<code>RSS</code>'],
        ['Windows, Get-Process', '<code>VirtualMemorySize64</code>', '<code>WorkingSet64</code> — рабочий набор'],
        ['Windows, VMMap', 'Size, Committed', 'Working Set'],
        ['macOS, <code>ps</code> и <code>vmmap</code>', '<code>VSZ</code>, VIRTUAL SIZE', '<code>RSS</code>; честнее — Physical footprint']]),
    '<code>ps</code> печатает размеры в килобайтах, Get-Process — в байтах.')

PIC_STAGES = V.scheme('Что должно происходить на этапах mem.py',
    V.tab(['Этап', 'Виртуальная', 'Резидентная'], [
        ['1. старт', 'как у пустого Python', 'как у пустого Python'],
        ['2. получил 300 МБ', ('+300 МБ', 'is-ok'), 'не меняется'],
        ['3. записал в каждую страницу', '+300 МБ', ('+300 МБ', 'is-bad')],
        ['4. освободил', 'обратно', 'обратно']]),
    'Ожидание, которое проверяет работа. Зелёное — обещание, розовое — настоящие затраты.')

SIMPLE_HOTEL = V.simple('Что такое виртуальная и занятая память',
    '          <p>Представь гостиницу. Процесс звонит и говорит: «забронируйте мне 300 номеров». Гостиница записывает бронь в журнал — это виртуальная память. Номера при этом пустые, бельё не стелили, уборщицы не бегали. Бронь стоит гостинице одну строчку в журнале.</p>\n'
    '          <p>Настоящие расходы начинаются, когда гость заселяется в номер: застелить, включить свет. Это резидентная память — номера, где реально кто-то живёт. Процесс «заселяется» в страницу, когда первый раз в неё пишет.</p>',
    V.steps(V.card('этап 2', 'бронь на 300 номеров', '<small>виртуальная +300 МБ</small>', 'sys'), V.arrow('гость пишет'),
            V.card('этап 3', 'заселились все 300', '<small>резидентная +300 МБ</small>', 'c'), V.arrow('выехал'),
            V.card('этап 4', 'бронь снята', '<small>обе цифры вернулись</small>', 'sys')),
    '<b>Что есть что.</b> Гостиница — система. Журнал броней — виртуальная память процесса. Заселённый номер — страница в оперативной памяти. <code>mmap.mmap(-1, 300 * MB)</code> — бронь, <code>data[i] = 1</code> — заселение, <code>close</code> — выезд.')

SIMPLE_ZIP = V.simple('Почему у macOS RSS почти не вырос',
    '          <p>macOS экономит место: если в номере почти ничего нет, она сворачивает его вещи вакуумным пакетом и убирает в кладовку. Наши 300 МБ — сплошные нули с редкими единицами, они сжимаются отлично.</p>\n'
    '          <p><code>ps</code> считает только номера, где вещи лежат развёрнутыми, поэтому показывает 11 МБ. Physical footprint считает всё, что процесс занимает, вместе с кладовкой: 306,8 МБ. Для вопроса «сколько памяти съел процесс» нужен второй счёт.</p>',
    V.steps(V.card('после записи', '300 МБ нулей', '', 'c'), V.arrow('сжатие'),
            V.card('RSS', '11,7 МБ', '<small>развёрнутые страницы</small>', 'sys'), V.arrow(),
            V.card('Physical footprint', '306,8 МБ', '<small>всё, вместе со сжатым</small>', 'py')),
    '<b>Что есть что.</b> Вакуумный пакет — сжатая память macOS, в <code>vmmap</code> — столбец SWAPPED у строки <code>VM_ALLOCATE</code>: 299,9 МБ.')

SIMPLE_LEAK = V.simple('Как выглядит утечка',
    '          <p>Постоялец каждую секунду приносит в номер новую коробку и ничего не выбрасывает. Через минуту номер забит. <code>leak.py</code> так же каждую секунду кладёт в список 10 МБ и держит их.</p>\n'
    '          <p>Одна цифра ничего не говорит: 137 МБ — может, процессу так и нужно. Утечку выдаёт ряд замеров, где число только растёт.</p>',
    V.steps(V.card('замер 1', '55 МБ', '', 'sys'), V.arrow('2 с'), V.card('замер 2', '76 МБ', '', 'sys'), V.arrow('2 с'),
            V.card('замер 3', '97 МБ', '', 'c'), V.arrow('…'), V.card('замер 5', '138 МБ', '<small>всё время вверх</small>', 'c')),
    '<b>Что есть что.</b> Коробка — <code>bytearray(10 * 1024 * 1024)</code>, номер — список <code>kept</code>. Числа — Linux, шаг 6.')

S = []

S.append(dict(
    do={'win': ('Запустите mem.py и посмотрите размеры', f'В командной строке в папке <code>labs\\{LAB}</code> выполните <code>start /b python mem.py</code>. Программа печатает номер процесса и этап и ждёт 20 секунд до следующего этапа. Сразу выполните<br><code>{SIZE_WIN}</code><br>Столбцы: рабочий набор (занятая память), личная память и виртуальная — в байтах.'),
        'mac': ('Запустите mem.py и посмотрите размеры', f'В Терминале в папке <code>labs/{LAB}</code> выполните <code>python3.14 mem.py &amp;</code>. Программа печатает номер процесса и этап и ждёт 20 секунд до следующего этапа. Сразу выполните<br><code>{SIZE_MAC}</code><br><code>vmmap -summary</code> печатает сводку памяти процесса, <code>grep</code> оставляет строку с физическим следом.'),
        'linux': ('Запустите mem.py и посмотрите размеры', f'В терминале в папке <code>labs/{LAB}</code> выполните <code>python3.14 mem.py &amp;</code>. Программа печатает номер процесса и этап и ждёт 20 секунд до следующего этапа. Сразу выполните <code>{SIZE_LIN}</code>: <code>vsz</code> — виртуальная память, <code>rss</code> — резидентная, в килобайтах.')},
    shot={'win': '01-start.png', 'mac': '01-start.png', 'linux': '01-start.png'},
    notes={'win': (f'<p>{mk(1)} — процесс 8168: рабочий набор 12 521 472 байта (12 МБ), личная 6 062 080 (6 МБ), виртуальная 4 397 719 552 (около 4,1 ГБ).</p>',
                   '<p>Пустой Python занимает 12 МБ, а адресов у него больше 4 ГБ. Виртуальная память Windows включает зарезервированные области, которые процесс ещё не использует.</p>'),
           'mac': (f'<p>{mk(1)} — процесс 14932: <code>VSZ</code> 435 266 992 КБ, <code>RSS</code> 8608 КБ. {mk(2)} — физический след 6944 КБ.</p>',
                   '<p>Пустой Python занимает около 7–9 МБ, а адресов у него — 415 ГБ. В macOS каждый процесс сразу получает огромное адресное пространство, и <code>VSZ</code> здесь почти ничего не говорит.</p>'),
           'linux': (f'<p>{mk(1)} — процесс 4365: <code>VSZ</code> 42 896 КБ, <code>RSS</code> 15 416 КБ.</p>',
                     '<p>Пустой Python обещал себе 42 МБ адресов, а занимает 15 МБ. Разница — части библиотек и областей, в которые процесс ещё не заглядывал.</p>')},
    q='виртуальная и занятая память процесса на старте.'))

S.append(dict(
    do={'win': ('Откройте карту памяти', 'Выполните <code>start vmmap64a -accepteula -p python</code> (на компьютере с x64 — <code>vmmap64</code>). VMMap откроется на процессе <code>python</code>. Посмотрите полосы сверху и таблицу по типам памяти. Закройте окно.'),
        'mac': ('Откройте карту памяти', f'Выполните<br><code>{MAP_MAC}</code><br>Команда печатает сводку по видам областей памяти; <code>grep</code> оставляет главные строки.'),
        'linux': ('Откройте карту памяти', 'Выполните <code>pmap -x $!</code>: <code>pmap</code> печатает каждую область памяти процесса с адресом, размером и тем, что в ней лежит.')},
    shot={'win': '02-map.png', 'mac': '02-map.png', 'linux': '02-map.png'},
    notes={'win': (f'<p>{mk(1)} — Committed: 37 956 K — память, которую система обязалась дать. {mk(2)} — Working Set: 12 240 K. {mk(3)} — строка <b>Shareable</b>: 1 452 K.</p>',
                   '<p>Таблица делит память по видам: Image — файлы программ и библиотек, Heap — куча, Stack — стеки потоков, Private Data — личные данные. Цвета полос сверху — те же виды.</p>'),
           'mac': (f'<p>{mk(1)} — <code>TOTAL</code>: 1.1G виртуальной, 207.7M резидентной.</p>',
                   '<p>Строки — виды областей: <code>__TEXT</code> — код Python и библиотек (282.2M), <code>__DATA</code> — их данные, <code>MALLOC_*</code> — куча, <code>Stack</code> — стек. Резидентная сумма больше <code>RSS</code>: в неё входит общий кэш библиотек, который делят все процессы.</p>'),
           'linux': (f'<p>{mk(1)} — области самого <code>python3.14</code>: код (<code>r-x--</code>), данные только для чтения и для записи. {mk(2)} — итог: 42 896 КБ виртуальной, 15 416 резидентной.</p>',
                     '<p>Ниже — <code>[ anon ]</code> — анонимная память, данные Python без файла; <code>libc.so.6</code> — библиотека C из ЛР 3; <code>[ stack ]</code> — стек главного потока. Столбец <code>Mode</code> — права: чтение, запись, выполнение.</p>')},
    q='из каких частей состоит память процесса и сколько её всего.'))

S.append(dict(
    do={'win': ('Получите 300 МБ', f'Дождитесь строки <code>2. got 300 MB</code> и сразу повторите команду шага 1, затем снова откройте VMMap: <code>start vmmap64a -p python</code>.'),
        'mac': ('Получите 300 МБ', f'Дождитесь строки <code>2. got 300 MB</code> и выполните команды шагов 1 и 2 одной строкой: <code>clear; {SIZE_MAC}; {MAP_MAC}</code>.'),
        'linux': ('Получите 300 МБ', 'Дождитесь строки <code>2. got 300 MB</code> и выполните <code>clear; ps -o pid,vsz,rss,comm -p $!; pmap -x $! | sort -n -k2 | tail -2</code>: <code>sort -n -k2</code> сортирует области по размеру, <code>tail -2</code> оставляет две самые большие.')},
    shot={'win': ['03-mapped.png', '03b-map.png'], 'mac': '03-mapped.png', 'linux': '03-mapped.png'},
    notes={'win': (f'<p>Первый кадр: {mk(1)} — рабочий набор 12 574 720, личная 6 680 576, виртуальная 4 712 292 352 байта — на 300 МБ больше. Второй: {mk(1)} — Committed 345 156 K; {mk(2)} — Working Set 12 248 K; {mk(3)} — Shareable: 308 652 K размер, 307 644 K committed, 264 K в рабочем наборе.</p>',
                   '<p>Система обещала 300 МБ — виртуальная и Committed выросли, — но рабочий набор прежний: страницы не тронуты. Python в Windows получает такую память как общий раздел, поэтому она в строке Shareable и в личную память не попала.</p>'),
           'mac': (f'<p>Процесс на кадре — 11330. {mk(1)} — физический след 6960 КБ. {mk(2)} — строка <code>VM_ALLOCATE (reserved)</code>: 300.0M виртуальной, 0K резидентной, «reserved VM address space (unallocated)».</p>',
                   '<p>Область 300 МБ появилась, но macOS прямо пишет: адреса зарезервированы, память не выделена. След не изменился.</p>'),
           'linux': (f'<p>{mk(1)} — <code>VSZ</code> 350 096 КБ (+300 МБ), <code>RSS</code> 15 416 КБ — прежний. {mk(2)} — новая область 307 200 КБ, в ней резидентно 0.</p>',
                     '<p>Обещание выросло на 300 МБ, а занятая память не изменилась ни на килобайт. Подпись <code>zero (deleted)</code> — так Linux называет общую анонимную память, которую создаёт <code>mmap</code> в Python.</p>')},
    q='виртуальная и занятая память после получения 300 МБ.'))

S.append(dict(
    do={'win': ('Запишите в каждую страницу', 'Дождитесь строки <code>3. wrote to every page</code>: программа записала единицу в каждую страницу. Повторите команду шага 1 и откройте VMMap.'),
        'mac': ('Запишите в каждую страницу', f'Дождитесь строки <code>3. wrote to every page</code>: программа записала единицу в каждую страницу. Повторите команду шага 3.'),
        'linux': ('Запишите в каждую страницу', 'Дождитесь строки <code>3. wrote to every page</code>: программа записала единицу в каждую страницу. Повторите команду шага 3.')},
    shot={'win': ['04-touched.png', '04b-map.png'], 'mac': '04-touched.png', 'linux': '04-touched.png'},
    notes={'win': (f'<p>Первый кадр: {mk(1)} — рабочий набор 327 147 520 байт (312 МБ). Второй: {mk(1)} — Committed прежний, 345 156 K; {mk(2)} — Working Set 319 448 K; {mk(3)} — Shareable в рабочем наборе 307 464 K.</p>',
                   '<p>Виртуальная память не изменилась — обещание то же. Рабочий набор вырос на 300 МБ: каждая страница, в которую записали, стала настоящей памятью.</p>'),
           'mac': (f'<p>{mk(1)} — <code>RSS</code> 11 744 КБ. {mk(2)} — физический след 306.8M. {mk(3)} — <code>VM_ALLOCATE</code>: 303.0M виртуальной, 2640K резидентной, 299.9M в столбце SWAPPED.</p>',
                   '<p>Страницы стали настоящими — след вырос на 300 МБ. Но macOS сразу сжала их: они почти сплошь из нулей. Поэтому <code>RSS</code> почти не вырос, а 299.9M лежат в сжатом виде. Для утечек в macOS смотрят физический след — его же показывает столбец «Память» в Мониторинге системы.</p>'),
           'linux': (f'<p>{mk(1)} — <code>RSS</code> 322 616 КБ. {mk(2)} — в области 307 200 КБ резидентно 307 200.</p>',
                     '<p>Обещание прежнее, а занятая память выросла на 300 МБ: система выдавала страницу при первой записи в неё. Ровно столько, сколько страниц тронули.</p>')},
    q='виртуальная и занятая память после записи в каждую страницу.'))

S.append(dict(
    do={'win': ('Освободите память', 'Дождитесь строки <code>4. freed</code> и повторите команду шага 1.'),
        'mac': ('Освободите память', f'Дождитесь строки <code>4. freed</code> и выполните <code>clear; {SIZE_MAC}</code>.'),
        'linux': ('Освободите память', 'Дождитесь строки <code>4. freed</code> и выполните <code>clear; ps -o pid,vsz,rss,comm -p $!</code>.')},
    shot={'win': '05-freed.png', 'mac': '05-freed.png', 'linux': '05-freed.png'},
    notes={'win': (f'<p>{mk(1)} — рабочий набор 12 574 720, личная 6 062 080, виртуальная 4 397 719 552 байта — как на старте.</p>', '<p><code>close</code> вернул и обещание, и страницы системе.</p>'),
           'mac': (f'<p>{mk(1)} — <code>RSS</code> 9328 КБ, физический след 6848 КБ.</p>', '<p>След вернулся к стартовому. <code>close</code> вернул память системе.</p>'),
           'linux': (f'<p>{mk(1)} — <code>VSZ</code> 42 896, <code>RSS</code> 15 416 КБ — числа шага 1.</p>', '<p><code>close</code> вернул и обещание, и страницы системе: процесс снова такой, каким был на старте.</p>')},
    q='память после освобождения.'))

S.append(dict(
    do={'win': ('Найдите утечку по замерам', 'Выполните <code>start /b python leak.py</code>, затем<br><code>for /l %i in (1,1,5) do @(powershell -c "(Get-Process python).WorkingSet64" &amp; timeout /t 2 &gt;nul)</code><br>Цикл пять раз с паузой 2 секунды печатает рабочий набор.'),
        'mac': ('Найдите утечку по замерам', "Выполните <code>python3.14 leak.py &amp;</code>, затем<br><code>for i in 1 2 3 4 5; do vmmap -summary $! | grep 'Physical footprint:'; sleep 2; done</code><br>Цикл пять раз с паузой 2 секунды печатает физический след."),
        'linux': ('Найдите утечку по замерам', 'Выполните <code>python3.14 leak.py &amp;</code>, затем <code>for i in 1 2 3 4 5; do ps -o rss= -p $!; sleep 2; done</code>: цикл пять раз с паузой 2 секунды печатает <code>RSS</code>. После замеров остановите программу: <code>kill %1</code>.')},
    shot={'win': '06-leak.png', 'mac': '06-leak.png', 'linux': '06-leak.png'},
    notes={'win': (f'<p>{mk(1)} — 75 415 552 → 96 395 264 → 117 374 976 → 138 354 688 → 159 338 496 байт.</p>', '<p>Каждые 2 секунды +21 МБ — две новые порции по 10 МБ. Число только растёт.</p>'),
           'mac': (f'<p>{mk(1)} — 36.6M → 56.7M → 86.8M → 106.9M → 137.0M.</p>', '<p>След растёт на 20–30 МБ каждые 2 секунды. <code>RSS</code> здесь не годится: macOS сжимает страницы, и он то растёт, то падает, хотя программа только копит.</p>'),
           'linux': (f'<p>{mk(1)} — 55 676 → 76 164 → 96 652 → 117 140 → 137 628 КБ.</p>', '<p>Каждые 2 секунды ровно +20 480 КБ — две порции по 10 МБ. Число только растёт: так и выглядит утечка.</p>')},
    q='пять замеров и на сколько память росла за 2 секунды.'))

STEPS = steps(S, LAB)

HTML = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>Лабораторная работа 8. Карта памяти · Справочник по системному программированию</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,600;0,7..72,700;1,7..72,400&family=Pixelify+Sans:wght@500;600;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css">
</head>
<body>
  <div class="book">
    <div class="book__body">
      <div class="spine"><span>Модуль 2 · Лабораторная работа 8</span></div>

      <main class="leaf">
        <div class="running">
          <p class="eyebrow"><a href="../../index.html" style="text-decoration:none;color:inherit">Справочник по системному программированию</a> · модуль 2 · лабораторная работа</p>
          <p class="running__folio">ЛР 8</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">ЛР 8</span>
          <h1>Карта<br>памяти</h1>
          <p class="lead">Программа на Python просит у системы 300 МБ, а занятая память не растёт ни на килобайт — пока программа в эти мегабайты ничего не запишет. В работе видно, чем память, которую система пообещала процессу, отличается от памяти, которую он действительно занимает, как выглядит карта памяти процесса и как по ряду замеров находят утечку.</p>
        </header>

        <dl class="passport">
          <div><dt>Пара</dt><dd>8</dd></div>
          <div><dt>Время</dt><dd>35–40 минут</dd></div>
          <div><dt>Программы</dt><dd><span data-os="win">VMMap, PowerShell, командная строка</span><span data-os="mac"><code>ps</code>, <code>vmmap</code>, Терминал</span><span data-os="linux"><code>ps</code>, <code>pmap</code>, терминал</span>, Python 3.14</dd></div>
          <div><dt>Сдать</dt><dd><code>report.md</code> и {len(snaps.SNAPS[LAB])} снимка в <code>screenshots/</code> в папке <code>labs/{LAB}</code> репозитория <code>sysprog-start</code></dd></div>
        </dl>

        <nav class="contents">
          <b>В этой работе</b>
          <ol>
            <li><a href="#s1">Подготовка</a></li>
            <li><a href="#s2">Обещанная и занятая память</a></li>
            <li><a href="#s3">Ход работы</a></li>
            <li><a href="#s4">Что получилось</a></li>
            <li><a href="#s5">Отчёт</a></li>
            <li><a href="#s6">Проверьте себя</a></li>
          </ol>
        </nav>

        <h2 id="s1"><span class="sec">§1</span>Подготовка</h2>

        <p>Нужен Python 3.14 из ЛР 7. <span data-os="win">Карту памяти показывает VMMap из набора Sysinternals: скачайте <code>VMMap.zip</code> с сайта Microsoft Learn и распакуйте в свою папку. На компьютере с процессором ARM запускается <code>vmmap64a.exe</code>, с x64 — <code>vmmap64.exe</code>; папку добавьте в <code>PATH</code> или запускайте программу по полному пути.</span><span data-os="mac"><code>ps</code> и <code>vmmap</code> входят в macOS.</span><span data-os="linux"><code>ps</code> и <code>pmap</code> входят в Ubuntu.</span> В шаблоне в папке <code>labs/{LAB}</code> лежат бланк <code>report.md</code>, папка <code>screenshots/</code> и две программы. Первая — <code>mem.py</code>:</p>
{pyfile('mem.py')}
        <p>Программа проходит четыре этапа и на каждом ждёт 20 секунд. За это время нужно успеть выполнить команду шага. <code>mmap.mmap(-1, 300 * MB)</code> просит у системы 300 МБ памяти, не связанной с файлом. Цикл записывает единицу в каждую страницу: <code>mmap.PAGESIZE</code> — размер страницы. <code>close</code> возвращает память системе. Вторая программа, <code>leak.py</code>, каждую секунду добавляет в список ещё 10 МБ и ничего не освобождает.</p>
{pyfile('leak.py')}

        <div class="margin-note">
          <b>Как читать шаг</b>
          <p>Вверху шага — действие. Ниже — кадр экрана после действия; красные рамки отмечают места, о которых идёт речь. Слева под кадром — что на нём видно, справа — что изменилось. Строка «В отчёт» — что записать в <code>report.md</code>. Номера процессов и размеры у вас будут другими. Если не успели выполнить команду за 20 секунд этапа, остановите программу (<span data-os="win"><code>taskkill /im python.exe /f</code></span><span data-os="mac linux"><code>kill %1</code></span>) и запустите её снова.</p>
        </div>

        <h2 id="s2"><span class="sec">§2</span>Обещанная и занятая память</h2>

        <p>Каждый процесс видит свою память как длинный ряд адресов — <span class="term">виртуальную память</span>. Система раздаёт её кусками — <span class="term">страницами</span>. Получить адреса и получить настоящую память — разные события. Адреса процесс получает, когда просит. Страницу в оперативной памяти он получает, когда первый раз в неё пишет. Страницы процесса, которые лежат в оперативной памяти, — <span class="term">резидентная память</span>.</p>

        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>Гостиница принимает бронь на сотню номеров одной строкой в журнале. Убирать и стелить начинают, только когда гость заселяется.</p>
          <p class="miss">Гость заселяется в номер целиком. Процесс «заселяет» страницу, даже если записал в неё один байт.</p>
        </div></div>
{PIC_TWO}
        <p>Левая половина — обещание, правая — настоящие затраты. Мониторы показывают обе цифры, но называют их по-разному:</p>
{PIC_NAMES}
        <p>Отсюда ожидание для <code>mem.py</code> — ход работы его проверит:</p>
{PIC_STAGES}
{SIMPLE_HOTEL}

        <h2 id="s3"><span class="sec">§3</span>Ход работы</h2>

{STEPS}
{SIMPLE_ZIP}
{SIMPLE_LEAK}

        <h2 id="s4"><span class="sec">§4</span>Что получилось</h2>

        <div class="table-scroll">
          <table>
            <thead><tr><th>Этап</th><th>Windows: виртуальная / рабочий набор</th><th>macOS: RSS / физический след</th><th>Linux: VSZ / RSS</th></tr></thead>
            <tbody>
              <tr><td>Старт</td><td>4,10 ГБ / 12 МБ</td><td>8,4 / 6,8 МБ</td><td>42 / 15 МБ</td></tr>
              <tr><td>Получил 300 МБ</td><td>4,39 ГБ / 12 МБ</td><td>след 6,8 МБ, область «reserved»</td><td>342 / 15 МБ</td></tr>
              <tr><td>Записал в каждую страницу</td><td>4,39 ГБ / 312 МБ</td><td>11,5 / 306,8 МБ</td><td>342 / 315 МБ</td></tr>
              <tr><td>Освободил</td><td>4,10 ГБ / 12 МБ</td><td>9,1 / 6,7 МБ</td><td>42 / 15 МБ</td></tr>
              <tr><td>Утечка, 5 замеров за 8 с</td><td>72 → 152 МБ</td><td>след 36,6 → 137,0 МБ</td><td>54 → 134 МБ</td></tr>
            </tbody>
          </table>
        </div>

        <p>На трёх системах просьба о памяти увеличила только обещание, а занятая память выросла лишь после записи. Освобождение вернуло обе цифры. Утечку выдаёт ряд замеров, где память только растёт; одно число её не показывает. Мерить нужно правильную цифру: в Windows и Linux — рабочий набор и <code>RSS</code>, в macOS — физический след, потому что macOS сжимает страницы и <code>RSS</code> там обманывает.</p>

        <h2 id="s5"><span class="sec">§5</span>Отчёт</h2>

        <p>Бланк — в <code>labs/{LAB}/report.md</code>. Замените каждый пропуск <code>___</code> данными со своего экрана, снимки положите в <code>screenshots/</code>. Коммит — <code>labs 08: карта памяти, отчёт</code>.</p>

        <pre class="report"># ЛР 8. Карта памяти

Система: <span class="blank">___</span>
Чем мерил (виртуальная и занятая): <span class="blank">___</span>

## Этапы mem.py
Старт: <span class="blank">___</span>
Получил 300 МБ: <span class="blank">___</span>
Записал в каждую страницу: <span class="blank">___</span>
Освободил: <span class="blank">___</span>
Почему занятая память выросла только на третьем этапе: <span class="blank">___</span>

## Карта памяти
Из каких частей состоит память процесса: <span class="blank">___</span>

## Утечка
Пять замеров leak.py: <span class="blank">___</span>
На сколько росла память за 2 секунды: <span class="blank">___</span>

Не получилось: <span class="blank">___</span>

{snaps.report_pre(LAB)}</pre>

{snaps.page_block(LAB)}

        <h2 id="s6"><span class="sec">§6</span>Проверьте себя</h2>

        <details>
          <summary>Почему после <code>mmap</code> на 300 МБ занятая память не изменилась?</summary>
          <p>Система выдала процессу адреса, но страницы в оперативной памяти даёт только при первой записи. Пока страницу не трогали, она ничего не стоит.</p>
        </details>
        <details>
          <summary>Какая цифра показывает, сколько памяти процесс действительно занимает?</summary>
          <p>Резидентная: <code>RSS</code> в Linux, рабочий набор в Windows. В macOS — физический след: он учитывает и сжатые страницы.</p>
        </details>
        <details>
          <summary>Почему в macOS <code>RSS</code> после записи почти не вырос?</summary>
          <p>Страницы почти сплошь из нулей, и macOS сразу их сжала. Сжатые страницы не входят в <code>RSS</code>, но входят в физический след — 306,8 МБ.</p>
        </details>
        <details>
          <summary>Как отличить утечку от программы, которой просто нужно много памяти?</summary>
          <p>По ряду замеров. Программе, которой нужно много, память растёт до какого-то уровня и останавливается. При утечке она растёт без остановки.</p>
        </details>
        <details>
          <summary>Что такое страница?</summary>
          <p>Кусок памяти, которым система её выдаёт: 4 КБ в Windows и Linux, 16 КБ в macOS на процессорах Apple. Записав один байт, процесс получает всю страницу.</p>
        </details>

        <div class="pager">
          <a href="../20-potoki/index.html">← 2.4 Потоки</a>
          <a href="../../index.html">Оглавление</a>
          <a href="../22-laboratornaya-9/index.html">ЛР 9 Разбор падения →</a>
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
