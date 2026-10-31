import { getManifest, type SourceEntry } from './data';
import { isoDate, num } from './format';
import { palette, type Palette } from './palette';
import { tpl, ui } from './ui';

export interface Column {
  key: string;
  label: string;
  digits?: number;
}
export interface LegendItem {
  label: string;
  color: string;
  dash?: boolean;
}
export type Cell = number | string | null;
export interface RenderCtx {
  width: number;
  range: [number, number] | null;
  pal: Palette;
}
export interface ChartInstance {
  title: string;
  subtitle?: string;
  /** Tekstalternativ (kort beskrivelse av hva grafen viser, med tallene som er relevante). */
  alt: string;
  sources: string[];
  columns: Column[];
  rows: Cell[][];
  csvName: string;
  /** Kolonneindeks som brukes til periodefilter (desimalår eller år). */
  rangeCol?: number;
  range?: { min: number; max: number; presets?: number[] };
  legend?: LegendItem[];
  render?: (ctx: RenderCtx) => HTMLElement | SVGElement;
  /** Vis tabellen åpen (for «grafer» som egentlig er tabeller). */
  tableOpen?: boolean;
  note?: string;
}
export type ChartFactory = () => Promise<ChartInstance>;

const MAX_TABLE_ROWS = 1500;

function el<K extends keyof HTMLElementTagNameMap>(tag: K, cls?: string, text?: string): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function cellText(v: Cell, digits?: number): string {
  if (v === null || v === undefined) return '';
  if (typeof v === 'number') return num(v, digits ?? (Number.isInteger(v) ? 0 : 2), false);
  return v;
}

function csvCell(v: Cell, digits?: number): string {
  if (v === null || v === undefined) return '';
  if (typeof v === 'number') return digits !== undefined ? v.toFixed(digits) : String(v);
  return /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
}

export function buildCsv(inst: ChartInstance, sources: SourceEntry[], generated: string | null): string {
  const lines: string[] = [];
  lines.push(`# ${inst.title}`);
  lines.push(`# Generert fra ${location.origin}${location.pathname} (datastand: ${generated ? isoDate(generated) : 'ukjent'})`);
  for (const s of sources) {
    lines.push(`# Kilde: ${s.name} – ${s.provider} – ${s.homepage}`);
    lines.push(`# Lisens: ${s.license}`);
    lines.push(`# Kildehenvisning: ${s.citation}`);
  }
  lines.push('# Desimaltegn: punktum. Tomme felt = mangler data.');
  lines.push(inst.columns.map((c) => c.key).join(','));
  for (const r of inst.rows) lines.push(r.map((v, i) => csvCell(v, inst.columns[i]?.digits)).join(','));
  return lines.join('\n') + '\n';
}

export async function mountChart(host: HTMLElement, factory: ChartFactory): Promise<void> {
  try {
    const [inst, manifest] = await Promise.all([factory(), getManifest().catch(() => null)]);
    const srcs = inst.sources.map((id) => manifest?.sources[id]).filter((s): s is SourceEntry => !!s);
    host.textContent = '';
    host.classList.add('chart-ready');

    host.append(el('h3', 'chart-title', inst.title));
    if (inst.subtitle) host.append(el('p', 'chart-sub', inst.subtitle));

    let range: [number, number] | null = inst.range ? [inst.range.min, inst.range.max] : null;
    const plot = el('div', 'plot-wrap');
    const legendBox = el('div', 'legend');
    const tableBox = document.createElement('details');
    tableBox.className = 'table-alt';
    const sum = document.createElement('summary');
    sum.textContent = ui.chart.table_summary;
    tableBox.append(sum);
    const tableHolder = el('div', 'table-holder');
    tableBox.append(tableHolder);
    if (inst.tableOpen) tableBox.open = true;

    const renderTable = () => {
      tableHolder.textContent = '';
      let rows = inst.rows;
      if (inst.rangeCol !== undefined && range) {
        const [a, b] = range;
        rows = rows.filter((r) => {
          const x = r[inst.rangeCol!];
          return typeof x === 'number' && x >= a && x <= b;
        });
      }
      const shown = rows.slice(0, MAX_TABLE_ROWS);
      const wrap = el('div', 'table-scroll');
      const t = document.createElement('table');
      const cap = document.createElement('caption');
      cap.textContent =
        `${inst.title}. ${ui.chart.table_rows} ${num(shown.length)} ${ui.chart.table_of} ${num(rows.length)} ${ui.chart.table_rows_suffix}` +
        (rows.length > shown.length ? ' (' + ui.chart.download + ' for alt).' : '.');
      t.append(cap);
      const thead = document.createElement('thead');
      const hr = document.createElement('tr');
      for (const c of inst.columns) {
        const th = document.createElement('th');
        th.scope = 'col';
        th.textContent = c.label;
        hr.append(th);
      }
      thead.append(hr);
      t.append(thead);
      const tb = document.createElement('tbody');
      for (const r of shown) {
        const tr = document.createElement('tr');
        r.forEach((v, i) => {
          const td = document.createElement(i === 0 ? 'th' : 'td');
          if (i === 0) (td as HTMLTableCellElement).scope = 'row';
          td.textContent = cellText(v, inst.columns[i]?.digits);
          tr.append(td);
        });
        tb.append(tr);
      }
      t.append(tb);
      wrap.append(t);
      tableHolder.append(wrap);
    };

    const draw = () => {
      if (!inst.render) return;
      const width = Math.max(280, Math.floor(plot.clientWidth || host.clientWidth - 32));
      plot.textContent = '';
      plot.setAttribute('role', 'img');
      plot.setAttribute('aria-label', inst.alt);
      try {
        plot.append(inst.render({ width, range, pal: palette() }));
      } catch (e) {
        console.error('chart render', inst.title, e);
        plot.textContent = ui.chart.error;
        host.dataset.error = '1';
      }
    };

    // Kontroller for periodevalg
    if (inst.range && inst.rangeCol !== undefined) {
      const { min, max, presets = [] } = inst.range;
      const controls = el('div', 'chart-controls');
      controls.setAttribute('role', 'group');
      controls.setAttribute('aria-label', ui.chart.period);
      const mk = (label: string, value: number) => {
        const l = el('label');
        l.append(el('span', undefined, label));
        const i = document.createElement('input');
        i.type = 'number';
        i.min = String(Math.floor(min));
        i.max = String(Math.ceil(max));
        i.step = '1';
        i.value = String(Math.round(value));
        l.append(i);
        return { l, i };
      };
      const from = mk(ui.chart.from, min);
      const to = mk(ui.chart.to, max);
      const apply = () => {
        let a = Number(from.i.value);
        let b = Number(to.i.value);
        if (!Number.isFinite(a) || !Number.isFinite(b)) return;
        a = Math.max(Math.floor(min), a);
        b = Math.min(Math.ceil(max), b);
        if (b - a < 2) b = a + 2;
        range = [a, b];
        from.i.value = String(a);
        to.i.value = String(b);
        draw();
        renderTable();
        presetBtns.forEach((p) => p.setAttribute('aria-pressed', 'false'));
      };
      from.i.addEventListener('change', apply);
      to.i.addEventListener('change', apply);
      const presetBtns: HTMLButtonElement[] = [];
      const setRange = (a: number, b: number, btn: HTMLButtonElement) => {
        range = [a, b];
        from.i.value = String(Math.round(a));
        to.i.value = String(Math.round(b));
        presetBtns.forEach((p) => p.setAttribute('aria-pressed', String(p === btn)));
        draw();
        renderTable();
      };
      controls.append(from.l, to.l);
      const allBtn = el('button', 'btn', ui.chart.all);
      allBtn.type = 'button';
      allBtn.setAttribute('aria-pressed', 'true');
      allBtn.addEventListener('click', () => setRange(min, max, allBtn));
      presetBtns.push(allBtn);
      controls.append(allBtn);
      for (const n of presets) {
        const b = el('button', 'btn', tpl(ui.chart.last_n, { n }));
        b.type = 'button';
        b.setAttribute('aria-pressed', 'false');
        b.addEventListener('click', () => setRange(Math.max(min, max - n), max, b));
        presetBtns.push(b);
        controls.append(b);
      }
      host.append(controls);
    }

    if (inst.legend?.length) {
      for (const l of inst.legend) {
        const s = el('span');
        const sw = el('span', 'swatch');
        sw.style.background = l.color;
        if (l.dash) sw.style.background = `repeating-linear-gradient(90deg, ${l.color} 0 4px, transparent 4px 7px)`;
        s.append(sw, document.createTextNode(l.label));
        legendBox.append(s);
      }
      host.append(legendBox);
    }
    if (inst.render) host.append(plot);
    if (inst.note) host.append(el('p', 'chart-sub', inst.note));

    // Metadata + handlinger
    const meta = el('p', 'chart-meta');
    const parts: string[] = [];
    if (srcs.length) {
      meta.append(document.createTextNode(`${ui.chart.source}: `));
      srcs.forEach((s, i) => {
        const a = document.createElement('a');
        a.href = `${import.meta.env.BASE_URL}metode/#kilde-${s.id}`;
        a.textContent = s.provider.split(' – ')[0];
        meta.append(a);
        if (i < srcs.length - 1) meta.append(document.createTextNode(', '));
      });
      const newest = srcs.map((s) => s.fetched_at).filter(Boolean).sort().pop();
      if (newest) parts.push(`${ui.chart.updated}: ${isoDate(newest)}`);
      const lp = srcs.map((s) => s.last_point).filter(Boolean)[0];
      if (lp) parts.push(`${ui.chart.last_point}: ${lp}`);
      if (srcs.some((s) => s.status !== 'ok')) parts.push(ui.chart.stale);
    }
    if (parts.length) meta.append(document.createTextNode(' · ' + parts.join(' · ')));
    host.append(meta);

    const actions = el('div', 'chart-actions');
    const dl = el('button', 'btn', ui.chart.download);
    dl.type = 'button';
    dl.addEventListener('click', () => {
      const blob = new Blob([buildCsv(inst, srcs, manifest?.generated_at ?? null)], { type: 'text/csv;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${inst.csvName}.csv`;
      document.body.append(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 2000);
    });
    actions.append(dl);
    host.append(actions);
    host.append(tableBox);

    renderTable();
    draw();
    host.setAttribute('aria-busy', 'false');

    // Responsivitet og temaskifte
    let lastW = plot.clientWidth;
    if (inst.render) {
      const ro = new ResizeObserver(() => {
        if (Math.abs(plot.clientWidth - lastW) > 24) {
          lastW = plot.clientWidth;
          draw();
        }
      });
      ro.observe(plot);
      document.addEventListener('themechange', draw);
    }
  } catch (e) {
    console.error('mountChart', e);
    host.textContent = ui.chart.error;
    host.dataset.error = '1';
    host.setAttribute('aria-busy', 'false');
  }
}
