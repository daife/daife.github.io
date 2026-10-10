'use strict';
(() => {
  const explorer = document.getElementById('explorer');
  const input = document.getElementById('project-search');
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const cards = [...document.querySelectorAll('[data-project]')];
  const sections = [...document.querySelectorAll('[data-section]')];
  const count = document.getElementById('result-count');
  let selected = 'all';
  function apply() {
    const terms = input.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const match = (selected === 'all' || card.dataset.category === selected) &&
        terms.every(term => card.dataset.search.includes(term));
      card.hidden = !match;
      if (match) visible += 1;
    }
    for (const section of sections) {
      const matches = [...section.querySelectorAll('[data-project]')].filter(card => !card.hidden).length;
      section.hidden = matches === 0;
      section.querySelector('.section-count').textContent = String(matches).padStart(2, '0');
    }
    for (const button of buttons) {
      const active = button.dataset.filter === selected;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    }
    count.textContent = selected === 'all' && !terms.length ? `显示全部 ${cards.length} 个项目组` : `找到 ${visible} / ${cards.length} 个项目组`;
    document.getElementById('empty-state').hidden = visible !== 0;
  }
  function reset() { selected = 'all'; input.value = ''; apply(); }
  buttons.forEach(button => button.addEventListener('click', () => { selected = button.dataset.filter; apply(); }));
  input.addEventListener('input', apply);
  document.getElementById('reset-filters').addEventListener('click', reset);
  document.getElementById('empty-reset').addEventListener('click', () => { reset(); input.focus(); });
  function followProjectLink() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const card = document.getElementById(id);
    if (!card || !card.matches('[data-project]')) return;
    reset();
    const details = card.querySelector('details');
    if (details) details.open = true;
    requestAnimationFrame(() => card.scrollIntoView({ block: 'start' }));
  }
  window.addEventListener('hashchange', followProjectLink);
  explorer.hidden = false;
  apply();
  followProjectLink();
})();
