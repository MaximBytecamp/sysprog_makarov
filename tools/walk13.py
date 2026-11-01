"""Пошаговый разбор главы 1.3: функция send и блок запуска brain.py. Строки — по фрагменту SEND."""
from walk11 import like, trace_html


def build(hl_py, SEND):
    W = {}
    W['send'] = trace_html('brain.py · send', 'win mac linux',
        'отправить сообщение агента в n8n по сети. Ядро и мозг работают на компьютере, а сценарий n8n — отдельная программа; связь между ними — запрос HTTP на адрес вебхука.',
        [('1', 'Функция с двумя параметрами',
          '<p><code>def send(message, url):</code> — своя функция. <code>message</code> — словарь с данными агента, <code>url</code> — адрес вебхука, куда отправлять.</p>'
          + like('Конверт и адрес на нём: что отправить и куда.')),
         ('2', 'Словарь → текст → байты',
          '<p>Строка делает два превращения подряд:</p>'
          '<ul class="words"><li><code>json.dumps(message, ensure_ascii=False)</code> — словарь в текст JSON, русские буквы остаются буквами;</li>'
          '<li><code>.encode("utf-8")</code> — текст в байты UTF-8. По сети передаются байты.</li></ul>'
          '<p><code>{"event": "agent_started", …}</code> → <code>b\'{"event": "agent_started", …}\'</code></p>'
          + like('Письмо сначала пишут, потом запечатывают в конверт. Почта возит конверты.')),
         ('3-4', 'Описать запрос',
          '<p><code>urllib.request.Request(…)</code> собирает запрос, но ещё не отправляет его:</p>'
          '<ul class="words"><li><code>url</code> — куда;</li><li><code>data=data</code> — тело запроса, те самые байты;</li>'
          '<li><code>method="POST"</code> — метод «принять данные». Вебхук в n8n настроен на POST;</li>'
          '<li><code>headers={"Content-Type": "application/json"}</code> — заголовок: «в теле JSON». По нему n8n разбирает тело в поле <code>body</code>.</li></ul>'
          + like('Бланк заказного письма: адрес, вложение и пометка «внутри документы».')),
         ('5', 'Отправить и дождаться ответа',
          '<p><code>urllib.request.urlopen(request, timeout=120)</code> отправляет запрос. Если n8n не ответит за 120 секунд, Python поднимет исключение.</p>'
          '<p><code>with … as response:</code> — ответ доступен под именем <code>response</code> внутри блока. После блока соединение закрывается само.</p>'),
         ('6', 'Вернуть код и текст ответа',
          '<p><code>response.status</code> — код ответа HTTP: 200 значит «принято». <code>response.read().decode("utf-8")</code> — тело ответа из байтов в строку, у n8n это <code>Workflow was started</code>.</p>'
          '<p>Функция возвращает сразу два значения через запятую.</p>'
          + like('Квитанция о вручении: отметка «вручено» и подпись получателя.')),
         ('9-11', 'Собрать и напечатать сообщение',
          '<p>Блок запуска из главы 1.2 без изменений: словарь <code>agent_started</code> со сведениями от ядра и его печать в JSON.</p>'),
         ('12-14', 'Отправить, если адрес передан',
          '<ul class="words"><li><code>sys.argv</code> — список слов командной строки: <code>["brain.py", "http://localhost:5678/…"]</code>;</li>'
          '<li><code>len(sys.argv) &gt; 1</code> — «после имени скрипта есть ещё слово»;</li>'
          '<li><code>status, body = send(…)</code> — два значения функции раскладываются в две переменные.</li></ul>'
          '<p>Без адреса скрипт только печатает сообщение, как в главе 1.2. С адресом — отправляет и печатает ответ n8n.</p>')],
        [('brain.py', 'словарь agent_started'), ('JSON → байты', 'json.dumps, encode'), ('POST по HTTP', 'urllib.request'), ('n8n', 'вебхук /agent → модель → письмо')],
        hl_py(SEND))
    return W
