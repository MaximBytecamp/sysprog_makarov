"""Картинки страницы задания модуля 1 (temy/11-zadanie-modulya-1/index.html, страница написана вручную).

Каждая картинка стоит между метками <!-- pic:имя --> и <!-- /pic:имя -->; при запуске содержимое между ними заменяется.
Если меток ещё нет, картинка вставляется после строки-якоря и метки ставятся. Числа — с эталонного запуска в задании."""
from pathlib import Path
import re
import viz as V
from ch11 import cells

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / 'temy/11-zadanie-modulya-1/index.html'

STRUCT = V.scheme('Структура ядра: было 272 байта, стало 280',
    V.mem([('смещение', '', cells([('0–7', '', 'w'), ('8–11', '', 'w'), ('12–15', '', 'w'), ('16–271', '', 'w'), ('272–279', '', 'w')])),
           ('глава 1.1', '272 байта', cells([('pid', '', 'w'), ('cpus', '', 'w'), ('page_size', '', 'w'), ('host[256]', '', 'w'), ('—', '', 'gap w')])),
           ('задание', '280 байт', cells([('pid', '', 'w'), ('cpus', '', 'w'), ('page_size', '', 'w'), ('host[256]', '', 'w'), ('uptime_s', 'int64_t', 'z w')]))])
    + V.steps(V.card('система', '<span data-os="win">GetTickCount64()</span><span data-os="mac">kern.boottime</span><span data-os="linux">sysinfo()</span>', '<small>время с запуска</small>', 'sys'), V.arrow('секунды'),
              V.card('core_info.c', 'out-&gt;uptime_s', '<small>байты 272–279</small>', 'c'), V.arrow('_fields_'),
              V.card('brain.py', '"uptime_s": 420834', '<small>в JSON агента</small>', 'py')),
    'Новое поле стоит последним, поэтому pid, cpus, page_size и host остаются на прежних байтах. 272 делится на 8, и 8-байтовое поле встаёт сразу за host без пропуска — отсюда ровно 280.')

AB = V.scheme('Кто считает дни и часы',
    V.split(('Запрос А · модель считает сама',
             V.steps(V.card('JSON', 'uptime_s = 420911', '', 'sys'), V.arrow('модель'),
                     V.card('ответ', '«12 дней и 10 часов»', '<small>в трёх запусках три разных ответа</small>', 'bad'))),
            ('Запрос Б · считает выражение n8n',
             V.steps(V.card('JSON', 'uptime_s = 420911', '', 'sys'), V.arrow('Math.floor'),
                     V.card('n8n', '4 дн. 20 ч.', '<small>точно, каждый раз</small>', 'ok'), V.arrow('модель'),
                     V.card('ответ', '«…работает без перезагрузки 4 дня 20 часов»', '<small>модель только пишет текст</small>', 'ok'))), rows=True),
    'Модель подбирает правдоподобные слова, а не делит числа. Деление делает код — выражение n8n или агент, — а модели остаётся объяснить готовый результат человеку.')

PICS = [('struct', STRUCT, '        </ol>\n\n        <div class="table-scroll">\n          <table>\n            <thead><tr><th>Система</th><th>Функция</th>'),
        ('ab', AB, '        <p>У нас с готовыми числами')]


def put(html, name, pic, anchor):
    block = f'<!-- pic:{name} -->\n{pic}\n        <!-- /pic:{name} -->'
    pat = re.compile(rf'<!-- pic:{name} -->.*?<!-- /pic:{name} -->', re.S)
    if pat.search(html):
        return pat.sub(lambda _: block, html)
    assert html.count(anchor) == 1, f'якорь {name}'
    if name == 'struct':  # после списка шагов, перед таблицей функций
        return html.replace(anchor, anchor.replace('</ol>\n\n', f'</ol>\n\n        {block}\n\n', 1))
    return html.replace(anchor, f'        {block}\n\n{anchor}')


html = PAGE.read_text()
for name, pic, anchor in PICS:
    html = put(html, name, pic, anchor)
PAGE.write_text(html)
print('ok', PAGE)
