// Genererer HTML-sidene (én per Markdown-fil i content/<lang>/) med felles layout.
// - Tall som avhenger av data hentes fra public/data/*.json ved bygging ({{sti|format}}); manglende sti → byggefeil.
// - Direktiver: :::chart, :::svg, :::evidence, :::box, :::sources, :::topics, :::timeline, :::dashboard
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { marked } from 'marked';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LANG = process.env.SITE_LANG || 'nb';
const BASE = (process.env.VITE_BASE || '/sun/').replace(/\/?$/, '/');
const CONTENT = path.join(ROOT, 'content', LANG);
const DATA = path.join(ROOT, 'public', 'data');

const ui = JSON.parse(fs.readFileSync(path.join(CONTENT, 'ui.json'), 'utf8'));
const readJSON = (name) => JSON.parse(fs.readFileSync(path.join(DATA, name), 'utf8'));
const manifest = readJSON('manifest.json');

// ---------- verdibinding ----------
const cache = new Map();
function fileFor(stem) {
  const map = { manifest: 'manifest.json', cycles: 'cycles.json' };
  return map[stem] ?? `analysis_${stem}.json`;
}
function lookup(pathStr) {
  const [stem, ...rest] = pathStr.split('.');
  const file = fileFor(stem);
  if (!cache.has(file)) cache.set(file, readJSON(file));
  let cur = cache.get(file);
  for (const seg of rest) {
    if (Array.isArray(cur)) {
      cur = /^\d+$/.test(seg) ? cur[Number(seg)] : cur.find((e) => e && e.id === seg);
    } else if (cur && typeof cur === 'object') cur = cur[seg];
    else cur = undefined;
    if (cur === undefined) throw new Error(`Verdibinding feilet: {{${pathStr}}} – «${seg}» finnes ikke i ${file}`);
  }
  if (cur === null || cur === undefined) throw new Error(`Verdibinding gir null: {{${pathStr}}}`);
  return cur;
}
const MONTHS = [
  'januar',
  'februar',
  'mars',
  'april',
  'mai',
  'juni',
  'juli',
  'august',
  'september',
  'oktober',
  'november',
  'desember',
];
function fmt(v, f = 'raw') {
  const nf = (d, signed = false) =>
    Number(v).toLocaleString('nb-NO', {
      minimumFractionDigits: d,
      maximumFractionDigits: d,
      signDisplay: signed ? 'exceptZero' : 'auto',
    });
  let m;
  if ((m = /^n(\d)$/.exec(f))) return nf(Number(m[1]));
  if ((m = /^s(\d)$/.exec(f))) return nf(Number(m[1]), true);
  if ((m = /^pct(\d)$/.exec(f)))
    return (
      Number(v * 100).toLocaleString('nb-NO', { minimumFractionDigits: +m[1], maximumFractionDigits: +m[1] }) + ' %'
    );
  switch (f) {
    case 'p': {
      const x = Number(v);
      if (x < 0.001) return '< 0,001';
      if (x < 0.01) return x.toLocaleString('nb-NO', { minimumFractionDigits: 3, maximumFractionDigits: 3 });
      return x.toLocaleString('nb-NO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    case 'year':
      return String(Math.round(Number(v)));
    case 'int':
      return Math.round(Number(v)).toLocaleString('nb-NO');
    case 'date': {
      const d = new Date(String(v).slice(0, 10) + 'T00:00:00Z');
      return `${d.getUTCDate()}. ${MONTHS[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
    }
    case 'ym': {
      const [y, mo] = String(v).split('-');
      return `${MONTHS[Number(mo) - 1]} ${y}`;
    }
    case 'my': {
      const t = Number(v);
      const y = Math.floor(t + 1e-9);
      const mo = Math.min(11, Math.floor((t - y) * 12 + 1e-6));
      return `${MONTHS[mo]} ${y}`;
    }
    default:
      return String(v);
  }
}
function bindValues(md) {
  return md.replace(/\{\{\s*([^}|]+?)\s*(?:\|\s*([a-z0-9]+))?\s*\}\}/g, (_, p, f) => {
    const val = lookup(p);
    return `<span class="bind" data-bind="${p}">${fmt(val, f)}</span>`;
  });
}

// ---------- direktiver ----------
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const abs = (href) => (href.startsWith('/') && !href.startsWith('//') ? BASE + href.slice(1) : href);

const EVIDENCE = {
  a: {
    cls: 'a',
    icon: '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M7 12.5l3.2 3.2L17 8.8" fill="none" stroke="var(--evidence-icon-fg)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
  b: {
    cls: 'b',
    icon: '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg>',
  },
  c: {
    cls: 'c',
    icon: '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M8.2 8.2l7.6 7.6M15.8 8.2l-7.6 7.6" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>',
  },
};
function evidenceBadge(level, withText = true) {
  const e = EVIDENCE[level];
  return `<span class="badge badge-${e.cls}">${e.icon}${withText ? `<span>${esc(ui.evidence[level].label)}</span>` : ''}</span>`;
}

function renderSources() {
  const items = Object.values(manifest.sources);
  const order = { daily: 0, monthly: 1, yearly: 2 };
  items.sort((a, b) => order[a.group] - order[b.group] || a.name.localeCompare(b.name, 'nb'));
  return (
    `<div class="sources">` +
    items
      .map((s) => {
        const status =
          s.status === 'ok'
            ? ui.sources.status_ok
            : s.status === 'stale'
              ? ui.sources.status_stale
              : ui.sources.status_failed;
        const urls = s.urls.map((u) => `<li><a href="${esc(u)}" rel="noopener">${esc(u)}</a></li>`).join('');
        return `<article class="source-card" id="kilde-${esc(s.id)}">
<h3>${esc(s.name)}</h3>
<p class="source-meta"><span class="pill pill-${esc(s.status)}">${esc(status)}</span> ${esc(ui.sources.group[s.group])} · ${esc(ui.sources.last_fetched)}: ${s.fetched_at ? esc(fmt(s.fetched_at, 'date')) : '–'} · ${esc(ui.sources.last_point)}: ${esc(s.last_point ?? '–')}</p>
<dl>
<dt>${esc(ui.sources.provider)}</dt><dd><a href="${esc(s.homepage)}" rel="noopener">${esc(s.provider)}</a></dd>
<dt>${esc(ui.sources.urls)}</dt><dd><ul class="plain">${urls}</ul></dd>
<dt>${esc(ui.sources.license)}</dt><dd>${esc(s.license)}</dd>
<dt>${esc(ui.sources.citation)}</dt><dd>${esc(s.citation)}</dd>
<dt>${esc(ui.sources.frequency)}</dt><dd>${esc(s.frequency)}</dd>
<dt>${esc(ui.sources.caveats)}</dt><dd>${esc(s.caveats)}</dd>
${s.fallback_note ? `<dt>${esc(ui.sources.fallback)}</dt><dd>${esc(s.fallback_note)}</dd>` : ''}
${s.error ? `<dt>${esc(ui.sources.error)}</dt><dd>${esc(s.error)}</dd>` : ''}
</dl></article>`;
      })
      .join('\n') +
    `</div>`
  );
}

function renderTopics(pages) {
  const subs = pages
    .filter((p) => p.meta.parent === 'sol-og-jord')
    .sort((a, b) => Number(a.meta.order) - Number(b.meta.order));
  return (
    `<ul class="topics">` +
    subs
      .map(
        (p) => `<li class="topic-card"><a href="${abs(p.meta.route)}"><h3>${esc(p.meta.title)}</h3></a>
<p>${esc(p.meta.description)}</p><p>${evidenceBadge(p.meta.evidence)}</p></li>`,
      )
      .join('') +
    `</ul>`
  );
}

function evalCondition(expr) {
  const m = /^([\w.]+)\s*(<=|>=|<|>|==|!=)\s*(true|false|-?[\d.]+)$/.exec(expr.trim());
  if (!m) throw new Error(`Ugyldig betingelse i :::when ${expr}`);
  const v = lookup(m[1]);
  const rhs = m[3] === 'true' ? true : m[3] === 'false' ? false : Number(m[3]);
  switch (m[2]) {
    case '<':
      return v < rhs;
    case '>':
      return v > rhs;
    case '<=':
      return v <= rhs;
    case '>=':
      return v >= rhs;
    case '==':
      return v === rhs;
    default:
      return v !== rhs;
  }
}

function preprocess(md, pages) {
  md = md.replace(/\[\[([abc])\]\]/g, (_, l) => evidenceBadge(l));
  const lines = md.split('\n');
  const out = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    let m;
    if ((m = /^:::when\s+(.+)$/.exec(line))) {
      const inner = [];
      let depth = 1;
      for (i++; i < lines.length; i++) {
        if (/^:::when\s/.test(lines[i])) depth++;
        if (lines[i] === ':::endwhen' && --depth === 0) break;
        inner.push(lines[i]);
      }
      if (evalCondition(m[1])) out.push(preprocess(inner.join('\n'), pages));
    } else if ((m = /^:::chart\s+([\w-]+)\s*$/.exec(line))) {
      out.push(
        `\n<figure class="chart" data-chart="${m[1]}" aria-busy="true"><p class="chart-loading">${esc(ui.chart.loading)}</p></figure>\n`,
      );
    } else if ((m = /^:::svg\s+([\w-]+)\s*\|\s*(.+)$/.exec(line))) {
      const svg = fs
        .readFileSync(path.join(ROOT, 'content', 'svg', `${m[1]}.svg`), 'utf8')
        .replace(/<\?xml[^>]*\?>/, '');
      out.push(`\n<figure class="illustration">${svg}<figcaption>${esc(m[2])}</figcaption></figure>\n`);
    } else if ((m = /^:::evidence\s+([abc])\s*(.*)$/.exec(line))) {
      const inner = [];
      for (i++; i < lines.length && lines[i] !== ':::'; i++) inner.push(lines[i]);
      const lvl = m[1];
      const title = m[2] || ui.evidence.box_title;
      out.push(
        `\n<aside class="evidence evidence-${lvl}" aria-labelledby="ev-${i}"><h2 id="ev-${i}" class="evidence-head">${evidenceBadge(lvl)}<span class="evidence-title">${esc(title)}</span></h2><p class="evidence-desc">${esc(ui.evidence[lvl].desc)}</p>\n\n${preprocess(inner.join('\n'), pages)}\n\n</aside>\n`,
      );
    } else if ((m = /^:::box\s*(.*)$/.exec(line))) {
      const inner = [];
      for (i++; i < lines.length && lines[i] !== ':::'; i++) inner.push(lines[i]);
      out.push(
        `\n<aside class="box">${m[1] ? `<h2 class="box-title">${esc(m[1])}</h2>` : ''}\n\n${preprocess(inner.join('\n'), pages)}\n\n</aside>\n`,
      );
    } else if (/^:::sources\s*$/.test(line)) {
      out.push('\n' + renderSources() + '\n');
    } else if (/^:::topics\s*$/.test(line)) {
      out.push('\n' + renderTopics(pages) + '\n');
    } else if (/^:::timeline\s*$/.test(line)) {
      out.push(
        `\n<div class="timeline-mount" data-timeline aria-busy="true"><p class="chart-loading">${esc(ui.chart.loading)}</p></div>\n`,
      );
    } else if (/^:::dashboard\s*$/.test(line)) {
      out.push('\n' + fs.readFileSync(path.join(CONTENT, 'dashboard.html'), 'utf8') + '\n');
    } else {
      out.push(line);
    }
  }
  return out.join('\n');
}

// ---------- markdown ----------
const slugs = new Map();
marked.use({
  gfm: true,
  renderer: {
    heading({ tokens, depth }) {
      const text = this.parser.parseInline(tokens);
      const plain = text.replace(/<[^>]+>/g, '');
      let slug = plain
        .toLowerCase()
        .replace(/[æ]/g, 'ae')
        .replace(/[ø]/g, 'o')
        .replace(/[å]/g, 'a')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '');
      const n = (slugs.get(slug) ?? 0) + 1;
      slugs.set(slug, n);
      if (n > 1) slug += `-${n}`;
      return `<h${depth} id="${slug}">${text}</h${depth}>\n`;
    },
    link({ href, title, tokens }) {
      const text = this.parser.parseInline(tokens);
      const external = /^https?:\/\//.test(href);
      return `<a href="${esc(abs(href))}"${title ? ` title="${esc(title)}"` : ''}${external ? ' rel="noopener"' : ''}>${text}</a>`;
    },
  },
});

function parseFrontMatter(src, file) {
  const m = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/.exec(src);
  if (!m) throw new Error(`Mangler front matter i ${file}`);
  const meta = {};
  for (const ln of m[1].split('\n')) {
    const k = /^(\w+):\s*(.*)$/.exec(ln);
    if (k) meta[k[1]] = k[2].replace(/^"(.*)"$/, '$1');
  }
  return { meta, body: m[2] };
}

// ---------- layout ----------
const themeInit = `try{var t=localStorage.getItem('theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t)}catch(e){}`;
function layout(page, pages) {
  const { meta, html } = page;
  const nav = ui.nav
    .map((n) => {
      const current = meta.nav === n.key ? ' aria-current="page"' : '';
      return `<li><a href="${abs(n.route)}"${current}>${esc(n.label)}</a></li>`;
    })
    .join('');
  const crumbs = [];
  if (meta.parent === 'sol-og-jord') {
    crumbs.push(`<a href="${abs('/sol-og-jord/')}">${esc(ui.nav.find((n) => n.key === 'sol-og-jord').label)}</a>`);
  }
  const sub =
    meta.parent === 'sol-og-jord'
      ? pages.filter((p) => p.meta.parent === 'sol-og-jord').sort((a, b) => Number(a.meta.order) - Number(b.meta.order))
      : [];
  const idx = sub.findIndex((p) => p.meta.route === meta.route);
  const pager =
    sub.length && idx >= 0
      ? `<nav class="pager" aria-label="${esc(ui.pager.label)}">${idx > 0 ? `<a rel="prev" href="${abs(sub[idx - 1].meta.route)}"><span>← ${esc(ui.pager.prev)}</span>${esc(sub[idx - 1].meta.title)}</a>` : '<span></span>'}${idx < sub.length - 1 ? `<a rel="next" href="${abs(sub[idx + 1].meta.route)}"><span>${esc(ui.pager.next)} →</span>${esc(sub[idx + 1].meta.title)}</a>` : '<span></span>'}</nav>`
      : '';
  const badge = meta.evidence
    ? `<p class="page-badge">${evidenceBadge(meta.evidence)} <span class="muted">${esc(ui.evidence[meta.evidence].desc)}</span></p>`
    : '';
  const generated = manifest.generated_at ? fmt(manifest.generated_at, 'date') : '–';
  return `<!doctype html>
<html lang="${ui.lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(meta.title)} – ${esc(ui.site.name)}</title>
<meta name="description" content="${esc(meta.description || ui.site.description)}">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="${BASE}favicon.svg" type="image/svg+xml">
<script>${themeInit}</script>
<script type="module" src="/src/main.ts"></script>
</head>
<body data-page="${esc(meta.slug || 'home')}">
<a class="skip" href="#innhold">${esc(ui.a11y.skip)}</a>
<header class="site-header">
<div class="wrap header-row">
<a class="brand" href="${abs('/')}"><svg viewBox="0 0 32 32" width="28" height="28" aria-hidden="true" focusable="false"><circle cx="16" cy="16" r="7" fill="currentColor"/><g stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M16 2.5v4M16 25.5v4M2.5 16h4M25.5 16h4M6.5 6.5l2.8 2.8M22.7 22.7l2.8 2.8M25.5 6.5l-2.8 2.8M9.3 22.7l-2.8 2.8"/></g></svg><span>${esc(ui.site.name)}</span></a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="hovednav">${esc(ui.a11y.menu)}</button>
<nav id="hovednav" class="main-nav" aria-label="${esc(ui.a11y.main_nav)}"><ul>${nav}</ul></nav>
<button class="theme-toggle" type="button" aria-label="${esc(ui.a11y.theme)}" title="${esc(ui.a11y.theme)}"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9z" fill="currentColor"/></svg></button>
</div>
</header>
<main id="innhold" class="wrap" tabindex="-1">
${crumbs.length ? `<p class="crumbs">${crumbs.join(' / ')}</p>` : ''}
<h1>${esc(meta.title)}</h1>
${badge}
${html}
${pager}
</main>
<footer class="site-footer">
<div class="wrap">
<p>${esc(ui.footer.line1)}</p>
<p>${esc(ui.footer.line2)} <a href="${abs('/metode/')}">${esc(ui.footer.sources_link)}</a>. ${esc(ui.footer.built)} ${esc(generated)}.</p>
<p><a href="https://github.com/sheffielddivided/sun" rel="noopener">${esc(ui.footer.repo)}</a></p>
</div>
</footer>
</body>
</html>
`;
}

// ---------- kjør ----------
const files = fs.readdirSync(CONTENT).filter((f) => f.endsWith('.md'));
const pages = files.map((f) => {
  const { meta, body } = parseFrontMatter(fs.readFileSync(path.join(CONTENT, f), 'utf8'), f);
  return { file: f, meta, body };
});
const outputs = [];
for (const p of pages) {
  slugs.clear();
  const md = bindValues(preprocess(p.body, pages));
  p.html = marked.parse(md);
}
for (const p of pages) {
  const route = p.meta.route;
  const dir = path.join(ROOT, route === '/' ? '' : route.replace(/^\//, ''));
  fs.mkdirSync(dir, { recursive: true });
  const out = path.join(dir, 'index.html');
  fs.writeFileSync(out, layout(p, pages), 'utf8');
  outputs.push(path.relative(ROOT, out));
}
// 404-side
const nf = layout(
  {
    meta: { title: ui.notfound.title, description: ui.notfound.title, route: '/404', nav: '' },
    html: `<p>${esc(ui.notfound.text)}</p><p><a href="${abs('/')}">${esc(ui.notfound.home)}</a></p>`,
  },
  pages,
);
fs.writeFileSync(path.join(ROOT, '404.html'), nf, 'utf8');
outputs.push('404.html');
fs.writeFileSync(path.join(ROOT, 'scripts', 'pages.generated.json'), JSON.stringify(outputs.sort(), null, 2) + '\n');
console.log(`gen-pages: ${outputs.length} sider (språk ${LANG}, base ${BASE})`);
