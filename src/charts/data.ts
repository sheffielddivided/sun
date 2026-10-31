import * as Plot from '@observablehq/plot';
import type { ChartInstance } from '../lib/chart';
import { getJSON, last, pts } from '../lib/data';
import { decYear, num } from '../lib/format';
import { baseOpts, timeSeries } from '../lib/plot';
import { rolling } from './common';

export async function ssnMonthly(): Promise<ChartInstance> {
  const m = await getJSON('ssn_monthly.json');
  const lastI = m.ssn
    .map((v: number | null, i: number) => (v !== null ? i : -1))
    .filter((i: number) => i >= 0)
    .pop()!;
  return {
    title: 'Månedlig og glattet månedlig solflekktall siden 1749',
    subtitle: 'SILSO V2.0. Glattet = 13-måneders glidende middel (halvvektet i endene). Velg periode for å zoome.',
    alt: `Månedlig solflekktall fra 1749 til ${decYear(m.t[lastI])}. Syklusene har topper mellom omtrent 80 og 285 i glattet verdi; seriens siste månedsverdi er ${num(m.ssn[lastI], 1)}.`,
    sources: ['silso_monthly'],
    columns: [
      { key: 'year_decimal', label: 'Tid (desimalår)', digits: 3 },
      { key: 'monthly_ssn', label: 'Månedlig', digits: 1 },
      { key: 'smoothed_ssn', label: 'Glattet (13 mnd)', digits: 1 },
      { key: 'definitive', label: 'Endelig (1) / foreløpig (0)' },
    ],
    rows: m.t.map((t: number, i: number) => [t, m.ssn[i], m.smoothed[i], m.definitive[i]]),
    rangeCol: 0,
    range: { min: m.t[0], max: m.t[m.t.length - 1], presets: [250, 100, 50, 25] },
    csvName: 'solflekktall_manedlig_V2.0',
    legend: [
      { label: 'Månedlig', color: 'var(--s5)' },
      { label: 'Glattet (13 mnd)', color: 'var(--s1)' },
    ],
    render: ({ width, range, pal }) =>
      timeSeries({
        width,
        pal,
        range,
        yLabel: 'Solflekktall',
        series: [
          { name: 'Månedlig', color: pal.s5, kind: 'line', width: 0.9, opacity: 0.8, data: pts(m.t, m.ssn) },
          { name: 'Glattet', color: pal.s1, width: 2.2, data: pts(m.t, m.smoothed) },
        ],
        yDomain: [0, 320],
      }),
  };
}

export async function ssnYearly(): Promise<ChartInstance> {
  const y = await getJSON('ssn_yearly.json');
  const x = y.year.map((v: number) => v + 0.5);
  return {
    title: 'Årlig solflekktall siden 1700',
    subtitle: 'Årsmiddel (SILSO V2.0). Før 1749 er serien basert på få observasjoner og har stor usikkerhet.',
    alt: `Årlig solflekktall fra ${y.year[0]} til ${last(y.year)}. Maunder-minimumets slutt rundt 1715, Dalton-minimumet rundt 1790–1830 og de høye syklusene på 1950-tallet vises som lave og høye partier.`,
    sources: ['silso_monthly'],
    columns: [
      { key: 'year', label: 'År' },
      { key: 'ssn', label: 'Årsmiddel', digits: 1 },
      { key: 'std', label: 'Standardavvik', digits: 1 },
      { key: 'definitive', label: 'Endelig (1)' },
    ],
    rows: y.year.map((v: number, i: number) => [v, y.ssn[i], y.std[i], y.definitive[i]]),
    rangeCol: 0,
    range: { min: y.year[0], max: last(y.year), presets: [200, 100, 50] },
    csvName: 'solflekktall_aarlig_V2.0',
    render: ({ width, range, pal }) =>
      timeSeries({
        width,
        pal,
        range: range ? [range[0], range[1] + 1] : null,
        yLabel: 'Solflekktall',
        series: [
          { name: 'Årsmiddel', color: pal.s1, width: 2, data: pts(x, y.ssn) },
          { name: 'Årsmiddel', color: pal.s1, kind: 'dot', r: 2.4, opacity: 1, data: pts(x, y.ssn) },
        ],
        spans: [{ x1: 1790, x2: 1830, label: 'Dalton' }],
        yDomain: [0, 220],
      }),
  };
}

export async function groupNumber(): Promise<ChartInstance> {
  const [g, y] = await Promise.all([getJSON('group_yearly.json'), getJSON('ssn_yearly.json')]);
  const x = g.year.map((v: number) => v + 0.5);
  return {
    title: 'Gruppesolflekktall 1610–2015 (to rekonstruksjoner)',
    subtitle:
      'Antall solflekkgrupper (ikke det samme som solflekktallet). Backbone-serien og Hoyt & Schatten-serien er uenige om nivået før ca. 1880.',
    alt: `Årlig gruppesolflekktall fra ${g.year[0]} til ${last(g.year)} for to rekonstruksjoner. Perioden ca. 1645–1715 (Maunder-minimum) har svært få observerte grupper. Før 1749 er dekningen sparsom.`,
    sources: ['silso_groups'],
    columns: [
      { key: 'year', label: 'År' },
      { key: 'backbone', label: 'Backbone (Svalgaard & Schatten)', digits: 3 },
      { key: 'backbone_err', label: 'Feil backbone', digits: 3 },
      { key: 'hoyt_schatten', label: 'Hoyt & Schatten', digits: 3 },
    ],
    rows: g.year.map((v: number, i: number) => [v, g.backbone[i], g.backbone_err[i], g.hs[i]]),
    rangeCol: 0,
    range: { min: g.year[0], max: last(g.year), presets: [250, 100] },
    csvName: 'gruppesolflekktall_aarlig',
    legend: [
      { label: 'Backbone (Svalgaard & Schatten 2016)', color: 'var(--s1)' },
      { label: 'Hoyt & Schatten 1998', color: 'var(--s2)' },
    ],
    render: ({ width, range, pal }) =>
      timeSeries({
        width,
        pal,
        range: range ? [range[0], range[1] + 1] : null,
        yLabel: 'Gruppetall',
        series: [
          { name: 'Backbone', color: pal.s1, width: 1.8, data: pts(x, g.backbone) },
          { name: 'Hoyt & Schatten', color: pal.s2, width: 1.8, data: pts(x, g.hs) },
        ],
        spans: [
          { x1: 1645, x2: 1715, label: 'Maunder' },
          { x1: 1790, x2: 1830, label: 'Dalton' },
        ],
        yDomain: [0, 14],
      }),
  };
  void y;
}

export async function cyclesOverlay(): Promise<ChartInstance> {
  const [m, c] = await Promise.all([getJSON('ssn_monthly.json'), getJSON('cycles.json')]);
  const cycles = c.cycles as any[];
  const lines: { n: number; pts: { x: number; y: number }[] }[] = cycles.map((cy) => {
    const p: { x: number; y: number }[] = [];
    for (let i = 0; i < m.t.length; i++) {
      if (m.t[i] >= cy.start_t && (cy.end_t === null || m.t[i] < cy.end_t) && m.smoothed[i] !== null)
        p.push({ x: m.t[i] - cy.start_t, y: m.smoothed[i] });
    }
    return { n: cy.n, pts: p };
  });
  const complete = cycles.filter((x) => x.complete);
  const meanLen = complete.reduce((a, b) => a + b.length_years, 0) / complete.length;
  return {
    title: 'Alle solsykluser lagt over hverandre',
    subtitle: 'Glattet månedlig solflekktall, justert til syklusstart (minimum). Syklus 25 (pågående) er uthevet.',
    alt: `Glattet solflekktall for syklus 1 til 25, justert til syklusstart. Gjennomsnittlig lengde for fullførte sykluser er ${num(meanLen, 1)} år. Syklus 19 hadde høyest topp (${num(cycles[18].max_smoothed, 0)}), syklus 5 og 6 lavest (rundt 81).`,
    sources: ['silso_monthly'],
    columns: [
      { key: 'cycle', label: 'Syklus' },
      { key: 'start', label: 'Start (desimalår)', digits: 2 },
      { key: 'length_years', label: 'Lengde (år)', digits: 1 },
      { key: 'max_smoothed', label: 'Maksimum (glattet)', digits: 1 },
      { key: 'max_time', label: 'Tid for maks (desimalår)', digits: 2 },
      { key: 'rise_years', label: 'Stigetid (år)', digits: 1 },
    ],
    rows: cycles.map((x) => [x.n, x.start_t, x.length_years, x.max_smoothed, x.max_t, x.rise_years]),
    tableOpen: true,
    csvName: 'solsykluser_lengde_og_maksimum',
    legend: [
      { label: 'Syklus 25 (pågående)', color: 'var(--s1)' },
      { label: 'Syklus 24', color: 'var(--s2)' },
      { label: 'Syklus 19 (høyest)', color: 'var(--s4)' },
      { label: 'Øvrige sykluser', color: 'var(--s5)' },
    ],
    render: ({ width, pal }) => {
      const color = (n: number) => (n === 25 ? pal.s1 : n === 24 ? pal.s2 : n === 19 ? pal.s4 : pal.s5);
      const marks: Plot.Markish[] = [Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 })];
      for (const l of lines.filter((l) => ![19, 24, 25].includes(l.n)))
        marks.push(Plot.line(l.pts, { x: 'x', y: 'y', stroke: color(l.n), strokeWidth: 1, strokeOpacity: 0.55 }));
      for (const l of lines.filter((l) => [19, 24].includes(l.n)))
        marks.push(Plot.line(l.pts, { x: 'x', y: 'y', stroke: color(l.n), strokeWidth: 2 }));
      marks.push(Plot.line(lines[24].pts, { x: 'x', y: 'y', stroke: color(25), strokeWidth: 3 }));
      marks.push(
        Plot.text(
          cycles.map((cy) => ({ x: cy.max_t - cy.start_t, y: cy.max_smoothed, t: String(cy.n) })),
          { x: 'x', y: 'y', text: 't', dy: -7, fill: pal.muted, fontSize: 10 },
        ),
      );
      return Plot.plot({
        ...baseOpts(width, pal),
        x: { label: 'År siden syklusstart', domain: [0, 14], ticks: 14, labelAnchor: 'right' },
        y: { label: 'Glattet solflekktall', labelAnchor: 'top', domain: [0, 310] },
        marks,
      });
    },
  };
}

export async function hemispheric(): Promise<ChartInstance> {
  const h = await getJSON('ssn_hemispheric_monthly.json');
  const n13 = rolling(h.north, 13);
  const s13 = rolling(h.south, 13);
  return {
    title: 'Nordlige og sørlige halvkule (1992–)',
    subtitle:
      'Månedlig solflekktall per halvkule (tynne linjer) og 13-måneders glidende middel (tykke linjer). Halvkulene topper ikke alltid samtidig.',
    alt: `Solflekktall for solens nordlige og sørlige halvkule fra ${decYear(h.t[0])} til ${decYear(last(h.t))}. Halvkulene varierer i takt over syklusen, men med tidvise forskjeller i styrke og tid.`,
    sources: ['silso_monthly'],
    columns: [
      { key: 'year_decimal', label: 'Tid (desimalår)', digits: 3 },
      { key: 'north', label: 'Nord', digits: 1 },
      { key: 'south', label: 'Sør', digits: 1 },
    ],
    rows: h.t.map((t: number, i: number) => [t, h.north[i], h.south[i]]),
    rangeCol: 0,
    range: { min: h.t[0], max: last(h.t), presets: [20, 10] },
    csvName: 'solflekktall_hemisfaerer_manedlig',
    legend: [
      { label: 'Nord', color: 'var(--s2)' },
      { label: 'Sør', color: 'var(--s1)' },
    ],
    render: ({ width, range, pal }) =>
      timeSeries({
        width,
        pal,
        range,
        yLabel: 'Solflekktall per halvkule',
        series: [
          { name: 'Nord (månedlig)', color: pal.s2, width: 0.8, opacity: 0.45, data: pts(h.t, h.north) },
          { name: 'Sør (månedlig)', color: pal.s1, width: 0.8, opacity: 0.45, data: pts(h.t, h.south) },
          { name: 'Nord (glattet)', color: pal.s2, width: 2.4, data: pts(h.t, n13) },
          { name: 'Sør (glattet)', color: pal.s1, width: 2.4, data: pts(h.t, s13) },
        ],
        yDomain: [0, 200],
      }),
  };
}

export async function butterfly(): Promise<ChartInstance> {
  const b = await getJSON('butterfly.json');
  const nlat = b.nlat as number;
  const nrot = b.area.length / nlat;
  // Aggregér til halvårsbiner × 25 breddebiner (par av sin(bredde)-biner)
  const binW = 0.5;
  const t0 = b.t0 as number;
  const dt = b.dt as number;
  const tStart = Math.floor(t0 / binW) * binW;
  const nb = Math.ceil((t0 + nrot * dt - tStart) / binW);
  const cells = new Float64Array(nb * 25);
  const counts = new Float64Array(nb);
  const annualN = new Map<number, number>();
  const annualS = new Map<number, number>();
  const annualC = new Map<number, number>();
  for (let r = 0; r < nrot; r++) {
    const t = t0 + r * dt;
    const k = Math.floor((t - tStart) / binW);
    counts[k]++;
    const yr = Math.floor(t);
    annualC.set(yr, (annualC.get(yr) ?? 0) + 1);
    for (let j = 0; j < nlat; j++) {
      const a = b.area[r * nlat + j];
      cells[k * 25 + (j >> 1)] += a;
      if (j < nlat / 2) annualS.set(yr, (annualS.get(yr) ?? 0) + a);
      else annualN.set(yr, (annualN.get(yr) ?? 0) + a);
    }
  }
  const lat = (s: number) => (Math.asin(s) * 180) / Math.PI;
  const edges = Array.from({ length: 26 }, (_, i) => lat(-1 + (2 * i) / 25));
  const years = [...annualC.keys()].sort((a, b) => a - b).filter((y) => (annualC.get(y) ?? 0) >= 10);
  const grid: { x1: number; x2: number; y1: number; y2: number; v: number }[] = [];
  let maxV = 0;
  for (let k = 0; k < nb; k++) {
    if (!counts[k]) continue;
    for (let j = 0; j < 25; j++) {
      const v = cells[k * 25 + j] / counts[k];
      if (v > 0) {
        grid.push({ x1: tStart + k * binW, x2: tStart + (k + 1) * binW, y1: edges[j], y2: edges[j + 1], v });
        maxV = Math.max(maxV, v);
      }
    }
  }
  return {
    title: 'Sommerfugldiagram: solflekkareal etter breddegrad 1874–2016',
    subtitle:
      'Gjennomsnittlig solflekkareal (millionedeler av en halvkule) per halvår og breddebånd. Flekkene starter på høye breddegrader og vandrer mot ekvator i løpet av hver syklus.',
    alt: `Sommerfugldiagram: breddegrad mot tid fra ${num(t0, 0)} til ${num(t0 + nrot * dt, 0)}. Solflekkene opptrer i to bånd, ett på hver halvkule, som starter rundt 30–35 graders bredde og nærmer seg ekvator mot slutten av hver syklus.`,
    sources: ['butterfly'],
    columns: [
      { key: 'year', label: 'År' },
      { key: 'north_mean_area', label: 'Nord, gj.snitt areal per rotasjon', digits: 0 },
      { key: 'south_mean_area', label: 'Sør, gj.snitt areal per rotasjon', digits: 0 },
      { key: 'rotations', label: 'Antall rotasjoner' },
    ],
    rows: years.map((y) => [
      y,
      (annualN.get(y) ?? 0) / (annualC.get(y) ?? 1),
      (annualS.get(y) ?? 0) / (annualC.get(y) ?? 1),
      annualC.get(y) ?? 0,
    ]),
    rangeCol: 0,
    range: { min: Math.ceil(t0), max: Math.floor(t0 + nrot * dt), presets: [100, 50, 25] },
    csvName: 'sommerfugldiagram_aarlig_areal_per_halvkule',
    note: 'Tabellen og CSV-filen viser årlig gjennomsnittsareal per halvkule; hele bredde-tid-matrisen finnes i butterfly.json.',
    render: ({ width, range, pal }) => {
      const r = range ?? [tStart, tStart + nb * binW];
      const g = grid.filter((c) => c.x2 >= r[0] && c.x1 <= r[1]);
      return Plot.plot({
        ...baseOpts(width, pal, Math.max(260, Math.min(420, width * 0.45))),
        x: { label: null, domain: r, tickFormat: (d: number) => String(d), ticks: Math.max(3, Math.floor(width / 90)) },
        y: { label: 'Breddegrad (°)', domain: [-50, 50], ticks: [-40, -20, 0, 20, 40], labelAnchor: 'top' },
        color: { type: 'sqrt', domain: [0, maxV], range: [pal.bg, pal.s1], legend: false },
        marks: [
          Plot.rect(g, {
            x1: 'x1',
            x2: 'x2',
            y1: 'y1',
            y2: 'y2',
            fill: 'v',
            title: (c: { v: number }) => `${num(c.v, 0)} millionedeler av en halvkule`,
          }),
          Plot.ruleY([0], { stroke: pal.muted, strokeOpacity: 0.6 }),
        ],
      });
    },
  };
}
