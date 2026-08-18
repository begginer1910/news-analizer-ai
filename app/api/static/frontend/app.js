const API_BASE = '';

async function apiFetch(path, options = {}) {
  const res = await fetch(API_BASE + path, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res;
}

async function apiGet(path) {
  const res = await apiFetch(path);
  return res.json();
}

async function apiPost(path, body) {
  const res = await apiFetch(path, {
    method: 'POST',
    body: JSON.stringify(body),
  });
  return res.json();
}

async function apiPut(path, body) {
  const res = await apiFetch(path, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
  return res.json();
}

function showInlineMsg(container, msg, type) {
  container.className = 'inline-msg inline-msg--' + type;
  container.textContent = msg;
  container.style.display = 'block';
}

function clearInlineMsg(container) {
  container.style.display = 'none';
  container.textContent = '';
  container.className = 'inline-msg';
}

function setLoading(btn, loading) {
  if (loading) {
    btn.disabled = true;
    btn.dataset.origText = btn.textContent;
    btn.textContent = 'Loading...';
  } else {
    btn.disabled = false;
    btn.textContent = btn.dataset.origText || btn.textContent;
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleString();
}

function sentimentLabel(s) {
  if (s === 1) return 'Positive';
  if (s === -1) return 'Negative';
  return 'Neutral';
}

function sentimentClass(s) {
  if (s === 1) return 'sentiment--positive';
  if (s === -1) return 'sentiment--negative';
  return 'sentiment--neutral';
}

function buildNavBar(activePage) {
  const pages = [
    { href: '/frontend/index.html', label: 'Home', key: 'index' },
    { href: '/frontend/news.html', label: 'Fetch News', key: 'news' },
    { href: '/frontend/scheduler.html', label: 'Scheduler', key: 'scheduler' },
    { href: '/frontend/export.html', label: 'Export', key: 'export' },
  ];
  const nav = document.createElement('nav');
  nav.className = 'navbar';
  const brand = document.createElement('a');
  brand.href = '/frontend/index.html';
  brand.className = 'navbar__brand';
  brand.textContent = 'News Analyzer';
  nav.appendChild(brand);
  const links = document.createElement('div');
  links.className = 'navbar__links';
  pages.forEach(p => {
    const a = document.createElement('a');
    a.href = p.href;
    a.className = 'navbar__link' + (p.key === activePage ? ' navbar__link--active' : '');
    a.textContent = p.label;
    links.appendChild(a);
  });
  nav.appendChild(links);
  return nav;
}

function createCombobox(containerEl, opts) {
  const wrapper = document.createElement('div');
  wrapper.className = 'combobox';
  const input = document.createElement('input');
  input.type = 'text';
  input.className = 'combobox__input';
  input.placeholder = opts.placeholder || '';
  input.autocomplete = 'off';
  input.setAttribute('role', 'combobox');
  input.setAttribute('aria-expanded', 'false');
  input.setAttribute('aria-autocomplete', 'list');

  const arrow = document.createElement('span');
  arrow.className = 'combobox__arrow';
  arrow.setAttribute('aria-hidden', 'true');

  const list = document.createElement('div');
  list.className = 'combobox__list';
  list.setAttribute('role', 'listbox');

  wrapper.appendChild(input);
  wrapper.appendChild(arrow);
  wrapper.appendChild(list);
  containerEl.appendChild(wrapper);

  let items = [];
  let filtered = [];
  let activeIdx = -1;
  let selectedValue = null;
  let selectedLabel = '';

  function setItems(newItems) {
    items = newItems;
    filtered = items.slice();
  }

  function renderList() {
    list.innerHTML = '';
    activeIdx = -1;
    if (filtered.length === 0) {
      list.style.display = 'none';
      input.setAttribute('aria-expanded', 'false');
      return;
    }
    filtered.forEach((item, idx) => {
      const opt = document.createElement('div');
      opt.className = 'combobox__option';
      opt.setAttribute('role', 'option');
      opt.dataset.index = idx;
      opt.textContent = item.label;
      opt.addEventListener('mousedown', (e) => {
        e.preventDefault();
        selectItem(idx);
      });
      list.appendChild(opt);
    });
    list.style.display = 'block';
    input.setAttribute('aria-expanded', 'true');
  }

  function selectItem(idx) {
    if (idx < 0 || idx >= filtered.length) return;
    const item = filtered[idx];
    selectedValue = item.value;
    selectedLabel = item.label;
    input.value = item.label;
    list.style.display = 'none';
    input.setAttribute('aria-expanded', 'false');
    if (opts.onChange) opts.onChange(item.value);
  }

  function highlightItem(idx) {
    const options = list.querySelectorAll('.combobox__option');
    options.forEach((o, i) => {
      o.classList.toggle('combobox__option--active', i === idx);
    });
  }

  input.addEventListener('input', () => {
    const q = input.value.toLowerCase().trim();
    if (!q) {
      filtered = items.slice();
      selectedValue = null;
      selectedLabel = '';
    } else {
      filtered = items.filter(item =>
        item.label.toLowerCase().includes(q) || item.searchKey.toLowerCase().includes(q)
      );
    }
    renderList();
  });

  input.addEventListener('click', () => {
    if (list.style.display === 'block') {
      list.style.display = 'none';
      input.setAttribute('aria-expanded', 'false');
    } else {
      const q = input.value.toLowerCase().trim();
      if (!q) {
        filtered = items.slice();
      } else {
        filtered = items.filter(item =>
          item.label.toLowerCase().includes(q) || item.searchKey.toLowerCase().includes(q)
        );
      }
      renderList();
    }
  });

  input.addEventListener('blur', () => {
    setTimeout(() => {
      list.style.display = 'none';
      input.setAttribute('aria-expanded', 'false');
    }, 150);
  });

  arrow.addEventListener('mousedown', (e) => {
    e.preventDefault();
    if (list.style.display === 'block') {
      list.style.display = 'none';
      input.setAttribute('aria-expanded', 'false');
    } else {
      input.focus();
      filtered = items.slice();
      renderList();
    }
  });

  input.addEventListener('keydown', (e) => {
    if (list.style.display === 'none' || filtered.length === 0) {
      if (e.key === 'Escape') {
        input.value = '';
        selectedValue = null;
        selectedLabel = '';
        if (opts.onChange) opts.onChange(null);
      }
      return;
    }
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        activeIdx = Math.min(activeIdx + 1, filtered.length - 1);
        highlightItem(activeIdx);
        break;
      case 'ArrowUp':
        e.preventDefault();
        activeIdx = Math.max(activeIdx - 1, 0);
        highlightItem(activeIdx);
        break;
      case 'Enter':
        e.preventDefault();
        selectItem(activeIdx);
        break;
      case 'Escape':
        list.style.display = 'none';
        input.setAttribute('aria-expanded', 'false');
        activeIdx = -1;
        break;
    }
  });

  function clear() {
    input.value = '';
    selectedValue = null;
    selectedLabel = '';
    if (opts.onChange) opts.onChange(null);
  }

  function setValue(val) {
    const item = items.find(i => i.value === val);
    if (item) {
      input.value = item.label;
      selectedValue = item.value;
      selectedLabel = item.label;
    }
  }

  return { setItems, getValue: () => selectedValue, clear, setValue, input };
}

function initNav(activePage) {
  const nav = buildNavBar(activePage);
  document.body.insertBefore(nav, document.body.firstChild);
}
