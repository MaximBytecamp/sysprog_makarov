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
    '<div data-os="win">' + birth(('родитель', '<code>cmd.exe</code>', 'подаёт заявку ядру', 'c'),
                                  ('ядро', 'новая программа', 'выдаёт номер и память', 'sys'),
                                  ('библиотеки', 'HOSTNAME.EXE и DLL', 'ntdll.dll, kernel32.dll, …', 'sys'),
                                  ('ребёнок', '<code>hostname</code> работает', 'печатает имя и оставляет отметку о результате', 'py')) + '</div>'
    + '<div data-os="mac linux">' + birth(('родитель', '<code>bash</code>', '<span data-os="linux">clone</span><span data-os="mac">fork</span>: делает копию себя', 'c'),
                                          ('копия', 'тот же код', 'новый номер', 'sys'),
                                          ('замена', '<code>hostname</code> вместо копии', 'подключаются библиотеки', 'sys'),
                                          ('ребёнок', '<code>hostname</code> работает', 'печатает имя и оставляет отметку о результате', 'py')) + '</div>',
    '<span data-os="win">В Windows рождение — одна заявка: ядро создаёт программу и сразу загружает в неё нужный файл.</span>'
    '<span data-os="mac linux">В <span data-os="mac">macOS</span><span data-os="linux">Linux</span> рождение — две заявки: сначала копия родителя, потом в копию загружается новая программа. Номер выдаётся при копии и дальше не меняется.</span>')

PIC_WAIT = V.scheme('Отметка о результате: от ребёнка к родителю',
    V.steps(V.card('ребёнок', '<code>exit 7</code>', '<small>заканчивает работу и оставляет число</small>', 'py'), V.arrow('число хранит ядро'),
            V.card('ядро', 'запись о ребёнке', '<small>число 7 лежит, пока его не заберут</small>', 'sys'), V.arrow('родитель ждёт'),
            V.card('родитель', '<span data-os="win"><code>%errorlevel%</code></span><span data-os="mac linux"><code>$?</code></span>', '<small>получил 7</small>', 'c')),
    '<span data-os="win">Командная строка ждёт ребёнка и читает его число.</span>'
    '<span data-os="mac linux">Оболочка ждёт ребёнка и забирает число. Для этого есть заявка <code>wait4</code>.</span>')

S = []

S.append(dict(
    why='Сначала смотрим, как рождается новая программа: кто просит её создать, что делает ядро и как это видно в записи.',
    see={'win': [see('Окно фильтра Process Monitor. Фильтр оставляет в записи только нужное. Внизу — список условий.',
                     'Четыре условия <b>Include</b> («включить»): программы <code>HOSTNAME.EXE</code>, <code>cmd.exe</code>, <code>python.exe</code> и события вида <code>Process</code>. В записи останутся только они.',
                     'Кнопка <b>Add</b> переносит условие из верхней строки в список. Так добавлено последнее условие.'),
                 see('Главное окно Process Monitor после записи. Одна строка — одно событие. Внизу: <code>Showing 34 of 128 546 events</code> — фильтр оставил 34 события из 128 546.',
                     'Строка <code>cmd.exe</code>, номер 1988, <code>Process Create</code>: родитель создал новую программу. В Path — путь к <code>HOSTNAME.EXE</code>, в Detail — <code>PID: 804</code>, её номер.',
                     'Строка <code>HOSTNAME.EXE</code>, номер 804, <code>Process Start</code>: новая программа начала работу. В Detail — <code>Parent PID: 1988</code>, то есть родитель — <code>cmd.exe</code>.'),
                 see('Окно <b>Event Properties</b> — подробности события. Оно открывается двойным щелчком. Открыто событие <code>Process Start</code> программы <code>HOSTNAME.EXE</code>.',
                     'Поле <b>Operation</b>: <code>Process Start</code> — первое событие новой программы.',
                     'Что новая программа получила от родителя: <code>Parent PID</code> — номер родителя, 1988; <code>Command line</code> — команда запуска, <code>hostname</code>; <code>Current directory</code> — папка, в которой она работает, <code>C:\\Users\\user\\</code>.',
                     'Поле <b>Environment</b> — настройки, которые достались от родителя, например <code>COMPUTERNAME=WIN11-LAB</code> и <code>ComSpec=C:\\WINDOWS\\system32\\cmd.exe</code>. Это копия настроек <code>cmd.exe</code>.')],
         'mac': see('Два окна Терминала. Сверху — запись, снизу — команды. В верхнем одна строка — один запуск программы.',
                    'Строка <code>execve</code> — замена программы: загружается <code>/bin/hostname</code>. В последнем столбце <code>bash.23813159</code>: запуск сделал <code>bash</code>, число после точки — номер потока.',
                    'Нижнее окно, команда <code>echo $$; hostname</code>. Первая строка — 37027, номер оболочки. Вторая — <code>MacBook-Air-Maxim.local</code>, имя компьютера.'),
         'linux': see('Окно терминала Ubuntu. Сверху команда <code>strace</code>, ниже её вывод: одна строка — одна заявка ядру. В <code>[pid …]</code> — номер программы, которая её подала. После знака равенства — ответ ядра.',
                      'Строка <code>clone(...) = 3862</code> — копия: оболочка <code>bash</code>, номер 3861, сделала свою копию. Ответ ядра — номер копии, 3862.',
                      'В программе 3862 строка <code>execve("/usr/bin/hostname", …) = 0</code> — замена программы: копия стала <code>hostname</code>. Ответ 0 — всё хорошо. Ниже слово <code>ubuntu</code> — имя компьютера, его напечатал <code>hostname</code>.',
                      'Строка <code>exit_group(0)</code>: программа 3862 закончила работу с отметкой 0.',
                      'Строка <code>wait4</code> у родителя вернула 3862, в скобках <code>WEXITSTATUS(s) == 0</code>: родитель дождался ребёнка и получил отметку 0. Ниже <code>code 0</code> — то же число, его напечатал <code>echo</code>.')},
    do={'win': ('Запишите, как рождается программа', 'Запустите Process Monitor (<code>Procmon64.exe</code>, на компьютере с ARM — <code>Procmon64a.exe</code>) и примите лицензию. Запись идёт сразу: остановите её <kbd>Ctrl</kbd>+<kbd>E</kbd> и очистите список <kbd>Ctrl</kbd>+<kbd>X</kbd>. Откройте фильтр <kbd>Ctrl</kbd>+<kbd>L</kbd>: выберите <b>Process Name</b>, <b>is</b>, введите <code>HOSTNAME.EXE</code>, оставьте <b>Include</b> и нажмите <b>Add</b>. Так же добавьте <code>cmd.exe</code>, <code>python.exe</code> и условие <b>Event Class is Process</b>, затем <b>OK</b>. Фильтр оставит только события этих программ. Включите запись <kbd>Ctrl</kbd>+<kbd>E</kbd>, в командной строке выполните <code>hostname</code>, вернитесь в Process Monitor и остановите запись. Дважды щёлкните по строке <code>Process Start</code>.'),
        'mac': ('Запишите, как рождается программа', 'Откройте два окна Терминала: верхнее широкое — для записи, нижнее — для команд. В нижнем выполните <code>bash</code>: запись не показывает оболочки <code>zsh</code> и <code>sh</code>, поэтому команды работы выполняйте в <code>bash</code>. В верхнем окне выполните <code>sudo fs_usage -f exec</code> и введите пароль. Команда записывает запуски программ. В нижнем окне выполните <code>echo $$; hostname</code>: <code>$$</code> — номер самой оболочки. В верхнем остановите запись <kbd>Ctrl</kbd>+<kbd>C</kbd>.'),
        'linux': ('Запишите, как рождается программа', 'Откройте терминал и разверните окно. Выполните <code>strace -f -e trace=process bash -c \'hostname; echo code $?\'</code>. Команда <code>strace</code> запускает <code>bash</code> и записывает все его заявки ядру. Нам нужны только заявки про создание, запуск и ожидание программ. Оболочка выполнит <code>hostname</code> и напечатает отметку о результате.<br>Ключи: <code>-f</code> — следить и за детьми, <code>-e trace=process</code> — оставить заявки про программы, <code>bash -c</code> — выполнить строку.')},
    shot={'win': ['00-filter.png', '01-birth.png', '01b-start.png'], 'linux': '01-birth.png',
          'mac': '01-birth.png'},
    notes={'win': ('', '<p>Командная строка не запускает программу сама. Она подаёт заявку ядру (в списке — <code>CreateProcessW</code>), и ядро создаёт программу. У родителя это одна строка <code>Process Create</code>, у ребёнка жизнь начинается со строки <code>Process Start</code>.</p>'),
           'mac': ('', '<p>Строки с копией нет: запись показывает только замену программы. Сначала <code>bash</code> делает свою копию (заявка <code>fork</code>), потом копия заменяет себя на <code>hostname</code>. Поэтому в строке стоит имя <code>bash</code>. Если в записи много чужих строк, добавьте их имена после ключа <code>-e</code>: <code>sudo fs_usage -e -f exec "Code Helper (Plugin)"</code>.</p>'),
           'linux': ('', '<p>Рождение — две заявки: <code>clone</code> делает копию, <code>execve</code> заменяет в ней программу. Номер 3862 выдан при копии и после замены остался тем же. Последняя строка <code>code 0</code> — то же число, что получил <code>wait4</code>.</p>')},
    q='имя и номер родителя, номер нового процесса и <span data-os="win">событие</span><span data-os="mac linux">вызов</span>, которым он создан.'))

S.append(dict(
    why='Программа hostname крошечная, но без библиотек не работает. Библиотеки — готовые наборы действий, которые берёт программа. Смотрим, как они подключаются до начала её работы.',
    see={'win': see('Главное окно Process Monitor, запись прокручена в конец. Строки <code>Load Image</code> — подключение файла к программе. Все строки на кадре относятся к <code>HOSTNAME.EXE</code>, номер 804.',
                    'Первые четыре библиотеки: <code>ntdll.dll</code>, <code>kernel32.dll</code>, <code>KernelBase.dll</code> и <code>msvcrt.dll</code>. Выше рамки — <code>Load Image</code> самой программы <code>HOSTNAME.EXE</code>.',
                    'Ещё 14 библиотек. Среди них <code>ws2_32.dll</code>, <code>mswsock.dll</code> и <code>dnsapi.dll</code>: через них <code>hostname</code> узнаёт имя компьютера.',
                    'Строка <code>Process Exit</code> — программа закончила работу. В Detail — <code>Exit Status: 0</code>: отметка о результате 0, всё хорошо.'),
         'mac': see('Два окна Терминала. Сверху — обращения к файлам, отобранные по слову <code>hostname</code>. Одна строка — одно обращение. Снизу — команда <code>hostname</code> и её ответ, <code>MacBook-Air-Maxim.local</code>.',
                    'Первые обращения новой программы: <code>/usr/lib/dyld</code> — то, что подключает библиотеки; <code>/bin/hostname</code> — сама программа; папка <code>/System/Library/dyld</code>.',
                    'Файл <code>dyld_shared_cache_arm64e</code> (строка <code>fsgetpath</code>) — один общий файл со всеми системными библиотеками.',
                    'Файл программы <code>/bin/hostname</code> открывается (<code>open</code>), закрывается (<code>close</code>) и открывается снова.'),
         'linux': see('Окно терминала Ubuntu. Команда <code>strace -e trace=openat hostname</code> показывает только открытие файлов. В скобках — путь к файлу, число после знака равенства (3) — номер, под которым файл открыт. Ниже — <code>ubuntu</code>, имя компьютера, и строка <code>+++ exited with 0 +++</code>: программа закончила с отметкой 0.',
                      'Открыт <code>/etc/ld.so.cache</code> — список библиотек системы и мест, где они лежат. По нему ищется нужная библиотека.',
                      'Открыт <code>/lib/aarch64-linux-gnu/libc.so.6</code> — главная библиотека языка C. Других библиотек <code>hostname</code> не берёт.')},
    do={'win': ('Посмотрите, какие библиотеки подключились', 'Закройте окно свойств и прокрутите запись в конец (<kbd>End</kbd>).'),
        'mac': ('Посмотрите, какие библиотеки подключились', 'В верхнем окне выполните <code>sudo fs_usage -f pathname | grep hostname</code>. Команда показывает обращения к файлам, а <code>grep</code> оставляет строки со словом <code>hostname</code>. В нижнем окне выполните <code>hostname</code>, подождите несколько секунд и остановите запись.'),
        'linux': ('Посмотрите, какие библиотеки подключились', 'Выполните <code>strace -e trace=openat hostname</code>. Команда показывает, какие файлы открывает программа. Ключ <code>-f</code> не нужен: <code>hostname</code> других программ не запускает.')},
    shot={'win': '02-libs.png', 'linux': '02-libs.png',
          'mac': '02-libs.png'},
    notes={'win': ('', '<p>Первой идёт сама <code>HOSTNAME.EXE</code>, второй — <code>ntdll.dll</code>: её система кладёт в каждую программу. Остальные подключаются по списку из файла программы — тот самый список, который в ЛР 3 печатал <code>dumpbin /dependents</code>. Всего 18 библиотек ради программы, которая печатает одну строку.</p>'),
           'mac': ('', '<p>Отдельных файлов библиотек в записи нет. В macOS системные библиотеки лежат в одном большом файле — общем кэше, и он уже есть в памяти каждой программы. Поэтому <code>otool -L</code> в ЛР 3 показывал библиотеки, которых нет на диске отдельными файлами.</p>'),
           'linux': ('', '<p>Оба файла открываются до начала работы самой программы. Сам файл <code>hostname</code> и программу, которая подключает библиотеки, ядро загрузило ещё при замене программы — поэтому их в этом выводе нет. Программе <code>hostname</code> хватает одной библиотеки — это видно и по <code>ldd /usr/bin/hostname</code> из ЛР 3.</p>')},
    q='сколько библиотек загрузил процесс и какая из них первая.'))

S.append(dict(
    why='Программа закончила работу. Как родитель узнаёт, получилось ли у ребёнка? По числу: оно показывает результат, 0 — всё хорошо. Программисты называют его кодом завершения. Смотрим на это число со стороны ребёнка и со стороны родителя.',
    see={'win': see('Главное окно Process Monitor. На кадре события двух <code>cmd.exe</code>: родителя, номер 1988, и новой, номер 7940. Новую запустила команда <code>cmd /c exit 7</code>. В окне командной строки, которого на кадре не видно, <code>echo</code> печатает <code>code 7</code>.',
                    'Строка <code>cmd.exe</code> 1988, <code>Process Create</code>: родитель создал вторую <code>cmd.exe</code>. В Detail — <code>PID: 7940</code>, её номер.',
                    'Строка <code>Process Start</code> программы 7940, в Detail — <code>Parent PID: 1988</code>.',
                    'Последнее событие программы 7940 — <code>Process Exit</code>. В Detail — <code>Exit Status: 7</code>: отметка о результате 7.'),
         'mac': see('Два окна Терминала. Сверху — запись, снизу — команда со второй оболочкой <code>bash</code>, которая сразу заканчивает работу с отметкой 7.',
                    'Строка <code>execve</code> с <code>/bin/bash</code>, <code>bash.23823227</code>: копия загружает в себя вторую оболочку. Строки о завершении в записи нет.',
                    'Нижнее окно: напечатано <code>code 7</code>. Родитель взял это число из <code>$?</code>.'),
         'linux': see('Окно терминала Ubuntu, вывод <code>strace -f</code>. Программа 3873 — вторая оболочка <code>sh</code>, её создал <code>bash</code> с номером 3872.',
                      'Строка <code>exit_group(7)</code> в программе 3873: <code>sh</code> закончила работу с отметкой 7. Строка ниже, <code>+++ exited with 7 +++</code>, это подтверждает.',
                      'Строка <code>wait4</code> у родителя вернула 3873, в скобках <code>WEXITSTATUS(s) == 7</code>: родитель получил отметку 7.',
                      'Строка <code>code 7</code>: <code>echo</code> напечатал число, которое оболочка взяла из <code>$?</code>.')},
    do={'win': ('Получите отметку о результате', 'Очистите запись <kbd>Ctrl</kbd>+<kbd>X</kbd> и включите её <kbd>Ctrl</kbd>+<kbd>E</kbd>. В командной строке выполните <code>cmd /c exit 7</code>: вторая командная строка сразу закончит работу с числом 7. Затем выполните <code>echo code %errorlevel%</code>: переменная <code>errorlevel</code> хранит число последней команды. Остановите запись и прокрутите её в конец.'),
        'mac': ('Получите отметку о результате', 'В верхнем окне снова выполните <code>sudo fs_usage -f exec</code>. В нижнем выполните <code>bash -c \'exit 7\'; echo code $?</code>: вторая оболочка <code>bash</code> сразу закончит работу с числом 7, а <code>$?</code> хранит число последней команды. Остановите запись.'),
        'linux': ('Получите отметку о результате', 'Выполните <code>strace -f -e trace=process bash -c \'sh -c "exit 7"; echo code $?\'</code>. Оболочка <code>bash</code> запустит вторую оболочку <code>sh</code>, та сразу закончит работу с числом 7, а <code>$?</code> хранит число последней команды.')},
    shot={'win': '03-exit.png', 'linux': '03-exit.png',
          'mac': '03-exit.png'},
    notes={'win': ('', '<p>Отметка о результате — число, которое программа оставляет, закончив работу. Система хранит его, пока родитель не прочитает. 0 — всё хорошо, другие числа — ошибка. Что значит каждое число, решает сама программа.</p>'),
           'mac': ('', '<p>Завершения в записи нет. Число видно у родителя: оболочка дождалась ребёнка и положила его в <code>$?</code>. 0 — всё хорошо, другие числа — ошибка. Что значит каждое число, решает сама программа.</p>'),
           'linux': ('', '<p>Число 7 прошло путь от ребёнка к родителю: <code>sh</code> оставила его при завершении, система хранила, <code>bash</code> забрал его заявкой <code>wait4</code>. В шаге 1 число было 0, здесь — 7.</p>')},
    q='код завершения, где он виден у ребёнка и где у родителя.'))

S.append(dict(
    why='Что будет, если нужной программы нет? Смотрим, как система ищет её по папкам и откуда берётся ошибка «не найдено».',
    see={'win': see('Главное окно Process Monitor, запись прокручена в начало. Все строки — <code>cmd.exe</code> 1988: он ищет файл <code>nosuch</code> в папках (операция <code>QueryDirectory</code>). Внизу: <code>Showing 11 of 132 414 events</code>. В окне командной строки, которого на кадре не видно, — сообщение «"nosuch" не является внутренней или внешней командой» и <code>code 9009</code>.',
                    'Первый поиск: <code>C:\\Users\\user\\nosuch.*</code>, ответ <code>NO SUCH FILE</code> — такого файла нет. Сначала <code>cmd.exe</code> ищет в текущей папке.',
                    'Ещё десять таких же поисков, по одному на каждую папку из списка <code>PATH</code>: папки Python, <code>System32</code>, <code>Windows</code> и другие. Везде <code>NO SUCH FILE</code>. Вместе с первым — 11 поисков.'),
         'mac': see('Два окна Терминала. Сверху — запись. В квадратных скобках после вызова стоит номер ошибки: <code>[ 2]</code> — «нет такого файла». Снизу — команда <code>env nosuch; echo code $?</code>.',
                    'Копия <code>bash</code> загружает программу <code>/usr/bin/env</code>.',
                    'Шесть строк <code>execve</code> программы <code>env</code> с путями <code>/opt/homebrew/bin/nosuch</code>, <code>/usr/local/bin/nosuch</code>, <code>/usr/bin/nosuch</code> и так далее. У каждой <code>[ 2]</code>: в этой папке программы нет.',
                    'Нижнее окно: <code>env: nosuch: No such file or directory</code> и <code>code 127</code> — число, с которым закончила <code>env</code>.'),
         'linux': see('Окно терминала Ubuntu. Команда <code>strace -f -e trace=execve env nosuch</code> показывает только замены программы (<code>execve</code>). <code>ENOENT</code> — ошибка «нет такого файла».',
                      'Строка <code>execve</code> загружает программу <code>env</code> с аргументом <code>nosuch</code>. Ответ 0 — всё хорошо.',
                      'Десять строк <code>execve</code> с путями <code>/usr/local/sbin/nosuch</code>, <code>/usr/local/bin/nosuch</code> и так далее: по одной на каждую папку из <code>PATH</code>. Везде <code>-1 ENOENT (No such file or directory)</code>: в папке программы нет.',
                      'Строка <code>+++ exited with 127 +++</code>: <code>env</code> закончила работу с числом 127. Выше рамки — её сообщение об ошибке.')},
    do={'win': ('Запустите программу, которой нет', 'Откройте фильтр <kbd>Ctrl</kbd>+<kbd>L</kbd>, снимите галочку у условия <b>Event Class</b> и добавьте условие <b>Path contains nosuch</b>, затем <b>OK</b>. Фильтр покажет только поиск файла <code>nosuch</code>. Очистите запись и включите её. В командной строке выполните <code>nosuch</code>, затем <code>echo code %errorlevel%</code>. Остановите запись и прокрутите её в начало (<kbd>Home</kbd>).'),
        'mac': ('Запустите программу, которой нет', 'В верхнем окне выполните <code>sudo fs_usage -f exec</code>. В нижнем выполните <code>env nosuch; echo code $?</code>. Команда <code>env</code> запускает программу по имени и ищет её так же, как это делает система. Остановите запись.'),
        'linux': ('Запустите программу, которой нет', 'Выполните <code>strace -f -e trace=execve env nosuch</code>. Команда <code>env</code> запускает программу по имени и ищет её так же, как это делает система. Ключ <code>-e trace=execve</code> оставляет только замены программы.')},
    shot={'win': '04-path.png', 'linux': '04-path.png',
          'mac': '04-path.png'},
    notes={'win': ('', '<p>Строки <code>Process Create</code> нет: <code>cmd.exe</code> сама искала файл по списку <code>PATH</code>, не нашла и ничего не создавала. 9009 — число, которым <code>cmd.exe</code> сообщает «команда не найдена». Если подать ядру заявку <code>CreateProcessW</code> с несуществующим именем, она вернёт ошибку 2, <code>ERROR_FILE_NOT_FOUND</code>.</p>'),
           'mac': ('', '<p>Ядро умеет искать программу только по полному пути. Папки из <code>PATH</code> перебирает сама <code>env</code> (функция <code>execvp</code>). Ошибка 2, <code>ENOENT</code>, — «нет такого файла». 127 — число «программа не найдена». Свой список папок покажет <code>echo $PATH</code>.</p>'),
           'linux': ('', '<p>Ядро умеет искать программу только по полному пути. Папки из <code>PATH</code> перебирает сама <code>env</code> (функция <code>execvp</code>). <code>ENOENT</code> — ошибка 2, «нет такого файла». 127 — число «программа не найдена».</p>')},
    q='сколько папок проверено, код ошибки поиска и код завершения.'))

S.append(dict(
    why='Остаётся проверить, что другие программы запускают так же. Берём Python и сравниваем с оболочкой из шага 1.',
    see={'win': see('Главное окно Process Monitor. Python (<code>python.exe</code>, номер 8364) сначала подключает свои библиотеки (строки выше рамок), потом создаёт ребёнка — <code>hostname.exe</code>. В окне командной строки, которого на кадре не видно, Python печатает <code>code 0</code>.',
                    'Строка <code>python.exe</code> 8364, <code>Process Create</code>: Python создал <code>hostname.exe</code>. В Detail — <code>PID: 1492</code>, его номер.',
                    'Строка <code>Process Start</code> программы <code>hostname.exe</code> 1492, в Detail — <code>Parent PID: 8364</code>: родитель — Python.'),
         'mac': see('Два окна Терминала. Сверху — запись, снизу — команда Python с <code>subprocess.run</code>. Внизу напечатано <code>code 0</code>: Python получил число 0.',
                    'Копия <code>bash</code> заменяется на <code>python3.14</code> — короткую программу-запускатель из Homebrew.',
                    'Строка <code>posix_spawn</code> — копия и замена программы одной заявкой. Так запускатель включает настоящий Python: <code>Python.app/Contents/MacOS/Python</code>.',
                    'Три строки <code>execve</code> программы <code>Python</code>, у каждой <code>[ 2]</code> (нет такого файла): ребёнок Python ищет <code>hostname</code> по папкам из <code>PATH</code>.',
                    'Четвёртая попытка, <code>/bin/hostname</code>, прошла без ошибки: программа найдена и загружена.'),
         'linux': see('Окно терминала Ubuntu, вывод <code>strace -f -e trace=process</code> для команды Python с <code>subprocess.run</code>. Родитель — <code>python3</code>, номер 3883, ребёнок — 3884. Пометка <code>&lt;unfinished ...&gt;</code> значит «ответ будет ниже, в строке <code>resumed</code>».',
                      'Строка <code>clone</code> с флагами <code>CLONE_VM|CLONE_VFORK</code> — копия: Python создаёт ребёнка. В той же строке <code>Process 3884 attached</code> — <code>strace</code> начал следить за ребёнком 3884.',
                      'Три строки <code>execve</code> в программе 3884 с ответом <code>ENOENT</code>: <code>/usr/local/sbin/hostname</code>, <code>/usr/local/bin/hostname</code>, <code>/usr/sbin/hostname</code>. Ребёнок ищет <code>hostname</code> по папкам из <code>PATH</code>.',
                      'Четвёртая попытка, <code>/usr/bin/hostname</code>, удалась. Её ответ 0 стоит ниже, в строке <code>&lt;... execve resumed&gt;</code>.',
                      'Строка <code>wait4(3884, …)</code> у Python: он дождался программы 3884 и получил отметку 0 (<code>WEXITSTATUS(s) == 0</code>). Ниже <code>code 0</code> напечатал сам Python.')},
    do={'win': ('Запустите программу из Python', 'Откройте фильтр, снимите галочки у обоих условий <b>Path</b> и верните галочку <b>Event Class</b>. Очистите запись и включите её. В командной строке выполните<br><code>python -c "import subprocess; r = subprocess.run([\'hostname\'], capture_output=True); print(\'code\', r.returncode)"</code><br>Python запустит <code>hostname</code> как дочернюю программу, дождётся её, заберёт её вывод и напечатает число-результат.<br>Ключи: <code>subprocess.run</code> — запуск с ожиданием, <code>capture_output=True</code> — забрать вывод, <code>r.returncode</code> — число-результат. Остановите запись и найдите строку <code>python.exe</code> с операцией <code>Process Create</code>.'),
        'mac': ('Запустите программу из Python', 'В верхнем окне выполните <code>sudo fs_usage -f exec</code>. В нижнем выполните<br><code>python3 -c "import subprocess; r = subprocess.run([\'hostname\'], capture_output=True); print(\'code\', r.returncode)"</code><br>Python запустит <code>hostname</code> как дочернюю программу, дождётся её, заберёт её вывод и напечатает число-результат.<br>Ключи: <code>subprocess.run</code> — запуск с ожиданием, <code>capture_output=True</code> — забрать вывод, <code>r.returncode</code> — число-результат. Остановите запись.'),
        'linux': ('Запустите программу из Python', 'Выполните<br><code>strace -f -e trace=process python3 -c "import subprocess; r = subprocess.run([\'hostname\'], capture_output=True); print(\'code\', r.returncode)"</code><br>Python запустит <code>hostname</code> как дочернюю программу, дождётся её, заберёт её вывод и напечатает число-результат.<br>Ключи: <code>subprocess.run</code> — запуск с ожиданием, <code>capture_output=True</code> — забрать вывод, <code>r.returncode</code> — число-результат.')},
    shot={'win': '05-python.png', 'linux': '05-python.png',
          'mac': '05-python.png'},
    notes={'win': ('', '<p>Родитель теперь Python, а запуск устроен так же, как у командной строки в шаге 1: <code>subprocess.run</code> подаёт ядру ту же заявку <code>CreateProcessW</code>.</p>'),
           'mac': ('', '<p>Python запускает программу так же, как оболочка: копия, затем замена с перебором папок из <code>PATH</code>. Строка <code>posix_spawn</code> — второй способ: копия и замена одной заявкой.</p>'),
           'linux': ('', '<p>Python запускает программу теми же двумя шагами, что оболочка в шаге 1. Разница одна: флаги в <code>clone</code> отключают копирование памяти родителя: копию всё равно сразу заменят. Так запуск быстрее.</p>')},
    q='номер процесса Python, номер ребёнка и <span data-os="win">событие</span><span data-os="mac linux">вызов</span>, которым ребёнок создан.'))

GIST = gist([
    ('Новую программу заводит ядро', 'Родитель только подаёт заявку ядру. Так руководитель просит отдел кадров принять сотрудника: номер, место и пропуск выдаёт отдел кадров.', 'Ядро даёт номер и память и загружает программу.'),
    ('Сначала копия, потом замена', 'В macOS и Linux ядро делает копию родителя и заменяет в ней программу на нужную. В Windows всё одной заявкой.', 'Номер при замене не меняется.'),
    ('В конце — отметка о результате', 'Ребёнок оставляет число: 0 — всё хорошо, другое — ошибка. Родитель его забирает, как отметку «сделано» или «не сделано».', 'Если программы нет, система перебирает папки из PATH и отвечает ошибкой.')],
    'как рождается программа → библиотеки → отметка о результате → программы нет → запуск из Python.')

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
          <p class="lead">Любая команда в терминале проходит три шага. Родитель просит ядро создать программу. Ядро её загружает. Программа в конце оставляет отметку о результате. Каждый шаг вы увидите в записи.</p>
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
          <p>Вверху шага — действие. Ниже — кадр экрана после действия; красные рамки отмечают места, о которых идёт речь, номера рамок повторяются в тексте. Под действием — «Зачем этот шаг». Под каждым кадром — «Что на кадре»: что это за окно и что в каждой рамке. Ниже — «Что это значит»: вывод шага. Строка «В отчёт» — что записать в <code>report.md</code>. Номера процессов у вас будут другими.</p>
        </div>

        <h2 id="s2"><span class="sec">§2</span>Как рождается процесс</h2>

        <p>Новую программу не запускает сама команда. Родитель (ЛР 4) подаёт ядру заявку, и ядро создаёт программу. Такую заявку программисты называют <span class="term">системным вызовом</span>.</p>

        <p>Ядро выдаёт новой программе номер и память и загружает её файл. Потом подключаются библиотеки — готовые наборы действий, без которых программа не работает. Их список в ЛР 3 печатал <span data-os="win"><code>dumpbin</code></span><span data-os="mac"><code>otool -L</code></span><span data-os="linux"><code>ldd</code></span>. Часть системы, которая их подключает, называется <span class="term">загрузчик</span>.</p>
{PIC_BIRTH}
        <p data-os="win">Слева на схеме — родитель, справа — работающий ребёнок. В Windows между ними одна заявка: ядро создаёт программу и сразу загружает в неё нужный файл.</p>
        <p data-os="win" class="tech"><b>В коде:</b> <code>CreateProcessW</code>; подключение библиотек начинается в <code>ntdll.dll</code>, её ядро кладёт в каждую программу.</p>
        <p data-os="mac linux">Слева на схеме — родитель, справа — работающий ребёнок. Между ними две заявки. Сначала ядро делает копию родителя с новым номером. Потом заменяет в копии программу на нужную. Номер остаётся прежним.</p>
        <p data-os="mac linux" class="tech"><b>В коде:</b> <span data-os="linux"><code>clone</code></span><span data-os="mac"><code>fork</code></span> — копия, <code>execve</code> — замена программы; библиотеки подключает <span data-os="linux"><code>ld-linux</code></span><span data-os="mac"><code>dyld</code></span>.</p>

        <p>Когда программа заканчивает работу, она оставляет число — <span class="term">код завершения</span>. Это отметка о результате: 0 — всё хорошо, другое число — ошибка. Родитель её забирает:</p>
{PIC_WAIT}
        <p>Ребёнок оставил 7. Ядро хранит число в записи о нём, родитель ждёт и получает его. Пока число не забрали, запись занимает место. Поэтому родитель должен забирать отметки о результате.</p>

        <p>Заявки ядру записывает отдельная программа. Вот какая в каждой системе:</p>

        <div class="table-scroll">
          <table>
            <thead><tr><th></th><th>Windows</th><th>macOS</th><th>Linux</th></tr></thead>
            <tbody>
              <tr><td>Программа</td><td>Process Monitor</td><td><code>fs_usage</code></td><td><code>strace</code></td></tr>
              <tr><td>Что записывает</td><td>события всех программ: запуск, файлы, реестр, сеть</td><td>обращения всех программ к файлам и запуск программ</td><td>заявки ядру одной программы и её детей</td></tr>
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
              <tr><td>Создать программу</td><td><code>CreateProcessW</code>: событие <code>Process Create</code> у родителя</td><td><code>fork</code>, затем <code>execve</code>; или <code>posix_spawn</code></td><td><code>clone</code>, затем <code>execve</code></td></tr>
              <tr><td>Первое событие ребёнка</td><td><code>Process Start</code> с <code>Parent PID</code></td><td colspan="2"><code>execve</code> загружает программу в копию родителя</td></tr>
              <tr><td>Библиотеки</td><td><code>Load Image</code>: сначала <code>ntdll.dll</code></td><td>загрузчик <code>dyld</code>: общий кэш <code>dyld_shared_cache</code></td><td>загрузчик <code>ld-linux</code>: <code>ld.so.cache</code>, <code>libc.so.6</code></td></tr>
              <tr><td>Отметка о результате</td><td><code>Process Exit</code>, <code>Exit Status</code>; в командной строке <code>%errorlevel%</code></td><td>в оболочке <code>$?</code>; <code>fs_usage</code> завершение не показывает</td><td><code>exit_group</code> у ребёнка, <code>wait4</code> у родителя; в оболочке <code>$?</code></td></tr>
              <tr><td>Программы нет</td><td>поиск по <code>PATH</code>, код <code>cmd.exe</code> 9009; у <code>CreateProcessW</code> ошибка 2</td><td colspan="2"><code>execve</code> по папкам <code>PATH</code> с ошибкой <code>ENOENT</code> (2), код 127</td></tr>
            </tbody>
          </table>
        </div>

        <ul>
          <li>Во всех пяти шагах путь один: родитель подаёт заявку ядру, ядро загружает программу, потом подключаются библиотеки.</li>
          <li>Программа заканчивает работу с отметкой о результате, родитель её забирает.</li>
          <li>Python в шаге 5 прошёл тот же путь, что и оболочка.</li>
          <li>В главе 2.2 этот путь пройдёт ядро агента: функция на C запустит программу, дождётся её и вернёт мозгу отметку о результате.</li>
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
          <summary>Кто создаёт новую программу: родитель или ядро?</summary>
          <p>Ядро. Родитель только подаёт заявку: <span data-os="win"><code>CreateProcessW</code></span><span data-os="mac linux"><code>fork</code> или <code>clone</code>, затем <code>execve</code></span>. Ядро выдаёт номер и память и загружает программу.</p>
        </details>
        <details>
          <summary>Почему в Linux номер не меняется после <code>execve</code>?</summary>
          <p><code>execve</code> заменяет программу в уже созданной копии. Номер выдан раньше, при <code>clone</code>, и остаётся до конца работы программы.</p>
        </details>
        <details>
          <summary>Какая библиотека подключается первой и почему?</summary>
          <p>В Windows — <code>ntdll.dll</code>: в ней находится то, что подключает остальные библиотеки. В Linux первым работает загрузчик <code>ld-linux</code>: он открывает <code>ld.so.cache</code>, потом библиотеки программы. В macOS это загрузчик <code>dyld</code>.</p>
        </details>
        <details>
          <summary>Откуда родитель узнаёт отметку о результате?</summary>
          <p>Ребёнок оставляет число ядру, когда заканчивает работу. Родитель ждёт ребёнка и забирает число: в Windows — <code>WaitForSingleObject</code> и <code>GetExitCodeProcess</code>, в macOS и Linux — <code>wait4</code> или <code>waitpid</code>.</p>
        </details>
        <details>
          <summary>Почему при запуске несуществующей программы в записи несколько попыток?</summary>
          <p>Имя без пути ищется по очереди во всех папках из <code>PATH</code>. Из каждой приходит ответ «нет такого файла». Только после последней запуск признаётся неудачным.</p>
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
