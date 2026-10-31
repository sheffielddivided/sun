import { ui } from './lib/ui';

interface Ev {
  sort: number;
  label: string;
  title: string;
  text: string;
  category: string;
  source?: string;
}
const files = import.meta.glob('../content/*/timeline.json', { eager: true, import: 'default' }) as Record<string, any>;
const lang = (import.meta.env.VITE_LANG as string | undefined) ?? 'nb';
const data = files[Object.keys(files).find((k) => k.includes(`/${lang}/`)) ?? Object.keys(files)[0]] as {
  categories: Record<string, { label: string; color: string }>;
  events: Ev[];
};

export function mountTimeline(host: HTMLElement): void {
  host.textContent = '';
  host.setAttribute('aria-busy', 'false');
  const cats = data.categories;
  const bar = document.createElement('div');
  bar.className = 'tl-filters';
  bar.setAttribute('role', 'group');
  bar.setAttribute('aria-label', ui.timeline.filter);
  let active = 'all';
  const mkBtn = (key: string, label: string) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'btn';
    b.textContent = label;
    b.setAttribute('aria-pressed', String(key === active));
    b.dataset.cat = key;
    b.addEventListener('click', () => {
      active = key;
      bar.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      apply();
    });
    return b;
  };
  bar.append(mkBtn('all', ui.timeline.all), ...Object.entries(cats).map(([k, v]) => mkBtn(k, v.label)));
  const hint = document.createElement('p');
  hint.className = 'chart-sub';
  hint.textContent = ui.timeline.hint;
  const list = document.createElement('ol');
  list.className = 'tl-track';
  list.setAttribute('aria-label', ui.timeline.label);
  const items: { li: HTMLLIElement; ev: Ev }[] = [];
  [...data.events]
    .sort((a, b) => a.sort - b.sort)
    .forEach((ev, i) => {
      const li = document.createElement('li');
      li.className = 'tl-item';
      li.style.setProperty('--tl-color', cats[ev.category]?.color ?? 'var(--accent)');
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'tl-btn';
      btn.setAttribute('aria-expanded', 'false');
      btn.setAttribute('aria-controls', `tl-body-${i}`);
      const y = document.createElement('span');
      y.className = 'tl-year';
      y.textContent = ev.label;
      const t = document.createElement('span');
      const strong = document.createElement('strong');
      strong.textContent = ev.title;
      const cat = document.createElement('span');
      cat.className = 'tl-cat';
      cat.textContent = ` · ${cats[ev.category]?.label ?? ev.category}`;
      t.append(strong, cat);
      btn.append(y, t);
      const body = document.createElement('div');
      body.className = 'tl-body';
      body.id = `tl-body-${i}`;
      body.hidden = true;
      const p = document.createElement('p');
      p.textContent = ev.text;
      body.append(p);
      if (ev.source) {
        const s = document.createElement('p');
        s.className = 'tl-cat';
        s.textContent = `Kilde: ${ev.source}`;
        body.append(s);
      }
      btn.addEventListener('click', () => {
        const open = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', String(!open));
        body.hidden = open;
        li.dataset.open = String(!open);
      });
      li.append(btn, body);
      list.append(li);
      items.push({ li, ev });
    });
  function apply() {
    for (const { li, ev } of items) li.hidden = active !== 'all' && ev.category !== active;
  }
  host.append(bar, hint, list);
}
