import * as Plot from '@observablehq/plot';
import type { ChartInstance } from '../lib/chart';
import { getJSON, last } from '../lib/data';
import { decYear, isoDate, num } from '../lib/format';
import { baseOpts, timeSeries } from '../lib/plot';
import { dateTick, parseDay } from './common';

const nz = (v: number | null) => (v === null ? null : v);

export async function cycle25(): Promise<ChartInstance> {
  const [m, f, c] = await Promise.all([getJSON('ssn_monthly.json'), getJSON('cycle25_forecast.json'), getJSON('cycles.json')]);
  const cy = last(c.cycles as any[]);
  const t0 = Math.floor(cy.start_t) - 1;
  const idx: number[] = m.t.map((_: number, i: number) => i).filter((i: number) => m.t[i] >= t0);
  const rows = new Map<number, (number | null)[]>();
  for (const i of idx) rows.set(m.t[i], [nz(m.ssn[i]), nz(m.smoothed[i]), null, null, null]);
  f.t.forEach((t: number, i: number) => {
    const r = rows.get(t) ?? [null, null, null, null, null];
    r[2] = nz(f.ssn[i]);
    r[3] = nz(f.ssn_low[i]);
    r[4] = nz(f.ssn_high[i]);
    rows.set(t, r);
  });
  const sorted = [...rows.entries()].sort((a, b) => a[0] - b[0]);
  const lastSm = idx.filter((i) => m.smoothed[i] !== null).pop()!;
  const lastObs = idx.filter((i) => m.ssn[i] !== null).pop()!;
  const fl = f.ssn.length - 1;
  return {
    title: 'Solsyklus 25: observert og NOAAs prognose',
    subtitle: 'Månedlig solflekktall (SILSO V2.0), 13-måneders glattet verdi og prognose fra NOAA SWPC med usikkerhetsbånd.',
    alt: `Linjediagram over månedlig solflekktall siden ${decYear(sorted[0][0])}. Glattet verdi er ${num(m.smoothed[lastSm], 1)} i ${decYear(m.t[lastSm])}; siste månedsverdi er ${num(m.ssn[lastObs], 0)} i ${decYear(m.t[lastObs])}. NOAAs prognose går mot ${num(f.ssn[fl], 0)} i ${decYear(f.t[fl])} (bånd ${num(f.ssn_low[fl], 0)}–${num(f.ssn_high[fl], 0)}).`,
    sources: ['silso_monthly', 'swpc_cycle'],
    columns: [
      { key: 'year_decimal', label: 'Tid (desimalår)', digits: 3 },
      { key: 'monthly_ssn', label: 'Månedlig', digits: 1 },
      { key: 'smoothed_ssn', label: 'Glattet (13 mnd)', digits: 1 },
      { key: 'noaa_forecast', label: 'NOAA prognose', digits: 1 },
      { key: 'forecast_low', label: 'Prognose lav', digits: 1 },
      { key: 'forecast_high', label: 'Prognose høy', digits: 1 },
    ],
    rows: sorted.map(([t, r]) => [t, ...r]),
    csvName: 'solsyklus25_observert_og_prognose',
    legend: [
      { label: 'Månedlig', color: 'var(--s5)' },
      { label: 'Glattet (13 mnd)', color: 'var(--s1)' },
      { label: 'NOAA prognose', color: 'var(--s2)', dash: true },
    ],
    render: ({ width, pal }) =>
      timeSeries({
        width,
        pal,
        yLabel: 'Solflekktall',
        series: [
          { name: 'Månedlig', color: pal.s5, kind: 'dot', data: sorted.filter(([, r]) => r[0] !== null).map(([t, r]) => ({ x: t, y: r[0]! })) },
          { name: 'Glattet', color: pal.s1, width: 2.4, data: sorted.filter(([, r]) => r[1] !== null).map(([t, r]) => ({ x: t, y: r[1]! })) },
          { name: 'Prognose', color: pal.s2, dash: '6 4', width: 2.2, data: sorted.filter(([, r]) => r[2] !== null).map(([t, r]) => ({ x: t, y: r[2]! })) },
        ],
        band: { color: pal.s2, data: sorted.filter(([, r]) => r[3] !== null).map(([t, r]) => ({ x: t, lo: r[3]!, hi: r[4]! })) },
        yDomain: [0, 260],
      }),
  };
}

export async function ssnDaily(): Promise<ChartInstance> {
  const d = await getJSON('ssn_daily_recent.json');
  const days = d.date as string[];
  const e = d.eisn_date as string[];
  const map = new Map<string, (number | null)[]>();
  days.forEach((s, i) => map.set(s, [d.ssn[i], null]));
  e.forEach((s, i) => {
    const r = map.get(s) ?? [null, null];
    r[1] = d.eisn[i];
    map.set(s, r);
  });
  const rows = [...map.entries()].sort((a, b) => (a[0] < b[0] ? -1 : 1));
  const lastE = e.length - 1;
  return {
    title: 'Daglig solflekktall siste to år',
    subtitle: 'Endelig dagsverdi (SILSO V2.0) og estimert internasjonalt solflekktall i nær sanntid (EISN).',
    alt: `Daglig solflekktall de siste ${days.length} dagene. Siste EISN-verdi er ${d.eisn[lastE]} den ${isoDate(e[lastE])}. Dagsverdiene varierer sterkt fra dag til dag.`,
    sources: ['silso_daily'],
    columns: [
      { key: 'date', label: 'Dato' },
      { key: 'silso_v2_daily', label: 'SILSO V2.0 daglig', digits: 0 },
      { key: 'eisn', label: 'EISN (foreløpig)', digits: 0 },
    ],
    rows: rows.map(([s, r]) => [s, r[0], r[1]]),
    csvName: 'solflekktall_daglig_siste_to_aar',
    legend: [
      { label: 'SILSO V2.0 (endelig)', color: 'var(--s1)' },
      { label: 'EISN (foreløpig)', color: 'var(--s2)' },
    ],
    render: ({ width, pal }) => {
      const mk = (idx: 0 | 1) => rows.filter(([, r]) => r[idx] !== null).map(([s, r]) => ({ x: parseDay(s), y: r[idx]! }));
      return Plot.plot({
        ...baseOpts(width, pal, 260),
        x: { type: 'utc', label: null, ticks: Math.max(3, Math.floor(width / 110)), tickFormat: (dt: Date) => `${dt.toLocaleDateString('nb-NO', { month: 'short', year: '2-digit', timeZone: 'UTC' })}` },
        y: { label: 'Solflekktall', grid: false, labelAnchor: 'top' },
        marks: [
          Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 }),
          Plot.ruleY([0], { stroke: pal.muted }),
          Plot.dot(mk(0), { x: 'x', y: 'y', fill: pal.s1, r: 1.8, fillOpacity: 0.75 }),
          Plot.line(mk(1), { x: 'x', y: 'y', stroke: pal.s2, strokeWidth: 1.5 }),
          Plot.tip(mk(1), Plot.pointerX({ x: 'x', y: 'y', fill: pal.bg, stroke: pal.border, title: (p: { x: Date; y: number }) => `${isoDate(p.x.toISOString())}\nEISN ${p.y}` })),
        ],
      });
    },
  };
}

export async function f107Recent(): Promise<ChartInstance> {
  const d = await getJSON('recent30.json');
  const n = d.date.length;
  const mean = d.f107.filter((v: number | null) => v !== null).reduce((a: number, b: number) => a + b, 0) / d.f107.filter((v: number | null) => v !== null).length;
  return {
    title: 'Radiofluks F10.7, siste 30 dager',
    subtitle: 'Solens radiostråling ved 10,7 cm (2800 MHz) i solar flux units (sfu), daglig middagsmåling.',
    alt: `Daglig F10.7 de siste ${n} dagene. Siste verdi er ${d.f107[n - 1]} sfu den ${isoDate(d.date[n - 1])}; gjennomsnittet i perioden er ${num(mean, 0)} sfu.`,
    sources: ['swpc_recent'],
    columns: [
      { key: 'date', label: 'Dato' },
      { key: 'f107_sfu', label: 'F10.7 (sfu)', digits: 0 },
      { key: 'sesc_sunspot_number', label: 'SESC-solflekktall', digits: 0 },
    ],
    rows: d.date.map((s: string, i: number) => [s, d.f107[i], d.sesc_ssn[i]]),
    csvName: 'f107_siste_30_dager',
    render: ({ width, pal }) =>
      Plot.plot({
        ...baseOpts(width, pal, 240),
        x: { type: 'utc', label: null, ticks: Math.max(3, Math.floor(width / 100)), tickFormat: dateTick },
        y: { label: 'sfu', grid: false, labelAnchor: 'top', domain: [60, Math.max(160, ...d.f107.filter((v: number | null) => v !== null))] },
        marks: [
          Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 }),
          Plot.line(
            d.date.map((s: string, i: number) => ({ x: parseDay(s), y: d.f107[i] })),
            { x: 'x', y: 'y', stroke: pal.s1, strokeWidth: 2 },
          ),
          Plot.dot(
            d.date.map((s: string, i: number) => ({ x: parseDay(s), y: d.f107[i] })),
            { x: 'x', y: 'y', fill: pal.s1, r: 2.5 },
          ),
          Plot.tip(
            d.date.map((s: string, i: number) => ({ x: parseDay(s), y: d.f107[i] })),
            Plot.pointerX({ x: 'x', y: 'y', fill: pal.bg, stroke: pal.border, title: (p: { x: Date; y: number }) => `${isoDate(p.x.toISOString())}\n${p.y} sfu` }),
          ),
        ],
      }),
  };
}

export async function kpRecent(): Promise<ChartInstance> {
  const d = await getJSON('kp_recent.json');
  const n = d.time.length;
  const mx = Math.max(...d.kp);
  return {
    title: 'Geomagnetisk aktivitet (Kp), siste 30 dager',
    subtitle: 'Planetarisk Kp-indeks hver tredje time (0–9). Kp ≥ 5 tilsvarer geomagnetisk storm (NOAA G1 eller sterkere).',
    alt: `Kp-indeks hver tredje time de siste ${num(n / 8, 0)} dagene. Høyeste verdi er ${num(mx, 1)}; siste verdi er ${num(d.kp[n - 1], 1)} (${d.time[n - 1].replace('T', ' ')} UTC). Kilde: ${d.origin}.`,
    sources: ['kp_recent'],
    columns: [
      { key: 'time_utc', label: 'Tid (UTC)' },
      { key: 'kp', label: 'Kp', digits: 2 },
    ],
    rows: d.time.map((s: string, i: number) => [s, d.kp[i]]),
    csvName: 'kp_siste_30_dager',
    legend: [
      { label: 'Kp < 5', color: 'var(--s2)' },
      { label: 'Kp ≥ 5 (storm)', color: 'var(--s1)' },
    ],
    render: ({ width, pal }) => {
      const data = d.time.map((s: string, i: number) => ({ x: new Date(s + ':00Z'), y: d.kp[i] as number }));
      return Plot.plot({
        ...baseOpts(width, pal, 240),
        x: { type: 'utc', label: null, ticks: Math.max(3, Math.floor(width / 100)), tickFormat: dateTick },
        y: { label: 'Kp', domain: [0, 9], grid: false, labelAnchor: 'top', ticks: 9 },
        marks: [
          Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 }),
          Plot.rectY(data, { x1: (p: { x: Date }) => new Date(p.x.getTime() - 3600e3 * 1.3), x2: (p: { x: Date }) => new Date(p.x.getTime() + 3600e3 * 1.3), y: 'y', fill: (p: { y: number }) => (p.y >= 5 ? pal.s1 : pal.s2) }),
          Plot.ruleY([5], { stroke: pal.muted, strokeDasharray: '4 3' }),
          Plot.tip(data, Plot.pointerX({ x: 'x', y: 'y', fill: pal.bg, stroke: pal.border, title: (p: { x: Date; y: number }) => `${p.x.toISOString().slice(0, 16).replace('T', ' ')} UTC\nKp ${p.y}` })),
        ],
      });
    },
  };
}

// ---------- dashbordtall ----------
export async function initDashboard(root: HTMLElement): Promise<void> {
  const set = (name: string, text: string) => {
    const e = root.querySelector<HTMLElement>(`[data-field="${name}"]`);
    if (e) e.textContent = text;
  };
  const [daily, cyc, mon, recent, kp, man] = await Promise.all([
    getJSON('ssn_daily_recent.json'),
    getJSON('cycles.json'),
    getJSON('ssn_monthly.json'),
    getJSON('recent30.json'),
    getJSON('kp_recent.json'),
    getJSON('manifest.json'),
  ]);
  // Dagens solflekktall
  const ie = daily.eisn.length - 1;
  set('ssn-value', String(daily.eisn[ie]));
  const il = daily.ssn.map((v: number | null, i: number) => (v !== null ? i : -1)).filter((i: number) => i >= 0).pop();
  set(
    'ssn-note',
    `EISN (foreløpig estimat) for ${isoDate(daily.eisn_date[ie])}. Siste endelige verdi (SILSO V2.0): ${daily.ssn[il]} for ${isoDate(daily.date[il])}.`,
  );
  // Syklus 25
  const c25 = last(cyc.cycles as any[]);
  const lastSm = mon.smoothed.map((v: number | null, i: number) => (v !== null ? i : -1)).filter((i: number) => i >= 0).pop();
  const lastMon = mon.ssn.map((v: number | null, i: number) => (v !== null ? i : -1)).filter((i: number) => i >= 0).pop();
  set('cycle-value', num(c25.max_smoothed, 0));
  set(
    'cycle-note',
    `Høyeste glattede verdi så langt (${decYear(c25.max_t)}). Syklus 25 startet ${decYear(c25.start_t)}. Siste glattede verdi: ${num(mon.smoothed[lastSm], 1)} (${decYear(mon.t[lastSm])}); siste månedsverdi: ${num(mon.ssn[lastMon], 0)} (${decYear(mon.t[lastMon])}).`,
  );
  // F10.7
  const ir = recent.f107.length - 1;
  const vals = recent.f107.filter((v: number | null) => v !== null) as number[];
  set('f107-value', `${recent.f107[ir]} sfu`);
  set('f107-note', `Målt ${isoDate(recent.date[ir])}. Gjennomsnitt siste ${vals.length} dager: ${num(vals.reduce((a, b) => a + b, 0) / vals.length, 0)} sfu.`);
  // Kp
  const nk = kp.kp.length;
  const last24 = kp.kp.slice(-8) as number[];
  set('kp-value', num(kp.kp[nk - 1], 1));
  set('kp-note', `Siste 24 timer: høyeste Kp ${num(Math.max(...last24), 1)}. Siste 30 dager: høyeste ${num(Math.max(...kp.kp), 1)} (${kp.time[kp.kp.indexOf(Math.max(...kp.kp))].slice(0, 10)}).`);
  // Ferskhet per dataserie
  const labels: Record<string, string> = {
    silso_daily: 'Daglig solflekktall (SILSO)',
    silso_monthly: 'Månedlig solflekktall (SILSO)',
    swpc_cycle: 'Prognose syklus 25 (NOAA)',
    swpc_recent: 'F10.7 (NOAA)',
    kp_recent: 'Kp (GFZ/NOAA)',
  };
  const fresh = root.querySelector<HTMLElement>('[data-field="freshness"]');
  if (fresh) {
    fresh.textContent = '';
    const ul = document.createElement('ul');
    ul.className = 'plain';
    for (const id of Object.keys(labels)) {
      const s = man.sources[id];
      if (!s) continue;
      const li = document.createElement('li');
      li.textContent = `${labels[id]}: sist endret ${s.fetched_at ? isoDate(s.fetched_at) : '–'}, siste datapunkt ${s.last_point ?? '–'}${s.status !== 'ok' ? ' (UTDATERT: siste oppdatering feilet)' : ''}`;
      ul.append(li);
    }
    const h = document.createElement('strong');
    h.textContent = 'Sist oppdatert per dataserie:';
    fresh.append(h, ul);
  }
}
