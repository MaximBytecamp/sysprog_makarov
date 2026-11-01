"""Лабораторная работа 2 «Программа в отладчике» → temy/09-laboratornaya-2/index.html.

Кадры macOS — VS Code 1.138 на Mac (macOS 26, Apple clang 17, расширение C/C++ 1.34.4, отладчик lldb через lldb-mi).
Кадры Linux — VS Code 1.138 для Linux в контейнере sp-lab2-linux (Debian, gcc 14, gdb 16.3), виртуальный экран Xvfb.
Съёмка: ~/sysprog-shots/lab2/shoot.py mac|linux, рамки — mark.py. Числа в тексте взяты с этих кадров.
Кадры Windows — ВМ Win11-lab (Windows 11 ARM64, VS Code 1.144, MSVC x64 через эмулятор, cppvsdbg); VS Code в ВМ снимается по CDP через проброс порта (~/sysprog-shots/winsrv/start.cmd)."""
from pathlib import Path
from lab_build import steps
from ch11 import hl

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'temy/09-laboratornaya-2/index.html'
SRC = Path.home() / 'sysprog-shots/lab2/src'
CODE = (SRC / 'debug.c').read_text()


def mk(n):
    return f'<span class="mk">{n}</span>'


S = []

# ─────────────── Часть 1. Запуск под отладчиком ───────────────
S.append(dict(
    do={'win': ('Соберите и запустите программу без отладчика', 'Откройте папку <code>02-debugger</code> в VS Code командой <code>code .</code> из <b>x64 Native Tools Command Prompt</b>. Откройте встроенный терминал (<b>Terminal → New Terminal</b>). Если в нём PowerShell, выберите справа от <b>+</b> стрелку и пункт <b>Command Prompt</b>. Выполните <code>cl /nologo /Zi /Od /W4 debug.c && debug.exe</code>.'),
        'mac': ('Соберите и запустите программу без отладчика', 'Откройте папку <code>02-debugger</code> в VS Code (<b>File → Open Folder</b>), затем встроенный терминал: <b>Terminal → New Terminal</b>. Выполните <code>clang -g -O0 -Wall -Wextra -o debug debug.c && ./debug</code>.'),
        'linux': ('Соберите и запустите программу без отладчика', 'Откройте папку <code>02-debugger</code> в VS Code (<b>File → Open Folder</b>), затем встроенный терминал: <b>Terminal → New Terminal</b>. Выполните <code>gcc -g -O0 -Wall -Wextra -o debug debug.c && ./debug</code>.')},
    shot='01-build.png',
    notes={'win': ('<p>' + mk(1) + ' — команда сборки и запуска. Ниже компилятор вывел имя файла и предупреждение C4996 для строки 19: функция <code>strcpy</code> «может быть небезопасна». ' + mk(2) + ' — вывод программы: <code>agent: total=6 area=12</code>.</p>',
                   '<p>Программа отработала целиком за долю секунды и напечатала одну строку. Что происходило внутри, по выводу не видно. Ключ <code>/Zi</code> записал рядом файл <code>debug.pdb</code> со сведениями для отладчика: какая машинная команда относится к какой строке кода и где лежит каждая переменная. Ключ <code>/Od</code> выключил оптимизацию. Предупреждение C4996 MSVC выдаёт на <code>strcpy</code>, потому что она не проверяет размер буфера: в главе 1.1, шаг 3, показано, что бывает при записи за его границу. Программа собрана, предупреждение работу не останавливает.</p>'),
           'mac': ('<p>' + mk(1) + ' — команда сборки и запуска. ' + mk(2) + ' — вывод программы: <code>agent: total=6 area=12</code>.</p>',
                   '<p>Программа отработала целиком за долю секунды и напечатала одну строку. Что происходило внутри, по выводу не видно. Ключ <code>-g</code> добавил сведения для отладчика: какая машинная команда относится к какой строке кода и где лежит каждая переменная. В macOS они лежат в папке <code>debug.dSYM</code> рядом с программой. Ключ <code>-O0</code> выключил оптимизацию, чтобы порядок команд совпадал с порядком строк.</p>'),
           'linux': ('<p>' + mk(1) + ' — команда сборки и запуска. ' + mk(2) + ' — вывод программы: <code>agent: total=6 area=12</code>.</p>',
                     '<p>Программа отработала целиком за долю секунды и напечатала одну строку. Что происходило внутри, по выводу не видно. Ключ <code>-g</code> добавил в файл <code>debug</code> сведения для отладчика: какая машинная команда относится к какой строке кода и где лежит каждая переменная. Ключ <code>-O0</code> выключил оптимизацию, чтобы порядок команд совпадал с порядком строк.</p>')},
    q='строку, которую напечатала программа.'))

S.append(dict(
    do=('Откройте настройки запуска', 'В панели Explorer раскройте папку <code>.vscode</code> и откройте <code>launch.json</code>. Файлы <code>launch.json</code> и <code>tasks.json</code> вы создали в §1 «Подготовка».'),
    shot='02-launch.png',
    notes={'win': ('<p>' + mk(1) + ' — папка настроек VS Code с двумя файлами. ' + mk(2) + ' — какую программу запускать: <code>debug.exe</code> в папке проекта. ' + mk(3) + ' — <code>"type": "cppvsdbg"</code>, отладчик Visual Studio для программ MSVC. ' + mk(4) + ' — перед запуском выполнить задачу <code>build</code> из <code>tasks.json</code>, то есть собрать программу заново.</p>',
                   '<p>Ничего не запустилось: файл только описывает, как запускать отладку. В Explorer видны файлы сборки из шага 1: <code>debug.exe</code>, <code>debug.obj</code>, <code>debug.pdb</code>, <code>debug.ilk</code> и <code>vc140.pdb</code>. Строка <code>"console": "integratedTerminal"</code> — программа будет печатать во встроенный терминал VS Code.</p>'),
           'mac': ('<p>' + mk(1) + ' — папка настроек VS Code с двумя файлами. ' + mk(2) + ' — какую программу запускать: <code>debug</code> в папке проекта. ' + mk(3) + ' — <code>"MIMode": "lldb"</code>, отладчик LLDB из Command Line Tools. ' + mk(4) + ' — перед запуском выполнить задачу <code>build</code> из <code>tasks.json</code>, то есть собрать программу заново.</p>',
                   '<p>Ничего не запустилось: файл только описывает, как запускать отладку. Строка <code>"targetArchitecture": "arm64"</code> нужна на Mac с процессором Apple: без неё отладчик считает программу программой для Intel и не останавливается. На Mac с Intel в ней пишут <code>x86_64</code>.</p>'),
           'linux': ('<p>' + mk(1) + ' — папка настроек VS Code с двумя файлами. ' + mk(2) + ' — какую программу запускать: <code>debug</code> в папке проекта. ' + mk(3) + ' — <code>"MIMode": "gdb"</code>, отладчик GDB. ' + mk(4) + ' — перед запуском выполнить задачу <code>build</code> из <code>tasks.json</code>, то есть собрать программу заново.</p>',
                     '<p>Ничего не запустилось: файл только описывает, как запускать отладку. Кнопка запуска отладчика прочитает его.</p>')}))

S.append(dict(
    do=('Поставьте точку останова на строке 15', 'Откройте <code>debug.c</code> и щёлкните слева от номера строки 15 — <code>struct point p = {3, 4};</code>. Появится красная точка. Затем откройте панель <b>Run and Debug</b> на левой полосе (значок треугольника с жуком) или нажмите <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>D</kbd> (на Mac — <kbd>⌘</kbd>+<kbd>⇧</kbd>+<kbd>D</kbd>).'),
    shot='03-breakpoint.png',
    notes=('<p>' + mk(1) + ' — строка 15 с красной точкой слева. ' + mk(2) + ' — та же точка в списке <b>Breakpoints</b>: файл <code>debug.c</code>, строка 15. Остальные разделы панели — Variables, Watch, Call Stack — пустые: программа ещё не запущена.</p>',
           '<p>Программа не изменилась, точка хранится в настройках VS Code. Когда программа под отладчиком дойдёт до строки 15, отладчик остановит её <b>перед</b> выполнением этой строки.</p>'),
    q='номер строки, на которой стоит точка останова.'))

S.append(dict(
    do=('Запустите отладку', 'Нажмите <kbd>F5</kbd> или зелёный треугольник <b>debug</b> вверху панели Run and Debug. Дождитесь, пока строка 15 подсветится жёлтым. В разделе <b>Variables</b> раскройте <b>Locals</b> и <code>p</code>.'),
    shot='04-paused.png',
    notes={'win': ('<p>' + mk(1) + ' — жёлтая стрелка у строки 15: программа стоит перед ней. ' + mk(2) + ' — локальные переменные <code>main</code>, по алфавиту: <code>a = 0</code>, массив <code>name</code> (справа его адрес), <code>p</code> с полями <code>x = 0</code> и <code>y = 0</code>, <code>total = 0</code>. ' + mk(3) + ' — стек вызовов: <code>debug.exe!main()</code>, строка 15.</p>',
                   '<p>Программа запущена и стоит. Все переменные <code>main</code> уже существуют, но строки, которые их заполняют, ещё не выполнены. В них лежит то, что осталось в этой памяти: в этот раз нули, при другом запуске или на другом компьютере могут быть случайные числа. Под <code>main</code> в стеке — функции, которые её запустили: служебный код MSVC <code>__scrt_common_main</code> и функции Windows из <code>kernel32.dll</code> и <code>ntdll.dll</code>. Строка состояния внизу стала синей: идёт отладка.</p>'),
           'mac': ('<p>' + mk(1) + ' — жёлтая стрелка у строки 15: программа стоит перед ней. ' + mk(2) + ' — локальные переменные <code>main</code>: <code>p</code> с полями <code>x = -16</code> и <code>y = -1</code>, массив <code>name</code>, <code>total = 2</code>, <code>a = 0</code>. ' + mk(3) + ' — стек вызовов: <code>debug!main</code>, файл <code>debug.c</code>, строка 15.</p>',
                   '<p>Программа запущена и стоит. Все переменные <code>main</code> уже существуют, но строки, которые их заполняют, ещё не выполнены. В них лежат случайные числа — то, что осталось в этой памяти от прошлой работы: <code>x = -16</code>, <code>total = 2</code>. При следующем запуске числа могут быть другими. Внизу экрана строка состояния стала синей: идёт отладка.</p>'),
           'linux': ('<p>' + mk(1) + ' — жёлтая стрелка у строки 15: программа стоит перед ней. ' + mk(2) + ' — локальные переменные <code>main</code>: <code>p</code> с полями <code>x = -136240616</code> и <code>y = 2555903</code>, массив <code>name</code>, <code>total = 2</code>, <code>a = 65535</code>. ' + mk(3) + ' — стек вызовов: <code>main()</code>, файл <code>debug.c</code>, строка 15.</p>',
                     '<p>Программа запущена и стоит. Все переменные <code>main</code> уже существуют, но строки, которые их заполняют, ещё не выполнены. В них лежат случайные числа — то, что осталось в этой памяти от прошлой работы: <code>x = -136240616</code>, <code>a = 65535</code>. При следующем запуске числа могут быть другими. Внизу экрана строка состояния стала синей: идёт отладка.</p>')},
    q='значения <code>p.x</code>, <code>p.y</code> и <code>total</code> до выполнения строки 15.'))

S.append(dict(
    do=('Выполните строку 15', 'Нажмите <kbd>F10</kbd> — <b>Step Over</b>, шаг с обходом. Это вторая кнопка на панели отладки, стрелка дугой.'),
    shot='05-step.png',
    notes=('<p>' + mk(1) + ' — стрелка теперь у строки 17 <code>int total = 0;</code>. ' + mk(2) + ' — поля <code>p</code>: <code>x = 3</code>, <code>y = 4</code>.</p>',
           '<p>Строка 15 выполнилась: в <code>p</code> записаны 3 и 4. Строку 16 отладчик пропустил: <code>char name[8];</code> только объявляет массив, машинных команд для неё нет. <code>total</code> пока прежний: строка 17 ещё не выполнена.</p>'),
    q='значения <code>p.x</code> и <code>p.y</code> после шага.'))

S.append(dict(
    do=('Пройдите строки 17 и 19, раскройте массив name', 'Нажмите <kbd>F10</kbd> ещё два раза: стрелка встанет у строки 20. В Variables сверните <code>p</code> и раскройте <code>name</code>.'),
    shot='06-strcpy.png',
    notes={'win': ('<p>' + mk(1) + ' — стрелка у строки 20 <code>for</code>. ' + mk(2) + ' — массив <code>name</code> по ячейкам: <code>[0] = 97 \'a\'</code>, <code>[1] = 103 \'g\'</code>, <code>[2] = 101 \'e\'</code>, <code>[3] = 110 \'n\'</code>, <code>[4] = 116 \'t\'</code>, <code>[5]</code>–<code>[7]</code> — <code>0 \'\\0\'</code>. Выше — переменная цикла <code>i = 0</code>.</p>',
                   '<p>Строка 17 записала 0 в <code>total</code>. Строка 19 — функция <code>strcpy</code> — записала в массив пять букв и завершающий ноль в <code>[5]</code>. Отладчик показывает каждую ячейку дважды: числом и буквой. 97 — код буквы <code>a</code>. Ячейки <code>[6]</code> и <code>[7]</code> <code>strcpy</code> не трогает: в них осталось то, что было. Переменная цикла <code>i</code> уже видна, но цикл ещё не начался.</p>'),
           'mac': ('<p>' + mk(1) + ' — стрелка у строки 20 <code>for</code>. ' + mk(2) + ' — массив <code>name</code> по ячейкам: <code>[0] = 97 \'a\'</code>, <code>[1] = 103 \'g\'</code>, <code>[2] = 101 \'e\'</code>, <code>[3] = 110 \'n\'</code>, <code>[4] = 116 \'t\'</code>, <code>[5]</code>–<code>[7]</code> — <code>0 \'\\0\'</code>. Ниже — <code>total = 0</code>.</p>',
                   '<p>Строка 17 записала 0 в <code>total</code>. Строка 19 — функция <code>strcpy</code> — записала в массив пять букв и завершающий ноль в <code>[5]</code>. Отладчик показывает каждую ячейку дважды: числом и буквой. 97 — код буквы <code>a</code>. Ячейки <code>[6]</code> и <code>[7]</code> <code>strcpy</code> не трогает: в этот раз в них оказались нули.</p>'),
           'linux': ('<p>' + mk(1) + ' — стрелка у строки 20 <code>for</code>. ' + mk(2) + ' — массив <code>name</code> по ячейкам: <code>[0] = 97 \'a\'</code> … <code>[4] = 116 \'t\'</code>, <code>[5]</code>–<code>[7]</code> — <code>0 \'\\000\'</code>. Выше — переменная цикла <code>i = 0</code>.</p>',
                     '<p>Строка 17 записала 0 в <code>total</code>. Строка 19 — функция <code>strcpy</code> — записала в массив пять букв и завершающий ноль в <code>[5]</code>. Отладчик показывает каждую ячейку дважды: числом и буквой. 97 — код буквы <code>a</code>, <code>\'\\000\'</code> — так GDB пишет нулевой байт. Переменная цикла <code>i</code> уже видна, но цикл ещё не начался: в ней случайный 0.</p>')},
    q='код буквы в ячейке <code>name[0]</code> и в какой ячейке стоит завершающий ноль.'))

S.append(dict(
    do=('Следите за циклом в Watch', 'В разделе <b>Watch</b> нажмите <b>+</b> (Add Expression), введите <code>i</code> и нажмите Enter. Так же добавьте <code>total</code>. Нажмите <kbd>F10</kbd> три раза.'),
    shot='07-loop.png',
    notes=('<p>' + mk(1) + ' — стрелка у строки 21 <code>total += i;</code>. ' + mk(2) + ' — Watch: <code>i = 2</code>, <code>total = 1</code>.</p>',
           '<p>Стрелка прошла строки 20 → 21 → 20 → 21: цикл идёт второй раз. На первом проходе <code>total</code> стал 1. Сейчас <code>i = 2</code>, и строка 21 ещё не выполнена — после неё <code>total</code> станет 3. В Watch можно вписать любое выражение на C, например <code>total * 2</code> или <code>name[1]</code>.</p>'),
    q='значения <code>i</code> и <code>total</code> на кадре и каким станет <code>total</code> после следующего шага.'))

S.append(dict(
    do=('Зайдите в функцию area', 'Нажимайте <kbd>F10</kbd>, пока стрелка не встанет у строки 22 <code>int a = area(p);</code>. В Watch нажмите <b>Remove All Expressions</b>. Затем нажмите <kbd>F11</kbd> — <b>Step Into</b>, шаг с заходом: стрелка вниз на панели отладки. В Windows отладчик сначала встаёт на строку 9 с именем функции — нажмите <kbd>F10</kbd> ещё раз, чтобы перейти на строку 10.'),
    shot='08-step-into.png',
    notes={'win': ('<p>' + mk(1) + ' — стрелка у строки 10 в функции <code>area</code>. ' + mk(2) + ' — переменные <code>area</code>: <code>p</code> с полями <code>x = 3</code>, <code>y = 4</code> и <code>s = 0</code>. ' + mk(3) + ' — стек вызовов: <code>debug.exe!area(point p)</code> сверху, <code>debug.exe!main()</code> на строке 22 под ней.</p>',
                   '<p>Отладчик вошёл в функцию. В Variables теперь переменные <code>area</code>. <code>p</code> здесь — копия структуры из <code>main</code>: в C структура передаётся в функцию по значению. <code>s</code> ещё не вычислена, строка 10 не выполнена. Стек показывает, кто кого вызвал: <code>main</code> на строке 22 вызвала <code>area</code>. На строке 9 стек был таким же, но <code>p</code> ещё не была заполнена: код входа в функцию копирует аргументы до первой строки тела.</p>'),
           'mac': ('<p>' + mk(1) + ' — стрелка у строки 10 в функции <code>area</code>. ' + mk(2) + ' — переменные <code>area</code>: <code>s = 1</code> и <code>p</code> с полями <code>x = 3</code>, <code>y = 4</code>. ' + mk(3) + ' — стек вызовов: <code>debug!area</code> на строке 10 сверху, <code>debug!main</code> на строке 22 под ней.</p>',
                   '<p>Отладчик вошёл в функцию. В Variables теперь переменные <code>area</code>. <code>p</code> здесь — копия структуры из <code>main</code>: в C структура передаётся в функцию по значению. <code>s = 1</code> — случайное число, строка 10 ещё не выполнена. Стек показывает, кто кого вызвал: <code>main</code> на строке 22 вызвала <code>area</code>.</p>'),
           'linux': ('<p>' + mk(1) + ' — стрелка у строки 10 в функции <code>area</code>. ' + mk(2) + ' — переменные <code>area</code>: <code>s = 0</code> и <code>p</code> с полями <code>x = 3</code>, <code>y = 4</code>. ' + mk(3) + ' — стек вызовов: <code>area(struct point p)</code> на строке 10 сверху, <code>main()</code> на строке 22 под ней.</p>',
                     '<p>Отладчик вошёл в функцию. В Variables теперь переменные <code>area</code>. <code>p</code> здесь — копия структуры из <code>main</code>: в C структура передаётся в функцию по значению. <code>s = 0</code> — случайное число, строка 10 ещё не выполнена. Стек показывает, кто кого вызвал: <code>main</code> на строке 22 вызвала <code>area</code>.</p>')},
    q='сколько строк в стеке вызовов и какая функция сверху.'))

S.append(dict(
    do=('Посмотрите машинный код строки 10', 'Щёлкните правой кнопкой по строке 10 и выберите <b>Open Disassembly View</b>.'),
    shot='09-disasm.png',
    notes={'win': ('<p>Вкладка <b>Disassembly</b>: строки C вперемешку с командами процессора x64, у каждой команды — адрес, байты и текст. ' + mk(1) + ' — строка 10 и команда <code>mov eax, dword ptr [p]</code>: взять <code>p.x</code> в регистр <code>eax</code>. ' + mk(2) + ' — <code>imul eax, dword ptr [rsp+24h]</code>: умножить <code>eax</code> на <code>p.y</code> прямо из памяти. ' + mk(3) + ' — <code>mov dword ptr [rsp], eax</code>: записать результат в <code>s</code>.</p>',
                   '<p>Одна строка C стала тремя машинными командами. Результат умножения процессор держит в <span class="term">регистре</span> <code>eax</code> — ячейке внутри процессора — и потом кладёт в память. Команды x64 разной длины: 4, 5 и 3 байта. Строки <code>CC  int 3</code> выше и ниже — заполнитель между функциями. Кадр снят на компьютере с процессором ARM: программа собрана для x64 и выполняется через эмулятор, поэтому команды те же, что на компьютере с Intel или AMD.</p>'),
           'mac': ('<p>Вкладка <b>Disassembly</b>: слева адрес команды в памяти, справа сама команда процессора ARM64. ' + mk(1) + ' — <code>ldr w8, [sp, #0x8]</code> и <code>ldr w9, [sp, #0xc]</code>: взять из памяти <code>p.x</code> и <code>p.y</code> в регистры <code>w8</code> и <code>w9</code>. ' + mk(2) + ' — <code>mul w8, w8, w9</code>: умножить. ' + mk(3) + ' — <code>str w8, [sp, #0x4]</code>: записать результат в <code>s</code>.</p>',
                   '<p>Одна строка C стала четырьмя машинными командами. Процессор не умеет умножать числа прямо в памяти: сначала он берёт их в <span class="term">регистры</span> — ячейки внутри процессора, — умножает и кладёт результат обратно. <code>sp</code> — адрес места функции в стеке, <code>#0x8</code> — смещение поля от него. Сверху видны строки <code>udf #0x0</code>: это байты, которые не являются командами, отладчик показывает их как есть.</p>'),
           'linux': ('<p>Вкладка <b>Disassembly</b>: адрес команды, её байты в шестнадцатеричном виде и сама команда процессора ARM64. ' + mk(1) + ' — <code>ldr w1, [sp, #8]</code> и <code>ldr w0, [sp, #12]</code>: взять из памяти <code>p.x</code> и <code>p.y</code> в регистры. ' + mk(2) + ' — <code>mul w0, w1, w0</code>: умножить. ' + mk(3) + ' — <code>str w0, [sp, #28]</code>: записать результат в <code>s</code>.</p>',
                     '<p>Одна строка C стала четырьмя машинными командами. Процессор не умеет умножать числа прямо в памяти: сначала он берёт их в <span class="term">регистры</span> — ячейки внутри процессора, — умножает и кладёт результат обратно. Каждая команда ARM64 занимает 4 байта: адреса идут через 4. Байты <code>20 7c 00 1b</code> — это и есть команда <code>mul</code> в том виде, в каком её читает процессор.</p>')},
    q='имя машинной команды умножения на своей системе.'))

S.append(dict(
    do=('Выйдите из функции', 'Нажмите <kbd>Shift</kbd>+<kbd>F11</kbd> — <b>Step Out</b>, выход из функции: стрелка вверх. Затем один раз <kbd>F10</kbd>. Вернитесь на вкладку <code>debug.c</code>.'),
    shot='10-step-out.png',
    notes=('<p>' + mk(1) + ' — стрелка у строки 23 <code>printf</code>. ' + mk(2) + ' — <code>a = 12</code>. Выше — <code>total = 6</code> и <code>p</code> с полями 3 и 4.</p>',
           '<p>Функция <code>area</code> доработала до конца и вернула 12, отладчик снова в <code>main</code>. Шаг с обходом выполнил присваивание <code>a = area(p)</code>, и в <code>a</code> вместо прежнего значения появился результат. В стеке снова одна строка — <code>main</code>.</p>'),
    q='значения <code>a</code> и <code>total</code> перед <code>printf</code>.'))

S.append(dict(
    do={'win': ('Доведите программу до конца', 'Нажмите <kbd>F5</kbd> — <b>Continue</b>, продолжить. Откройте вкладку <b>Terminal</b> внизу и справа в списке терминалов выберите строку с путём к <code>debug.exe</code>.'),
        'mac': ('Доведите программу до конца', 'Нажмите <kbd>F5</kbd> — <b>Continue</b>, продолжить. Откройте вкладку <b>Debug Console</b> внизу.'),
        'linux': ('Доведите программу до конца', 'Нажмите <kbd>F5</kbd> — <b>Continue</b>, продолжить. Откройте вкладку <b>Terminal</b> внизу и справа в списке терминалов выберите <b>cppdbg: debug</b>.')},
    shot='11-finish.png',
    notes={'win': ('<p>' + mk(1) + ' — вывод программы <code>agent: total=6 area=12</code>. ' + mk(2) + ' — терминал программы в списке справа: он называется путём к <code>debug.exe</code>. Выше — терминал <code>cmd</code> из шага 1 и терминал задачи <code>build</code>.</p>',
                   '<p>Программа отработала без остановок до <code>return 0</code>. Разделы Variables и Call Stack опустели: процесса больше нет. Сообщение о коде завершения — «The program … has exited with code 0» — появляется во вкладке <b>Debug Console</b>. Вывод тот же, что в шаге 1: отладчик не меняет работу программы.</p>'),
           'mac': ('<p>Вкладка <b>Debug Console</b> — служебные сообщения отладчика. ' + mk(1) + ' — вывод программы <code>agent: total=6 area=12</code>. ' + mk(2) + ' — «The program … has exited with code 0»: программа завершилась с кодом 0.</p>',
                   '<p>Программа отработала без остановок до <code>return 0</code>. Разделы Variables и Call Stack опустели, панель отладки исчезла: процесса больше нет. Вывод тот же, что в шаге 1: отладчик не меняет работу программы, он только останавливает её и показывает память.</p>'),
           'linux': ('<p>' + mk(1) + ' — вывод программы <code>agent: total=6 area=12</code> в терминале отладчика. Строка <code>[1] + Done "/usr/bin/gdb" …</code> под ним — оболочка сообщает, что отладчик GDB завершился. ' + mk(2) + ' — терминал <b>cppdbg: debug</b> в списке.</p>',
                     '<p>Программа отработала без остановок до <code>return 0</code>. Разделы Variables и Call Stack опустели: процесса больше нет. В Linux программа под отладчиком пишет в отдельный терминал, а сообщение о коде завершения — «exited normally» — появляется во вкладке <b>Debug Console</b>. Вывод тот же, что в шаге 1: отладчик не меняет работу программы.</p>')},
    q='что напечатала программа под отладчиком и с каким кодом завершилась.'))

LAB = steps(S)

LAUNCH = {
    'win': '''{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "debug",
      "type": "cppvsdbg",
      "request": "launch",
      "program": "${workspaceFolder}/debug.exe",
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal",
      "preLaunchTask": "build"
    }
  ]
}''',
    'mac': (SRC / 'vscode-mac/launch.json').read_text().rstrip(),
    'linux': (SRC / 'vscode-linux/launch.json').read_text().rstrip()}
TASKS = {
    'win': '''{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "build",
      "type": "shell",
      "command": "cl /nologo /Zi /Od /W4 debug.c",
      "group": "build"
    }
  ]
}''',
    'mac': (SRC / 'vscode-mac/tasks.json').read_text().rstrip(),
    'linux': (SRC / 'vscode-linux/tasks.json').read_text().rstrip()}


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def files(o):
    return (f'<figure class="code" data-os="{o}"><figcaption><span>.vscode/launch.json</span></figcaption><pre>{esc(LAUNCH[o])}</pre></figure>\n'
            f'        <figure class="code" data-os="{o}"><figcaption><span>.vscode/tasks.json</span></figcaption><pre>{esc(TASKS[o])}</pre></figure>')


WORDS = [
    ('Точка останова', 'breakpoint', 'красная точка у строки: программа остановится перед этой строкой', 'закладка в книге с надписью «стоп, читать отсюда»'),
    ('Шаг с обходом', 'Step Over, F10', 'выполнить текущую строку целиком, даже если в ней вызов функции', 'пройти по коридору мимо двери кабинета'),
    ('Шаг с заходом', 'Step Into, F11', 'если в строке вызов функции — войти в неё и встать на её первую строку', 'открыть дверь и зайти в кабинет'),
    ('Выход из функции', 'Step Out, Shift+F11', 'доработать текущую функцию и встать в месте, откуда её вызвали', 'выйти из кабинета обратно в коридор'),
    ('Продолжить', 'Continue, F5', 'работать без остановок до следующей точки или до конца', 'читать дальше до следующей закладки'),
    ('Переменные', 'Variables', 'все переменные текущей функции и их значения сейчас', 'содержимое ящиков стола в этом кабинете'),
    ('Наблюдение', 'Watch', 'выражения, которые вы выбрали сами; пересчитываются на каждом шаге', 'табло, на которое вывели два-три важных числа'),
    ('Стек вызовов', 'Call Stack', 'цепочка функций: кто кого вызвал; сверху та, что работает сейчас', 'стопка папок на столе: верхнюю дочитать, под ней та, из-за которой её открыли'),
    ('Машинный код', 'Disassembly', 'команды процессора, в которые компилятор превратил строки C', 'та же инструкция, переведённая на язык станка'),
]
WORDS_HTML = '\n'.join(f'              <tr><td><b>{a}</b><br><code>{b}</code></td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in WORDS)

HTML = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>Лабораторная работа 2. Программа в отладчике · Справочник по системному программированию</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,600;0,7..72,700;1,7..72,400&family=Pixelify+Sans:wght@500;600;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css">
</head>
<body>
  <div class="book">
    <div class="book__body">
      <div class="spine"><span>Модуль 1 · Лабораторная работа 2</span></div>

      <main class="leaf">
        <div class="running">
          <p class="eyebrow"><a href="../../index.html" style="text-decoration:none;color:inherit">Справочник по системному программированию</a> · модуль 1 · лабораторная работа</p>
          <p class="running__folio">ЛР 2</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">ЛР 2</span>
          <h1>Программа<br>в отладчике</h1>
          <p class="lead">Обычный запуск показывает только то, что программа напечатала. Отладчик останавливает программу на нужной строке и показывает, что лежит в каждой переменной, какая функция кого вызвала и в какие команды процессора превратилась строка. В работе маленькая программа на C проходится по шагам в VS Code: точка останова, шаг с обходом и с заходом в функцию, переменные, массив по байтам, стек вызовов и машинный код. Каждый шаг — действие, кадр экрана и объяснение для системы, выбранной переключателем вверху страницы.</p>
        </header>

        <dl class="passport">
          <div><dt>Пара</dt><dd>2, первая половина; перед главой 1.1</dd></div>
          <div><dt>Время</dt><dd>35–40 минут</dd></div>
          <div><dt>Программы</dt><dd>VS Code с расширением C/C++, <span data-os="win">компилятор MSVC и отладчик Visual Studio</span><span data-os="mac">clang и отладчик LLDB</span><span data-os="linux">gcc и отладчик GDB</span></dd></div>
          <div><dt>Сдать</dt><dd><code>debug.c</code>, папку <code>.vscode</code> и <code>report.md</code> в папке <code>labs/02-debugger</code> репозитория <code>sysprog-start</code></dd></div>
        </dl>

        <nav class="contents">
          <b>В этой работе</b>
          <ol>
            <li><a href="#s1">Подготовка</a></li>
            <li><a href="#s2">Словарь отладчика</a></li>
            <li><a href="#s3">Часть 1. Запуск и остановка</a></li>
            <li><a href="#s4">Часть 2. Функция и машинный код</a></li>
            <li><a href="#s5">Что получилось</a></li>
            <li><a href="#s6">Отчёт</a></li>
            <li><a href="#s7">Проверьте себя</a></li>
          </ol>
        </nav>

        <h2 id="s1"><span class="sec">§1</span>Подготовка</h2>

        <p>Нужны VS Code, расширение <b>C/C++</b> от Microsoft и компилятор из ЛР 1. Расширение ставится во вкладке <b>Extensions</b> на левой полосе VS Code (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>X</kbd>, на Mac — <kbd>⌘</kbd>+<kbd>⇧</kbd>+<kbd>X</kbd>): поиск <code>C/C++</code>, кнопка <b>Install</b>. Вместе с ним ставится программа-посредник между VS Code и отладчиком системы. <span data-os="win">Отладчик для программ MSVC входит в само расширение.</span><span data-os="mac">Отладчик LLDB входит в Command Line Tools, которые ставились в ЛР 1.</span><span data-os="linux">Отладчик GDB ставится командой <code>sudo apt install gdb</code>.</span></p>

        <p>Работа лежит в репозитории <code>sysprog-start</code>, в папке <code>labs/02-debugger</code>. Создайте в ней файл <code>debug.c</code> и папку <code>.vscode</code> с двумя файлами настроек. Программа короткая: структура из двух чисел, массив под слово, цикл и функция. Всё это разбирается в главе 1.1; здесь программа нужна, чтобы было что рассматривать.</p>

        <figure class="code"><figcaption><span>labs/02-debugger/debug.c</span></figcaption><pre>{hl(CODE)}</pre></figure>

        <p><code>launch.json</code> описывает, какую программу и каким отладчиком запускать. <code>tasks.json</code> — как собрать программу перед запуском. В имени папки <code>.vscode</code> точка в начале обязательна.</p>

        {files('win')}
        {files('mac')}
        {files('linux')}

        <p data-os="win">Компилятор <code>cl</code> находится, только если VS Code запущен из <b>x64 Native Tools Command Prompt</b>: перейдите в папку работы и выполните <code>code .</code>. Из меню «Пуск» VS Code не знает, где лежит компилятор, и задача <code>build</code> завершится ошибкой «cl не является внутренней или внешней командой».</p>

        <div class="margin-note">
          <b>Как читать шаг</b>
          <p>Вверху шага — действие. Ниже — кадр экрана после действия; красные рамки отмечают места, о которых идёт речь, номера рамок повторяются в тексте. Слева под кадром — что на нём видно, справа — что изменилось по сравнению с прошлым шагом. Строка «В отчёт» — что записать в <code>report.md</code>. Случайные числа в переменных у вас будут другими.</p>
        </div>

        <h2 id="s2"><span class="sec">§2</span>Словарь отладчика</h2>

        <p>Отладчик — программа, которая запускает другую программу и управляет ею: останавливает, выполняет по одной строке и читает её память. Сама программа об этом не знает. Ниже — слова, которые встретятся в шагах. Справа — сравнение: программа как здание с коридором и кабинетами-функциями.</p>

        <div class="table-scroll">
          <table>
            <thead><tr><th>Слово</th><th>Что делает</th><th>Сравнение</th></tr></thead>
            <tbody>
{WORDS_HTML}
            </tbody>
          </table>
        </div>

        <h2 id="s3"><span class="sec">§3</span>Часть 1. Запуск и остановка</h2>

        <p>В первой части программа запускается обычным способом, затем под отладчиком: останавливается на строке 15 и проходится по строкам до цикла.</p>

{LAB}

        <h2 id="s5"><span class="sec">§5</span>Что получилось</h2>

        <p>Программа под отладчиком выполнила те же команды, что и без него, и напечатала ту же строку. Разница в том, что между строками её можно было остановить и посмотреть память.</p>

        <div class="table-scroll">
          <table>
            <thead><tr><th>Что увидели</th><th>Где в отладчике</th><th>Зачем это системному программисту</th></tr></thead>
            <tbody>
              <tr><td>Случайные значения до присваивания</td><td>Variables, шаг 4</td><td>Переменная без значения содержит старые байты. Ядро агента в главе 1.1 поэтому обнуляет структуру перед заполнением.</td></tr>
              <tr><td>Строка — байты с нулём в конце</td><td>Variables, массив <code>name</code>, шаг 6</td><td>Так же лежит имя компьютера в буфере ядра агента, глава 1.1, шаг 3.</td></tr>
              <tr><td>Значение меняется по шагам</td><td>Watch, шаг 7</td><td>Ошибку в цикле видно по тому, на каком проходе число стало не тем.</td></tr>
              <tr><td>Кто кого вызвал</td><td>Call Stack, шаг 8</td><td>При падении программы стек показывает функцию и строку, где это случилось.</td></tr>
              <tr><td>Строка C — несколько команд процессора</td><td>Disassembly, шаг 9</td><td>Так читают программы без исходного кода, ЛР 22.</td></tr>
            </tbody>
          </table>
        </div>

        <h2 id="s6"><span class="sec">§6</span>Отчёт</h2>

        <p>Создайте в <code>labs/02-debugger</code> файл <code>report.md</code> по образцу ниже и замените каждый пропуск <code>___</code> данными со своего экрана. Рядом должны лежать <code>debug.c</code> и папка <code>.vscode</code>. Собранную программу (<code>debug</code>, <code>debug.exe</code>, <code>debug.dSYM</code>, <code>.pdb</code>, <code>.obj</code>) в репозиторий не кладите. Коммит — <code>labs 02: отладчик, отчёт</code>.</p>

        <pre class="report"># ЛР 2. Программа в отладчике

Система: <span class="blank">___</span> · отладчик: <span class="blank">___</span> (LLDB, GDB или Visual Studio)

## Остановка и переменные
Программа без отладчика напечатала: <span class="blank">___</span>
Точка останова на строке <span class="blank">___</span>.
До строки 15: p.x = <span class="blank">___</span>, p.y = <span class="blank">___</span>, total = <span class="blank">___</span>.
После строки 15: p.x = <span class="blank">___</span>, p.y = <span class="blank">___</span>.
Строку 16 отладчик пропустил, потому что <span class="blank">___</span>.
name[0] = <span class="blank">___</span> (код буквы), завершающий ноль в ячейке <span class="blank">___</span>.

## Цикл и функция
На кадре цикла: i = <span class="blank">___</span>, total = <span class="blank">___</span>; после следующего шага total = <span class="blank">___</span>.
В стеке внутри area строк: <span class="blank">___</span>, сверху функция <span class="blank">___</span>.
Команда умножения в машинном коде: <span class="blank">___</span>.
Перед printf: a = <span class="blank">___</span>, total = <span class="blank">___</span>.
Код завершения программы: <span class="blank">___</span>.

## Помощник ИИ (Р1)
Запрос: «Почему до выполнения строки 15 в p.x лежит случайное число?». Совпал ли ответ с шагом 4: <span class="blank">___</span>.

Не получилось: <span class="blank">___</span>
ИИ: не использовал / использовал для <span class="blank">___</span></pre>

        <p>На защите программа запускается под отладчиком, и те же значения показываются на экране. Случайные числа шага 4 при каждом запуске могут быть другими — это ожидаемо.</p>

        <h2 id="s7"><span class="sec">§7</span>Проверьте себя</h2>

        <details>
          <summary>Почему до выполнения строки 15 в p.x уже есть число?</summary>
          <p>Место под переменные функции выделяется сразу при входе в неё. Строка 15 только записывает в это место 3 и 4. До неё там лежат байты, которые остались от прошлой работы программы, — их отладчик и показывает.</p>
        </details>
        <details>
          <summary>Чем шаг с обходом отличается от шага с заходом?</summary>
          <p>На строке с вызовом функции шаг с обходом (<kbd>F10</kbd>) выполняет функцию целиком и встаёт на следующую строку. Шаг с заходом (<kbd>F11</kbd>) входит в функцию и встаёт на её первую строку. На строке без вызова они делают одно и то же.</p>
        </details>
        <details>
          <summary>Почему в area переменная p — копия, а не та же структура из main?</summary>
          <p>В C аргументы передаются по значению: функция получает копию. Чтобы функция могла менять структуру вызывающей программы, ей передают адрес — так устроена <code>core_get_info</code> в главе 1.1.</p>
        </details>
        <details>
          <summary>Зачем ключ -O0 или /Od при сборке для отладки?</summary>
          <p>С оптимизацией компилятор переставляет и выбрасывает команды, хранит переменные только в регистрах. Тогда отладчик прыгает между строками в неожиданном порядке и показывает «optimized out» вместо значений. Без оптимизации каждая строка — свои команды, в том же порядке.</p>
        </details>

        <div class="pager">
          <a href="../05-laboratornaya-1/index.html">← ЛР 1 Процесс изнутри</a>
          <a href="../../index.html">Оглавление</a>
          <a href="../06-c-dlya-sistemnogo-programmista/index.html">1.1 C для системного программиста →</a>
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
# Части 1 и 2: шаги 1–7 и 8–11; заголовок второй части вставляется перед шагом 8.
marker = '        <li>\n<div class="lab__do"><b>Зайдите в функцию area'
part2 = ('        </ol>\n\n        <h2 id="s4"><span class="sec">§4</span>Часть 2. Функция и машинный код</h2>\n\n'
         '        <p>Во второй части отладчик заходит в функцию <code>area</code>, показывает стек вызовов и машинные команды одной строки, затем доводит программу до конца.</p>\n\n'
         '        <ol class="lab" start="8" style="counter-reset: lab 7">\n')
assert marker in HTML, 'нет шага 8'
HTML = HTML.replace(marker, part2 + marker, 1)
OUT.write_text(HTML)
print('ok', OUT)
