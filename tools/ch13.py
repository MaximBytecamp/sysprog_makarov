"""Глава 1.3 «n8n и Ollama: первая автоматизация» → temy/08-n8n-i-ollama/index.html.

Стенд (28.10.2026, macOS 26.1): n8n 2.45.4, Ollama 0.40.12 и Mailpit в Docker в общем сетевом пространстве, поэтому
адреса те же, что у студента: n8n — localhost:5678, Ollama — localhost:11434, SMTP Mailpit — localhost:1025.
Модель qwen2.5:3b импортирована в Ollama из GGUF Qwen2.5-3B-Instruct Q4_K_M (Hugging Face): загрузка из библиотеки
Ollama на стенде не проходила из-за подмены адресов в сети. Кадры n8n и Mailpit одинаковы для трёх систем —
браузер, Playwright по CDP (src13/pw.py, сценарии s*.py), рамки — src13/mark13.py. Выводы терминала и ответы
модели — src13/out-*.txt, настоящие запуски brain.py на macOS (Python 3.12)."""
import html
from pathlib import Path

from ch11 import M, per
from ch12 import cmd, hl_py

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / 'src13'
OUT = ROOT / 'temy/08-n8n-i-ollama/index.html'

BRAIN = (SRC / 'brain.py').read_text()
OUT_TEST = (SRC / 'out-test.txt').read_text().strip()
OUT_PROD = (SRC / 'out-prod.txt').read_text().strip()
LLM = (SRC / 'out-llm.txt').read_text().strip()


def fig(name, cap, alt):
    return (f'        <figure class="shot">\n          <img src="img/{name}.png" alt="{html.escape(alt)}" loading="lazy">\n'
            f'          <figcaption>{cap}</figcaption>\n        </figure>')


def out(cap, text, cmdline):
    return (f'        <figure class="code code--out">\n          <figcaption><span>{cap}</span><span>команда и ответ</span></figcaption>\n'
            f'<pre><span class="cmd">{html.escape(cmdline)}</span>\n{html.escape(text)}</pre>\n        </figure>')


def between(text, start, end=None):
    lines = text.rstrip('\n').split('\n')
    i = next(k for k, l in enumerate(lines) if start in l)
    j = len(lines) - 1 if end is None else next(k for k in range(i, len(lines)) if end in lines[k])
    return '\n'.join(lines[i:j + 1])


S = []

S.append(f'''
        <h2 id="s1"><span class="sec">§1</span>Задача главы</h2>
        <p>В главе 1.2 <code>brain.py</code> вызвал ядро на C и напечатал сообщение <code>agent_started</code> в формате JSON. Пока это сообщение видно только в терминале. Агент работает без человека, поэтому его сообщения должны попадать к администратору сами, и желательно с пояснением: что произошло и нужно ли что-то делать. В главе собирается такой путь: <code>brain.py</code> отправляет сообщение в сервис автоматизации n8n, модель ИИ в Ollama пишет к нему пояснение, и n8n отправляет письмо.</p>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>В отделении почты письмо принимают в окошке, сотрудник заполняет к нему сопроводительный лист, а курьер относит всё адресату. Каждый делает одну операцию и передаёт письмо дальше по цепочке. Порядок операций висит на стене в виде схемы.</p>
          <p class="miss">Сотрудник почты сверяет сопроводительный лист с письмом. Модель составляет текст по образцам, на которых её обучили, и может ошибиться в смысле чисел.</p>
        </div></div>
        <p><span class="term">n8n</span> — сервис автоматизации: в браузере из блоков собирается <span class="term">сценарий</span> (workflow), и n8n выполняет его, когда приходит событие. Блоки называются <span class="term">узлами</span> (nodes). Узел принимает данные от предыдущего узла и делает одну операцию: принимает HTTP-запрос, вызывает модель или отправляет письмо. Результат он передаёт следующему узлу. n8n устанавливается на свой компьютер и работает без облака.</p>
        <p><span class="term">Ollama</span> — программа, которая запускает модели ИИ на своём компьютере и отвечает на запросы по адресу <code>http://localhost:11434</code>. В курсе используется модель <code>qwen2.5:3b</code>: три миллиарда параметров, файл около 2 ГБ, работает на компьютере с 8 ГБ памяти без видеокарты. Текст тревоги не уходит в облако, поэтому в нём можно оставить имя компьютера и пути.</p>
        <figure class="scheme">
          <p class="scheme__head">Путь сообщения агента</p>
          <div class="scheme__body">
            <svg viewBox="0 0 760 230" role="img" aria-label="Схема: brain.py отправляет JSON запросом POST на вебхук n8n; узел Webhook передаёт сообщение узлу Basic LLM Chain, тот вызывает модель в Ollama и получает текст; узел Send an Email отправляет письмо">
              <rect x="10" y="70" width="120" height="70" fill="var(--acc-pale)" stroke="var(--ink)" stroke-width="3"/>
              <text x="70" y="100" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="13" font-weight="700" fill="var(--ink)">brain.py</text>
              <text x="70" y="122" text-anchor="middle" font-family="Inter, sans-serif" font-size="11.5" fill="var(--ink-soft)">агент</text>
              <path d="M132 105 H182" stroke="var(--ink)" stroke-width="3"/><path d="M174 98 L184 105 L174 112" stroke="var(--ink)" stroke-width="3" fill="none"/>
              <text x="158" y="94" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="10.5" fill="var(--ink-soft)">POST</text>
              <rect x="186" y="20" width="460" height="170" fill="var(--paper)" stroke="var(--ink)" stroke-width="3" stroke-dasharray="8 5"/>
              <text x="200" y="40" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">сценарий n8n · localhost:5678</text>
              <rect x="200" y="70" width="110" height="70" fill="var(--page)" stroke="var(--ink)" stroke-width="3"/>
              <text x="255" y="102" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">Webhook</text>
              <text x="255" y="122" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" fill="var(--ink-soft)">принять</text>
              <path d="M312 105 H350" stroke="var(--ink)" stroke-width="3"/><path d="M342 98 L352 105 L342 112" stroke="var(--ink)" stroke-width="3" fill="none"/>
              <rect x="354" y="70" width="140" height="70" fill="var(--page)" stroke="var(--ink)" stroke-width="3"/>
              <text x="424" y="102" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">Basic LLM Chain</text>
              <text x="424" y="122" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" fill="var(--ink-soft)">пояснение</text>
              <path d="M496 105 H526" stroke="var(--ink)" stroke-width="3"/><path d="M518 98 L528 105 L518 112" stroke="var(--ink)" stroke-width="3" fill="none"/>
              <rect x="530" y="70" width="104" height="70" fill="var(--page)" stroke="var(--ink)" stroke-width="3"/>
              <text x="582" y="102" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">Send Email</text>
              <text x="582" y="122" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" fill="var(--ink-soft)">отправить</text>
              <path d="M424 142 V178" stroke="var(--ng)" stroke-width="3" stroke-dasharray="6 4"/>
              <rect x="350" y="180" width="148" height="44" fill="var(--ng-pale)" stroke="var(--ink)" stroke-width="3"/>
              <text x="424" y="200" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">Ollama</text>
              <text x="424" y="216" text-anchor="middle" font-family="Roboto Mono, monospace" font-size="10.5" fill="var(--ink-soft)">qwen2.5:3b · :11434</text>
              <path d="M636 105 H686" stroke="var(--ink)" stroke-width="3"/><path d="M678 98 L688 105 L678 112" stroke="var(--ink)" stroke-width="3" fill="none"/>
              <rect x="690" y="70" width="62" height="70" fill="var(--acc-pale)" stroke="var(--ink)" stroke-width="3"/>
              <text x="721" y="110" text-anchor="middle" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">почта</text>
            </svg>
          </div>
          <p class="scheme__note">Пунктирная рамка — сценарий n8n из трёх узлов. Сплошные стрелки — путь данных от узла к узлу. Пунктир вниз — узел Basic LLM Chain вызывает модель в Ollama и получает от неё текст.</p>
        </figure>
        <div class="why">
          <p class="why__head">Зачем это нужно в работе</p>
          <ul class="why__list">
            <li><b>Доставлять события без человека.</b> Агенты мониторинга и защиты отправляют события на адрес сервиса, а в сервисе настроено, куда их передать: в почту, мессенджер, таблицу.</li>
            <li><b>Менять доставку без правки агента.</b> В агенте записан только адрес вебхука. Получателя, текст письма и модель меняют в сценарии n8n, код на C и Python не трогают.</li>
            <li><b>Держать данные у себя.</b> Модель в Ollama работает на своём компьютере, и сведения о компьютере не уходят во внешний сервис.</li>
          </ul>
        </div>
        <p>Глава продолжает репозиторий <code>sysprog-start</code> из главы 1.2: в <code>agent/core</code> собрана библиотека ядра, в <code>agent/brain</code> лежит <code>brain.py</code>. Кадры n8n и почты одинаковы для трёх систем: n8n работает в браузере. По системам различаются установка программ и команда запуска <code>brain.py</code>.</p>
        <p class="bridge">Сценарий вызывает модель, поэтому первая часть — установить Ollama и n8n и проверить, что оба отвечают.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>1</b>Программы</span></div>
        <h2 id="s2"><span class="sec">§2</span>Шаг 1. Установить Ollama и скачать модель</h2>
        <p>Ollama ставится как обычная программа. После установки она работает в фоне и принимает запросы на порту 11434.</p>
{per(win='<p>Установщик <code>OllamaSetup.exe</code> скачивается со страницы <a href="https://ollama.com/download">ollama.com/download</a>. После установки значок Ollama появляется в области уведомлений, команда <code>ollama</code> доступна в новом окне командной строки.</p>',
     mac='<p>Архив <code>Ollama.dmg</code> скачивается со страницы <a href="https://ollama.com/download">ollama.com/download</a>, программа переносится в папку Программы и запускается. Значок Ollama появляется в строке меню, команда <code>ollama</code> доступна в Терминале.</p>',
     linux='<p>В Linux Ollama ставится сценарием с сайта, он же регистрирует службу systemd <code>ollama</code>:</p><figure class="code"><figcaption><span>терминал</span></figcaption><pre>curl -fsSL https://ollama.com/install.sh | sh</pre></figure>')}
        <p>Модель скачивается командой <code>ollama pull</code>, около 2 ГБ. В кабинете модель раздаётся из общей папки, если интернет медленный. Затем модель проверяется одним вопросом:</p>
        <figure class="code">
          <figcaption><span>терминал</span></figcaption>
<pre>ollama pull qwen2.5:3b
ollama list
ollama run qwen2.5:3b "Объясни по-русски в двух предложениях: агент-сторож запустился на компьютере lab-linux, 10 процессоров."</pre>
        </figure>
        <figure class="code code--out">
          <figcaption><span>ответ модели на стенде</span><span>около 30 секунд без видеокарты</span></figcaption>
<pre><span class="cmd">ollama run qwen2.5:3b "Объясни по-русски в двух предложениях: …"</span>
Агент-сторож был запущен на компьютере lab-linux и теперь активно использует 10 процессоров.</pre>
        </figure>
        <p>Модель ответила по-русски, значит Ollama и модель работают. В ответе есть ошибка: «10 процессоров» — это сколько процессоров у компьютера, а модель написала, что агент их «активно использует». Модель составляет правдоподобный текст и не проверяет его по данным, поэтому её ответы сверяют с исходными числами.</p>
        <p class="step-done"><b>Что получилось.</b>Ollama работает и отвечает по адресу <code>http://localhost:11434</code>, модель <code>qwen2.5:3b</code> скачана. Теперь — n8n.</p>

        <h2 id="s3"><span class="sec">§3</span>Шаг 2. Запустить n8n</h2>
        <p>n8n написан на JavaScript и запускается через Node.js. Нужна версия Node.js от 20.19 до 24.x — более новые n8n не поддерживает. Node.js ставится с <a href="https://nodejs.org">nodejs.org</a>, версию показывает <code>node -v</code>. Затем n8n запускается одной командой; при первом запуске <code>npx</code> скачивает его, это несколько минут:</p>
        <figure class="code">
          <figcaption><span>терминал</span><span>окно оставить открытым</span></figcaption>
<pre>node -v
npx n8n</pre>
        </figure>
        <p>Когда в терминале появится строка <code>Editor is now accessible via: http://localhost:5678</code>, адрес открывается в браузере. Пока окно терминала открыто, n8n работает; закрытие окна останавливает его. Свои данные — сценарии, подключения, журнал запусков — n8n хранит в папке <code>.n8n</code> в домашней папке пользователя.</p>
        <p>При первом входе n8n просит создать учётную запись владельца. Она хранится только на этом компьютере и нужна, чтобы входить в n8n:</p>
{fig('01-owner', f'{M(1)} Почта владельца. {M(2)} Пароль: не короче 8 символов, с цифрой и заглавной буквой. {M(3)} Кнопка <b>Next</b>.', 'Окно Set up owner account: поля Email, First Name, Last Name, Password и кнопка Next')}
        <p>После входа n8n предлагает подключить облачного помощника n8n Assistant. Он работает через серверы n8n, и в курсе не используется: нажимаем <b>Set up later in Settings</b>. Открывается главная страница:</p>
{fig('02-home', f'{M(1)} <b>Build a workflow</b> — создать пустой сценарий.', 'Главная страница n8n: Let’s build your first automation, карточки Build an agent и Build a workflow')}
        <p>Нажимаем <b>Build a workflow</b>. Открывается редактор с пустым холстом. Имя сценария задаётся щелчком по надписи <b>My workflow</b> вверху: <code>Агент-сторож: запуск</code>.</p>
        <p class="step-done"><b>Что получилось.</b>n8n работает по адресу <code>http://localhost:5678</code>, создан пустой сценарий. Первый узел сценария принимает сообщение агента.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>2</b>Сценарий</span></div>
        <h2 id="s4"><span class="sec">§4</span>Шаг 3. Принять сообщение: узел Webhook</h2>
        <div class="analogy"><div>
          <b>Сравнение из жизни</b>
          <p>У офиса есть почтовый ящик с адресом. Кто угодно может опустить в него письмо, и сотрудник забирает его сам. Отправителю не нужно знать, кто работает в офисе и что будет с письмом дальше.</p>
          <p class="miss">Почтовый ящик принимает письмо в любое время. Тестовый адрес n8n принимает одно сообщение и только после нажатия кнопки ожидания.</p>
        </div></div>
        <p><span class="term">Вебхук</span> (webhook) — адрес, на который другая программа отправляет HTTP-запрос, чтобы запустить сценарий. Агенту нужен только этот адрес: он отправляет на него JSON запросом POST, а что произойдёт дальше, задаётся в n8n.</p>
        <p>На пустом холсте нажимаем <b>Add first step…</b>. Справа открывается список узлов, в поиске набираем <code>Webhook</code>:</p>
{fig('03-webhook-pick', f'{M(1)} Поиск по узлам. {M(2)} Узел <b>Webhook</b>: «Starts the workflow when a webhook is called» — запускает сценарий при вызове вебхука.', 'Список What triggers this workflow? с поиском Webhook, первый результат — узел Webhook')}
        <p>Выбираем узел. Открывается окно его настроек. Меняем две настройки: метод — <b>POST</b>, им передают данные в теле запроса; путь — <code>agent</code> вместо случайной строки, чтобы адрес было легко набрать:</p>
{fig('04-webhook', f'{M(1)} Тестовый адрес: <code>http://localhost:5678/webhook-test/agent</code>. {M(2)} Метод <b>POST</b>. {M(3)} Путь <code>agent</code>.', 'Окно узла Webhook: Test URL http://localhost:5678/webhook-test/agent, HTTP Method POST, Path agent')}
        <p>У вебхука два адреса, они переключаются кнопками <b>Test URL</b> и <b>Production URL</b> над адресом. Тестовый, с <code>webhook-test</code>, работает, пока собирается сценарий: после нажатия <b>Listen for test event</b> он принимает одно сообщение и показывает его в окне узла. Боевой, с <code>webhook</code>, работает постоянно, но только после публикации сценария в шаге 7. Настройка <b>Respond: Immediately</b> означает, что n8n отвечает агенту сразу, не дожидаясь письма.</p>
        <p class="step-done"><b>Что получилось.</b>В сценарии есть вебхук <code>/webhook-test/agent</code>, принимающий POST. Чтобы проверить его, агент должен уметь отправлять сообщение.</p>
''')

SEND = between(BRAIN, 'def send(message, url)')
S.append(f'''
        <h2 id="s5"><span class="sec">§5</span>Шаг 4. Отправить сообщение из brain.py</h2>
        <p>Отправка делается модулем <code>urllib.request</code> из стандартной библиотеки Python: ставить ничего не нужно. В <code>brain.py</code> добавляются строка <code>import urllib.request</code> в начале и функция <code>send</code>, а блок запуска получает адрес из командной строки:</p>
        <figure class="code">
          <figcaption><span>agent/brain/brain.py · конец файла</span></figcaption>
<pre>{hl_py(SEND)}</pre>
        </figure>
        <ul>
          <li><code>json.dumps(...).encode("utf-8")</code> — словарь превращается в текст JSON, текст — в байты UTF-8: по сети передаются байты. <code>ensure_ascii=False</code> оставляет русские буквы как есть.</li>
          <li><code>urllib.request.Request(url, data=..., method="POST", headers=...)</code> — описание запроса: адрес, тело, метод и заголовок <code>Content-Type: application/json</code>. По заголовку n8n разбирает тело как JSON.</li>
          <li><code>with urllib.request.urlopen(request, timeout=120) as response</code> — запрос отправляется. Если n8n не ответит за 120 секунд, Python поднимет исключение. <code>with</code> закрывает соединение после чтения ответа.</li>
          <li><code>sys.argv</code> — список слов командной строки, <code>sys.argv[1]</code> — первое слово после имени скрипта. Адрес передаётся при запуске, поэтому один и тот же <code>brain.py</code> отправляет и на тестовый, и на боевой адрес.</li>
        </ul>
        <p>В окне узла Webhook нажимаем <b>Listen for test event</b> — узел переходит в режим приёма. Сразу после этого в терминале из папки <code>agent/brain</code> запускаем:</p>
{cmd('python brain.py http://localhost:5678/webhook-test/agent', 'python3 brain.py http://localhost:5678/webhook-test/agent', 'python3 brain.py http://localhost:5678/webhook-test/agent', 'терминал в папке agent/brain')}
{out('терминал на macOS', OUT_TEST, 'python3 brain.py http://localhost:5678/webhook-test/agent')}
        <p>Последняя строка — ответ n8n: код 200 и текст <code>Workflow was started</code>, «сценарий запущен». В окне узла справа появилось само сообщение. Вкладка <b>JSON</b> показывает его целиком:</p>
{fig('05-test-event', f'{M(1)} Кнопка ожидания тестового сообщения. {M(2)} <code>body</code> — тело запроса: то, что отправил <code>brain.py</code>. {M(3)} <code>executionMode: test</code> — запуск через тестовый адрес.', 'Окно узла Webhook после тестового вызова: вкладка JSON, headers, body с event agent_started, os, pid, cpus, page_size, host, executionMode test')}
        <p>Кроме тела, n8n записал заголовки запроса (<code>headers</code>), параметры адреса (<code>query</code>) и адрес вебхука. Следующие узлы берут данные агента из поля <code>body</code>. В Windows в поле <code>os</code> будет <code>win32</code>, в Linux — <code>linux</code>.</p>
        <p class="step-done"><b>Что получилось.</b><code>brain.py</code> отправил сообщение, n8n его принял и показал. Дальше к сообщению добавляется пояснение модели.</p>
''')

S.append(f'''
        <h2 id="s6"><span class="sec">§6</span>Шаг 5. Добавить пояснение модели</h2>
        <p>Модель вызывается узлом <b>Basic LLM Chain</b> — «простая цепочка для запроса к большой языковой модели». Узел собирает текст запроса и отправляет его модели, которая подключается к нему снизу отдельным узлом. Закрываем окно Webhook и нажимаем <b>+</b> справа от узла на холсте:</p>
{fig('06-llm-pick', f'{M(1)} Поиск <code>Basic LLM Chain</code>. {M(2)} Узел в списке «What happens next?» — что происходит дальше.', 'Холст с узлом Webhook и список What happens next? с найденным узлом Basic LLM Chain')}
        <p>В окне узла меняем источник запроса: <b>Source for Prompt</b> → <b>Define below</b>, «задать ниже». Вариант по умолчанию берёт текст из узла чата, а у нас вебхук. В поле <b>Prompt</b> вписываем запрос:</p>
        <figure class="code">
          <figcaption><span>Prompt (User Message)</span></figcaption>
<pre>Ты помогаешь администратору компьютера. Агент-сторож прислал событие в формате JSON. Объясни по-русски в двух-трёх предложениях, что произошло и нужно ли что-то делать.

Событие: {{{{ JSON.stringify($json.body) }}}}</pre>
        </figure>
        <p>Двойные фигурные скобки <code>{{{{ … }}}}</code> — <span class="term">выражение</span> n8n: вместо него подставляется значение, вычисленное по входным данным узла. <code>$json</code> — данные, пришедшие из предыдущего узла, <code>$json.body</code> — тело сообщения агента, <code>JSON.stringify</code> превращает его в строку JSON. Выражение подсвечивается зелёным, а под полем n8n показывает текст запроса с подставленными данными.</p>
{fig('07-prompt', f'{M(1)} Источник запроса — <b>Define below</b>. {M(2)} Запрос с выражением. {M(3)} <b>Model</b> — сюда подключается модель.', 'Окно Basic LLM Chain: слева входные данные Webhook, в центре Source for Prompt Define below и текст запроса с выражением JSON.stringify($json.body)')}
        <p>Нажимаем <b>+</b> под словом <b>Model</b> {M(3)} и в поиске набираем <code>Ollama</code>. Нужен узел <b>Ollama Chat Model</b>: Basic LLM Chain отправляет запрос в виде сообщений чата.</p>
{fig('08-ollama-pick', f'{M(1)} Поиск <code>Ollama</code>. {M(2)} <b>Ollama Chat Model</b>.', 'Список Language Models с поиском Ollama: Ollama Model и Ollama Chat Model')}
        <p>В окне узла нажимаем <b>Connect to Ollama</b>. Открывается окно <span class="term">подключения</span> (credential) — так n8n называет сохранённые адрес и пароль внешнего сервиса. Адрес уже заполнен адресом Ollama на этом же компьютере:</p>
{fig('09-credential', f'{M(1)} <b>Base URL</b> — <code>http://localhost:11434</code>. {M(2)} <b>Save</b>.', 'Окно Ollama account: Base URL http://localhost:11434, поле API Key пустое, кнопка Save')}
        <p>После сохранения n8n запрашивает у Ollama список моделей. В поле <b>Model</b> по умолчанию стоит <code>llama3.2</code>, которой нет на компьютере, поэтому открываем список и выбираем свою:</p>
{fig('10-model', f'{M(1)} Поле <b>Model</b>. {M(2)} <code>qwen2.5:3b</code> — единственная модель в Ollama на стенде.', 'Окно Ollama Chat Model: подключение Ollama account, список моделей с qwen2.5:3b')}
        <p>Закрываем окно модели, открываем Basic LLM Chain и нажимаем <b>Execute step</b> — n8n выполнит узел на сообщении, пришедшем в шаге 4. Без видеокарты ответ занимает от 10 до 30 секунд:</p>
{fig('11-llm-output', f'{M(1)} <b>Execute step</b>. {M(2)} Ответ модели в поле <code>text</code>. {M(3)} Подключённая модель Ollama.', 'Окно Basic LLM Chain после выполнения: справа поле text с ответом модели по-русски')}
        <figure class="code code--out">
          <figcaption><span>поле text, ответ модели на стенде</span></figcaption>
<pre>{html.escape(LLM)}</pre>
        </figure>
        <p>Ответ сверяем с данными сообщения. Система определена верно: <code>darwin</code> — это macOS. Размер страницы назван верно. «Работает на 10 ядрах» — неточность: в поле <code>cpus</code> число процессоров компьютера, а о том, сколько из них занимает агент, в сообщении ничего нет. В шаге 1 модель ошиблась так же. Поэтому в письме кроме пояснения модели всегда отправляется исходное сообщение агента: по нему администратор проверит числа.</p>
        <p class="step-done"><b>Что получилось.</b>Модель в Ollama пишет пояснение к сообщению агента. Пояснение и сообщение осталось отправить письмом.</p>
''')

S.append(f'''
        <h2 id="s7"><span class="sec">§7</span>Шаг 6. Отправить письмо</h2>
        <p>Письмо отправляет узел <b>Send Email</b> по протоколу <span class="term">SMTP</span> — так почтовые программы передают письма почтовому серверу. Нажимаем <b>+</b> справа от Basic LLM Chain, ищем <code>Send Email</code> и выбираем действие:</p>
{fig('12-email-pick', f'{M(1)} <b>Send an Email</b> — отправить письмо. Второе действие останавливает сценарий до ответа получателя, оно здесь не нужно.', 'Список действий Send Email: Send an Email и Send message and wait for response')}
        <p>В окне узла нажимаем <b>Connect to SMTP</b>. Для подключения нужны адрес почтового сервера, порт и учётная запись. Для Яндекс Почты это сервер <code>smtp.yandex.ru</code>, порт 465 и включённый <b>SSL/TLS</b>. В <b>User</b> пишется адрес ящика, в <b>Password</b> — пароль приложения. Его создают в настройках Яндекс ID: обычный пароль от ящика сервер не принимает. Кадры главы сняты с почтовым сервером для проверки Mailpit. Он принимает письма на своём компьютере и показывает их в браузере, в интернет письма не уходят.</p>
{fig('13-smtp', f'{M(1)} <b>Host</b> — <code>localhost</code>, Mailpit на этом компьютере. {M(2)} <b>Port</b> — 1025. {M(3)} <b>SSL/TLS</b> выключен: Mailpit работает без шифрования. {M(4)} <b>Save</b>.', 'Окно SMTP account: User и Password пустые, Host localhost, Port 1025, SSL/TLS выключен, кнопка Save')}
        <p>Затем заполняем само письмо. Тема и текст — выражения. В теме <code>$('Webhook').item.json.body</code> — тело сообщения из узла Webhook. <code>$json</code> здесь уже ответ модели, а сообщение агента лежит двумя узлами раньше, поэтому к узлу обращаются по имени. Формат письма — <b>Text</b>, простой текст.</p>
        <figure class="code">
          <figcaption><span>узел Send an Email</span></figcaption>
<pre>From Email:   agent@sysprog.local
To Email:     ivan.petrov@example.com
Subject:      Агент-сторож: {{{{ $('Webhook').item.json.body.event }}}} на {{{{ $('Webhook').item.json.body.host }}}}
Email Format: Text
Text:
{{{{ $json.text }}}}

Сообщение агента:
{{{{ JSON.stringify($('Webhook').item.json.body, null, 2) }}}}</pre>
        </figure>
{fig('14-email', f'{M(1)} Получатель. {M(2)} Тема: под полем подставленное значение «Агент-сторож: agent_started на MacBook-Air-Maxim.local». {M(3)} Текст: ответ модели и сообщение агента.', 'Окно Send an Email: SMTP account, From agent@sysprog.local, To ivan.petrov@example.com, Subject и Text с выражениями')}
        <p><code>JSON.stringify(…, null, 2)</code> печатает JSON с отступом в два пробела, так он читается в письме. Нажимаем <b>Execute step</b> — письмо уходит. В Mailpit (<code>http://localhost:8025</code>) оно выглядит так:</p>
{fig('15-mail', f'{M(1)} Тема с событием и именем компьютера. {M(2)} Пояснение модели. {M(3)} Исходное сообщение агента.', 'Письмо в Mailpit: тема Агент-сторож: agent_started на MacBook-Air-Maxim.local, текст пояснения модели и JSON сообщения агента')}
        <p>Последнюю строку «This email was sent automatically with n8n» узел добавляет сам. Она отключается в <b>Options</b> узла: <b>Add option</b> → <b>Append n8n Attribution</b> → выключить.</p>
        <p class="step-done"><b>Что получилось.</b>Сценарий из трёх узлов принимает сообщение, получает пояснение модели и отправляет письмо. Пока он работает только по кнопкам в редакторе.</p>
''')

S.append(f'''
        <div class="part" role="separator"><span><b>3</b>Работа без редактора</span></div>
        <h2 id="s8"><span class="sec">§8</span>Шаг 7. Опубликовать сценарий</h2>
        <p>Закрываем окно узла. На холсте виден весь сценарий:</p>
{fig('16-canvas', f'{M(1)} Webhook. {M(2)} Basic LLM Chain. {M(3)} Ollama Chat Model — подключена снизу. {M(4)} Send an Email. {M(5)} <b>Publish</b>.', 'Холст n8n: Webhook, Basic LLM Chain с моделью Ollama Chat Model снизу, Send an Email; кнопка Publish вверху справа')}
        <p>Чтобы сценарий работал без открытого редактора, его публикуют: кнопка <b>Publish</b> {M(5)} вверху справа. n8n просит имя версии — по нему в журнале видно, какая версия сценария обработала сообщение:</p>
{fig('17-publish', f'{M(1)} Имя версии. {M(2)} <b>Publish</b>.', 'Окно Publish workflow: Version name v1: письмо с объяснением модели, кнопка Publish')}
{fig('18-published', f'{M(1)} Статус сценария — <b>Published</b>. {M(2)} «Теперь можно вызывать боевой адрес вебхука. Эти запуски не появятся в редакторе, но видны в списке запусков».', 'Окно Workflow published с пояснением о боевом адресе и списке запусков, статус Published вверху')}
        <p>Теперь агент отправляет сообщение на боевой адрес, без <code>-test</code>. Нажимать кнопки в n8n больше не нужно:</p>
{cmd('python brain.py http://localhost:5678/webhook/agent', 'python3 brain.py http://localhost:5678/webhook/agent', 'python3 brain.py http://localhost:5678/webhook/agent', 'терминал в папке agent/brain')}
{out('терминал на macOS', OUT_PROD, 'python3 brain.py http://localhost:5678/webhook/agent')}
        <p>Ответ n8n тот же, а письмо приходит через 10–30 секунд, когда модель закончит ответ. Каждый запуск сценария n8n записывает в журнал. Он открывается вкладкой <b>Executions</b> над холстом:</p>
{fig('19-executions', f'{M(1)} Боевой запуск: выполнен за 13,4 секунды. {M(2)} Номер запуска 5 и версия сценария. {M(3)} Значок колбы — запуски из редактора по тестовому адресу и кнопкам.', 'Вкладка Executions: список запусков, первый Succeeded in 13.409s, остальные с отметкой тестового запуска; справа схема сценария с отметками выполнения')}
        <p>Щелчок по запуску показывает схему с данными каждого узла: что пришло в Webhook, что ответила модель, что ушло в письмо. Если письмо не пришло, причину ищут здесь: узел с ошибкой отмечен красным.</p>
        <p class="step-done"><b>Что получилось.</b>Сценарий опубликован, <code>brain.py</code> отправляет сообщение на боевой адрес, и письмо с пояснением модели приходит без участия человека.</p>

        <h2 id="s9"><span class="sec">§9</span>Шаг 8. Сохранить работу в репозитории</h2>
        <p>В репозиторий уходит изменённый <code>brain.py</code>. Сценарий n8n хранится в базе n8n на компьютере. Его копия сохраняется в репозиторий файлом: меню <b>…</b> рядом с именем сценария → <b>Download</b>, файл кладётся в <code>agent/n8n/agent-started.json</code>. Подключения в этот файл не попадают — только их имена, поэтому пароль от почты в репозиторий не уйдёт.</p>
        <figure class="code">
          <figcaption><span>терминал в папке sysprog-start</span><span>то же, что плюс, Commit и Sync Changes</span></figcaption>
<pre>git add agent/brain/brain.py agent/n8n/agent-started.json
git commit -m "brain: отправка agent_started в n8n, сценарий с пояснением модели"
git push</pre>
        </figure>
        <p class="step-done"><b>Что получилось.</b>Код агента и копия сценария в репозитории. Ниже — справка по узлам и адресам главы.</p>
''')

S.append('''
        <div class="part" role="separator"><span><b>4</b>Справка</span></div>
        <h2 id="s10"><span class="sec">§10</span>Справка: адреса, узлы, выражения</h2>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Что</th><th>Адрес</th><th>Когда работает</th></tr></thead>
            <tbody>
              <tr><td>Редактор n8n</td><td><code>http://localhost:5678</code></td><td>пока запущен <code>npx n8n</code></td></tr>
              <tr><td>Тестовый вебхук</td><td><code>http://localhost:5678/webhook-test/agent</code></td><td>после <b>Listen for test event</b>, одно сообщение</td></tr>
              <tr><td>Боевой вебхук</td><td><code>http://localhost:5678/webhook/agent</code></td><td>после <b>Publish</b>, постоянно</td></tr>
              <tr><td>Ollama</td><td><code>http://localhost:11434</code></td><td>пока работает программа Ollama</td></tr>
              <tr><td>Mailpit (проверка писем)</td><td><code>http://localhost:8025</code>, SMTP — порт 1025</td><td>пока запущен Mailpit</td></tr>
            </tbody>
          </table>
        </div>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Узел</th><th>Что делает</th><th>Главные настройки</th></tr></thead>
            <tbody>
              <tr><td>Webhook</td><td>запускает сценарий по HTTP-запросу</td><td>HTTP Method, Path, Respond</td></tr>
              <tr><td>Basic LLM Chain</td><td>отправляет запрос модели</td><td>Source for Prompt, Prompt, Model</td></tr>
              <tr><td>Ollama Chat Model</td><td>модель для Basic LLM Chain</td><td>подключение Base URL, Model</td></tr>
              <tr><td>Send Email</td><td>отправляет письмо по SMTP</td><td>подключение Host, Port, SSL/TLS; From, To, Subject, Text</td></tr>
            </tbody>
          </table>
        </div>
        <div class="table-scroll">
          <table>
            <thead><tr><th>Выражение</th><th>Что подставляется</th></tr></thead>
            <tbody>
              <tr><td><code>{{ $json.body }}</code></td><td>поле <code>body</code> данных, пришедших из предыдущего узла</td></tr>
              <tr><td><code>{{ $('Webhook').item.json.body.host }}</code></td><td>поле из данных узла с именем Webhook, сколько бы узлов ни было между ними</td></tr>
              <tr><td><code>{{ JSON.stringify(x, null, 2) }}</code></td><td>объект в виде текста JSON с отступами</td></tr>
              <tr><td><code>{{ $json.text }}</code></td><td>ответ модели после Basic LLM Chain</td></tr>
            </tbody>
          </table>
        </div>

        <div class="part" role="separator"><span><b>5</b>Проверка себя</span></div>
        <h2 id="s11"><span class="sec">§11</span>Частые вопросы</h2>
        <div class="myths">
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Тестовый адрес вебхука работает так же, как боевой.</div>
            <div class="myth__yes"><b>На самом деле</b>Тестовый принимает одно сообщение после нажатия <b>Listen for test event</b>. Постоянно работает боевой адрес <code>/webhook/…</code>, и только у опубликованного сценария.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Ответ модели можно отправлять администратору без проверки.</div>
            <div class="myth__yes"><b>На самом деле</b>В шагах 1 и 5 модель неверно описала число процессоров. Вместе с пояснением отправляется исходное сообщение агента.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Ответ <code>200 Workflow was started</code> означает, что письмо отправлено.</div>
            <div class="myth__yes"><b>На самом деле</b>При <b>Respond: Immediately</b> n8n отвечает сразу, до вызова модели. Дошло ли письмо, видно во вкладке <b>Executions</b>.</div>
          </div>
          <div class="myth">
            <div class="myth__no"><b>Обычно думают</b>Для Ollama нужен интернет при каждом запросе.</div>
            <div class="myth__yes"><b>На самом деле</b>Интернет нужен один раз, чтобы скачать модель. Дальше модель работает на компьютере по адресу <code>localhost:11434</code>.</div>
          </div>
        </div>

        <h2 id="s12"><span class="sec">§12</span>Проверьте себя</h2>
        <details>
          <summary>Чем адрес <code>/webhook-test/agent</code> отличается от <code>/webhook/agent</code>?</summary>
          <p>Тестовый работает в редакторе после нажатия <b>Listen for test event</b> и принимает одно сообщение. Боевой работает постоянно, когда сценарий опубликован.</p>
        </details>
        <details>
          <summary>Почему в узле Basic LLM Chain источник запроса меняют на <b>Define below</b>?</summary>
          <p>Вариант по умолчанию берёт текст из узла чата. В этом сценарии данные приходят из вебхука, поэтому запрос задаётся в поле Prompt с выражением.</p>
        </details>
        <details>
          <summary>Почему в узле Send an Email используется <code>$('Webhook').item.json.body</code>, а не <code>$json.body</code>?</summary>
          <p><code>$json</code> — данные предыдущего узла, Basic LLM Chain, в них только ответ модели. Сообщение агента лежит в узле Webhook, к нему обращаются по имени.</p>
        </details>
        <details>
          <summary><code>brain.py</code> получил ответ 200, но письма нет. Где искать причину?</summary>
          <p>Во вкладке <b>Executions</b>: открыть запуск и найти узел, отмеченный красным. Частые причины — Ollama не запущена или неверные настройки SMTP.</p>
        </details>
        <details>
          <summary>Зачем в письмо добавлять исходный JSON, если есть пояснение модели?</summary>
          <p>Модель может ошибиться в смысле чисел. По исходному сообщению администратор проверяет пояснение.</p>
        </details>

        <h2 id="s13"><span class="sec">§13</span>Шпаргалка по главе</h2>
        <div class="cheat">
          <div><b>Программы</b><span><code>ollama pull qwen2.5:3b</code></span><span><code>npx n8n</code> → <code>localhost:5678</code></span><span>Node.js 20.19–24.x</span></div>
          <div><b>Сценарий</b><span>Webhook: POST, path <code>agent</code></span><span>Basic LLM Chain + Ollama Chat Model</span><span>Send Email по SMTP</span></div>
          <div><b>Отправка</b><span><code>python3 brain.py адрес</code></span><span>тест: <code>/webhook-test/agent</code></span><span>боевой: <code>/webhook/agent</code></span></div>
          <div><b>Выражения</b><span><code>{{ $json.body }}</code></span><span><code>{{ $('Webhook').item.json.body }}</code></span></div>
          <div><b>Проверка</b><span>вкладка Executions</span><span>ответ модели сверять с JSON</span></div>
        </div>

        <h3>Итог главы</h3>
        <p>Сообщение агента доставляется по цепочке из трёх узлов n8n. <code>brain.py</code> отправляет JSON запросом POST на вебхук модулем <code>urllib.request</code>. Узел Webhook принимает его, Basic LLM Chain с моделью <code>qwen2.5:3b</code> в Ollama пишет пояснение, Send an Email отправляет письмо с пояснением и исходным сообщением. Пока сценарий собирается, используется тестовый адрес и кнопки в редакторе. После публикации работает боевой адрес, а каждый запуск записывается во вкладку Executions. Модель работает на своём компьютере, но ошибается в смысле чисел, поэтому её ответ отправляется вместе с данными агента.</p>

        <div class="sources">
          <b>Откуда взяты факты</b>
          <ol>
            <li>Кадры и ответы: n8n 2.45.4, Ollama 0.40.12, Mailpit, Chromium; <code>brain.py</code> запущен на macOS 26.1 с Python 3.12. На стенде n8n, Ollama и Mailpit работали в Docker с общей сетью, поэтому адреса в кадрах те же, что при установке на компьютер. Модель <code>qwen2.5:3b</code> на стенде импортирована из файла GGUF Qwen2.5-3B-Instruct Q4_K_M: загрузка из библиотеки Ollama в сети стенда не проходила.</li>
            <li>Установка n8n через npm и npx, требования к версии Node.js — <a href="https://docs.n8n.io/hosting/installation/npm/">документация n8n</a>.</li>
            <li>Узлы <a href="https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/">Webhook</a>, <a href="https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.chainllm/">Basic LLM Chain</a>, <a href="https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatollama/">Ollama Chat Model</a>, <a href="https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.sendemail/">Send Email</a> — документация n8n.</li>
            <li>Установка Ollama и модель qwen2.5 — <a href="https://ollama.com/download">ollama.com</a>, <a href="https://ollama.com/library/qwen2.5">ollama.com/library/qwen2.5</a>.</li>
            <li><code>urllib.request</code> — <a href="https://docs.python.org/3/library/urllib.request.html">документация Python</a>; Mailpit — <a href="https://mailpit.axllent.org">mailpit.axllent.org</a>.</li>
          </ol>
        </div>

        <div class="pager">
          <a href="../07-c-i-python-vmeste/index.html">← 1.2 C и Python вместе</a>
          <a href="../../index.html">Оглавление</a>
        </div>

        <div class="colophon">
          <span>Глава 1.3 · n8n и Ollama: первая автоматизация · Справочник по системному программированию</span>
          <span class="author-line">Автор: Макаров Максим Николаевич</span>
        </div>
''')

CONTENTS = [('s1', 'Задача главы'), ('s2', 'Шаг 1. Установить Ollama и скачать модель'), ('s3', 'Шаг 2. Запустить n8n'),
            ('s4', 'Шаг 3. Принять сообщение: узел Webhook'), ('s5', 'Шаг 4. Отправить сообщение из brain.py'),
            ('s6', 'Шаг 5. Добавить пояснение модели'), ('s7', 'Шаг 6. Отправить письмо'), ('s8', 'Шаг 7. Опубликовать сценарий'),
            ('s9', 'Шаг 8. Сохранить работу в репозитории'), ('s10', 'Справка: адреса, узлы, выражения'),
            ('s11', 'Частые вопросы'), ('s12', 'Проверьте себя'), ('s13', 'Шпаргалка по главе')]
TOC = '\n'.join(f'            <li><a href="#{a}">{t}</a></li>' for a, t in CONTENTS)

PAGE = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#F0EEE8">
  <title>1.3 n8n и Ollama: первая автоматизация · Справочник по системному программированию</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,600;0,7..72,700;1,7..72,400&family=Pixelify+Sans:wght@500;600;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css">
</head>
<body>
  <div class="book">
    <div class="book__body">
      <div class="spine"><span>Модуль 1 · Рабочее место: C, Python и ИИ</span></div>

      <main class="leaf">
        <div class="running">
          <p class="eyebrow"><a href="../../index.html" style="text-decoration:none;color:inherit">Справочник по системному программированию</a> · модуль 1 · рабочее место</p>
          <p class="running__folio">1.3</p>
        </div>

        <header class="chapter-head">
          <span class="chapter-num">1.3</span>
          <h1>n8n и Ollama:<br>первая автоматизация</h1>
          <p class="lead">В главе сообщение агента <code>agent_started</code> из главы 1.2 доставляется администратору письмом с пояснением модели ИИ. Устанавливаются модель в Ollama и сервис автоматизации n8n, в n8n собирается сценарий из трёх узлов: вебхук принимает сообщение, модель пишет пояснение, узел почты отправляет письмо. <code>brain.py</code> получает функцию отправки. В конце сценарий публикуется и работает без редактора, а ответ модели проверяется по данным агента.</p>
        </header>

        <dl class="passport">
          <div><dt>Категория</dt><dd>Автоматизация и ИИ</dd></div>
          <div><dt>Уровень</dt><dd>Начальный</dd></div>
          <div><dt>Что получится</dt><dd>Письмо с пояснением модели после запуска <code>brain.py</code></dd></div>
          <div><dt>Сколько занимает</dt><dd>Пара 3, около пятидесяти минут; модель скачивается заранее</dd></div>
        </dl>

        <nav class="contents">
          <b>Порядок действий</b>
          <ol>
{TOC}
          </ol>
        </nav>
{''.join(S)}
      </main>
    </div>
  </div>
  <script src="../../book.js"></script>
</body>
</html>
'''

if __name__ == '__main__':
    OUT.write_text(PAGE)
    print('ok', OUT, len(PAGE))
