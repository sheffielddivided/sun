import './styles/main.css';
import { registry } from './charts/registry';
import { mountChart } from './lib/chart';

// ---- tema (lagres kun lokalt i nettleseren; ingen cookies, ingen sporing) ----
const root = document.documentElement;
function currentTheme(): 'light' | 'dark' {
  const t = root.getAttribute('data-theme');
  if (t === 'light' || t === 'dark') return t;
  return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}
document.querySelector<HTMLButtonElement>('.theme-toggle')?.addEventListener('click', () => {
  const next = currentTheme() === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', next);
  try {
    localStorage.setItem('theme', next);
  } catch {
    /* lagring kan være blokkert; valget gjelder da bare for denne økten */
  }
  document.dispatchEvent(new Event('themechange'));
});
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  if (!root.getAttribute('data-theme')) document.dispatchEvent(new Event('themechange'));
});

// ---- mobilmeny ----
const toggle = document.querySelector<HTMLButtonElement>('.nav-toggle');
const nav = document.getElementById('hovednav');
toggle?.addEventListener('click', () => {
  const open = nav?.classList.toggle('open') ?? false;
  toggle.setAttribute('aria-expanded', String(open));
});

// ---- grafer lastes når de nærmer seg skjermen ----
const figures = document.querySelectorAll<HTMLElement>('[data-chart]');
const mounted = new WeakSet<Element>();
function start(el: HTMLElement) {
  if (mounted.has(el)) return;
  mounted.add(el);
  const factory = registry[el.dataset.chart ?? ''];
  if (!factory) {
    el.textContent = `Ukjent graf: ${el.dataset.chart}`;
    el.dataset.error = '1';
    return;
  }
  void mountChart(el, factory);
}
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries)
        if (e.isIntersecting) {
          io.unobserve(e.target);
          start(e.target as HTMLElement);
        }
    },
    { rootMargin: '500px 0px' },
  );
  figures.forEach((f) => io.observe(f));
} else figures.forEach(start);

// ---- tidslinje og dashbord ----
const tl = document.querySelector<HTMLElement>('[data-timeline]');
if (tl) void import('./timeline').then((m) => m.mountTimeline(tl));
const dash = document.querySelector<HTMLElement>('[data-dashboard]');
if (dash) void import('./charts/home').then((m) => m.initDashboard(dash)).catch((e) => console.error('dashbord', e));
