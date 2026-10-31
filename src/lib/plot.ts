import * as Plot from '@observablehq/plot';
import type { Palette } from './palette';

export const yearFmt = (d: number) => String(d);
const nbFmt = (d: number) => d.toLocaleString('nb-NO', { maximumFractionDigits: 3 });

export function baseOpts(width: number, pal: Palette, height?: number) {
  const h = height ?? Math.max(240, Math.min(420, Math.round(width * 0.5)));
  return {
    width,
    height: h,
    marginLeft: 52,
    marginRight: 16,
    marginTop: 14,
    marginBottom: 38,
    style: { background: 'transparent', color: pal.fg, fontSize: '13px', fontFamily: 'system-ui, sans-serif', overflow: 'visible' } as Record<string, string>,
  };
}

export interface Series {
  name: string;
  color: string;
  data: { x: number; y: number }[];
  kind?: 'line' | 'dot' | 'step' | 'area' | 'bar';
  width?: number;
  dash?: string;
  opacity?: number;
  r?: number;
}

function inRange<T extends { x: number }>(d: T[], r: [number, number] | null): T[] {
  return r ? d.filter((p) => p.x >= r[0] && p.x <= r[1]) : d;
}

export interface TSOpts {
  width: number;
  pal: Palette;
  series: Series[];
  range?: [number, number] | null;
  yLabel: string;
  yDomain?: [number, number];
  zeroLine?: boolean;
  height?: number;
  xTicks?: number;
  vlines?: { x: number; label?: string }[];
  hlines?: { y: number; label?: string }[];
  spans?: { x1: number; x2: number; label: string }[];
  band?: { color: string; data: { x: number; lo: number; hi: number }[] };
  yTickFormat?: (d: number) => string;
  xLabel?: string;
  tipLabel?: Record<string, string>;
}

export function timeSeries(o: TSOpts) {
  const { pal } = o;
  const r = o.range ?? null;
  const marks: Plot.Markish[] = [Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 })];
  if (o.spans)
    for (const s of o.spans) {
      marks.push(Plot.rectY([{ x1: s.x1, x2: s.x2 }], { x1: 'x1', x2: 'x2', fill: pal.s5, fillOpacity: 0.14 }));
      marks.push(Plot.text([{ x: (s.x1 + s.x2) / 2, text: s.label }], { x: 'x', text: 'text', frameAnchor: 'top', dy: 4, fill: pal.muted, fontSize: 11 }));
    }
  if (o.band) {
    const d = r ? o.band.data.filter((p) => p.x >= r[0] && p.x <= r[1]) : o.band.data;
    marks.push(Plot.areaY(d, { x: 'x', y1: 'lo', y2: 'hi', fill: o.band.color, fillOpacity: 0.22 }));
  }
  if (o.zeroLine) marks.push(Plot.ruleY([0], { stroke: pal.muted, strokeOpacity: 0.7 }));
  for (const v of o.vlines ?? []) {
    marks.push(Plot.ruleX([v.x], { stroke: pal.muted, strokeDasharray: '4 3' }));
    if (v.label) marks.push(Plot.text([{ x: v.x, t: v.label }], { x: 'x', text: 't', frameAnchor: 'top', textAnchor: 'start', dx: 4, dy: 2, fill: pal.muted, fontSize: 11 }));
  }
  for (const h of o.hlines ?? []) {
    marks.push(Plot.ruleY([h.y], { stroke: pal.muted, strokeDasharray: '4 3' }));
    if (h.label) marks.push(Plot.text([{ y: h.y, t: h.label }], { y: 'y', text: 't', frameAnchor: 'left', textAnchor: 'start', dy: -6, dx: 4, fill: pal.muted, fontSize: 11 }));
  }
  for (const s of o.series) {
    const d = inRange(s.data, r);
    if (!d.length) continue;
    const common = { x: 'x', y: 'y' } as const;
    switch (s.kind ?? 'line') {
      case 'dot':
        marks.push(Plot.dot(d, { ...common, fill: s.color, fillOpacity: s.opacity ?? 0.7, r: s.r ?? 2.2 }));
        break;
      case 'step':
        marks.push(Plot.line(d, { ...common, stroke: s.color, strokeWidth: s.width ?? 1.6, curve: 'step-after', strokeDasharray: s.dash }));
        break;
      case 'area':
        marks.push(Plot.areaY(d, { ...common, fill: s.color, fillOpacity: s.opacity ?? 0.3 }));
        break;
      case 'bar':
        marks.push(Plot.rectY(d, { x1: (p: { x: number }) => p.x - 0.4, x2: (p: { x: number }) => p.x + 0.4, y: 'y', fill: s.color, fillOpacity: s.opacity ?? 0.85 }));
        break;
      default:
        marks.push(Plot.line(d, { ...common, stroke: s.color, strokeWidth: s.width ?? 1.8, strokeDasharray: s.dash, strokeOpacity: s.opacity ?? 1 }));
    }
  }
  // Verktøytips (peker), bare for mus/pekeskjerm. Tastatur og skjermleser bruker tabellen.
  const tipSeries = o.series.filter((s) => s.kind !== 'area').slice(0, 3);
  for (const s of tipSeries) {
    const d = inRange(s.data, r);
    if (d.length)
      marks.push(
        Plot.tip(d, Plot.pointerX({ x: 'x', y: 'y', title: (p: { x: number; y: number }) => `${s.name}\n${o.xLabel ?? ''} ${p.x.toLocaleString('nb-NO', { maximumFractionDigits: 3, useGrouping: false })}\n${nbFmt(p.y)}`, fill: pal.bg, stroke: pal.border, fontSize: 12 })),
      );
  }
  // Y-domene fra synlige data
  let yDomain = o.yDomain;
  if (!yDomain) {
    const ys = o.series.flatMap((s) => inRange(s.data, r).map((p) => p.y));
    if (o.band) ys.push(...(r ? o.band.data.filter((p) => p.x >= r[0] && p.x <= r[1]) : o.band.data).flatMap((p) => [p.lo, p.hi]));
    if (ys.length) {
      let lo = Math.min(...ys);
      let hi = Math.max(...ys);
      if (o.zeroLine) {
        lo = Math.min(lo, 0);
        hi = Math.max(hi, 0);
      }
      const pad = (hi - lo) * 0.05 || 1;
      yDomain = [lo >= 0 && lo - pad < 0 && !o.zeroLine ? 0 : lo - pad, hi + pad];
    }
  }
  const xs = o.series.flatMap((s) => inRange(s.data, r).map((p) => p.x));
  const xDomain: [number, number] = r ?? [Math.min(...xs), Math.max(...xs)];
  return Plot.plot({
    ...baseOpts(o.width, pal, o.height),
    x: { label: o.xLabel ?? null, tickFormat: yearFmt, ticks: o.xTicks ?? Math.max(3, Math.floor(o.width / 90)), domain: xDomain, labelAnchor: 'right' },
    y: { label: o.yLabel, domain: yDomain, tickFormat: o.yTickFormat, labelAnchor: 'top', grid: false },
    marks,
  });
}

/** Stabler flere plott vertikalt i én container (delt x-akse i tid). */
export function stack(...children: (SVGElement | HTMLElement)[]): HTMLElement {
  const div = document.createElement('div');
  div.append(...children);
  return div;
}
