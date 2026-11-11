"""Снимки экрана, которые студент кладёт в отчёт лабораторной.

Один список на работу: (номер шага на странице, имя файла, заголовок, что должно быть видно).
По нему строятся: пометка «Снимок в отчёт» в шаге страницы (lab_build), раздел «Снимки экрана» в бланке
report.md и заглушки screenshots/*.png в шаблоне студента (запуск: python3 tools/snaps.py <шаблон>).
Заглушка помечена в PNG текстом PLACEHOLDER — по нему checks/run_checks.py отличает её от снимка."""
import html
import re
import sys
from pathlib import Path

MARK = 'sysprog-placeholder'

SNAPS = {
    '01-process-inside': [
        (1, '01_program_started', 'Программа на C запущена', 'команда сборки и строка <code>agent v0, pid=…</code> в терминале'),
        (3, '02_process_found', 'Свой процесс в мониторе', 'строка процесса <code>hello</code> с тем же номером, что напечатала программа'),
        (4, '03_process_properties', 'Свойства процесса', 'окно процесса <code>hello</code>: номер, память, процессорное время'),
        (5, '04_process_files', 'Дескрипторы процесса', 'открытые файлы или дескрипторы: папка программы и устройство терминала'),
        (6, '05_process_libraries', 'Библиотеки процесса', 'загруженные библиотеки (в Linux — карта памяти)'),
        (8, '06_killed', 'Процесс завершён из монитора', 'терминал после завершения: сообщение оболочки и код завершения'),
        (9, '07_python_process', 'Программа на Python в мониторе', 'строка <code>agent v0 (python), pid=…</code> и процесс Python с тем же номером'),
        (11, '08_python_exit', 'Обычный выход', 'терминал после Enter: код завершения 0'),
    ],
    '02-debugger': [
        (1, '01_build_run', 'Сборка и запуск без отладчика', 'команда сборки и строка <code>agent: total=6 area=12</code>'),
        (3, '02_breakpoint', 'Точка останова', 'красная точка у строки 15 и она же в списке Breakpoints'),
        (4, '03_paused', 'Остановка перед строкой 15', 'жёлтая стрелка у строки 15, переменные в Variables до присваивания'),
        (6, '04_array_name', 'Массив name по ячейкам', 'раскрытый <code>name</code>: буквы <code>agent</code> и ноль в <code>[5]</code>'),
        (7, '05_watch_loop', 'Цикл в Watch', '<code>i</code> и <code>total</code> в разделе Watch на втором проходе цикла'),
        (8, '06_call_stack', 'Внутри функции area', 'стрелка в <code>area</code>, копия <code>p</code> в Variables, две строки в Call Stack'),
        (9, '07_disassembly', 'Машинный код строки 10', 'вкладка Disassembly с командой умножения'),
        (11, '08_finished', 'Программа доработала', 'вывод программы под отладчиком и код завершения'),
    ],
    '03-libraries': [
        (1, '01_build_run', 'Сборка и запуск', 'команда сборки и строка <code>sqrt(2) = 1.414214</code>'),
        (2, '02_file_libraries', 'Библиотеки файла libs', 'вывод <span data-os="win"><code>dumpbin /dependents</code></span><span data-os="mac"><code>otool -L</code></span><span data-os="linux"><code>ldd</code></span> для своей программы'),
        (3, '03_python_libraries', 'Библиотеки интерпретатора Python', 'тот же вывод для файла Python'),
        (4, '04_python_pid', 'Номер процесса Python', 'запущенный Python и его номер процесса'),
        (5, '05_libraries_before', 'Библиотеки процесса до загрузки', 'число библиотек процесса Python до <code>ctypes.CDLL</code>'),
        (6, '06_library_loaded', 'Библиотека загружена', 'строка <code>ctypes.CDLL</code> и результат вызова функции библиотеки'),
        (7, '07_libraries_after', 'Библиотеки процесса после загрузки', 'новое число библиотек и строка загруженной библиотеки'),
    ],
    '04-process-tree': [
        (1, '01_tree_root', 'Начало дерева процессов', 'дерево процессов в мониторе: первые процессы системы и их номера'),
        (2, '02_terminal_parents', 'Терминал и его родители', 'ветка дерева от процесса терминала вверх до процесса системы'),
        (3, '03_child', 'Дочерний процесс терминала', 'запущенный из терминала процесс под оболочкой терминала'),
        (4, '04_ppid_command', 'Родитель по команде', 'вывод команды с номером процесса и номером его родителя'),
        (5, '05_browser', 'Процессы браузера', 'раскрытая ветка браузера с дочерними процессами'),
        (6, '06_orphan_command', 'Процесс без родителя', 'команда запуска и номер родителя у оставшегося процесса'),
        (7, '07_orphan_tree', 'Сирота в дереве', 'тот же процесс в дереве монитора на новом месте'),
    ],
    '05-process-birth': [
        (1, '01_birth', 'Рождение процесса', 'запись запуска <code>hostname</code>: родитель создаёт процесс, у нового процесса номер родителя'),
        (2, '02_libraries', 'Библиотеки нового процесса', 'библиотеки, которые загрузил <code>hostname</code>, и первая из них'),
        (3, '03_exit_code', 'Код завершения 7', 'завершение ребёнка с кодом 7 и тот же код у родителя'),
        (4, '04_no_program', 'Программы нет', 'поиск <code>nosuch</code> по папкам из PATH и ошибка «не найдено»'),
        (5, '05_python_child', 'Запуск из Python', 'Python создаёт процесс <code>hostname</code>: номер Python и номер ребёнка'),
    ],
    '06-cpu-load': [
        (1, '01_one_load', 'Одна нагрузка', 'процесс Python в мониторе: его процент и общая загрузка'),
        (3, '02_two_loads', 'Две нагрузки', 'два процесса Python и загрузка ядер'),
        (4, '03_one_core', 'Нагрузки на одном ядре', 'две нагрузки на одном ядре и их проценты; в macOS — два числа оборотов цикла'),
        (5, '04_cpu_time', 'Процессорное время', 'два замера процессорного времени с паузой между ними'),
    ],
    '07-python-threads': [
        (1, '01_gil_monitor', 'Четыре потока с GIL', 'процесс Python в мониторе: его процент и число потоков'),
        (2, '02_threads', 'Потоки процесса', 'список потоков процесса: сколько выполняется, сколько ждёт'),
        (3, '03_nogil_monitor', 'Четыре потока без GIL', 'процесс python3.14t в мониторе: его процент'),
        (4, '04_time', 'Время работы', 'вывод threads.py в Python с GIL и без'),
    ],
    '08-memory-map': [
        (2, '01_memory_map', 'Карта памяти', 'карта памяти процесса mem.py на старте и её итог'),
        (3, '02_reserved', 'Получено 300 МБ', 'виртуальная память выросла на 300 МБ, занятая — нет'),
        (4, '03_touched', 'Страницы заняты', 'занятая память (в macOS — физический след) после записи в каждую страницу'),
        (6, '04_leak', 'Утечка', 'пять замеров памяти leak.py'),
    ],
    '09-crash': [
        (1, '01_crash', 'Падение', 'запуск crash null и код завершения'),
        (2, '02_python_crash', 'Падение Python', 'вывод ctypes_crash.py и запись системы о падении'),
        (4, '03_asan', 'Отчёт AddressSanitizer', 'вывод crash heap без проверки и с AddressSanitizer (на Windows с ARM — без проверки)'),
        (6, '04_fixed', 'Исправление', 'разница файлов и вывод исправленной программы'),
    ],
}

HOW = ('<span data-os="win"><kbd>Win</kbd>+<kbd>Shift</kbd>+<kbd>S</kbd> → «Окно», затем сохранить из «Ножниц» как PNG</span>'
       '<span data-os="mac"><kbd>⌘</kbd>+<kbd>⇧</kbd>+<kbd>4</kbd>, затем <kbd>Пробел</kbd> и щелчок по окну — PNG появится на Рабочем столе</span>'
       '<span data-os="linux"><kbd>PrtSc</kbd> → «Окно», PNG сохраняется в папку «Изображения/Снимки экрана»</span>')


def plain(s):
    """HTML подписи → текст Markdown: варианты по системам через «/», код в обратных кавычках."""
    s = re.sub(r'</span><span data-os="[^"]+">', ' / ', s)
    s = re.sub(r'</?span[^>]*>', '', s)
    s = re.sub(r'</?code>', '`', s)
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def step_note(lab, n):
    """Пометка в шаге страницы: какой снимок сделать после этого шага."""
    for step, name, title, what in SNAPS[lab]:
        if step == n:
            return (f'<p class="lab-snap"><b>Снимок в отчёт · {name[:2]}</b> Сохраните окно как <code>screenshots/{name}.png</code>. '
                    f'На снимке должно быть видно: {what}.</p>')
    return ''


def page_block(lab):
    """Раздел страницы лабораторной: что снять и куда положить."""
    rows = '\n'.join(f'              <tr><td class="num-cell">{name[:2]}</td><td>{s}</td><td><code>{name}.png</code></td><td>{what}</td></tr>'
                     for s, name, title, what in SNAPS[lab])
    return f'''        <p>Кроме чисел в отчёт кладутся {len(SNAPS[lab])} снимков экрана. В папке <code>labs/{lab}/screenshots</code> уже лежат заглушки с нужными именами, а в <code>report.md</code> — ссылки на них с подписями. Сделайте снимок окна после шага из таблицы и сохраните его поверх заглушки с тем же именем: подпись и ссылку менять не нужно, на GitHub отчёт сразу покажет ваш снимок. В каждом шаге такой снимок отмечен оранжевой строкой «Снимок в отчёт».</p>
        <p>Как снять окно: {HOW}. Снимок — всё окно программы, без обрезки; имя файла — строго из таблицы.</p>
        <div class="table-scroll">
          <table>
            <thead><tr><th>№</th><th>После шага</th><th>Файл</th><th>Что должно быть видно</th></tr></thead>
            <tbody>
{rows}
            </tbody>
          </table>
        </div>'''


def report_md(lab):
    """Раздел «Снимки экрана» бланка report.md."""
    out = ['## Снимки экрана', '',
           'Сохраните снимок поверх заглушки в папке `screenshots/` с тем же именем — ссылки ниже менять не нужно.', '']
    for i, (s, name, title, what) in enumerate(SNAPS[lab], 1):
        out += [f'### {i}. {title}', f'Шаг {s}. Видно: {plain(what)}.', '', f'![{i}. {title}](screenshots/{name}.png)', '']
    return '\n'.join(out).rstrip() + '\n'


def report_pre(lab):
    """Тот же раздел для образца бланка на странице (pre.report)."""
    lines = ['## Снимки экрана']
    lines += [f'![{i}. {html.escape(t)}](screenshots/{n}.png)' for i, (s, n, t, w) in enumerate(SNAPS[lab], 1)]
    return '\n'.join(lines)


def placeholder(path, num, title, name):
    from PIL import Image, ImageDraw, ImageFont
    from PIL.PngImagePlugin import PngInfo
    W, H = 1280, 720
    im = Image.new('RGB', (W, H), '#F0EEE8')
    d = ImageDraw.Draw(im)
    for x in range(40, W - 40, 28):
        d.line([(x, 40), (x + 14, 40)], fill='#8E93AE', width=4); d.line([(x, H - 40), (x + 14, H - 40)], fill='#8E93AE', width=4)
    for y in range(40, H - 40, 28):
        d.line([(40, y), (40, y + 14)], fill='#8E93AE', width=4); d.line([(W - 40, y), (W - 40, y + 14)], fill='#8E93AE', width=4)
    sup = '/System/Library/Fonts/Supplemental/'
    big = ImageFont.truetype(sup + 'Arial Bold.ttf', 64)
    mid = ImageFont.truetype(sup + 'Arial.ttf', 40)
    small = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 30)
    d.text((W / 2, 230), f'Снимок {num}', font=big, fill='#B8650A', anchor='mm')
    d.text((W / 2, 320), title, font=mid, fill='#161A2E', anchor='mm')
    d.text((W / 2, 440), 'Замените этот файл своим снимком экрана', font=mid, fill='#444A66', anchor='mm')
    d.text((W / 2, 510), f'{name}.png', font=small, fill='#0B7A75', anchor='mm')
    info = PngInfo(); info.add_text('Comment', MARK)
    im.save(path, pnginfo=info, optimize=True)


def apply_template(root):
    """Заглушки и раздел снимков в бланках шаблона; раздел «Помощник ИИ» из бланков убирается."""
    root = Path(root)
    for lab, snaps in SNAPS.items():
        d = root / 'labs' / lab
        (d / 'screenshots').mkdir(exist_ok=True)
        for i, (s, name, title, what) in enumerate(snaps, 1):
            placeholder(d / 'screenshots' / f'{name}.png', f'{i:02d}', title, name)
        rep = d / 'report.md'
        text = rep.read_text(encoding='utf-8')
        text = re.sub(r'## Помощник ИИ.*?\n\n', '', text, flags=re.S)
        text = re.sub(r'\nИИ: не использовал / использовал для ___\n?', '\n', text)
        text = re.sub(r'\n## Снимки экрана\n.*', '\n', text, flags=re.S).rstrip() + '\n\n' + report_md(lab)
        rep.write_text(text, encoding='utf-8')
        print('ok', lab, len(snaps))


if __name__ == '__main__':
    apply_template(sys.argv[1])
