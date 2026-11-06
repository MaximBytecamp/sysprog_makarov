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
