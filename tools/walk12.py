"""Пошаговые разборы главы 1.2: первая версия brain.py (загрузка библиотеки) и окончательная.

Номера строк — по файлам tools/src12/py. Оформление блока — trace_html из walk11."""
from walk11 import like, trace_html
import viz as V


def build(hl_py, cells, V1, BRAIN):
    W = {}
    W['v1'] = trace_html('brain.py · шаг 3', 'win mac linux',
        'загрузить библиотеку ядра в процесс Python и найти в ней функцию <code>core_get_info</code>. Пока функция не вызывается: шаг проверяет, что Python видит библиотеку.',
        [('1-3', 'Подключить модули Python',
          '<p><code>import</code> подключает готовый модуль из стандартной библиотеки Python.</p>'
          '<ul class="words"><li><code>ctypes</code> — загрузка библиотек на C и вызов их функций;</li>'
          '<li><code>sys</code> — сведения о самом Python, здесь нужен <code>sys.platform</code>;</li>'
          '<li><code>from pathlib import Path</code> — из модуля <code>pathlib</code> берётся только <code>Path</code>, работа с путями к файлам.</li></ul>'
          + like('Перед работой из ящика достают нужные инструменты: переходник, линейку и карту.')),
         ('5', 'Найти папку ядра',
          '<p>Выражение читается слева направо:</p>'
          '<ul class="words"><li><code>__file__</code> — путь к самому <code>brain.py</code>;</li>'
          '<li><code>.resolve()</code> — полный путь от корня диска;</li>'
          '<li><code>.parent</code> — папка, где лежит файл: <code>agent/brain</code>; второй <code>.parent</code> — на уровень выше: <code>agent</code>;</li>'
          '<li><code>/ "core"</code> — в <code>Path</code> знак <code>/</code> соединяет части пути: <code>agent/core</code>.</li></ul>'
          '<p>Так скрипт находит библиотеку, из какой бы папки его ни запустили.</p>'
          + like('Адрес «соседний подъезд, второй этаж» работает, откуда бы ни вышел человек из своего подъезда.')),
         ('6', 'Выбрать имя файла библиотеки',
          '<p><code>{"win32": …, "darwin": …}</code> — <span class="term">словарь</span>: пары «ключ: значение». <code>.get(sys.platform, "libsentry_core.so")</code> берёт значение по ключу, а если ключа нет — значение по умолчанию.</p>'
          '<ul class="words"><li>Windows: <code>sys.platform</code> = <code>win32</code> → <code>sentry_core.dll</code>;</li>'
          '<li>macOS: <code>darwin</code> → <code>libsentry_core.dylib</code>;</li>'
          '<li>Linux: <code>linux</code>, такого ключа нет → <code>libsentry_core.so</code>.</li></ul>'
          + like('Таблица на двери: «Windows — кабинет 1, macOS — кабинет 2, остальные — кабинет 3».')),
         ('8', 'Загрузить библиотеку',
          '<p><code>ctypes.CDLL(путь)</code> загружает библиотеку в память процесса Python и возвращает объект <code>core</code>. Через него доступны функции библиотеки. <code>str(…)</code> переводит <code>Path</code> в обычную строку, которую ждёт <code>CDLL</code>.</p>'
          + V.steps(V.card('файл на диске', 'библиотека ядра', '<small>.dll / .dylib / .so в agent/core</small>', 'sys'), V.arrow('CDLL'),
                    V.card('память процесса Python', 'тот же код', '<small>рядом с интерпретатором</small>', 'c'), V.arrow('объект'),
                    V.card('Python', 'core', '<small>через него зовут функции</small>', 'py'))
          + like('Переходник для розетки: вилка C входит в гнездо Python.')),
         ('9-10', 'Проверить, что функция нашлась',
          '<p><code>print(core)</code> печатает объект библиотеки с путём к файлу. <code>core.core_get_info</code> ищет функцию в таблице экспорта библиотеки — той, что показали <span data-os="win"><code>dumpbin /exports</code></span><span data-os="mac linux"><code>nm</code></span> в шаге 2. Если имени там нет, Python сообщит <code>AttributeError</code>.</p>')],
        [('brain.py', 'Python'), ('ctypes.CDLL', 'загрузка'), ('библиотека ядра', '.dll / .dylib / .so'), ('core_get_info', 'найдена по имени')],
        hl_py(V1))

    W['brain'] = trace_html('brain.py', 'win mac linux',
        'получить сведения о компьютере от ядра на C и превратить их в сообщение агента. Python здесь — «мозг»: он вызывает ядро, проверяет ответ и готовит JSON, который в главе 1.3 уйдёт в n8n.',
        [('1', 'Строка описания',
          '<p>Текст в тройных кавычках в начале файла — описание модуля. Python его не выполняет, его показывают редактор и команда <code>help</code>.</p>'),
         ('2-6', 'Модули',
          '<p>К модулям из шага 3 добавились <code>json</code> — перевод словаря в текст JSON — и <code>os</code> — функции системы, здесь <code>os.strerror</code>.</p>'),
         ('8-9', 'Путь к библиотеке',
          '<p>Те же две строки, что в шаге 3: папка <code>agent/core</code> и имя файла по системе. Имена из заглавных букв — договорённость Python: значение задаётся один раз и дальше не меняется.</p>'),
         ('12-18', 'Описать структуру ядра на Python',
          '<p><code>class CoreInfo(ctypes.Structure)</code> — новый тип Python, устроенный в памяти как структура C. <code>_fields_</code> — список полей в том же порядке и того же размера, что в <code>core.h</code>:</p>'
          + cells([('pid', '0 · c_int64', 'w'), ('cpus', '8 · c_int32', 'w'), ('page_size', '12 · c_int32', 'w'), ('host', '16 · c_char × 256', 'w')])
          + '<ul class="words"><li><code>ctypes.c_int64</code> — то же, что <code>int64_t</code> в C, 8 байт;</li>'
          '<li><code>ctypes.c_char * 256</code> — массив из 256 байт, как <code>char host[256]</code>.</li></ul>'
          '<p>Python не читает <code>core.h</code>. Если порядок полей здесь разойдётся с C, ошибки не будет, но числа окажутся в чужих полях — опыт шага 6.</p>'
          + like('Трафарет, который кладут на чужой бланк: прорези должны совпасть с графами до клетки.')),
         ('21', 'Загрузить библиотеку',
          '<p><code>core = ctypes.CDLL(…)</code> — как в шаге 3. Строки печати убраны: проверка уже пройдена.</p>'),
         ('22-23', 'Описать функцию для Python',
          '<ul class="words"><li><code>argtypes</code> — типы параметров. <code>ctypes.POINTER(CoreInfo)</code> — «адрес структуры <code>CoreInfo</code>», то есть <code>struct core_info *</code>;</li>'
          '<li><code>restype</code> — тип результата, <code>int</code>.</li></ul>'
          '<p>С этим описанием ctypes проверяет, что в функцию передают адрес нужной структуры, и правильно читает её ответ.</p>'
          + like('Инструкция к переходнику: какую вилку можно вставлять и какое напряжение выйдет.')),
         ('26-29', 'Текст ошибки по коду',
          '<p><code>def error_text(code):</code> — своя функция Python с параметром <code>code</code>. Тело функции — строки с отступом.</p>'
          '<ul class="words"><li><code>if sys.platform == "win32":</code> — на Windows текст даёт <code>ctypes.FormatError</code>: 87 → «Параметр задан неверно.»;</li>'
          '<li>иначе <code>os.strerror</code>: 22 → «Invalid argument».</li></ul>'
          '<p>Таблицы кодов у систем разные — это вывод шага 4 главы 1.1.</p>'),
         ('32-34', 'Вызвать ядро',
          '<ul class="words"><li><code>info = CoreInfo()</code> — пустая структура, 272 байта нулей. Память выделяет Python;</li>'
          '<li><code>ctypes.byref(info)</code> — адрес этой структуры, то же, что <code>&amp;info</code> в C;</li>'
          '<li><code>err</code> — код, который вернула <code>core_get_info</code>: 0 или код ошибки.</li></ul>'
          + ''.join(f'<div data-os="{o}">' + V.mem([('CoreInfo()', '', cells([('0', 'pid', 'w'), ('0', 'cpus', 'w'), ('0', 'page_size', 'w'), ('0 0 …', 'host', 'w')])),
                   ('после вызова', '', cells([(pid, 'pid', 'w'), (cpus, 'cpus', 'w'), (page, 'page_size', 'w'), (host, 'host', 'w')]))]) + '</div>'
                    for o, pid, cpus, page, host in (('win', '4656', '4', '4096', 'WIN11-LAB'), ('mac', 'PID', '10', '16384', 'MacBook-Air…'), ('linux', 'PID', '10', '4096', 'lab-linux')))
          + like('Тот же бланк в окошке МФЦ, только посетитель теперь Python.')),
         ('35-36', 'Код ошибки → исключение',
          '<p>Если ядро вернуло не 0, <code>raise OSError(err, error_text(err))</code> поднимает <span class="term">исключение</span>: выполнение функции прерывается, и Python сообщает код и текст. Тот, кто вызвал <code>get_info</code>, может перехватить его через <code>try</code>/<code>except OSError</code>.</p>'
          + V.steps(V.card('ядро', '<span data-os="win">err = 87</span><span data-os="mac linux">err = 22</span>', '', 'c'), V.arrow('err != 0'),
                    V.card('get_info', '<span data-os="win">raise OSError(87, "Параметр задан неверно.")</span><span data-os="mac linux">raise OSError(22, "Invalid argument")</span>', '', 'bad'), V.arrow('исключение'),
                    V.card('вызывающий код', 'try / except OSError', '<small>или остановка с сообщением</small>', 'sys'))
          + like('Пожарная сигнализация: при сбое работа сразу останавливается, и сигнал идёт тому, кто отвечает за здание.')),
         ('37-42', 'Собрать словарь',
          '<p>Фигурные скобки с парами «ключ: значение» — словарь Python. Числа берутся из полей структуры как есть.</p>'
          '<p><code>info.host</code> ctypes отдаёт как <code>bytes</code> — байты до первого нуля. <code>.decode("utf-8")</code> переводит их в строку Python: ядро отдаёт имя в UTF-8 на всех системах.</p>'
          + cells([('b"lab-linux"', 'bytes', 'w'), ('→', '', ''), ('"lab-linux"', 'str', 'w')])),
         ('45-47', 'Запуск как программы',
          '<p><code>if __name__ == "__main__":</code> — блок выполняется, только когда <code>brain.py</code> запущен командой <code>python brain.py</code>. Если его подключат через <code>import</code>, сообщение не печатается.</p>'
          '<ul class="words"><li><code>**get_info()</code> — пары словаря вставляются в новый словарь рядом с <code>event</code> и <code>os</code>;</li>'
          '<li><code>json.dumps(…, ensure_ascii=False, indent=2)</code> — словарь в текст JSON: кириллица без кодов <code>\\u…</code>, отступ 2 пробела.</li></ul>'
          '<p>Это первое сообщение агента <code>agent_started</code>. В главе 1.3 его же функция <code>send</code> отправит в n8n.</p>')],
        [('ядро на C', 'core_get_info'), ('ctypes', 'CoreInfo, byref'), ('словарь Python', 'pid, cpus, page_size, host'), ('JSON agent_started', 'уйдёт в n8n, глава 1.3')],
        hl_py(BRAIN))
    return W
