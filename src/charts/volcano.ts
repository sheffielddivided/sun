import * as Plot from '@observablehq/plot';
import type { ChartInstance } from '../lib/chart';
import { getJSON, last, pts } from '../lib/data';
import { num, pval } from '../lib/format';
import { baseOpts, stack, timeSeries } from '../lib/plot';
import { barsByCategory } from './common';

const sc = (a: any, id: string) => a.scenarios.find((s: any) => s.id === id);

export async function volcanoTimeline(): Promise<ChartInstance> {
  const [e, m] = await Promise.all([getJSON('volcano_eruptions.json'), getJSON('ssn_monthly.json')]);
  const idx: number[] = e.t.map((_: number, i: number) => i).filter((i: number) => e.vei[i] >= 4 && e.confirmed[i]);
  const rows = idx.map((i) => [e.t[i], e.year[i], e.volcano[i], e.vei[i], e.precise[i] ? 'ja' : 'nei']);
  return {
    title: 'Store vulkanutbrudd (VEI ≥ 4) og solflekktall',
    subtitle:
      'Hvert punkt er ett bekreftet utbrudd i Smithsonian GVP; størrelsen viser VEI. Nederst: glattet solflekktall (fra 1749).',
    alt: `Tidslinje 1500–2025 over ${idx.length} bekreftede utbrudd med VEI ≥ 4 og solflekktall. Antall registrerte utbrudd per tiår er lavere før 1850 enn senere, som tyder på ufullstendig registrering.`,
    sources: ['gvp_eruptions', 'silso_monthly'],
    columns: [
      { key: 'time_decimal', label: 'Tid (desimalår)', digits: 2 },
      { key: 'year', label: 'År' },
      { key: 'volcano', label: 'Vulkan' },
      { key: 'vei', label: 'VEI' },
      { key: 'precise_start', label: 'Presis startdato' },
    ],
    rows,
    rangeCol: 0,
    range: { min: 1500, max: 2026, presets: [250, 150] },
    csvName: 'vulkanutbrudd_vei4_og_over',
    legend: [
      { label: 'VEI 4', color: 'var(--s2)' },
      { label: 'VEI ≥ 5', color: 'var(--s1)' },
      { label: 'Solflekktall (glattet)', color: 'var(--s4)' },
    ],
    render: ({ width, range, pal }) => {
      const r: [number, number] = range ?? [1500, 2026];
      const d = idx.map((i) => ({
        x: e.t[i] as number,
        vei: e.vei[i] as number,
        v: e.volcano[i] as string,
        y: e.year[i] as number,
      }));
      const top = Plot.plot({
        ...baseOpts(width, pal, 200),
        x: { domain: r, label: null, tickFormat: (q: number) => String(q), ticks: Math.max(3, Math.floor(width / 90)) },
        y: { domain: [3.5, 7.5], ticks: [4, 5, 6, 7], label: 'VEI', labelAnchor: 'top' },
        r: { range: [3, 10], domain: [4, 7] },
        marks: [
          Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 }),
          Plot.dot(
            d.filter((q) => q.x >= r[0] && q.x <= r[1]),
            {
              x: 'x',
              y: 'vei',
              r: 'vei',
              fill: (q: { vei: number }) => (q.vei >= 5 ? pal.s1 : pal.s2),
              fillOpacity: 0.65,
              stroke: pal.bg,
              title: (q: { v: string; y: number; vei: number }) => `${q.v} ${q.y}, VEI ${q.vei}`,
            },
          ),
        ],
      });
      const bottom = timeSeries({
        width,
        pal,
        range: r,
        height: 170,
        yLabel: 'Solflekktall',
        series: [{ name: 'Glattet', color: pal.s4, width: 1.8, data: pts(m.t, m.smoothed) }],
        yDomain: [0, 300],
      });
      return stack(top, bottom);
    },
  };
}

export async function volcanoReporting(): Promise<ChartInstance> {
  const a = await getJSON('analysis_volcano.json');
  const r = a.reporting;
  const cats = r.bins.map((b: number) => `${b}–${b + 49}`);
  const data = cats.flatMap((c: string, i: number) => [
    { cat: c, series: 'VEI ≥ 4', v: r.vei4[i] },
    { cat: c, series: 'VEI ≥ 5', v: r.vei5[i] },
  ]);
  return {
    title: 'Antall registrerte utbrudd per 50 år: ufullstendig i eldre tid',
    subtitle:
      'Bekreftede utbrudd i GVP. Økningen mot nåtid speiler bedre registrering, ikke nødvendigvis flere utbrudd.',
    alt: `Antall utbrudd med VEI ≥ 4 per 50-årsperiode stiger fra ${r.vei4[0]} (1500–1549) til ${Math.max(...r.vei4)} (maks) mens antallet VEI ≥ 5 er mer stabilt (${Math.min(...r.vei5.slice(1))}–${Math.max(...r.vei5)}).`,
    sources: ['gvp_eruptions'],
    columns: [
      { key: 'period', label: 'Periode' },
      { key: 'vei_ge3', label: 'VEI ≥ 3' },
      { key: 'vei_ge4', label: 'VEI ≥ 4' },
      { key: 'vei_ge5', label: 'VEI ≥ 5' },
    ],
    rows: cats.map((c: string, i: number) => [c, r.vei3[i], r.vei4[i], r.vei5[i]]),
    tableOpen: true,
    csvName: 'registrerte_utbrudd_per_50_aar',
    legend: [
      { label: 'VEI ≥ 4', color: 'var(--s2)' },
      { label: 'VEI ≥ 5', color: 'var(--s1)' },
    ],
    render: ({ width, pal }) =>
      barsByCategory({
        width,
        pal,
        data,
        colors: { 'VEI ≥ 4': pal.s2, 'VEI ≥ 5': pal.s1 },
        yLabel: 'Utbrudd per 50 år',
        height: 280,
      }),
  };
}

export async function volcanoPhase(): Promise<ChartInstance> {
  const a = await getJSON('analysis_volcano.json');
  const A = sc(a, 'A'),
    B = sc(a, 'B');
  const labs = ['0–25 %', '25–50 %', '50–75 %', '75–100 %'];
  const mk = (s: any) =>
    labs.flatMap((l, i) => [
      { cat: `${s.label}`, series: `${l} observert`, v: s.phase.observed[i], phase: l },
      { cat: `${s.label}`, series: `${l} forventet`, v: s.phase.expected[i], phase: l },
    ]);
  void mk;
  return {
    title: 'Utbrudd fordelt på fase i solsyklusen',
    subtitle:
      'Antall observerte utbrudd per kvartal av solsyklusen (0 % = minimum) mot antallet som ville forventes hvis utbruddene var jevnt fordelt i tid.',
    alt: `Observerte og forventede utbrudd per fase i solsyklusen. VEI ≥ 4, 1850–2019 (${A.n_events} utbrudd): observert ${A.phase.observed.join(', ')} mot forventet ${A.phase.expected.map((v: number) => num(v, 1)).join(', ')} (p = ${pval(A.phase.p)}). VEI ≥ 5, 1755–2019 (${B.n_events} utbrudd): observert ${B.phase.observed.join(', ')} (p = ${pval(B.phase.p)}).`,
    sources: ['gvp_eruptions', 'silso_monthly'],
    columns: [
      { key: 'scenario', label: 'Scenario' },
      { key: 'phase', label: 'Fase' },
      { key: 'observed', label: 'Observert' },
      { key: 'expected', label: 'Forventet', digits: 1 },
    ],
    rows: [A, B].flatMap((s) => labs.map((l, i) => [s.label, l, s.phase.observed[i], s.phase.expected[i]])),
    csvName: 'vulkanutbrudd_per_syklusfase',
    legend: [
      { label: 'Observert', color: 'var(--s1)' },
      { label: 'Forventet', color: 'var(--s5)' },
    ],
    render: ({ width, pal }) => {
      const panel = (s: any) => {
        const d = labs.flatMap((l, i) => [
          { ph: l, k: 'Observert', v: s.phase.observed[i] as number },
          { ph: l, k: 'Forventet', v: s.phase.expected[i] as number },
        ]);
        return Plot.plot({
          ...baseOpts(width, pal, 240),
          marginBottom: 56,
          title: undefined,
          x: { axis: null, domain: ['Observert', 'Forventet'] },
          fx: {
            label: `${s.label} (${s.n_events} utbrudd)`,
            domain: labs,
            tickSize: 0,
            padding: 0.15,
            labelAnchor: 'center',
          },
          y: { label: 'Utbrudd', grid: false, labelAnchor: 'top' },
          color: { domain: ['Observert', 'Forventet'], range: [pal.s1, pal.s5] },
          marks: [
            Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 }),
            Plot.barY(d, { x: 'k', y: 'v', fx: 'ph', fill: 'k' }),
            Plot.ruleY([0], { stroke: pal.muted }),
          ],
        });
      };
      return stack(panel(A), panel(B));
    },
  };
}

export async function volcanoSea(): Promise<ChartInstance> {
  const a = await getJSON('analysis_volcano.json');
  const A = sc(a, 'A'),
    B = sc(a, 'B');
  return {
    title: 'Superposed epoch: solflekktall rundt utbruddene',
    subtitle:
      'Gjennomsnittlig standardisert solflekktall (z) i år −5 til +5 rundt utbruddsåret, mot båndet (95 %) som tilfeldig plasserte utbruddsrekker gir.',
    alt: `Gjennomsnittlig solflekktall rundt utbruddene mot 95 %-bånd fra ${num(a.n_shifts, 0)} sirkulært forskjøvede utbruddsrekker. VEI ≥ 4 (1850–2019): største avvik ${num(A.sea.max_abs_z, 1)} standardavvik, global p = ${pval(A.sea.p_global)}. VEI ≥ 5: største avvik ${num(B.sea.max_abs_z, 1)}, global p = ${pval(B.sea.p_global)}.`,
    sources: ['gvp_eruptions', 'silso_monthly'],
    columns: [
      { key: 'scenario', label: 'Scenario' },
      { key: 'lag_years', label: 'År relativt utbrudd' },
      { key: 'composite_z', label: 'Gj.snitt z', digits: 3 },
      { key: 'null_mean', label: 'Nullforventning', digits: 3 },
      { key: 'band_lo', label: 'Nullbånd 2,5 %', digits: 3 },
      { key: 'band_hi', label: 'Nullbånd 97,5 %', digits: 3 },
    ],
    rows: [A, B].flatMap((s) =>
      s.sea.lags.map((l: number, i: number) => [
        s.label,
        l,
        s.sea.composite_z[i],
        s.sea.null_mean[i],
        s.sea.band_lo[i],
        s.sea.band_hi[i],
      ]),
    ),
    csvName: 'vulkan_superposed_epoch',
    legend: [
      { label: 'Observert', color: 'var(--s1)' },
      { label: '95 %-bånd under nullhypotesen', color: 'var(--s5)' },
    ],
    render: ({ width, pal }) => {
      const panel = (s: any) => {
        const d = s.sea.lags.map((l: number, i: number) => ({
          x: l,
          y: s.sea.composite_z[i],
          lo: s.sea.band_lo[i],
          hi: s.sea.band_hi[i],
        }));
        return Plot.plot({
          ...baseOpts(width, pal, 230),
          x: {
            label: 'År relativt utbruddsåret',
            ticks: 11,
            tickFormat: (q: number) => String(q),
            labelAnchor: 'right',
          },
          y: { label: `z · ${s.label}`, grid: false, labelAnchor: 'top' },
          marks: [
            Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 }),
            Plot.areaY(d, { x: 'x', y1: 'lo', y2: 'hi', fill: pal.s5, fillOpacity: 0.25 }),
            Plot.ruleY([0], { stroke: pal.muted }),
            Plot.ruleX([0], { stroke: pal.muted, strokeDasharray: '4 3' }),
            Plot.line(d, { x: 'x', y: 'y', stroke: pal.s1, strokeWidth: 2.4 }),
            Plot.dot(d, {
              x: 'x',
              y: 'y',
              fill: pal.s1,
              r: 3.5,
              title: (q: { x: number; y: number }) => `år ${q.x}: z = ${q.y.toFixed(2)}`,
            }),
          ],
        });
      };
      return stack(panel(A), panel(B));
    },
  };
}

export async function volcanoScenarios(): Promise<ChartInstance> {
  const a = await getJSON('analysis_volcano.json');
  const s = a.scenarios as any[];
  return {
    title: 'Alle scenarier og tester',
    subtitle: `${a.n_tests} tester totalt (${a.n_primary_tests} primærtester med Holm-korreksjon). p-verdier fra ${num(a.n_shifts, 0)} sirkulære skift av utbruddsrekken.`,
    alt: `Tabell med seks scenarier. Minste Holm-justerte p-verdi blant primærtestene er ${pval(a.min_p_primary_adjusted)}. ${a.any_primary_significant ? 'Minst én primærtest er signifikant.' : 'Ingen primærtest er signifikant etter korreksjon for flere tester.'}`,
    sources: ['gvp_eruptions', 'silso_monthly'],
    columns: [
      { key: 'id', label: 'ID' },
      { key: 'scenario', label: 'Scenario' },
      { key: 'primary', label: 'Primær' },
      { key: 'n_events', label: 'Utbrudd' },
      { key: 'p_phase', label: 'p fase', digits: 4 },
      { key: 'p_high_low', label: 'p høy/lav', digits: 4 },
      { key: 'p_sea', label: 'p epoke', digits: 4 },
      { key: 'p_holm_min', label: 'Holm (primær, minste)', digits: 4 },
      { key: 'share_high', label: 'Andel i høy aktivitet', digits: 3 },
    ],
    rows: s.map((x) => [
      x.id,
      x.label,
      x.primary ? 'ja' : 'nei',
      x.n_events,
      x.phase.p,
      x.high_low.p,
      x.sea.p_global,
      x.primary ? Math.min(x.phase.p_holm, x.high_low.p_holm, x.sea.p_holm) : null,
      x.high_low.observed_share_high,
    ]),
    tableOpen: true,
    csvName: 'vulkan_alle_scenarier',
  };
  void last;
}
