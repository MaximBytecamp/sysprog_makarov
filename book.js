/* Справочник по системному программированию — мелкая механика страницы (из справочника по Angular и React).
   1. Кадр открывается во весь экран по клику.
   2. Переключатель фреймворка: React или Angular.
   3. Кнопка «копировать» у блоков кода.
   4. Подсветка шага цикла при наведении. */
(() => {
  /* ---- Увеличение кадра ---------------------------------------- */
  const shots = [...document.querySelectorAll('.shot img')];
  if (shots.length) {
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('aria-hidden', 'true');
    box.innerHTML = '<figure><img alt=""><figcaption></figcaption></figure>'
      + '<p class="lightbox__hint">клик или Esc — закрыть</p>';
    document.body.appendChild(box);

    const image = box.querySelector('img');
    const caption = box.querySelector('figcaption');

    const open = source => {
      image.src = source.currentSrc || source.src;
      image.alt = source.alt || '';
      const own = source.closest('figure')?.querySelector('figcaption');
      caption.textContent = own ? own.textContent.trim() : image.alt;
      caption.hidden = !caption.textContent;
      box.classList.add('is-open');
      box.setAttribute('aria-hidden', 'false');
    };
    const close = () => {
      box.classList.remove('is-open');
      box.setAttribute('aria-hidden', 'true');
      image.removeAttribute('src');
    };

    shots.forEach(source => {
      source.tabIndex = 0;
      source.addEventListener('click', () => open(source));
      source.addEventListener('keydown', event => {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        event.preventDefault();
        open(source);
      });
    });
    box.addEventListener('click', close);
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && box.classList.contains('is-open')) close();
    });
  }

  /* ---- Переключатель фреймворка -------------------------------- */
  /* Выбор общий для всей книги. Блоки помечены data-fw, видимостью управляет CSS. */
  const KEY = 'ar-book-fw';
  const ITEMS = [['react', 'React'], ['angular', 'Angular']];
  const running = document.querySelector('.running');

  if (document.querySelector('.book [data-fw]') && running) {
    const read = () => {
      try {
        const saved = localStorage.getItem(KEY);
        return ITEMS.some(([id]) => id === saved) ? saved : 'react';
      } catch (_) {
        return 'react';
      }
    };

    const bar = document.createElement('div');
    bar.className = 'langbar';
    bar.innerHTML = '<span class="langbar__label">фреймворк</span>';
    const buttons = ITEMS.map(([id, title]) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = title;
      button.dataset.value = id;
      bar.appendChild(button);
      return button;
    });

    const apply = (value, save) => {
      document.documentElement.setAttribute('data-fw', value);
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.value === value)));
      if (save) {
        try { localStorage.setItem(KEY, value); } catch (_) { /* приватный режим */ }
      }
    };

    buttons.forEach(button => button.addEventListener('click', () => apply(button.dataset.value, true)));
    running.insertBefore(bar, running.querySelector('.running__folio'));
    apply(read(), false);

    window.addEventListener('storage', event => {
      if (event.key === KEY && event.newValue) apply(read(), false);
    });
  }

  /* ---- Переключатель операционной системы ---------------------- */
  /* Блоки помечены data-os="win|mac|linux" (можно несколько через пробел).
     Пока читатель не выбрал систему кнопкой, она определяется по браузеру. */
  const OS_KEY = 'sp-book-os';
  const OS_ITEMS = [['win', 'Windows'], ['mac', 'macOS'], ['linux', 'Linux']];
  const detectOs = () => {
    const p = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || '';
    if (/win/i.test(p)) return 'win';
    if (/mac|iphone|ipad/i.test(p)) return 'mac';
    return 'linux';
  };
  if (document.querySelector('.book [data-os]') && running) {
    const readOs = () => {
      try {
        const saved = localStorage.getItem(OS_KEY);
        return OS_ITEMS.some(([id]) => id === saved) ? saved : detectOs();
      } catch (_) {
        return detectOs();
      }
    };
    const bar = document.createElement('div');
    bar.className = 'langbar';
    bar.innerHTML = '<span class="langbar__label">система</span>';
    const buttons = OS_ITEMS.map(([id, title]) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = title;
      button.dataset.value = id;
      bar.appendChild(button);
      return button;
    });
    const applyOs = (value, save) => {
      document.documentElement.setAttribute('data-os', value);
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.value === value)));
      // Схемы глав перерисовываются под выбранную систему.
      document.dispatchEvent(new CustomEvent('book:os', { detail: value }));
      if (save) {
        try { localStorage.setItem(OS_KEY, value); } catch (_) { /* приватный режим */ }
      }
    };
    buttons.forEach(button => button.addEventListener('click', () => applyOs(button.dataset.value, true)));
    running.insertBefore(bar, running.querySelector('.running__folio'));
    applyOs(readOs(), false);
  }

  /* ---- Копирование кода ---------------------------------------- */
  document.querySelectorAll('figure.code > figcaption').forEach(caption => {
    const block = caption.parentElement.querySelector('pre');
    if (!block || caption.parentElement.classList.contains('code--out')) return;
    // Блок для чтения (data-read): код показан для разбора, вставлять его не нужно.
    if (caption.parentElement.hasAttribute('data-read')) {
      const mark = document.createElement('span');
      mark.className = 'read-mark';
      mark.textContent = 'для чтения';
      caption.appendChild(mark);
      return;
    }

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy';
    button.textContent = 'копировать';

    let timer = 0;
    const report = (text, state) => {
      button.textContent = text;
      button.dataset.state = state;
      clearTimeout(timer);
      timer = setTimeout(() => {
        button.textContent = 'копировать';
        delete button.dataset.state;
      }, 2000);
    };

    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(block.textContent);
        report('скопировано', 'done');
      } catch (_) {
        const range = document.createRange();
        range.selectNodeContents(block);
        const selection = getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        report('выделено — Ctrl+C', 'fail');
      }
    });
    caption.appendChild(button);
  });

  /* ---- Пошаговый разбор кода ----------------------------------- */
  /* У шага атрибут data-lines="3-5,9" — строки кода, которые он объясняет.
     Код делится на строки с номерами; виден один шаг, остальные — по кнопкам. */
  document.querySelectorAll('.trace').forEach(trace => {
    const code = trace.querySelector('.trace__code');
    const steps = [...trace.querySelectorAll('.trace__steps > li')];
    const nav = trace.querySelector('.trace__nav');
    if (!code || !steps.length || !nav) return;

    const lines = code.innerHTML.replace(/\n$/, '').split('\n');
    code.innerHTML = lines.map((line, i) => `<span class="ln" data-n="${i + 1}">${line || ' '}</span>`).join('');
    const rows = [...code.querySelectorAll('.ln')];

    const parse = value => (value || '').split(',').flatMap(part => {
      const [a, b] = part.split('-').map(Number);
      if (!a) return [];
      return Array.from({ length: (b || a) - a + 1 }, (_, i) => a + i);
    });

    steps.forEach((step, i) => step.querySelector(':scope > b')?.setAttribute('data-step', `${i + 1} из ${steps.length}`));
    nav.innerHTML = '<button type="button" data-go="-1">← Назад</button><span class="trace__dots"></span>'
      + '<button type="button" data-go="1">Дальше →</button>';
    const dots = nav.querySelector('.trace__dots');
    const back = nav.querySelector('[data-go="-1"]');
    const next = nav.querySelector('[data-go="1"]');
    steps.forEach((_, i) => {
      const dot = document.createElement('i');
      dot.title = `Шаг ${i + 1}`;
      dot.addEventListener('click', () => show(i));
      dots.appendChild(dot);
    });

    let current = 0;
    const show = index => {
      current = Math.max(0, Math.min(steps.length - 1, index));
      steps.forEach((step, i) => step.classList.toggle('is-on', i === current));
      [...dots.children].forEach((dot, i) => dot.classList.toggle('is-on', i === current));
      const lit = parse(steps[current].dataset.lines);
      rows.forEach((row, i) => row.classList.toggle('is-lit', lit.includes(i + 1)));
      back.disabled = current === 0;
      next.disabled = current === steps.length - 1;
      // Подсвеченные строки прокручиваются в видимую часть блока кода, страница стоит на месте.
      const first = rows[lit[0] - 1];
      if (first && code.scrollHeight > code.clientHeight) {
        code.scrollTo({ top: first.offsetTop - code.clientHeight / 3, behavior: 'smooth' });
      }
    };
    back.addEventListener('click', () => show(current - 1));
    next.addEventListener('click', () => show(current + 1));
    trace.tabIndex = 0;
    trace.addEventListener('keydown', event => {
      if (event.target.closest('button') && event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      if (event.key === 'ArrowRight') { event.preventDefault(); show(current + 1); }
      if (event.key === 'ArrowLeft') { event.preventDefault(); show(current - 1); }
    });
    trace.classList.add('is-live');
    show(0);
  });

  /* ---- Подсветка шага цикла ------------------------------------ */
  document.querySelectorAll('.cycle').forEach(cycle => {
    const steps = [...cycle.children];
    steps.forEach(step => step.addEventListener('mouseenter', () => {
      steps.forEach(other => other.classList.toggle('is-lit', other === step));
    }));
    cycle.addEventListener('mouseleave', () => steps.forEach(step => step.classList.remove('is-lit')));
  });
})();
