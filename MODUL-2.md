# Модуль 2. Процессы, потоки и память — план

Пары 4–9. Каждая пара: лабораторная в программах системы → глава с ядром агента по шагам → (на 4, 6, 8) новая проверка агента.
Оформление как в модуле 1: шаги «действие → код по системам → кадр с рамками → разбор», пошаговые разборы `.trace`
для каждой программы, картинки данных (`tools/viz.py`), снимки в отчёт ЛР (`tools/snaps.py`), в конце модуля — 2.0 «Как пройти модуль 2»,
задание модуля и тест.

| Пара | Лабораторная | Глава | Ядро агента | Проверка |
|---|---|---|---|---|
| 4 | ЛР 4 «Дерево процессов» | 2.1 Список процессов | `struct core_proc` (pid, ppid, name — 80 байт), `core_list_procs(out, max, &count)`: Toolhelp32 / `proc_listallpids` + `proc_pidinfo` / чтение `/proc/PID/stat`; мозг: повтор при нехватке места, цепочка родителей | 1. Список процессов совпадает с системным |
| 5 | ЛР 5 «Рождение процесса» | 2.2 Запуск процесса | `CreateProcessW` / `posix_spawn`, ожидание и код завершения; кто родитель у запущенного | — |
| 6 | ЛР 6 «Кто загружает процессор» | 2.3 Процессорное время | `GetProcessTimes` / `proc_pidinfo(PROC_PIDTASKINFO)` / `/proc/PID/stat` utime+stime; загрузка = разница за интервал | 2. Процесс загружает процессор больше 80% |
| 7 | ЛР 7 «Потоки Python и GIL» | 2.4 Потоки | `CreateThread` / `pthread_create`, потоки Python 3.14 с GIL и без | — |
| 8 | ЛР 8 «Карта памяти» | 2.5 Память процесса | рабочий набор: `GetProcessMemoryInfo` / `PROC_PIDTASKINFO` / `/proc/PID/status` VmRSS; рост за несколько замеров | 3. Память процесса растёт без остановки |
| 9 | ЛР 9 «Разбор падения» | 2.6 Ошибки памяти | AddressSanitizer, отчёт о сбое, ядро без утечек | тест модуля 2 |

## Пара 4 (в работе)

Код главы 2.1 — `tools/src21`: `core.h` (с `uptime_s` из задания модуля 1 и `struct core_proc`), `win|mac|linux/core_procs.c`,
`list_procs.c`, `py/brain.py`. Проверено: macOS 26 (566 процессов, как `ps -A`), Linux в `gcc:14` (5 против 6 у `ps` — сам ps),
Windows — windows-latest в закрытом `sysprog-win-shots` (workflow `m2.yml`).
Имена в macOS и Linux обрезаны до 15 символов (MAXCOMLEN / TASK_COMM_LEN), в Windows — полное имя файла.
Нехватка места: ERANGE (34) в macOS и Linux, ERROR_INSUFFICIENT_BUFFER (122) в Windows; `count` получает нужное число.
Глава 2.1 готова (06.11.2026): `temy/14-spisok-processov`, генератор `tools/ch21.py`, разборы `tools/walk21.py`, ссылка в index.html.
Кадр Windows `05-brain` снят экраном ВМ (сеть ВМ не работает, CDP недоступен), рамки — `tools/src21/winmark21.py`; в ВМ нет
x64 Python (C:\Py314x64 пропал), кадр — Python ARM64 + ядро, собранное `vcvarsamd64_arm64.bat`.
В открытый репозиторий не класть `tools/src21/*/core_info.c` (решение задания 1) и собранные библиотеки — они в .gitignore.
Следующее: ЛР 4 «Дерево процессов» → `temy/13-laboratornaya-4`, `tools/lab4.py` по образцу lab3.py, SNAPS в snaps.py.
ЛР 4 готова (06.11.2026): `temy/13-laboratornaya-4`, генератор `tools/lab4.py`, рамки `tools/src_lab4/mark4.py` + `marks4.json`
(сырые кадры `~/sysprog-shots/raw/lab4`), SNAPS `04-process-tree` в snaps.py, ссылка в index.html. Кадры всех трёх систем сняты:
Linux — ВМ Ubuntu-lab-01, Windows — ВМ Win11-lab (шаг 5 — ветка msedgewebview2 под SearchHost: Edge в сборке нет),
macOS — `tools/src_lab4/mac4.py`. В шаблоне — labs/04-process-tree, LABS в run_checks.py, конспект 2.1. Вычитана 06.11.2026.
Находка: Мониторинг системы в иерархическом виде держит сироту в ветке Терминала, хотя `ps` даёт PPID 1.
Проверка 1 (08.11.2026, в шаблоне не закоммичена): `check_agent1` в `checks/run_checks.py`, OPENED = 1. Ядро собирается из всех
agent/core/*.c без main (`build_core`, общая с «Модуль 1 · agent» — раньше та собирала только core_info.c и ломалась на brain.py 2.1);
система файла — `target_of_core` (windows.h / libproc.h / "/proc" / общий posix). Проверка: max = 1 → 34/122 и count > 1; процесс проверки
в списке с ppid = os.getppid() и именем python; сверка с `ps -A -o pid=,ppid=` / Win32_Process: пропущенных и лишних ≤ max(5, 10%),
ppid совпал у ≥ 95% общих. Прогнано: macOS (642/643), Linux gcc:14 (3/4), Windows — workflow checks1.yml в sysprog-win-shots (141/142);
испорченный ppid ловится, ядро Linux на macOS — «пропущено». Дальше — пара 5 (ЛР 5, глава 2.2).

## Пара 5 (в работе, 08.11.2026)

Код главы 2.2 — `tools/src22`: `core.h` + `struct core_child {pid, handle}`, `core_spawn(argv, &child)` и `core_wait(&child, timeout_ms, &code)`;
`win/core_spawn.c` (argv → командная строка UTF-16, аргумент с пробелом в кавычках, CreateProcessW, hThread закрывается сразу, hProcess — в
handle до core_wait), `posix/core_spawn.c` (posix_spawnp + waitpid WNOHANG шагами по 10 мс; сигнал → 128 + номер), `run_child.c`, `py/brain.py`
(spawn/wait, ребёнок-Python с кодом 3, цепочка родителей ребёнка). Проверено: macOS, Linux gcc:14, Windows (workflow m22.yml в sysprog-win-shots).
Коды: «нет программы» 2 везде; «время вышло» 258 / 60 / 110; kill -9 → 137. Утечки для темы ИИ: Windows — не закрыт hThread/hProcess,
POSIX — нет waitpid → зомби.
ЛР 5 «Рождение процесса»: Process Monitor / fs_usage (sudo; на Mac автора правило /etc/sudoers.d/fs_usage только для /usr/bin/fs_usage — снять после съёмки) / strace.
ЛР 5, план из 5 шагов (одинаков на трёх системах, программа — `hostname`: ping под strace теряет cap_net_raw и выходит с кодом 2):
1 рождение (bash → clone → execve → exit_group → wait4), 2 библиотеки (openat: ld.so.cache, libc.so.6), 3 код 7 (`sh -c "exit 7"`),
4 нет программы (`env nosuch`: execve по 10 папкам PATH, ENOENT, код 127), 5 Python subprocess (clone CLONE_VM|CLONE_VFORK, execve по PATH, wait4).
Кадры Linux сняты 08.11 (`~/sysprog-shots/l5linux.txt` → raw/lab5/linux/01-birth…05-python; bash 3861 → hostname 3862; sh 3873 код 7; python 3883 → 3884).
Windows: Process Monitor на ISO `~/sysprog-shots/win/procmon.iso` (Procmon64a.exe) — подключить к Win11-lab как DVD.
Кадры Windows ЛР 5 сняты 08.11 (ВМ Win11-lab, Process Monitor 64a в C:\Users\user\ProcessMonitor, raw/lab5/win): 00-filter (Process Name is
HOSTNAME.EXE / cmd.exe / python.exe + Event Class is Process), 01-birth (cmd 1988 Process Create → HOSTNAME 804, Process Start Parent PID 1988),
01b-start (свойства Process Start: Parent PID, Command line, Current directory, Environment), 02-libs (18 Load Image, Process Exit 0),
03-exit (cmd 1988 → cmd 7940, Exit Status 7), 04-path (`nosuch`: 11 QueryDirectory NO SUCH FILE, без Process Create; код cmd 9009 — 04-cmd),
05-python (python 8364 Process Create → hostname 1492). После сна Mac на кадрах появилась надпись «Активация Windows» (с 04-path) — важные строки выше неё.
Фильтр Procmon с клавиатуры: Ctrl+L, Tab Tab → столбец (набрать «Proc»), Tab Tab → значение, Alt+A; отношение — набрать первую букву после Shift+Tab.
ЛР 5 (09.11): страница `temy/15-laboratornaya-5` (генератор `tools/lab5.py`, рамки `tools/src_lab5/mark5.py` + `marks5.json`), шаг 1 Windows —
три кадра (lab_build.shot принимает список). Тексты macOS — «Заполняется после съёмки кадра», кадры macOS — места `todo:`.
Шаблон (не закоммичен): labs/05-process-birth (README, report.md, 5 заглушек), строка в labs/README.md, LABS в run_checks.py, SNAPS в snaps.py.
Осталось: кадры macOS (fs_usage, ждёт правила sudoers от пользователя), ссылка в index.html, глава 2.2 (`temy/16-zapusk-processa`), вычитка, коммиты.
ЛР 5 опубликована 09.11 (книга 04aec18, шаблон b80351f): кадры macOS — `tools/src_lab5/shoot_mac5.py` (два окна Терминала,
в нижнем bash: fs_usage по умолчанию скрывает Terminal, sh, zsh даже с -e; шум исключается `-e "Code Helper (Plugin)" "Docker Desktop" …` —
по имени, число после точки в выводе — номер потока; без -w имя процесса без точки; fs_usage из sudo останавливать kill -TERM на pid sudo,
INT не доходит; вывод в файл/канал буферизуется). Дальше — глава 2.2 `temy/16-zapusk-processa`, код `tools/src22`.
Глава 2.2 — кадры сняты 09.11 (`~/sysprog-shots/m22`: shoot22.py mac|linux через CDP, рамки mark.py + marks.json; Windows — экран ВМ 800×600,
файлы и start22.cmd на ISO `~/sysprog-shots/win/m22.iso`, ядро ARM64 через vcvarsamd64_arm64, рамки winmark22.py; EfiGraphicsResolution не помог).
Числа: 02-run — mac pid 88026, linux 308, win 8952, код 7; 03-errors — 60 (pid 88235) / 110 (348) / 258 (4664, cmd /c "ping -n 3 127.0.0.1 >nul"), нет программы — 2;
04-brain — child 88861 / 484 / 4448, child_code 3, procs 695 / 19 / 139; parents mac: python3.9, Python, zsh, Code Helper, Code, launchd, kernel_task;
linux: python3, python3, bash, code, code, sleep; win: python.exe ×2, cmd.exe, Code.exe ×2, cmd.exe, explorer.exe.
05-leak (leak.c, 20 core_spawn без core_wait): зомби 0 → 20 (mac, linux); Windows дескрипторы 44 → 72, без CloseHandle(pi.hThread) — 44 → 92.
Разборы — tools/walk22.py. Дальше: ch22.py → temy/16-zapusk-processa.
