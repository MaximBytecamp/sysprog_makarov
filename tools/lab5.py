"""Лабораторная работа 5 «Рождение процесса» → temy/15-laboratornaya-5/index.html.

Кадры: Linux — ВМ Ubuntu-lab-01 (Ubuntu 24.04.4 Live, strace 6.8, команды — ~/sysprog-shots/l5linux.txt), Windows — ВМ Win11-lab
(Windows 11 24H2 ARM64, Process Monitor Procmon64a.exe с ISO ~/sysprog-shots/win/procmon.iso), macOS — fs_usage (нужен sudo).
Программа во всех шагах — hostname: ping под strace теряет право на сетевой сокет (cap_net_raw) и выходит с кодом 2.
Сырые кадры — ~/sysprog-shots/raw/lab5, рамки — tools/src_lab5/mark5.py. Числа в тексте — с кадров."""
from pathlib import Path
from lab_build import steps, gist, see
import snaps
import viz as V

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'temy/15-laboratornaya-5/index.html'


def mk(n):
    return f'<span class="mk">{n}</span>'


def birth(*items):
    out = []
    for k, (label, title, note, kind) in enumerate(items):
        if k:
            out.append(V.arrow())
        out.append(V.card(label, title, f'<small>{note}</small>' if note else '', kind))
    return V.steps(*out)


PIC_BIRTH = V.scheme('Как родитель запускает программу',
    '<div data-os="win">' + birth(('родитель', '<code>cmd.exe</code>', 'вызывает CreateProcessW', 'c'),
                                  ('ядро', 'новый процесс', 'номер, память, первый поток', 'sys'),
                                  ('загрузчик', 'HOSTNAME.EXE и DLL', 'ntdll.dll, kernel32.dll, …', 'sys'),
                                  ('ребёнок', '<code>hostname</code> работает', 'печатает имя и завершается с кодом', 'py')) + '</div>'
    + '<div data-os="mac linux">' + birth(('родитель', '<code>bash</code>', '<span data-os="linux">clone</span><span data-os="mac">fork</span>: копия родителя', 'c'),
                                          ('копия', 'тот же код', 'новый номер процесса', 'sys'),
                                          ('execve', '<code>hostname</code> вместо копии', 'загрузчик подключает библиотеки', 'sys'),
                                          ('ребёнок', '<code>hostname</code> работает', 'печатает имя и завершается с кодом', 'py')) + '</div>',
    '<span data-os="win">В Windows рождение — один вызов: ядро создаёт процесс и сразу загружает в него программу.</span>'
    '<span data-os="mac linux">В <span data-os="mac">macOS</span><span data-os="linux">Linux</span> рождение — два вызова: сначала копия родителя, потом в копию загружается новая программа. Номер процесса появляется на первом шаге и после второго не меняется.</span>')

PIC_WAIT = V.scheme('Код завершения: от ребёнка к родителю',
    V.steps(V.card('ребёнок', '<code>exit 7</code>', '<small>процесс завершается и оставляет число</small>', 'py'), V.arrow('код хранит ядро'),
            V.card('ядро', 'запись о процессе', '<small>код 7 хранится, пока его не заберут</small>', 'sys'), V.arrow('родитель ждёт'),
            V.card('родитель', '<span data-os="win"><code>%errorlevel%</code></span><span data-os="mac linux"><code>$?</code></span>', '<small>получил 7</small>', 'c')),
    '<span data-os="win">Командная строка ждёт ребёнка функцией WaitForSingleObject и читает код функцией GetExitCodeProcess.</span>'
    '<span data-os="mac linux">Оболочка ждёт ребёнка вызовом <code>wait4</code>: он возвращает номер завершившегося процесса и его код.</span>')

S = []

S.append(dict(
    why='Сначала смотрим на сам момент рождения: кто просит создать процесс, что для этого делает ядро и как это выглядит в записи.',
    see={'win': [see('Окно фильтра Process Monitor поверх главного окна. Фильтр оставляет в записи только нужные события. Внизу окна — список условий, столбцы: Column (что проверять), Relation (как сравнивать), Value (значение), Action (что делать с подходящими событиями).',
                     'Четыре условия с действием <b>Include</b> (включить): <code>Process Name is HOSTNAME.EXE</code>, <code>cmd.exe</code>, <code>python.exe</code> и <code>Event Class is Process</code>. Условия одного столбца объединяются через «или», разных столбцов — через «и». В записи останутся события процессов этих трёх программ.',
                     'Кнопка <b>Add</b> (добавить) переносит в список условие из верхней строки. Так появилось последнее из четырёх: <code>Event Class is Process</code>.'),
                 see('Главное окно Process Monitor после записи. Одна строка — одно событие. Столбцы: Time (время), Process Name (имя процесса), PID (номер процесса), Operation (операция), Path (путь), Result (результат), Detail (подробности). В строке состояния внизу: <code>Showing 34 of 128 546 events</code> — фильтр оставил 34 события из 128 546.',
                     'Строка <code>cmd.exe</code>, номер 1988, операция <code>Process Create</code> (создание процесса). В Path — <code>C:\\WINDOWS\\system32\\HOSTNAME.EXE</code>, в Detail — <code>PID: 804</code>. Родитель создал процесс с номером 804.',
                     'Первая строка нового процесса <code>HOSTNAME.EXE</code>, номер 804, операция <code>Process Start</code> (начало процесса). В Detail — <code>Parent PID: 1988</code>: родитель — процесс 1988, то есть <code>cmd.exe</code>.'),
                 see('Окно <b>Event Properties</b> — свойства события. Оно открывается двойным щелчком по строке. На вкладке Event открыто событие <code>Process Start</code> процесса <code>HOSTNAME.EXE</code>.',
                     'Поле <b>Operation</b>: <code>Process Start</code> — первое событие нового процесса.',
                     'Что процесс получил от родителя: <code>Parent PID</code> — номер родителя, 1988; <code>Command line</code> — командная строка, то есть команда запуска, <code>hostname</code>; <code>Current directory</code> — текущая папка процесса, <code>C:\\Users\\user\\</code>.',
                     'Поле <b>Environment</b>: переменные окружения — пары «имя=значение», например <code>COMPUTERNAME=WIN11-LAB</code> и <code>ComSpec=C:\\WINDOWS\\system32\\cmd.exe</code>. Это копия переменных <code>cmd.exe</code>.')],
         'mac': see('Два окна Терминала. Верхнее — запись <code>fs_usage -f exec</code>, нижнее — команды. В верхнем одна строка — один запуск программы. Столбцы: время, вызов, путь программы, время вызова в секундах, процесс.',
                    'Строка с вызовом <code>execve</code> (загрузка программы) и путём <code>/bin/hostname</code>. Время вызова — 0,000918 секунды. В последнем столбце — <code>bash.23813159</code>: вызов сделал процесс <code>bash</code>, число после точки — номер потока внутри процесса.',
                    'Нижнее окно, команда <code>echo $$; hostname</code>. Первая строка вывода — 37027, номер самой оболочки. Вторая — <code>MacBook-Air-Maxim.local</code>, имя компьютера, которое напечатал <code>hostname</code>.'),
         'linux': see('Окно терминала Ubuntu. Сверху команда <code>strace</code>, ниже её вывод: одна строка — один системный вызов, то есть обращение программы к ядру. В квадратных скобках <code>[pid …]</code> — номер процесса, который сделал вызов. Число после знака равенства — результат вызова.',
                      'Вызов <code>clone(...) = 3862</code>: оболочка <code>bash</code>, номер 3861, создала свою копию. Результат вызова — номер копии, 3862.',
                      'В процессе 3862 вызов <code>execve("/usr/bin/hostname", ["hostname"], … /* 47 vars */) = 0</code>: копия заменила программу <code>bash</code> на <code>hostname</code>. В скобках — путь к программе, её аргументы и 47 переменных окружения. Результат 0 означает успех. Ниже рамки слово <code>ubuntu</code> — имя компьютера, которое напечатал <code>hostname</code>.',
                      'Вызов <code>exit_group(0)</code> в процессе 3862: процесс завершается с кодом 0.',
                      'Вызов <code>wait4</code> у родителя вернул 3862, в скобках <code>WEXITSTATUS(s) == 0</code>: оболочка дождалась ребёнка и получила его код 0. Ниже строка <code>code 0</code> — тот же код, который напечатала команда <code>echo</code>.')},
    do={'win': ('Запишите рождение процесса', 'Запустите Process Monitor (<code>Procmon64.exe</code>, на компьютере с ARM — <code>Procmon64a.exe</code>) и примите лицензию. Запись начнётся сразу: остановите её <kbd>Ctrl</kbd>+<kbd>E</kbd> и очистите список <kbd>Ctrl</kbd>+<kbd>X</kbd>. Откройте фильтр <kbd>Ctrl</kbd>+<kbd>L</kbd>: выберите <b>Process Name</b>, <b>is</b>, введите <code>HOSTNAME.EXE</code>, оставьте <b>Include</b> и нажмите <b>Add</b>. Так же добавьте <code>cmd.exe</code>, <code>python.exe</code> и условие <b>Event Class is Process</b>, затем <b>OK</b>. Включите запись <kbd>Ctrl</kbd>+<kbd>E</kbd>, в командной строке выполните <code>hostname</code>, вернитесь в Process Monitor и остановите запись. Дважды щёлкните по строке <code>Process Start</code>.'),
        'mac': ('Запишите рождение процесса', 'Откройте два окна Терминала: верхнее широкое — для записи, нижнее — для команд. В нижнем выполните <code>bash</code>: <code>fs_usage</code> по умолчанию скрывает события оболочек <code>zsh</code> и <code>sh</code>. Оболочки <code>bash</code> в этом списке нет, поэтому команды работы выполняются в ней. В верхнем окне выполните <code>sudo fs_usage -f exec</code> и введите пароль: <code>fs_usage</code> печатает обращения процессов к ядру, <code>-f exec</code> оставляет только запуск программ. В нижнем окне выполните <code>echo $$; hostname</code>: <code>$$</code> — номер самой оболочки. В верхнем остановите запись <kbd>Ctrl</kbd>+<kbd>C</kbd>.'),
        'linux': ('Запишите рождение процесса', 'Откройте терминал и разверните окно. Выполните <code>strace -f -e trace=process bash -c \'hostname; echo code $?\'</code>. <code>strace</code> запускает программу и показывает каждое её обращение к ядру — системный вызов. Нам нужны только вызовы, которые создают, запускают и ждут процессы, в том числе дочерние. Оболочка <code>bash</code> выполнит <code>hostname</code> и напечатает код завершения.<br>Ключи: <code>-f</code> — следить за детьми, <code>-e trace=process</code> — оставить вызовы про процессы, <code>bash -c</code> — выполнить строку.')},
    shot={'win': ['00-filter.png', '01-birth.png', '01b-start.png'], 'linux': '01-birth.png',
          'mac': '01-birth.png'},
    notes={'win': (f'<p>Первый кадр — фильтр: {mk(1)} четыре условия <b>Include</b>, {mk(2)} кнопка <b>Add</b>. Условия одного столбца объединяются через «или», разных столбцов — через «и»: остаются события процессов <code>cmd.exe</code>, <code>HOSTNAME.EXE</code> и <code>python.exe</code>.</p>'
                    f'<p>Второй кадр — запись. {mk(1)} — <code>cmd.exe</code> с номером 1988 выполняет <code>Process Create</code>: путь <code>C:\\WINDOWS\\system32\\HOSTNAME.EXE</code>, в столбце Detail — номер нового процесса, 804. {mk(2)} — первое событие нового процесса, <code>Process Start</code>, в Detail — <code>Parent PID: 1988</code>.</p>'
                    f'<p>Третий кадр — свойства события <code>Process Start</code>. {mk(1)} — операция. {mk(2)} — что новый процесс получил от родителя: номер родителя 1988, командную строку <code>hostname</code> и текущую папку. {mk(3)} — переменные окружения, копия переменных <code>cmd.exe</code>.</p>',
                    '<p>Командная строка не запускает программу сама: она просит ядро функцией <code>CreateProcessW</code>. Ядро создаёт процесс, загружает в него программу и запускает первый поток. В записи родителя это одно событие <code>Process Create</code>, у ребёнка жизнь начинается с <code>Process Start</code>.</p>'),
           'mac': (f'<p>{mk(1)} — строка записи: время, вызов <code>execve</code>, путь <code>/bin/hostname</code>, время вызова в секундах и процесс, который его сделал, — <code>bash</code>. Число после точки — номер потока внутри процесса. {mk(2)} — в нижнем окне номер оболочки 37027 и имя компьютера, которое напечатал <code>hostname</code>.</p>',
                   '<p><code>execve</code> вызвала копия оболочки, поэтому у неё имя <code>bash</code>. Оболочка сначала создаёт копию себя вызовом <code>fork</code>, и копия вызывает <code>execve</code>, чтобы загрузить в себя <code>hostname</code>. Вызов <code>fork</code> режим <code>-f exec</code> не показывает, видна только вторая половина рождения. Если в записи много строк других программ, перечислите их имена после ключа <code>-e</code>: <code>sudo fs_usage -e -f exec "Code Helper (Plugin)"</code>.</p>'),
           'linux': (f'<p>{mk(1)} — <code>clone(...) = 3862</code>: <code>bash</code> с номером 3861 создаёт свою копию, у копии номер 3862. {mk(2)} — в процессе 3862 вызов <code>execve("/usr/bin/hostname", ["hostname"], … /* 47 vars */) = 0</code>: копия заменяет программу <code>bash</code> на <code>hostname</code>. В скобках — путь к программе, её аргументы и 47 переменных окружения. Ниже <code>hostname</code> печатает имя компьютера <code>ubuntu</code>. {mk(3)} — <code>exit_group(0)</code>: процесс завершается с кодом 0. {mk(4)} — <code>wait4</code> возвращает 3862 и <code>WEXITSTATUS(s) == 0</code>: оболочка дождалась ребёнка и получила его код.</p>',
                     '<p>Рождение заняло два вызова: <code>clone</code> создал копию оболочки, <code>execve</code> загрузил в копию другую программу. Номер 3862 появился при <code>clone</code> и после <code>execve</code> остался тем же. Последняя строка <code>code 0</code> — тот же код, который оболочка получила в <code>wait4</code>.</p>')},
    q='имя и номер родителя, номер нового процесса и <span data-os="win">событие</span><span data-os="mac linux">вызов</span>, которым он создан.'))

S.append(dict(
    why='Программа hostname крошечная, но без библиотек она не работает. Смотрим, кто подключает их, пока сама программа ещё не начала работу.',
    see={'win': see('Главное окно Process Monitor, запись прокручена в конец. Операция <code>Load Image</code> — загрузка в процесс файла программы или библиотеки (файла <code>.dll</code>). Все строки на кадре — процесс <code>HOSTNAME.EXE</code>, номер 804.',
                    'Первые четыре библиотеки: <code>ntdll.dll</code>, <code>kernel32.dll</code>, <code>KernelBase.dll</code> и <code>msvcrt.dll</code>. Выше рамки стоит <code>Load Image</code> самой программы <code>HOSTNAME.EXE</code>.',
                    'Ещё 14 библиотек, среди них сетевые <code>ws2_32.dll</code>, <code>mswsock.dll</code> и <code>dnsapi.dll</code>. Имя компьютера <code>hostname</code> узнаёт через сетевые функции.',
                    'Строка <code>Process Exit</code> (завершение процесса). В Detail — <code>Exit Status: 0</code>: код завершения 0, процесс закончил работу без ошибки.'),
         'mac': see('Два окна Терминала. Сверху — вывод <code>fs_usage -f pathname</code>, отфильтрованный по слову <code>hostname</code>. Одна строка — одно обращение к файлу. Столбцы: время, вызов, путь, время вызова, имя процесса. Снизу — команда <code>hostname</code> и её вывод, <code>MacBook-Air-Maxim.local</code>.',
                    'Первые обращения нового процесса: <code>/usr/lib/dyld</code> — загрузчик macOS (<code>dyld</code>), <code>/bin/hostname</code> — сама программа и папка <code>/System/Library/dyld</code>, которую открыл загрузчик.',
                    'Файл <code>dyld_shared_cache_arm64e</code> (вызов <code>fsgetpath</code> — получение пути): общий кэш системных библиотек. Начало пути обрезано границей окна.',
                    'Загрузчик открывает файл программы <code>/bin/hostname</code> (вызов <code>open</code>), закрывает его (<code>close</code>) и открывает снова.'),
         'linux': see('Окно терминала Ubuntu. Команда <code>strace -e trace=openat hostname</code> показывает только открытия файлов. В скобках вызова — путь к файлу, число после знака равенства (3) — номер, под которым файл открыт в процессе. Ниже — слово <code>ubuntu</code>, имя компьютера, и строка <code>+++ exited with 0 +++</code>: процесс завершился с кодом 0.',
                      'Загрузчик открыл <code>/etc/ld.so.cache</code> — список библиотек системы и путей к ним. По нему он ищет нужный файл.',
                      'Загрузчик открыл <code>/lib/aarch64-linux-gnu/libc.so.6</code> — стандартную библиотеку C. Других библиотек <code>hostname</code> не открывает.')},
    do={'win': ('Посмотрите библиотеки нового процесса', 'Закройте окно свойств и прокрутите запись в конец (<kbd>End</kbd>).'),
        'mac': ('Посмотрите библиотеки нового процесса', 'В верхнем окне выполните <code>sudo fs_usage -f pathname | grep hostname</code>. <code>-f pathname</code> оставляет обращения к файлам по имени, а <code>grep hostname</code> — только строки, где встречается <code>hostname</code>: в последнем столбце стоит имя процесса. В нижнем окне выполните <code>hostname</code>, подождите несколько секунд и остановите запись.'),
        'linux': ('Посмотрите библиотеки нового процесса', 'Выполните <code>strace -e trace=openat hostname</code>. <code>openat</code> — вызов, которым процесс открывает файл; <code>-f</code> здесь не нужен, потому что <code>hostname</code> детей не запускает.')},
    shot={'win': '02-libs.png', 'linux': '02-libs.png',
          'mac': '02-libs.png'},
    notes={'win': (f'<p>{mk(1)} — первые библиотеки: <code>ntdll.dll</code>, <code>kernel32.dll</code>, <code>KernelBase.dll</code>, <code>msvcrt.dll</code>. {mk(2)} — ещё 14 библиотек, среди них сетевые <code>ws2_32.dll</code>, <code>mswsock.dll</code>, <code>dnsapi.dll</code>: <code>hostname</code> узнаёт имя компьютера через сетевые функции. {mk(3)} — <code>Process Exit</code>, в Detail — <code>Exit Status: 0</code>.</p>',
                    '<p>Первой строкой <code>Load Image</code> идёт сама программа <code>HOSTNAME.EXE</code>, второй — <code>ntdll.dll</code>: её ядро загружает в каждый процесс. Остальные библиотеки подключает загрузчик из <code>ntdll.dll</code> по списку, записанному в файле программы, — тот список, который в ЛР 3 печатал <code>dumpbin /dependents</code>. Всего 18 библиотек ради программы, которая печатает одну строку.</p>'),
           'mac': (f'<p>{mk(1)} — первые обращения нового процесса: <code>/usr/lib/dyld</code> — загрузчик macOS, и папка <code>/System/Library/dyld</code>. {mk(2)} — файл <code>dyld_shared_cache_arm64e</code>: общий кэш системных библиотек. {mk(3)} — загрузчик открывает сам файл программы <code>/bin/hostname</code>.</p>',
                   '<p>Отдельных файлов библиотек в записи нет. В macOS системные библиотеки собраны в один большой файл — общий кэш, и <code>dyld</code> подключает его целиком; в каждом процессе он уже лежит в памяти. Поэтому в ЛР 3 <code>otool -L</code> показывал пути к библиотекам, которых нет на диске отдельными файлами: они внутри кэша.</p>'),
           'linux': (f'<p>{mk(1)} — <code>/etc/ld.so.cache</code>: список библиотек системы и путей к ним, по нему загрузчик ищет нужный файл. {mk(2)} — <code>/lib/aarch64-linux-gnu/libc.so.6</code>, стандартная библиотека C. Других библиотек <code>hostname</code> не открывает.</p>',
                     '<p>Оба файла открывает загрузчик <code>ld-linux</code> ещё до функции <code>main</code> программы. Саму программу и загрузчик ядро подключило при <code>execve</code>, поэтому их открытия в этом выводе нет. Программе <code>hostname</code> хватает одной библиотеки — это видно и командой <code>ldd /usr/bin/hostname</code> из ЛР 3.</p>')},
    q='сколько библиотек загрузил процесс и какая из них первая.'))

S.append(dict(
    why='Процесс закончил работу. Как родитель узнаёт, получилось ли у ребёнка? По числу — коду завершения. Смотрим на него со стороны ребёнка и со стороны родителя.',
    see={'win': see('Главное окно Process Monitor. На кадре события двух процессов <code>cmd.exe</code>: родителя с номером 1988 и нового с номером 7940. Новый — вторая командная строка, которую запустила команда <code>cmd /c exit 7</code>. В окне командной строки, которого на кадре не видно, <code>echo</code> печатает <code>code 7</code>.',
                    'Строка <code>cmd.exe</code> 1988, операция <code>Process Create</code>. В Path — <code>C:\\WINDOWS\\system32\\cmd.exe</code>, в Detail — <code>PID: 7940</code>. Родитель создал второй <code>cmd.exe</code>.',
                    'Операция <code>Process Start</code> процесса 7940, в Detail — <code>Parent PID: 1988</code>.',
                    'Последнее событие процесса 7940 — <code>Process Exit</code>. В Detail — <code>Exit Status: 7</code>: процесс завершился с кодом 7.'),
         'mac': see('Два окна Терминала. Сверху — запись <code>fs_usage -f exec</code>, снизу — команда со второй оболочкой <code>bash</code>, которая сразу завершается с кодом 7.',
                    'Строка с вызовом <code>execve</code> и путём <code>/bin/bash</code>, процесс <code>bash.23823227</code>: копия оболочки загружает в себя вторую оболочку <code>bash</code>. Строки о завершении процесса в записи нет.',
                    'Нижнее окно: после команды напечатано <code>code 7</code>. Это код второй оболочки, который родитель взял из <code>$?</code>.'),
         'linux': see('Окно терминала Ubuntu, вывод <code>strace -f</code>. Процесс 3873 — вторая оболочка <code>sh</code>, её создал <code>bash</code> с номером 3872.',
                      'В процессе 3873 вызов <code>exit_group(7)</code>: <code>sh</code> завершается с кодом 7. Строка ниже, <code>+++ exited with 7 +++</code>, подтверждает это.',
                      'Вызов <code>wait4</code> у родителя вернул 3873, в скобках <code>WEXITSTATUS(s) == 7</code>: родитель получил код 7.',
                      'Строка <code>code 7</code>: команда <code>echo</code> напечатала код, который оболочка взяла из <code>$?</code>.')},
    do={'win': ('Получите код завершения', 'Очистите запись <kbd>Ctrl</kbd>+<kbd>X</kbd> и включите её <kbd>Ctrl</kbd>+<kbd>E</kbd>. В командной строке выполните <code>cmd /c exit 7</code>: вторая командная строка сразу завершится с кодом 7. Затем выполните <code>echo code %errorlevel%</code>: переменная <code>errorlevel</code> хранит код последней команды. Остановите запись и прокрутите её в конец.'),
        'mac': ('Получите код завершения', 'В верхнем окне снова выполните <code>sudo fs_usage -f exec</code>. В нижнем выполните <code>bash -c \'exit 7\'; echo code $?</code>: вторая оболочка <code>bash</code> сразу завершится с кодом 7, а <code>$?</code> — код последней команды. Остановите запись.'),
        'linux': ('Получите код завершения', 'Выполните <code>strace -f -e trace=process bash -c \'sh -c "exit 7"; echo code $?\'</code>. Оболочка <code>bash</code> запустит вторую оболочку <code>sh</code>, та сразу завершится с кодом 7, а <code>$?</code> — код последней команды.')},
    shot={'win': '03-exit.png', 'linux': '03-exit.png',
          'mac': '03-exit.png'},
    notes={'win': (f'<p>{mk(1)} — <code>cmd.exe</code> 1988 выполняет <code>Process Create</code> для второго <code>cmd.exe</code>, его номер 7940. {mk(2)} — <code>Process Start</code> процесса 7940. {mk(3)} — последнее событие процесса 7940, <code>Process Exit</code>, в Detail — <code>Exit Status: 7</code>. В окне командной строки <code>echo</code> печатает <code>code 7</code>.</p>',
                    '<p>Код завершения — число, которое процесс оставляет, когда заканчивает работу. Ядро хранит его, пока родитель не прочитает. 0 означает успех, другие числа — ошибку, а смысл каждого числа задаёт сама программа.</p>'),
           'mac': (f'<p>{mk(1)} — копия оболочки загружает <code>/bin/bash</code>: это вторая оболочка из команды. {mk(2)} — в нижнем окне <code>code 7</code>.</p>',
                   '<p>Завершения процесса в записи <code>fs_usage</code> нет. Код виден у родителя: оболочка дождалась ребёнка и положила его код в <code>$?</code>. Код завершения — число, которое процесс оставляет, когда заканчивает работу. Ядро хранит его, пока родитель не прочитает. 0 означает успех, другие числа — ошибку, а смысл каждого числа задаёт сама программа.</p>'),
           'linux': (f'<p>{mk(1)} — <code>exit_group(7)</code>: процесс <code>sh</code> 3873 завершается с кодом 7. {mk(2)} — <code>wait4</code> у родителя возвращает 3873 и <code>WEXITSTATUS(s) == 7</code>. {mk(3)} — <code>echo</code> печатает <code>code 7</code>.</p>',
                     '<p>Код прошёл путь от ребёнка к родителю: <code>sh</code> оставил число 7 при завершении, ядро хранило его, пока <code>bash</code> не забрал его вызовом <code>wait4</code>. В шаге 1 код был 0, здесь — 7.</p>')},
    q='код завершения, где он виден у ребёнка и где у родителя.'))

S.append(dict(
    why='Что будет, если программы нет? Увидим, как система ищет её по папкам и откуда берётся ошибка «не найдено».',
    see={'win': see('Главное окно Process Monitor, запись прокручена в начало. Все строки — процесс <code>cmd.exe</code> 1988, операция <code>QueryDirectory</code> (чтение списка файлов в папке). В Path записаны папка и маска <code>nosuch.*</code>, в Result — ответ. В строке состояния: <code>Showing 11 of 132 414 events</code>. В окне командной строки, которого на кадре не видно, — сообщение «"nosuch" не является внутренней или внешней командой» и <code>code 9009</code>.',
                    'Первый запрос: <code>C:\\Users\\user\\nosuch.*</code>, результат <code>NO SUCH FILE</code> (файла нет). Так <code>cmd.exe</code> сначала ищет программу в текущей папке.',
                    'Ещё десять таких же запросов, по одному на папку из переменной <code>PATH</code>: папки Python, <code>System32</code>, <code>Windows</code> и другие. Все с ответом <code>NO SUCH FILE</code>. Вместе с первым — 11 запросов.'),
         'mac': see('Два окна Терминала. Сверху — запись <code>fs_usage -f exec</code>. В столбце после вызова в квадратных скобках стоит код ошибки: <code>[ 2]</code> — ошибка 2, «нет такого файла». Снизу — команда <code>env nosuch; echo code $?</code>.',
                    'Копия <code>bash</code> загружает программу <code>/usr/bin/env</code>.',
                    'Шесть вызовов <code>execve</code> процесса <code>env</code> с путями <code>/opt/homebrew/bin/nosuch</code>, <code>/usr/local/bin/nosuch</code>, <code>/usr/bin/nosuch</code> и так далее. У каждого <code>[ 2]</code>: в этой папке программы нет.',
                    'Нижнее окно: сообщение <code>env: nosuch: No such file or directory</code> и <code>code 127</code> — код завершения <code>env</code>.'),
         'linux': see('Окно терминала Ubuntu. Команда <code>strace -f -e trace=execve env nosuch</code> показывает только вызовы <code>execve</code> — загрузку программы. <code>ENOENT</code> — ошибка «нет такого файла».',
                      'Вызов <code>execve</code> загружает программу <code>env</code> с аргументом <code>nosuch</code>. Результат 0 означает успех.',
                      'Десять вызовов <code>execve</code> с путями <code>/usr/local/sbin/nosuch</code>, <code>/usr/local/bin/nosuch</code> и так далее: по одному на каждую запись из <code>PATH</code>. Каждый вернул <code>-1 ENOENT (No such file or directory)</code>: в этой папке программы нет.',
                      'Строка <code>+++ exited with 127 +++</code>: <code>env</code> завершился с кодом 127. Выше рамки — его сообщение об ошибке.')},
    do={'win': ('Запустите программу, которой нет', 'Откройте фильтр <kbd>Ctrl</kbd>+<kbd>L</kbd>, снимите галочку у условия <b>Event Class</b> и добавьте условие <b>Path contains nosuch</b>, затем <b>OK</b>. Очистите запись и включите её. В командной строке выполните <code>nosuch</code>, затем <code>echo code %errorlevel%</code>. Остановите запись и прокрутите её в начало (<kbd>Home</kbd>).'),
        'mac': ('Запустите программу, которой нет', 'В верхнем окне выполните <code>sudo fs_usage -f exec</code>. В нижнем выполните <code>env nosuch; echo code $?</code>: программа <code>env</code> запускает другую программу по имени и ищет её так же, как функции запуска процесса. Остановите запись.'),
        'linux': ('Запустите программу, которой нет', 'Выполните <code>strace -f -e trace=execve env nosuch</code>. Программа <code>env</code> запускает другую программу по имени и ищет её так же, как функции запуска процесса. <code>-e trace=execve</code> оставляет только вызовы загрузки программы.')},
    shot={'win': '04-path.png', 'linux': '04-path.png',
          'mac': '04-path.png'},
    notes={'win': (f'<p>{mk(1)} — <code>QueryDirectory C:\\Users\\user\\nosuch.*</code>, результат <code>NO SUCH FILE</code>: сначала <code>cmd.exe</code> ищет файл в текущей папке. {mk(2)} — тот же запрос в каждой папке из переменной <code>PATH</code>: папки Python, <code>System32</code>, <code>Windows</code> и другие, всего 11 запросов, и все с ответом <code>NO SUCH FILE</code>. В окне командной строки — сообщение «"nosuch" не является внутренней или внешней командой» и <code>code 9009</code>.</p>',
                    '<p>Строки <code>Process Create</code> нет: <code>cmd.exe</code> сама искала файл по <code>PATH</code>, не нашла и процесс не создавала. 9009 — код, которым <code>cmd.exe</code> сообщает «команда не найдена». Если вызвать <code>CreateProcessW</code> с именем программы, которой нет, функция вернёт ошибку 2, <code>ERROR_FILE_NOT_FOUND</code>.</p>'),
           'mac': (f'<p>{mk(1)} — копия <code>bash</code> загружает <code>/usr/bin/env</code>. {mk(2)} — шесть вызовов <code>execve</code> процесса <code>env</code> с путями <code>/opt/homebrew/bin/nosuch</code>, <code>/usr/local/bin/nosuch</code> и так далее, у каждого в третьем столбце <code>[ 2]</code> — код ошибки 2. {mk(3)} — в нижнем окне сообщение <code>No such file or directory</code> и <code>code 127</code>.</p>',
                   '<p>Ядро ищет программу только по полному пути. Перебирает папки <code>PATH</code> сама библиотека C — функция <code>execvp</code>, которую вызывает <code>env</code>. Ошибка 2, <code>ENOENT</code>, — «нет такого файла». 127 — код, которым оболочки и <code>env</code> сообщают «программа не найдена». Папок у вас может быть больше: их список — в переменной <code>PATH</code>, посмотреть его можно командой <code>echo $PATH</code>.</p>'),
           'linux': (f'<p>{mk(1)} — <code>execve</code> загружает саму программу <code>env</code>. {mk(2)} — десять вызовов <code>execve</code> с путями <code>/usr/local/sbin/nosuch</code>, <code>/usr/local/bin/nosuch</code> и так далее: по одному на каждую папку из <code>PATH</code>. Каждый возвращает <code>-1 ENOENT (No such file or directory)</code>. {mk(3)} — <code>env</code> печатает ошибку и завершается с кодом 127.</p>',
                     '<p>Ядро ищет программу только по полному пути. Перебирает папки <code>PATH</code> сама библиотека C — функция <code>execvp</code>, которую вызывает <code>env</code>. <code>ENOENT</code> — ошибка номер 2, «нет такого файла». 127 — код, которым оболочки и <code>env</code> сообщают «программа не найдена».</p>')},
    q='сколько папок проверено, код ошибки поиска и код завершения.'))

S.append(dict(
    why='Остаётся проверить, что другие программы запускают процессы так же. Берём Python и сравниваем с оболочкой из шага 1.',
    see={'win': see('Главное окно Process Monitor. Процесс <code>python.exe</code> с номером 8364 сначала загружает свои библиотеки (строки выше рамок), потом создаёт ребёнка — <code>hostname.exe</code>. В окне командной строки, которого на кадре не видно, Python печатает <code>code 0</code>.',
                    'Строка <code>python.exe</code> 8364, операция <code>Process Create</code>. В Path — <code>C:\\WINDOWS\\SYSTEM32\\hostname.exe</code>, в Detail — <code>PID: 1492</code>. Python создал процесс 1492.',
                    'Операция <code>Process Start</code> процесса <code>hostname.exe</code> 1492, в Detail — <code>Parent PID: 8364</code>: родитель — Python.'),
         'mac': see('Два окна Терминала. Сверху — запись <code>fs_usage -f exec</code>, снизу — команда Python с <code>subprocess.run</code>. Внизу напечатано <code>code 0</code>: Python получил код завершения 0.',
                    'Копия <code>bash</code> загружает <code>python3.14</code>. Это короткий запускатель из Homebrew.',
                    'Вызов <code>posix_spawn</code> — создание процесса и загрузка программы одним вызовом. Запускатель так запускает настоящий интерпретатор <code>Python.app/Contents/MacOS/Python</code>. Начало пути обрезано границей окна.',
                    'Три вызова <code>execve</code> процесса <code>Python</code>, у каждого <code>[ 2]</code> (нет такого файла): ребёнок Python ищет <code>hostname</code> в папках <code>PATH</code>.',
                    'Четвёртая попытка, <code>/bin/hostname</code>, прошла без ошибки: программа найдена и загружена.'),
         'linux': see('Окно терминала Ubuntu, вывод <code>strace -f -e trace=process</code> для команды Python с <code>subprocess.run</code>. Родитель — <code>python3</code>, номер 3883, ребёнок — 3884. Пометка <code>&lt;unfinished ...&gt;</code> значит, что вызов ещё не закончился: его результат <code>strace</code> напечатает ниже, в строке <code>resumed</code>.',
                      'Вызов <code>clone</code> с флагами <code>CLONE_VM|CLONE_VFORK</code>: Python создаёт ребёнка. В той же строке <code>Process 3884 attached</code> — <code>strace</code> начал следить за новым процессом 3884.',
                      'Три вызова <code>execve</code> в процессе 3884 с ответом <code>ENOENT</code>: <code>/usr/local/sbin/hostname</code>, <code>/usr/local/bin/hostname</code>, <code>/usr/sbin/hostname</code>. Ребёнок сам ищет <code>hostname</code> в папках <code>PATH</code>.',
                      'Четвёртая попытка, <code>/usr/bin/hostname</code>, удалась. Вызов помечен <code>unfinished</code>: его результат 0 стоит ниже, в строке <code>&lt;... execve resumed&gt;</code>.',
                      'Вызов <code>wait4(3884, …)</code> у Python: он дождался процесса 3884 и получил код 0 (<code>WEXITSTATUS(s) == 0</code>). Ниже <code>code 0</code> напечатал сам Python.')},
    do={'win': ('Запустите программу из Python', 'Откройте фильтр, снимите галочки у обоих условий <b>Path</b> и верните галочку <b>Event Class</b>. Очистите запись и включите её. В командной строке выполните<br><code>python -c "import subprocess; r = subprocess.run([\'hostname\'], capture_output=True); print(\'code\', r.returncode)"</code><br>Python запустит <code>hostname</code> как дочернюю программу, дождётся её, заберёт её вывод и напечатает код завершения.<br>Ключи: <code>subprocess.run</code> — запуск с ожиданием, <code>capture_output=True</code> — забрать вывод, <code>r.returncode</code> — код. Остановите запись и найдите строку <code>python.exe</code> с операцией <code>Process Create</code>.'),
        'mac': ('Запустите программу из Python', 'В верхнем окне выполните <code>sudo fs_usage -f exec</code>. В нижнем выполните<br><code>python3 -c "import subprocess; r = subprocess.run([\'hostname\'], capture_output=True); print(\'code\', r.returncode)"</code><br>Python запустит <code>hostname</code> как дочернюю программу, дождётся её, заберёт её вывод и напечатает код завершения.<br>Ключи: <code>subprocess.run</code> — запуск с ожиданием, <code>capture_output=True</code> — забрать вывод, <code>r.returncode</code> — код. Остановите запись.'),
        'linux': ('Запустите программу из Python', 'Выполните<br><code>strace -f -e trace=process python3 -c "import subprocess; r = subprocess.run([\'hostname\'], capture_output=True); print(\'code\', r.returncode)"</code><br>Python запустит <code>hostname</code> как дочернюю программу, дождётся её, заберёт её вывод и напечатает код завершения.<br>Ключи: <code>subprocess.run</code> — запуск с ожиданием, <code>capture_output=True</code> — забрать вывод, <code>r.returncode</code> — код.')},
    shot={'win': '05-python.png', 'linux': '05-python.png',
          'mac': '05-python.png'},
    notes={'win': (f'<p>{mk(1)} — <code>python.exe</code> с номером 8364 выполняет <code>Process Create</code> для <code>C:\\WINDOWS\\SYSTEM32\\hostname.exe</code>, номер нового процесса 1492. {mk(2)} — <code>Process Start</code> процесса 1492, в Detail — <code>Parent PID: 8364</code>. Выше видно, как <code>python.exe</code> сам загружал свои библиотеки. В окне командной строки — <code>code 0</code>.</p>',
                    '<p>Родителем стал Python, а сам запуск устроен так же, как у командной строки в шаге 1: <code>subprocess.run</code> вызывает ту же функцию <code>CreateProcessW</code>.</p>'),
           'mac': (f'<p>{mk(1)} — копия <code>bash</code> загружает <code>python3.14</code>. {mk(2)} — <code>posix_spawn</code>: у Python из Homebrew <code>python3.14</code> — короткий запускатель, он сразу запускает настоящий интерпретатор <code>Python.app/<wbr>Contents/<wbr>MacOS/<wbr>Python</code>. {mk(3)} — три вызова <code>execve</code> процесса <code>Python</code> с кодом <code>[ 2]</code>: ребёнок Python ищет <code>hostname</code> по папкам <code>PATH</code>. {mk(4)} — <code>/bin/hostname</code> нашёлся и загружен. В нижнем окне — <code>code 0</code>.</p>',
                   '<p>Python запускает программу так же, как оболочка: копия процесса, затем <code>execve</code> с перебором папок <code>PATH</code>. Строка {mk(2)} показывает второй способ запуска — <code>posix_spawn</code>, который делает копию и загрузку программы одним вызовом.</p>'),
           'linux': (f'<p>{mk(1)} — <code>clone</code> с флагами <code>CLONE_VM|CLONE_VFORK</code>: Python 3883 создаёт ребёнка 3884. {mk(2)} — три вызова <code>execve</code> в процессе 3884 с ответом <code>ENOENT</code>: ребёнок сам ищет <code>hostname</code> по папкам <code>PATH</code>. {mk(3)} — четвёртая попытка, <code>/usr/bin/hostname</code>, удалась. {mk(4)} — <code>wait4(3884, …)</code>: Python дожидается процесса 3884 и получает код 0.</p>',
                     '<p>Python запускает программу теми же двумя шагами, что оболочка в шаге 1. Разница в флагах <code>clone</code>: <code>CLONE_VM</code> значит, что ребёнок до <code>execve</code> пользуется той же памятью, что родитель: копия памяти не создаётся. <code>CLONE_VFORK</code> значит, что родитель стоит, пока ребёнок не вызовет <code>execve</code>. Без копии памяти запуск быстрее.</p>')},
    q='номер процесса Python, номер ребёнка и <span data-os="win">событие</span><span data-os="mac linux">вызов</span>, которым ребёнок создан.'))

GIST = gist([
    ('Процесс заводит ядро', 'Новый процесс создаёт ядро системы, родитель только подаёт заявку. Так руководитель просит отдел кадров принять сотрудника: номер, место и пропуск выдаёт отдел кадров.', 'Ядро даёт процессу номер и память и загружает программу.'),
    ('Копия, потом другая программа', 'В macOS и Linux ядро сначала делает копию родителя, а потом заменяет в копии программу на нужную. В Windows всё одним вызовом.', 'Номер процесса при замене не меняется.'),
    ('В конце — код завершения', 'Ребёнок оставляет число: 0 значит успех, другое — ошибку. Родитель его забирает — как отметку «сделано» или «не сделано».', 'Если программы нет, система перебирает папки PATH и отвечает ошибкой.')],
    'запись рождения процесса → библиотеки → код завершения → программа, которой нет → запуск из Python.')

LAB = steps(S, '05-process-birth')

HTML = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>Лабораторная работа 5. Рождение процесса · Справочник по системному программированию</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,600;0,7..72,700;1,7..72,400&family=Pixelify+Sans:wght@500;600;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css">
</head>
<body>
  <div class="book">
    <div class="book__body">
      <div class="spine"><span>Модуль 2 · Лабораторная работа 5</span></div>

      <main class="leaf">
        <div class="running">
          <p class="eyebrow"><a href="../../index.html" style="text-decoration:none;color:inherit">Справочник по системному программированию</a> · модуль 2 · лабораторная работа</p>
          <p class="running__folio">ЛР 5</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">ЛР 5</span>
          <h1>Рождение<br>процесса</h1>
          <p class="lead">Любая команда в терминале — это короткая цепочка: родитель просит ядро создать процесс, ядро загружает программу, программа оставляет код завершения. Каждое звено вы увидите в записи.</p>
        </header>

        <dl class="passport">
          <div><dt>Пара</dt><dd>5, первая половина; перед главой 2.2</dd></div>
          <div><dt>Время</dt><dd>30–35 минут</dd></div>
          <div><dt>Программы</dt><dd><span data-os="win">Process Monitor, командная строка</span><span data-os="mac"><code>fs_usage</code>, Терминал</span><span data-os="linux"><code>strace</code>, терминал</span>, Python</dd></div>
          <div><dt>Сдать</dt><dd><code>report.md</code> и 5 снимков в <code>screenshots/</code> в папке <code>labs/05-process-birth</code> репозитория <code>sysprog-start</code></dd></div>
        </dl>

{GIST}

        <nav class="contents">
          <b>В этой работе</b>
          <ol>
            <li><a href="#s1">Подготовка</a></li>
            <li><a href="#s2">Как рождается процесс</a></li>
            <li><a href="#s3">Ход работы</a></li>
            <li><a href="#s4">Что получилось</a></li>
            <li><a href="#s5">Отчёт</a></li>
            <li><a href="#s6">Проверьте себя</a></li>
          </ol>
        </nav>

        <h2 id="s1"><span class="sec">§1</span>Подготовка</h2>

        <p><span data-os="win">Нужен Process Monitor из набора Sysinternals: скачайте архив <code>ProcessMonitor.zip</code> с сайта Microsoft Learn и распакуйте его в свою папку, например <code>C:\\Users\\имя\\ProcessMonitor</code>. Программа записывает обращения процессов к файлам, реестру и ядру. Поэтому она работает от имени администратора: при запуске Windows спросит разрешение.</span><span data-os="mac">Нужна программа <code>fs_usage</code>: она входит в macOS и печатает обращения процессов к файлам и ядру. Она читает события всех процессов системы, поэтому запускается через <code>sudo</code> с паролем администратора. Работа идёт в двух окнах Терминала: в одном запись, в другом команды.</span><span data-os="linux">Нужна программа <code>strace</code>. В Ubuntu она обычно уже есть; проверьте командой <code>strace -V</code>, а если её нет, поставьте: <code>sudo apt install strace</code>.</span> Во всех шагах запускается одна и та же короткая программа <code>hostname</code>: она печатает имя компьютера и завершается. Создайте в репозитории <code>sysprog-start</code> папку <code>labs/05-process-birth</code>: в шаблоне в ней уже лежат бланк <code>report.md</code> и папка <code>screenshots/</code>.</p>

        <div class="margin-note">
          <b>Как читать шаг</b>
          <p>Вверху шага — действие. Ниже — кадр экрана после действия; красные рамки отмечают места, о которых идёт речь, номера рамок повторяются в тексте. Слева под кадром — что на нём видно, справа — что изменилось. Строка «В отчёт» — что записать в <code>report.md</code>. Номера процессов у вас будут другими.</p>
        </div>

        <h2 id="s2"><span class="sec">§2</span>Как рождается процесс</h2>

        <p>У каждого процесса есть родитель (ЛР 4). Ребёнка создаёт ядро по просьбе родителя — системному вызову. Это заявка в отдел кадров из «Сути».</p>

        <p>Ядро даёт новому процессу номер и память и загружает файл программы. Затем <span class="term">загрузчик</span> — часть системы, которая подключает библиотеки до начала работы программы, — берёт тот список, который в ЛР 3 печатал <span data-os="win"><code>dumpbin</code></span><span data-os="mac"><code>otool -L</code></span><span data-os="linux"><code>ldd</code></span>.</p>
{PIC_BIRTH}
        <p data-os="win">Слева на схеме — родитель, справа — работающий ребёнок. В Windows между ними один вызов: ядро создаёт процесс и сразу загружает в него программу.</p>
        <p data-os="win" class="tech"><b>В коде:</b> <code>CreateProcessW</code>; загрузчик — в <code>ntdll.dll</code>, которую ядро кладёт в каждый процесс.</p>
        <p data-os="mac linux">Слева на схеме — родитель, справа — работающий ребёнок. Между ними два вызова: сначала ядро делает копию родителя с новым номером, потом заменяет в копии программу на новую. Код родителя пропадает, номер остаётся.</p>
        <p data-os="mac linux" class="tech"><b>В коде:</b> <span data-os="linux"><code>clone</code></span><span data-os="mac"><code>fork</code></span> — копия, <code>execve</code> — замена программы; загрузчик — <span data-os="linux"><code>ld-linux</code></span><span data-os="mac"><code>dyld</code></span>.</p>

        <p>Работа программы кончается <span class="term">кодом завершения</span> — числом, которое процесс оставляет ядру. Его забирает родитель:</p>
{PIC_WAIT}
        <p>Ребёнок оставил 7, ядро хранит число в записи о процессе, родитель ждёт и получает его. Пока код не забран, запись остаётся в ядре и занимает место. Поэтому программа, которая запускает процессы, обязана забирать их коды.</p>

        <p>Вызовы записывает программа, которой ядро сообщает об обращениях процессов:</p>

        <div class="table-scroll">
          <table>
            <thead><tr><th></th><th>Windows</th><th>macOS</th><th>Linux</th></tr></thead>
            <tbody>
              <tr><td>Программа</td><td>Process Monitor</td><td><code>fs_usage</code></td><td><code>strace</code></td></tr>
              <tr><td>Что записывает</td><td>события всех процессов: процессы, файлы, реестр, сеть</td><td>обращения всех процессов к файлам и запуск программ</td><td>системные вызовы одной программы и её детей</td></tr>
              <tr><td>Права</td><td>администратор</td><td><code>sudo</code></td><td>обычный пользователь</td></tr>
            </tbody>
          </table>
        </div>

        <h2 id="s3"><span class="sec">§3</span>Ход работы</h2>

{LAB}

        <h2 id="s4"><span class="sec">§4</span>Что получилось</h2>

        <div class="table-scroll">
          <table>
            <thead><tr><th></th><th>Windows</th><th>macOS</th><th>Linux</th></tr></thead>
            <tbody>
              <tr><td>Создать процесс</td><td><code>CreateProcessW</code>: событие <code>Process Create</code> у родителя</td><td><code>fork</code>, затем <code>execve</code>; или <code>posix_spawn</code></td><td><code>clone</code>, затем <code>execve</code></td></tr>
              <tr><td>Первое событие ребёнка</td><td><code>Process Start</code> с <code>Parent PID</code></td><td colspan="2"><code>execve</code> загружает программу в копию родителя</td></tr>
              <tr><td>Библиотеки</td><td><code>Load Image</code>: сначала <code>ntdll.dll</code></td><td>загрузчик <code>dyld</code>: общий кэш <code>dyld_shared_cache</code></td><td>загрузчик <code>ld-linux</code>: <code>ld.so.cache</code>, <code>libc.so.6</code></td></tr>
              <tr><td>Код завершения</td><td><code>Process Exit</code>, <code>Exit Status</code>; в командной строке <code>%errorlevel%</code></td><td>в оболочке <code>$?</code>; <code>fs_usage</code> завершение не показывает</td><td><code>exit_group</code> у ребёнка, <code>wait4</code> у родителя; в оболочке <code>$?</code></td></tr>
              <tr><td>Программы нет</td><td>поиск по <code>PATH</code>, код <code>cmd.exe</code> 9009; у <code>CreateProcessW</code> ошибка 2</td><td colspan="2"><code>execve</code> по папкам <code>PATH</code> с ошибкой <code>ENOENT</code> (2), код 127</td></tr>
            </tbody>
          </table>
        </div>

        <ul>
          <li>Во всех пяти шагах путь один: родитель просит ядро, ядро загружает программу, загрузчик — библиотеки.</li>
          <li>Программа завершается с кодом, родитель его забирает.</li>
          <li>Python в шаге 5 прошёл тот же путь, что и командная оболочка.</li>
          <li>В главе 2.2 этот путь пройдёт ядро агента: функция на C запустит программу, дождётся её и вернёт мозгу код завершения.</li>
        </ul>

        <h2 id="s5"><span class="sec">§5</span>Отчёт</h2>

        <p>Бланк — в <code>labs/05-process-birth/report.md</code>. Замените каждый пропуск <code>___</code> данными со своего экрана, снимки положите в <code>screenshots/</code>. Коммит — <code>labs 05: рождение процесса, отчёт</code>.</p>

        <pre class="report"># ЛР 5. Рождение процесса

Система: <span class="blank">___</span>
Программа записи: <span class="blank">___</span>

## Рождение
Родитель (имя и номер): <span class="blank">___</span>
Номер нового процесса: <span class="blank">___</span>
Событие или вызов, которым создан процесс: <span class="blank">___</span>
Библиотек загружено и первая из них: <span class="blank">___</span>

## Завершение
Код завершения у ребёнка и у родителя: <span class="blank">___</span>
Программа nosuch: папок проверено <span class="blank">___</span>, ошибка <span class="blank">___</span>, код <span class="blank">___</span>

## Запуск из Python
Номер Python и номер ребёнка: <span class="blank">___</span>
Чем запуск из Python отличается от запуска из оболочки: <span class="blank">___</span>

Не получилось: <span class="blank">___</span>

{snaps.report_pre('05-process-birth')}</pre>

{snaps.page_block('05-process-birth')}

        <h2 id="s6"><span class="sec">§6</span>Проверьте себя</h2>
        <details class="more">
          <summary>Пять вопросов с ответами</summary>

        <details>
          <summary>Кто создаёт процесс: родитель или ядро?</summary>
          <p>Ядро. Родитель только просит его системным вызовом: <span data-os="win"><code>CreateProcessW</code></span><span data-os="mac linux"><code>fork</code> или <code>clone</code>, затем <code>execve</code></span>. Ядро выделяет номер и память и загружает программу.</p>
        </details>
        <details>
          <summary>Почему в Linux номер процесса не меняется после <code>execve</code>?</summary>
          <p><code>execve</code> заменяет программу в уже созданном процессе. Номер появился раньше, при <code>clone</code>, и остаётся у процесса до его завершения.</p>
        </details>
        <details>
          <summary>Какая библиотека загружается в процесс первой и почему?</summary>
          <p>В Windows — <code>ntdll.dll</code>: в ней загрузчик, который подключает остальные библиотеки. В Linux первым работает загрузчик <code>ld-linux</code>, он открывает <code>ld.so.cache</code> и затем библиотеки программы, в macOS — загрузчик <code>dyld</code>.</p>
        </details>
        <details>
          <summary>Откуда родитель узнаёт код завершения ребёнка?</summary>
          <p>Ребёнок оставляет код ядру при завершении. Родитель ждёт ребёнка и забирает код: в Windows — <code>WaitForSingleObject</code> и <code>GetExitCodeProcess</code>, в macOS и Linux — <code>wait4</code> или <code>waitpid</code>.</p>
        </details>
        <details>
          <summary>Почему при запуске несуществующей программы в записи несколько попыток?</summary>
          <p>Имя без пути ищется по очереди во всех папках переменной <code>PATH</code>. Ошибка «нет такого файла» приходит из каждой папки, и только после последней запуск признаётся неудачным.</p>
        </details>
        </details>

        <div class="pager">
          <a href="../14-spisok-processov/index.html">← 2.1 Список процессов</a>
          <a href="../../index.html">Оглавление</a>
          <a href="../16-zapusk-processa/index.html">2.2 Запуск процесса →</a>
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
