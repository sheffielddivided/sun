import * as Plot from '@observablehq/plot';
import type { Palette } from '../lib/palette';
import { baseOpts } from '../lib/plot';

const MON = ['jan', 'feb', 'mar', 'apr', 'mai', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'des'];
export const dateTick = (d: Date) => `${d.getUTCDate()}. ${MON[d.getUTCMonth()]}`;
export const dateTickYear = (d: Date) => `${MON[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
export const parseDay = (s: string) => new Date(s.length > 10 ? s + 'Z' : s + 'T00:00:00Z');

export function rolling(values: (number | null)[], k: number): (number | null)[] {
  const out: (number | null)[] = new Array(values.length).fill(null);
  const h = Math.floor(k / 2);
  for (let i = h; i < values.length - h; i++) {
    let s = 0;
    let n = 0;
    for (let j = i - h; j <= i + h; j++) {
      const v = values[j];
      if (v !== null && Number.isFinite(v)) {
        s += v;
        n++;
      }
    }
    out[i] = n >= k * 0.8 ? s / n : null;
  }
  return out;
}

/** Enkle søylediagram med kategorier (x som tekst). */
export function barsByCategory(opts: {
  width: number;
  pal: Palette;
  data: { cat: string; v: number; series: string }[];
  colors: Record<string, string>;
  yLabel: string;
  hline?: { y: number; label: string };
  height?: number;
  yDomain?: [number, number];
  catLabel?: string;
}) {
  const { pal } = opts;
  const series = Object.keys(opts.colors);
  const marks: Plot.Markish[] = [
    Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 }),
    Plot.ruleY([0], { stroke: pal.muted }),
  ];
  marks.push(
    Plot.barY(opts.data, {
      x: 'series',
      y: 'v',
      fx: 'cat',
      fill: 'series',
      title: (d: { cat: string; series: string; v: number }) =>
        `${d.cat} – ${d.series}: ${d.v.toLocaleString('nb-NO', { maximumFractionDigits: 3 })}`,
    }),
  );
  if (opts.hline) {
    marks.push(Plot.ruleY([opts.hline.y], { stroke: pal.muted, strokeDasharray: '4 3' }));
    marks.push(
      Plot.text([{ y: opts.hline.y, t: opts.hline.label }], {
        y: 'y',
        text: 't',
        frameAnchor: 'right',
        textAnchor: 'end',
        dy: -6,
        fill: pal.muted,
        fontSize: 11,
      }),
    );
  }
  return Plot.plot({
    ...baseOpts(opts.width, pal, opts.height),
    marginBottom: 54,
    x: { axis: null, domain: series },
    fx: { label: opts.catLabel ?? null, tickSize: 0, padding: 0.12 },
    y: { label: opts.yLabel, domain: opts.yDomain, labelAnchor: 'top' },
    color: { domain: series, range: series.map((s) => opts.colors[s]) },
    marks,
  });
}

/** Korrelasjon per lag med konfidensintervall; åpne symboler = ikke signifikant etter Holm-korreksjon. */
export interface LagRow {
  lag: number;
  r: number;
  ci_lo: number | null;
  ci_hi: number | null;
  neff: number;
  p_surrogate: number;
  p_holm: number;
  n: number;
}
export function lagPlot(opts: {
  width: number;
  pal: Palette;
  sets: { name: string; color: string; rows: LagRow[] }[];
  height?: number;
  xLabel?: string;
}) {
  const { pal } = opts;
  const marks: Plot.Markish[] = [
    Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 }),
    Plot.ruleY([0], { stroke: pal.muted }),
  ];
  const nSets = opts.sets.length;
  opts.sets.forEach((s, i) => {
    const off = (i - (nSets - 1) / 2) * 0.16;
    const d = s.rows.map((r) => ({ ...r, x: r.lag + off, sig: r.p_holm < 0.05 }));
    marks.push(
      Plot.ruleX(d, {
        x: 'x',
        y1: (r: LagRow) => r.ci_lo ?? r.r,
        y2: (r: LagRow) => r.ci_hi ?? r.r,
        stroke: s.color,
        strokeWidth: 1.6,
      }),
    );
    marks.push(
      Plot.dot(d, {
        x: 'x',
        y: 'r',
        r: 4.5,
        stroke: s.color,
        strokeWidth: 2,
        fill: (r: { sig: boolean }) => (r.sig ? s.color : opts.pal.bg),
        title: (r: LagRow) =>
          `${s.name}, lag ${r.lag}: r = ${r.r.toFixed(2)}, 95 % KI [${r.ci_lo?.toFixed(2)}, ${r.ci_hi?.toFixed(2)}], N_eff = ${r.neff.toFixed(0)}, p(surrogat) = ${r.p_surrogate.toFixed(3)}, p(Holm) = ${r.p_holm.toFixed(3)}`,
      }),
    );
  });
  return Plot.plot({
    ...baseOpts(opts.width, pal, opts.height ?? 300),
    x: {
      label: opts.xLabel ?? 'Forsinkelse (år)',
      ticks: 12,
      tickFormat: (d: number) => String(d),
      labelAnchor: 'right',
    },
    y: { label: 'Korrelasjon (r)', domain: [-1, 1], labelAnchor: 'top' },
    marks,
  });
}

export function lagColumns() {
  return [
    { key: 'lag', label: 'Forsinkelse (år)' },
    { key: 'r', label: 'r', digits: 3 },
    { key: 'ci_lo', label: 'KI nedre', digits: 3 },
    { key: 'ci_hi', label: 'KI øvre', digits: 3 },
    { key: 'n', label: 'N' },
    { key: 'neff', label: 'N_eff', digits: 1 },
    { key: 'p_surrogate', label: 'p (surrogat)', digits: 4 },
    { key: 'p_holm', label: 'p (Holm)', digits: 4 },
  ];
}
export const lagRows = (rows: LagRow[], label?: string) =>
  rows.map((r) => [...(label ? [label] : []), r.lag, r.r, r.ci_lo, r.ci_hi, r.n, r.neff, r.p_surrogate, r.p_holm]);
