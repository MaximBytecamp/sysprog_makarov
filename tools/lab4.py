"""Лабораторная работа 4 «Дерево процессов» → temy/13-laboratornaya-4/index.html.

Кадры: Linux — ВМ Ubuntu-lab-01 (Ubuntu 24.04.4 Live, GNOME System Monitor 46.0, Firefox), Windows — ВМ Win11-lab
(Windows 11 24H2 ARM64, Process Explorer procexp64a.exe, PowerShell 5.1; Edge в сборке нет — в шаге 5 ветка msedgewebview2 под SearchHost),
macOS — Мониторинг системы и Терминал рядом, tools/src_lab4/mac4.py (macOS 26.1; окно Мониторинга выводится вперёд, в фоне оно не перерисовывается).
Сырые кадры — ~/sysprog-shots/raw/lab4, рамки — tools/src_lab4/mark4.py. Числа в тексте — с кадров;
цепочка Terminal → login → -zsh и переход сироты к launchd (PID 1) проверены на macOS 26.1 командой ps."""
from pathlib import Path
from lab_build import steps
import snaps
import viz as V

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'temy/13-laboratornaya-4/index.html'


def mk(n):
    return f'<span class="mk">{n}</span>'



def chain(*items):
    out = []
    for k, (name, pid, note, kind) in enumerate(items):
        if k:
            out.append(V.arrow('запустил'))
        out.append(V.card(f'PID {pid}', f'<code>{name}</code>', f'<small>{note}</small>' if note else '', kind))
    return V.steps(*out)


PIC_TREE = V.scheme('Ветка дерева от системы до команды',
    '<div data-os="win">' + chain(('explorer.exe', 4684, 'Проводник', 'sys'), ('cmd.exe', 7912, 'командная строка', 'c'), ('PING.EXE', 1308, 'PPID 7912', 'py')) + '</div>'
    + '<div data-os="mac">' + chain(('launchd', 1, 'первый процесс', 'sys'), ('Терминал', 38262, '', 'c'), ('login', 38302, '', 'c'), ('zsh', 38305, 'оболочка', 'c'), ('sleep', 46701, 'PPID 38305', 'py')) + '</div>'
    + '<div data-os="linux">' + chain(('systemd', 1, 'первый процесс', 'sys'), ('systemd', 1696, 'сеанс', 'sys'), ('gnome-terminal-server', 3530, '', 'c'), ('bash', 3843, 'оболочка', 'c'), ('sleep', 7567, 'PPID 3843', 'py')) + '</div>',
    'Стрелка — «запустил». В записи каждого процесса хранится только номер родителя: у последнего процесса он подписан внизу. Бирюзовая карточка — процесс, запущенный вами.')


def orphan(parent, child, after, kind):
    return V.steps(V.card('родитель', f'<code>{parent}</code>', '<small>запустил и завершился</small>', 'bad'), V.arrow('PPID был'),
                   V.card('сирота', f'<code>{child}</code>', '', 'py'), V.arrow('PPID стал'),
                   V.card('новый родитель', after, '', kind))


PIC_ORPHAN = V.scheme('Что стало с сиротой',
    '<div data-os="win">' + orphan('cmd /c, PID 1392', 'PING.EXE 4056', '1392 — процесса нет', 'bad') + '</div>'
    + '<div data-os="mac">' + orphan('bash -c', 'sleep 49759', '<code>launchd</code>, PID 1', 'sys') + '</div>'
    + '<div data-os="linux">' + orphan('bash -c', 'sleep 11922', '<code>systemd</code> сеанса, PID 1696', 'sys') + '</div>',
    '<span data-os="win">Windows номер родителя не меняет: в записи остаётся 1392, хотя такого процесса уже нет.</span><span data-os="mac">macOS отдаёт сироту процессу 1. В дереве Мониторинга он остаётся в ветке Терминала.</span><span data-os="linux">Linux отдаёт сироту ближайшему предку, который объявил себя приёмным родителем, — <code>systemd</code> сеанса.</span>')

S = []

S.append(dict(
    do={'win': ('Откройте дерево процессов', 'Запустите Process Explorer (<code>procexp64.exe</code>, на компьютере с ARM — <code>procexp64a.exe</code>) и разверните окно. Дерево включено сразу: дочерние процессы стоят под родителем со сдвигом вправо. Если список плоский, включите <b>View → Show Process Tree</b> (<kbd>Ctrl</kbd>+<kbd>T</kbd>). Прокрутите список в самое начало.'),
        'mac': ('Откройте дерево процессов', 'Запустите Мониторинг системы и выберите в меню <b>Вид → Все процессы, иерархически</b>. Дочерние процессы встанут под родителем, у родителя появится стрелка, которая сворачивает ветку. Прокрутите список в самое начало.'),
        'linux': ('Откройте дерево процессов', 'Запустите Системный монитор. В меню <b>☰</b> (или <kbd>F10</kbd>) выберите <b>All Processes</b>, затем <b>Show Dependencies</b> (<kbd>Ctrl</kbd>+<kbd>D</kbd>). Разверните окно и прокрутите список в начало.')},
    shot={'win': '01-tree.png', 'linux': '02-tree.png',
          'mac': '01-tree.png'},
    notes={'win': (f'<p>{mk(1)} — <code>System Idle Process</code> с номером 0: так Windows показывает время, когда процессор свободен. {mk(2)} — <code>System</code> с номером 4, потоки ядра Windows. {mk(3)} — <code>wininit.exe</code> и под ним <code>services.exe</code>, который запускает службы <code>svchost.exe</code>.</p>',
                   '<p>В Диспетчере задач в ЛР 1 процессы шли списком. В дереве видно, кто кого запустил: <code>services.exe</code> — ребёнок <code>wininit.exe</code>, а все <code>svchost.exe</code> ниже — дети <code>services.exe</code>.</p>'),
           'mac': (f'<p>{mk(1)} — <code>kernel_task</code> с номером 0, само ядро macOS. {mk(2)} — <code>launchd</code> с номером 1, первый процесс системы. {mk(3)} — программы и службы, которые запустил <code>launchd</code>: <code>WindowServer</code> (397) рисует окна, <code>logd</code> (324) собирает журнал. Внутри одного уровня список отсортирован по столбцу «% ЦП».</p>',
                   '<p>Почти всё в системе — дети <code>launchd</code>: он запускает и службы, и программы, которые вы открываете из Dock или Launchpad.</p>'),
           'linux': (f'<p>{mk(1)} — <code>kthreadd</code> с номером 2, родитель потоков ядра Linux. {mk(2)} — <code>systemd</code> с номером 1, первый процесс системы; под ним службы. {mk(3)} — ещё один <code>systemd</code>, номер 1696, пользователь <code>ubuntu</code>: менеджер вашего сеанса.</p>',
                     '<p>В плоском списке ЛР 1 процессы шли по алфавиту. В дереве видно, кто кого запустил: службы — дети <code>systemd</code> с номером 1, а программы сеанса пользователя будут под вторым <code>systemd</code>.</p>')},
    q='имя и номер процесса в начале дерева.'))

S.append(dict(
    do={'win': ('Найдите терминал и его родителей', 'Откройте командную строку через <kbd>Win</kbd>+<kbd>R</kbd> → <code>cmd</code>. Вернитесь в Process Explorer, щёлкните по списку и наберите на клавиатуре <code>cmd.exe</code>: выделение перейдёт к процессу. Прокрутите так, чтобы были видны его родитель и дети.'),
        'mac': ('Найдите терминал и его родителей', 'Откройте Терминал. В Мониторинге системы введите в поле поиска <code>zsh</code>: в иерархическом виде поиск оставляет найденные процессы вместе с их родителями. Если ветка свёрнута, щёлкните по стрелке у первой строки с нажатой <kbd>Option</kbd>.'),
        'linux': ('Найдите терминал и его родителей', 'Откройте терминал (<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd>). В Системном мониторе нажмите <kbd>Ctrl</kbd>+<kbd>F</kbd> и введите <code>bash</code>: в виде дерева поиск оставляет найденные процессы вместе с их родителями.')},
    shot={'win': '02-terminal.png', 'linux': '03-terminal.png',
          'mac': '02-terminal.png'},
    notes={'win': (f'<p>{mk(1)} — <code>explorer.exe</code>, номер 4684, Проводник: он запускает всё, что вы открываете с рабочего стола, из меню «Пуск» и через <kbd>Win</kbd>+<kbd>R</kbd>. {mk(2)} — <code>cmd.exe</code>, номер 7912. {mk(3)} — <code>conhost.exe</code>, номер 2420: окно консоли, в котором рисуется текст командной строки.</p>',
                   '<p>У <code>explorer.exe</code> нет родителя в дереве: он стоит у левого края. Его запустил процесс входа в систему, который сразу завершился. Цепочка терминала короткая: Проводник → командная строка → её окно.</p>'),
           'mac': (f'<p>{mk(1)} — <code>launchd</code>, номер 1. {mk(2)} — <code>Терминал</code>, номер 38262. {mk(3)} — <code>login</code> (38302) и под ним <code>zsh</code> (38305): Терминал запускает для каждого окна программу входа <code>login</code>, а она — оболочку. Выше видны и другие <code>zsh</code>: их запустили программы внутри VS Code.</p>',
                   '<p>Цепочка терминала: <code>launchd</code> → Терминал → <code>login</code> → <code>zsh</code>. В <code>ps</code> эта оболочка называется <code>-zsh</code>: минус означает оболочку входа, которая читает настройки пользователя.</p>'),
           'linux': (f'<p>{mk(1)} — <code>systemd</code> сеанса, номер 1696. {mk(2)} — <code>gnome-terminal-server</code>, номер 3530: одна программа терминала на все окна. {mk(3)} — два <code>bash</code>: по оболочке на каждое открытое окно терминала.</p>',
                     '<p>Цепочка терминала: <code>systemd</code> (1) → <code>systemd</code> сеанса (1696) → <code>gnome-terminal-server</code> → <code>bash</code>. Все окна терминала обслуживает один процесс <code>gnome-terminal-server</code>, а оболочка у каждого окна своя.</p>')},
    q='цепочку родителей терминала от оболочки вверх, с номерами.'))

S.append(dict(
    do={'win': ('Запустите дочерний процесс', 'В командной строке выполните <code>start /b ping -n 600 127.0.0.1 &gt;nul</code>. Команда <code>ping</code> 600 раз проверит связь с этим же компьютером, около 10 минут. <code>start /b</code> запускает её в фоне, и командная строка остаётся свободной. <code>&gt;nul</code> убирает вывод <code>ping</code>. В Process Explorer наберите <code>ping</code>.'),
        'mac': ('Запустите дочерний процесс', 'В Терминале выполните <code>sleep 600 &amp;</code>. Команда <code>sleep</code> ждёт 600 секунд и ничего не делает, знак <code>&amp;</code> запускает её в фоне: оболочка печатает номер задания и номер процесса. В Мониторинге системы найдите <code>sleep</code>.'),
        'linux': ('Запустите дочерний процесс', 'Поставьте окна рядом: терминал справа, Системный монитор слева (<kbd>Super</kbd>+<kbd>→</kbd> и <kbd>Super</kbd>+<kbd>←</kbd>). В терминале выполните <code>sleep 600 &amp;</code>. Команда <code>sleep</code> ждёт 600 секунд, знак <code>&amp;</code> запускает её в фоне. В поиске монитора введите <code>sleep</code> и раскройте ветку клавишей <kbd>*</kbd>.')},
    shot={'win': '03-child.png', 'linux': '04-child.png',
          'mac': '03-child.png'},
    notes={'win': (f'<p>{mk(1)} — <code>cmd.exe</code>, номер 7912. {mk(2)} — <code>PING.EXE</code>, номер 1308, сдвинут под <code>cmd.exe</code>.</p>',
                   '<p>У командной строки появился второй ребёнок, кроме <code>conhost.exe</code>: процесс, который вы запустили своей командой. Его родитель — та командная строка, в которой набрана команда.</p>'),
           'mac': (f'<p>{mk(1)} — оболочка <code>zsh</code>, номер 38305. {mk(2)} — <code>sleep</code>, номер 46701, под ней. {mk(3)} — оболочка напечатала <code>[1] 46701</code>: номер задания и номер процесса.</p>',
                   '<p>Оболочка стала родителем: в дереве появилась новая ветка на уровень ниже <code>zsh</code>.</p>'),
           'linux': (f'<p>{mk(1)} — <code>bash</code>, номер 3843. {mk(2)} — <code>sleep</code>, номер 7567, под ним. {mk(3)} — оболочка напечатала <code>[1] 7567</code>: номер задания и номер процесса.</p>',
                     '<p>Номер в терминале и в мониторе совпал. Оболочка стала родителем: под <code>bash</code> появилась новая ветка.</p>')},
    q='номер запущенного процесса и номер его родителя по дереву.'))

S.append(dict(
    do={'win': ('Узнайте родителя командой', 'В командной строке выполните<br><code>powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \\"Name=\'PING.EXE\'\\" | Format-Table ProcessId,ParentProcessId,Name"</code><br><code>Get-CimInstance Win32_Process</code> возвращает записи процессов, <code>-Filter</code> оставляет те, чьё имя <code>PING.EXE</code>, <code>Format-Table</code> печатает три поля таблицей.'),
        'mac': ('Узнайте родителя командой', 'Выполните <code>ps -o pid,ppid,comm -p $!</code>. <code>$!</code> — номер последнего процесса, запущенного в фоне, <code>-o pid,ppid,comm</code> выбирает столбцы: номер, номер родителя, имя. Затем выполните <code>echo $$</code>: <code>$$</code> — номер самой оболочки.'),
        'linux': ('Узнайте родителя командой', 'В терминале выполните <code>echo $$</code>, <code>ps -o pid,ppid,comm -p 7567</code> (ваш номер <code>sleep</code>) и <code>pstree -l -s -p 7567</code>. <code>$$</code> — номер самой оболочки. <code>-o pid,ppid,comm</code> выбирает столбцы: номер, номер родителя, имя. <code>pstree -s</code> печатает всех предков процесса, <code>-p</code> — с номерами, <code>-l</code> не обрезает длинную строку.')},
    shot={'win': '04-ps.png', 'linux': '05-ps.png',
          'mac': '04-ps.png'},
    notes={'win': (f'<p>{mk(1)} — строка таблицы: <code>ProcessId</code> 1308, <code>ParentProcessId</code> 7912, <code>PING.EXE</code>.</p>',
                   '<p>Номер родителя из команды совпал с номером <code>cmd.exe</code> в дереве шага 3. Process Explorer строит дерево по тому же полю: у каждого процесса записан номер родителя.</p>'),
           'mac': (f'<p>{mk(1)} — у <code>sleep</code> 46701 в столбце PPID стоит 38305. {mk(2)} — этот же номер напечатал <code>echo $$</code>: это сама оболочка.</p>',
                   '<p>Номер родителя из <code>ps</code> совпал с оболочкой, под которой <code>sleep</code> стоит в дереве шага 3.</p>'),
           'linux': (f'<p>{mk(1)} — <code>ps</code>: у <code>sleep</code> 7567 PPID 3843, а первая строка, <code>echo $$</code>, — тоже 3843. {mk(2)} — <code>pstree</code>: <code>systemd(1)</code> → <code>systemd(1696)</code> → <code>gnome-terminal-(3530)</code> → <code>bash(3843)</code> → <code>sleep(7567)</code>. {mk(3)} — та же ветка в мониторе.</p>',
                     '<p>Команда, <code>pstree</code> и монитор показали одну цепочку. Монитор строит дерево по полю PPID: у каждого процесса записан номер родителя, а список детей не хранится.</p>')},
    q='вывод команды: номер процесса и номер родителя; совпал ли родитель с деревом.'))

S.append(dict(
    do={'win': ('Посмотрите процессы браузера', 'Откройте браузер, которым пользуетесь, например Microsoft Edge, и две-три вкладки. В Process Explorer наберите имя его процесса, например <code>msedge.exe</code>, и раскройте ветку.'),
        'mac': ('Посмотрите процессы браузера', 'Откройте браузер, которым пользуетесь, и две-три вкладки. В поле поиска Мониторинга введите его название и посмотрите, что стоит под главным процессом.'),
        'linux': ('Посмотрите процессы браузера', 'Запустите Firefox через <kbd>Alt</kbd>+<kbd>F2</kbd> → <code>firefox</code> или с панели и поставьте его справа. В поиске монитора введите <code>firefox</code> и раскройте ветку клавишей <kbd>*</kbd>.')},
    shot={'linux': '06-browser.png', 'win': '05-browser.png',
          'mac': '05-browser.png'},
    notes={'win': (f'<p>В Windows на кадрах книги браузера нет, и на кадре — его движок: <code>msedgewebview2.exe</code>, Microsoft Edge WebView2. Это тот же движок, что у Edge; через него панель поиска Windows показывает веб-страницы. {mk(1)} — <code>SearchHost.exe</code>, номер 5164, панель поиска. {mk(2)} — главный процесс движка, 5772. {mk(3)} — пять дочерних процессов с тем же именем. У браузера Edge под <code>explorer.exe</code> ветка устроена так же.</p>',
                   '<p>Браузер — дерево процессов: главный процесс запускает отдельный процесс на группу вкладок и на служебные задачи. Описание и командная строка процесса (двойной щелчок, вкладка Image) показывают, чем занят каждый.</p>'),
           'mac': (f'<p>{mk(1)} — <code>Yandex</code>, номер 1057, главный процесс браузера под <code>launchd</code>. {mk(2)} — его дети: <code>Yandex Helper (Renderer)</code> — процессы страниц, <code>Yandex Helper</code> — служебные процессы. На кадре их больше двадцати, и список продолжается ниже.</p>',
                   '<p>Браузер — дерево процессов: падение одной вкладки завершает её процесс, а остальные продолжают работать.</p>'),
           'linux': (f'<p>{mk(1)} — <code>gnome-shell</code>, номер 2021: оболочка рабочего стола запустила браузер по <kbd>Alt</kbd>+<kbd>F2</kbd>. {mk(2)} — <code>firefox</code>, номер 8464. {mk(3)} — три процесса <code>Web Content</code>: в них работают страницы вкладок.</p>',
                     '<p>Firefox — дерево процессов. Вкладки <code>Web Content</code> стоят под служебным процессом <code>forkserver</code>: через него Firefox их запускает. Падение одной вкладки завершает только её процесс.</p>')},
    q='сколько дочерних процессов у браузера и как называется процесс вкладок.'))

S.append(dict(
    do={'win': ('Оставьте процесс без родителя', 'Выполните <code>cmd /c "start /b ping -n 900 127.0.0.1 &gt;nul"</code>. Вторая командная строка <code>cmd /c</code> запускает <code>ping</code> в фоне и сразу завершается. Повторите команду PowerShell из шага 4. Затем проверьте, есть ли процесс-родитель: <code>tasklist /fi "PID eq номер"</code> с номером из столбца <code>ParentProcessId</code>.'),
        'mac': ('Оставьте процесс без родителя', 'Выполните <code>bash -c \'sleep 900 &amp; echo child $!\'</code>. Вторая оболочка <code>bash -c</code> запускает <code>sleep</code> в фоне, печатает его номер и сразу завершается. Затем выполните <code>ps -o pid,ppid,comm -p номер</code> с напечатанным номером.'),
        'linux': ('Оставьте процесс без родителя', 'Выполните <code>bash -c \'sleep 900 &amp; echo child $!\'</code>. Вторая оболочка <code>bash -c</code> запускает <code>sleep</code> в фоне, печатает его номер и сразу завершается. Затем выполните <code>ps -o pid,ppid,comm -C sleep</code>: <code>-C</code> выбирает процессы по имени.')},
    shot={'win': '06-orphan-ps.png', 'linux': '07-orphan-ps.png',
          'mac': '06-orphan-ps.png'},
    notes={'win': (f'<p>{mk(1)} — команда. {mk(2)} — новый <code>PING.EXE</code> 4056 записал родителем номер 1392. {mk(3)} — процесса 1392 нет: <code>tasklist</code> отвечает «Задачи, отвечающие заданным критериям, отсутствуют».</p>',
                   '<p>Родитель завершился, а номер родителя в записи процесса остался. Windows его не меняет. В записи хранится только число, и позже оно может достаться другому процессу.</p>'),
           'mac': (f'<p>{mk(1)} — номер нового <code>sleep</code>, 49759. {mk(2)} — <code>ps</code>: его PPID равен 1, это <code>launchd</code>.</p>',
                   '<p>Оболочка-родитель завершилась, и macOS отдала её ребёнка процессу 1. Такой процесс называют <span class="term">сиротой</span>: его родитель завершился раньше него.</p>'),
           'linux': (f'<p>{mk(1)} — команда. {mk(2)} — номер нового <code>sleep</code>, 11922. {mk(3)} — у него PPID 1696, а у первого <code>sleep</code> 7567 родитель прежний, 3843.</p>',
                     '<p>Оболочка-родитель завершилась, и ядро Linux передало её ребёнка процессу 1696 — <code>systemd</code> сеанса. Такой процесс называют <span class="term">сиротой</span>. Ядро отдаёт сироту ближайшему предку, который объявил себя приёмным родителем (так делает <code>systemd</code> сеанса). Если такого предка нет, сирота достаётся процессу 1.</p>')},
    q='номер сироты и номер его родителя после того, как настоящий родитель завершился.'))

S.append(dict(
    do={'win': ('Найдите сироту в дереве', 'Вернитесь в Process Explorer и прокрутите список в самый конец (<kbd>End</kbd>).'),
        'mac': ('Найдите сироту в дереве', 'В поле поиска Мониторинга введите <code>sleep</code>. Если ветка свернулась, щёлкните по стрелке у первой строки с нажатой клавишей <kbd>Option</kbd>: раскроется всё дерево.'),
        'linux': ('Найдите сироту в дереве', 'В поиске Системного монитора введите <code>sleep</code> и раскройте ветку клавишей <kbd>*</kbd>.')},
    shot={'win': '07-orphan-tree.png', 'linux': '08-orphan-tree.png',
          'mac': '07-orphan-tree.png'},
    notes={'win': (f'<p>{mk(1)} — <code>explorer.exe</code> у левого края. {mk(2)} — первый <code>PING.EXE</code> 1308 на своём месте под <code>cmd.exe</code>. {mk(3)} — сирота <code>PING.EXE</code> 4056 тоже у левого края: его родителя в списке нет.</p>',
                   '<p>Process Explorer ставит к левому краю каждый процесс, чей родитель не найден в списке. Поэтому у края стоят и <code>explorer.exe</code>, и сирота: оба пережили своих родителей.</p>'),
           'mac': (f'<p>{mk(1)} — <code>Терминал</code>, 38262. {mk(2)} — сирота <code>sleep</code> 49759 прямо под Терминалом, хотя <code>ps</code> в шаге 6 показал PPID 1. {mk(3)} — первый <code>sleep</code> 46701 на прежнем месте: <code>login</code> → <code>zsh</code> → <code>sleep</code>.</p>',
                   '<p>Дерево Мониторинга системы в иерархическом виде строится с учётом программы, которая отвечает за процесс. Сирота <code>sleep</code> запущен из Терминала, поэтому остался в его ветке. Что номер родителя сменился на 1, видно только в выводе <code>ps</code>.</p>'),
           'linux': (f'<p>{mk(1)} — <code>systemd</code> сеанса, 1696. {mk(2)} — сирота <code>sleep</code> 11922 прямо под ним. Первый <code>sleep</code> к этому времени завершился: 600 секунд прошли.</p>',
                     '<p>Сирота переехал в дереве: раньше он был бы под <code>bash</code>, теперь он ребёнок <code>systemd</code> сеанса.</p>')},
    q='где стоит сирота в дереве и почему именно там.'))

LAB = steps(S, '04-process-tree')

HTML = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>Лабораторная работа 4. Дерево процессов · Справочник по системному программированию</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,600;0,7..72,700;1,7..72,400&family=Pixelify+Sans:wght@500;600;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css">
</head>
<body>
  <div class="book">
    <div class="book__body">
      <div class="spine"><span>Модуль 2 · Лабораторная работа 4</span></div>

      <main class="leaf">
        <div class="running">
          <p class="eyebrow"><a href="../../index.html" style="text-decoration:none;color:inherit">Справочник по системному программированию</a> · модуль 2 · лабораторная работа</p>
          <p class="running__folio">ЛР 4</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">ЛР 4</span>
          <h1>Дерево<br>процессов</h1>
          <p class="lead">Каждый процесс кто-то запустил, и система помнит, кто: у процесса записан номер родителя. В работе монитор системы показывает процессы деревом. По нему видно, с какого процесса начинается система, кто родитель терминала и браузера, и что происходит с процессом, когда его родитель завершается. После работы в главе 2.1 ядро агента получит этот же список своим кодом.</p>
        </header>

        <dl class="passport">
          <div><dt>Пара</dt><dd>4, первая половина; перед главой 2.1</dd></div>
          <div><dt>Время</dt><dd>30–35 минут</dd></div>
          <div><dt>Программы</dt><dd><span data-os="win">Process Explorer, командная строка, PowerShell</span><span data-os="mac">Мониторинг системы, Терминал</span><span data-os="linux">Системный монитор GNOME, терминал, pstree</span>, браузер</dd></div>
          <div><dt>Сдать</dt><dd><code>report.md</code> и 7 снимков в <code>screenshots/</code> в папке <code>labs/04-process-tree</code> репозитория <code>sysprog-start</code></dd></div>
        </dl>

        <nav class="contents">
          <b>В этой работе</b>
          <ol>
            <li><a href="#s1">Подготовка</a></li>
            <li><a href="#s2">Родитель и дети</a></li>
            <li><a href="#s3">Ход работы</a></li>
            <li><a href="#s4">Что получилось</a></li>
            <li><a href="#s5">Отчёт</a></li>
            <li><a href="#s6">Проверьте себя</a></li>
          </ol>
        </nav>

        <h2 id="s1"><span class="sec">§1</span>Подготовка</h2>

        <p>Нужен монитор процессов из ЛР 1: <span data-os="win">Process Explorer из набора Sysinternals</span><span data-os="mac">Мониторинг системы из папки Программы → Утилиты</span><span data-os="linux">Системный монитор GNOME</span>. Создайте в репозитории <code>sysprog-start</code> папку <code>labs/04-process-tree</code>: в шаблоне в ней уже лежат бланк <code>report.md</code> и папка <code>screenshots/</code>. Код в этой работе не пишется, все команды набираются в терминале.</p>

        <div class="margin-note">
          <b>Как читать шаг</b>
          <p>Вверху шага — действие. Ниже — кадр экрана после действия; красные рамки отмечают места, о которых идёт речь, номера рамок повторяются в тексте. Слева под кадром — что на нём видно, справа — что изменилось. Строка «В отчёт» — что записать в <code>report.md</code>. Номера процессов у вас будут другими.</p>
        </div>

        <h2 id="s2"><span class="sec">§2</span>Родитель и дети</h2>

        <p>Процесс запускается другим процессом. Оболочка терминала запускает набранную команду. Программы с рабочего стола запускает <span data-os="win">Проводник <code>explorer.exe</code></span><span data-os="mac"><code>launchd</code></span><span data-os="linux">оболочка рабочего стола <code>gnome-shell</code></span>. Тот, кто запустил, — <span class="term">родитель</span>, запущенный — <span class="term">ребёнок</span> (дочерний процесс). В записи каждого процесса ядро хранит номер родителя — <span class="term">PPID</span> (parent process ID). Если нарисовать все процессы и соединить каждого с родителем, получится <span class="term">дерево процессов</span>.</p>

        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>В родословной у каждого человека записаны родители. Если родословную нарисовать, получится дерево с общим предком наверху.</p>
          <p class="miss">У людей двое родителей, у процесса — один. И в записи процесса нет списка детей: детей находят, просматривая записи всех процессов.</p>
        </div></div>

        <p>Наверху дерева стоят процессы, которые создала сама система при загрузке:</p>

        <div class="table-scroll">
          <table>
            <thead><tr><th></th><th>Windows</th><th>macOS</th><th>Linux</th></tr></thead>
            <tbody>
              <tr><td>Начало дерева</td><td><code>System Idle Process</code> (0), <code>System</code> (4)</td><td><code>kernel_task</code> (0), <code>launchd</code> (1)</td><td><code>systemd</code> (1), <code>kthreadd</code> (2)</td></tr>
              <tr><td>Кто запускает программы пользователя</td><td><code>explorer.exe</code></td><td><code>launchd</code></td><td><code>systemd</code> сеанса пользователя, <code>gnome-shell</code></td></tr>
              <tr><td>Терминал</td><td><code>cmd.exe</code> и его окно <code>conhost.exe</code></td><td>Терминал → <code>login</code> → <code>zsh</code></td><td><code>gnome-terminal-server</code> → <code>bash</code></td></tr>
            </tbody>
          </table>
        </div>

        <p>На схеме — одна ветка такого дерева: от процесса системы до команды, запущенной в терминале. Числа взяты с кадров шагов 2–4, у вас они будут другими.</p>
{PIC_TREE}
        <p>Последние два шага работы — про <span class="term">сироту</span>: процесс, чей родитель завершился раньше него. Что с ним делает система, на трёх системах разное, и это видно по дереву.</p>

        <h2 id="s3"><span class="sec">§3</span>Ход работы</h2>

{LAB}

        <h2 id="s4"><span class="sec">§4</span>Что получилось</h2>

        <div class="table-scroll">
          <table>
            <thead><tr><th></th><th>Windows</th><th>macOS</th><th>Linux</th></tr></thead>
            <tbody>
              <tr><td>Дерево в мониторе</td><td>Process Explorer, сразу</td><td>Вид → Все процессы, иерархически</td><td>☰ → Show Dependencies</td></tr>
              <tr><td>Родитель командой</td><td><code>Get-CimInstance Win32_Process</code>, поле <code>ParentProcessId</code></td><td colspan="2"><code>ps -o pid,ppid,comm</code>; в Linux ещё <code>pstree -s -p</code></td></tr>
              <tr><td>Родитель сироты</td><td>прежний номер, процесса с ним нет</td><td><code>launchd</code>, PID 1</td><td><code>systemd</code> сеанса; без него — PID 1</td></tr>
              <tr><td>Сирота в дереве</td><td>у левого края</td><td>в ветке Терминала, хотя PPID = 1</td><td>под <code>systemd</code> сеанса</td></tr>
            </tbody>
          </table>
        </div>

        <p>На схеме — что стало с сиротой в шагах 6–7 на каждой системе.</p>
{PIC_ORPHAN}
        <p>Монитор строит дерево по номеру родителя: детей он находит сам, просматривая весь список. Мониторинг системы в macOS держит процесс ещё и в ветке программы, которая за него отвечает. Поэтому номер родителя в macOS проверяют командой <code>ps</code>. Так же в главе 2.1 мозг агента построит цепочку родителей из списка, который отдаст ядро.</p>

        <h2 id="s5"><span class="sec">§5</span>Отчёт</h2>

        <p>Бланк — в <code>labs/04-process-tree/report.md</code>. Замените каждый пропуск <code>___</code> данными со своего экрана, снимки положите в <code>screenshots/</code>. Коммит — <code>labs 04: дерево процессов, отчёт</code>.</p>

        <pre class="report"># ЛР 4. Дерево процессов

Система: <span class="blank">___</span>

## Дерево
Процесс в начале дерева и его номер: <span class="blank">___</span>
Цепочка родителей терминала (имя и номер): <span class="blank">___</span>
Дочерний процесс: номер <span class="blank">___</span>, родитель <span class="blank">___</span>
Команда, которой проверен родитель: <span class="blank">___</span>
Процессов у браузера и имя процесса вкладок: <span class="blank">___</span>

## Сирота
Номер сироты: <span class="blank">___</span>
Номер родителя до и после завершения настоящего родителя: <span class="blank">___</span>
Где сирота стоит в дереве: <span class="blank">___</span>

Не получилось: <span class="blank">___</span>

{snaps.report_pre('04-process-tree')}</pre>

{snaps.page_block('04-process-tree')}

        <h2 id="s6"><span class="sec">§6</span>Проверьте себя</h2>

        <details>
          <summary>По какому полю монитор строит дерево?</summary>
          <p>У каждого процесса ядро хранит номер родителя — PPID. Монитор читает его у всех процессов и раскладывает их по родителям. Списка детей в записи процесса нет.</p>
        </details>
        <details>
          <summary>Почему родитель командной строки — Проводник, а родитель <code>ping</code> — командная строка?</summary>
          <p>Родитель — процесс, который вызвал функцию запуска. Окно <kbd>Win</kbd>+<kbd>R</kbd> — часть Проводника, поэтому <code>cmd</code> запустил Проводник. <code>ping</code> запустила командная строка, когда выполняла команду.</p>
        </details>
        <details>
          <summary>Почему у <code>explorer.exe</code> в дереве нет родителя?</summary>
          <p>Его запустил процесс входа в систему, который сразу завершился. Process Explorer не находит родителя по номеру и ставит процесс к левому краю.</p>
        </details>
        <details>
          <summary>Что такое сирота и что с ним делают macOS и Linux?</summary>
          <p>Сирота — процесс, родитель которого завершился. macOS отдаёт его процессу 1, <code>launchd</code>. Linux — ближайшему предку, который объявил себя приёмным родителем, например <code>systemd</code> сеанса, а если такого нет — процессу 1.</p>
        </details>
        <details>
          <summary>Почему в Windows по номеру родителя нельзя слепо идти вверх по дереву?</summary>
          <p>Windows оставляет у сироты прежний номер родителя. Процесса с этим номером может уже не быть. Или номер достался позже другому, более новому процессу.</p>
        </details>

        <div class="pager">
          <a href="../11-zadanie-modulya-1/index.html">← Задание модуля 1</a>
          <a href="../../index.html">Оглавление</a>
          <a href="../14-spisok-processov/index.html">2.1 Список процессов →</a>
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
OUT.write_text(HTML)
print('ok', OUT)
