import * as Plot from '@observablehq/plot';
import type { ChartInstance } from '../lib/chart';
import { getJSON, last, pts } from '../lib/data';
import { num } from '../lib/format';
import { baseOpts, stack, timeSeries } from '../lib/plot';
import { barsByCategory, lagColumns, lagPlot, lagRows, rolling } from './common';

// ---------------- TSI ----------------
export async function tsiSeries(): Promise<ChartInstance> {
  const [t, s] = await Promise.all([getJSON('tsi_yearly.json'), getJSON('tsi_tsis_monthly.json')]);
  const x = t.year.map((v: number) => v + 0.5);
  const rows = [
    ...t.year.map((y: number, i: number) => [y + 0.5, t.tsi[i], null] as (number | null)[]),
    ...s.t.map((tt: number, i: number) => [tt, null, s.tsi[i]] as (number | null)[]),
  ];
  return {
    title: 'Total solinnstråling (TSI) 1850–i dag',
    subtitle:
      'Årsmiddel fra NOAA CDR (modell, NNLTSI) og månedlig måling fra TSIS-1 (2018–). Merk den korte y-aksen: variasjonen er rundt 0,1 %.',
    alt: `TSI i watt per kvadratmeter ved ett astronomisk enhet. NNLTSI-modellen varierer mellom ca. ${num(Math.min(...t.tsi.filter((v: number | null) => v !== null)), 1)} og ${num(Math.max(...t.tsi.filter((v: number | null) => v !== null)), 1)} W/m² siden 1610, med en syklus på omtrent 1 W/m². TSIS-1 viser økningen i syklus 25.`,
    sources: ['tsi'],
    columns: [
      { key: 'year_decimal', label: 'Tid (desimalår)', digits: 3 },
      { key: 'nnl_tsi_wm2', label: 'NNLTSI (modell), årlig', digits: 3 },
      { key: 'tsis1_tsi_wm2', label: 'TSIS-1 (måling), månedlig', digits: 3 },
    ],
    rows,
    rangeCol: 0,
    range: { min: 1850, max: 2027, presets: [100, 50] },
    csvName: 'total_solinnstraling',
    legend: [
      { label: 'NNLTSI årlig (modell)', color: 'var(--s1)' },
      { label: 'TSIS-1 månedlig (måling)', color: 'var(--s2)' },
    ],
    render: ({ width, range, pal }) =>
      timeSeries({
        width,
        pal,
        range: range ?? [1850, 2027],
        yLabel: 'W/m²',
        series: [
          { name: 'NNLTSI', color: pal.s1, width: 2, data: pts(x, t.tsi) },
          { name: 'TSIS-1', color: pal.s2, width: 1.6, data: pts(s.t, s.tsi) },
        ],
        yDomain: [1360.4, 1363.2],
      }),
  };
}

export async function tsiCycleRange(): Promise<ChartInstance> {
  const a = await getJSON('analysis_tsi.json');
  const cyc = a.per_cycle as { cycle: number; range_wm2: number }[];
  return {
    title: 'Variasjon i TSI innenfor hver solsyklus (modell)',
    subtitle: 'Forskjell mellom høyeste og laveste årsmiddel innenfor syklusen, NNLTSI.',
    alt: `Stolpediagram over TSI-variasjonen per solsyklus (syklus ${cyc[0].cycle}–${last(cyc).cycle}). Gjennomsnittet for syklus 20–24 er ${num(a.mean_range_cycles_20_24, 2)} W/m², omtrent ${num(a.mean_range_pct, 3)} %.`,
    sources: ['tsi', 'silso_monthly'],
    columns: [
      { key: 'cycle', label: 'Syklus' },
      { key: 'tsi_max', label: 'Høyeste årsmiddel (W/m²)', digits: 3 },
      { key: 'tsi_min', label: 'Laveste årsmiddel (W/m²)', digits: 3 },
      { key: 'range', label: 'Variasjon (W/m²)', digits: 3 },
    ],
    rows: a.per_cycle.map((c: any) => [c.cycle, c.tsi_max, c.tsi_min, c.range_wm2]),
    csvName: 'tsi_variasjon_per_syklus',
    render: ({ width, pal }) =>
      Plot.plot({
        ...baseOpts(width, pal, 260),
        x: { label: 'Solsyklus', tickFormat: (d: number) => String(d), padding: 0.2 },
        y: { label: 'W/m²', grid: false, labelAnchor: 'top', domain: [0, 1.6] },
        marks: [
          Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 }),
          Plot.barY(cyc, {
            x: 'cycle',
            y: 'range_wm2',
            fill: pal.s1,
            title: (c: { cycle: number; range_wm2: number }) => `Syklus ${c.cycle}: ${c.range_wm2.toFixed(2)} W/m²`,
          }),
          Plot.ruleY([0], { stroke: pal.muted }),
        ],
      }),
  };
}

// ---------------- Temperatur ----------------
export async function tempSeries(): Promise<ChartInstance> {
  const [ta, a] = await Promise.all([getJSON('temp_annual.json'), getJSON('analysis_temperature.json')]);
  const ssn = a.series as { year: number[]; ssn_smooth11: (number | null)[] };
  const rows = ta.year.map((y: number, i: number) => {
    const j = ssn.year.indexOf(y);
    return [y, ta.gistemp[i], ta.hadcrut5[i], j >= 0 ? ssn.ssn_smooth11[j] : null];
  });
  const xs = ta.year.map((y: number) => y + 0.5);
  return {
    title: 'Global temperatur og solaktivitet 1850–2025',
    subtitle:
      'Øverst: årlig global temperaturanomali (referanse 1961–1990). Nederst: solflekktall, 11-årig glidende middel. Stiplet linje: 1980.',
    alt: `To paneler. Øverst stiger global temperatur fra rundt −0,3 °C (1880) til ca. +${num(ta.gistemp[ta.gistemp.length - 1], 1)} °C anomali i 2025. Nederst svinger det glattede solflekktallet i 11-års sykluser uten stigende trend siden 1950-tallet. Etter 1980 divergerer seriene.`,
    sources: ['temperature', 'silso_monthly'],
    columns: [
      { key: 'year', label: 'År' },
      { key: 'gistemp_anomaly_c', label: 'GISTEMP (°C)', digits: 3 },
      { key: 'hadcrut5_anomaly_c', label: 'HadCRUT5 (°C)', digits: 3 },
      { key: 'ssn_11yr_mean', label: 'Solflekktall, 11-års middel', digits: 1 },
    ],
    rows,
    rangeCol: 0,
    range: { min: 1850, max: 2025, presets: [100, 50] },
    csvName: 'global_temperatur_og_solflekktall_aarlig',
    legend: [
      { label: 'GISTEMP v4', color: 'var(--s1)' },
      { label: 'HadCRUT5', color: 'var(--s2)' },
      { label: 'Solflekktall (11-års middel)', color: 'var(--s4)' },
    ],
    render: ({ width, range, pal }) => {
      const r: [number, number] = range ? [range[0], range[1] + 1] : [1850, 2026];
      const top = timeSeries({
        width,
        pal,
        range: r,
        height: 250,
        yLabel: 'Temperaturanomali (°C)',
        series: [
          { name: 'HadCRUT5', color: pal.s2, width: 1.8, data: pts(xs, ta.hadcrut5) },
          { name: 'GISTEMP', color: pal.s1, width: 1.8, data: pts(xs, ta.gistemp) },
        ],
        vlines: [{ x: 1980, label: '1980' }],
        zeroLine: true,
      });
      const sx = ssn.year.map((y) => y + 0.5);
      const bottom = timeSeries({
        width,
        pal,
        range: r,
        height: 190,
        yLabel: 'Solflekktall (11 år)',
        series: [{ name: 'Solflekktall', color: pal.s4, width: 2.2, data: pts(sx, ssn.ssn_smooth11) }],
        vlines: [{ x: 1980 }],
        yDomain: [0, 130],
      });
      return stack(top, bottom);
    },
  };
}

export async function lagScanTemp(): Promise<ChartInstance> {
  const a = await getJSON('analysis_temperature.json');
  const g = a.scan_gistemp,
    h = a.scan_hadcrut5;
  return {
    title: 'Korrelasjon mellom solflekktall og temperatur ved ulike forsinkelser',
    subtitle: `Årlige verdier, temperatur uten jevn langtidstrend. ${g.n_tests + h.n_tests} tester (lag 0–10 år for to temperaturserier), ${num(g.n_surrogates, 0)} fase-surrogater per lag. Fylte punkter = signifikant etter Holm-korreksjon.`,
    alt: `Korrelasjonskoeffisienter mellom solflekktall og detrendet global temperatur for forsinkelser 0–10 år. Sterkeste korrelasjon er r = ${num(g.best_r, 2)} (GISTEMP, forsinkelse ${g.best_lag} år); familievis p-verdi ${num(g.p_family, 2)}. Ingen forsinkelse er signifikant etter korreksjon for flere tester.`,
    sources: ['temperature', 'silso_monthly'],
    columns: [{ key: 'serie', label: 'Temperaturserie' }, ...lagColumns()],
    rows: [...lagRows(g.lags, 'GISTEMP'), ...lagRows(h.lags, 'HadCRUT5')],
    csvName: 'korrelasjon_solflekktall_temperatur_per_lag',
    legend: [
      { label: 'GISTEMP', color: 'var(--s1)' },
      { label: 'HadCRUT5', color: 'var(--s2)' },
    ],
    render: ({ width, pal }) =>
      lagPlot({
        width,
        pal,
        sets: [
          { name: 'GISTEMP', color: pal.s1, rows: g.lags },
          { name: 'HadCRUT5', color: pal.s2, rows: h.lags },
        ],
      }),
  };
}

// ---------------- Kosmisk stråling ----------------
export async function cosmicSeries(): Promise<ChartInstance> {
  const [c, m] = await Promise.all([getJSON('cosmic_phi_monthly.json'), getJSON('ssn_monthly.json')]);
  const phi13 = rolling(c.phi, 13);
  const rows = c.t.map((t: number, i: number) => {
    const j = m.t.indexOf(t);
    return [t, c.phi[i], j >= 0 ? m.smoothed[j] : null];
  });
  return {
    title: 'Kosmisk stråling (modulasjonspotensial Φ) og solflekktall',
    subtitle:
      'Høy Φ = sterk skjerming fra solvinden = lav intensitet av kosmisk stråling ved Jorden. Φ er rekonstruert fra bakkebaserte nøytronmonitorer.',
    alt: `To paneler 1936–2025. Φ (øverst) og glattet solflekktall (nederst) følger hverandre: Φ er høy når solflekktallet er høyt, noe som betyr at kosmisk stråling er lavest ved solmaksimum.`,
    sources: ['cosmic', 'silso_monthly'],
    columns: [
      { key: 'year_decimal', label: 'Tid (desimalår)', digits: 3 },
      { key: 'phi_mv', label: 'Φ (MV)', digits: 0 },
      { key: 'smoothed_ssn', label: 'Solflekktall (glattet)', digits: 1 },
    ],
    rows,
    rangeCol: 0,
    range: { min: c.t[0], max: last(c.t), presets: [50, 25] },
    csvName: 'kosmisk_straling_phi_og_solflekktall',
    legend: [
      { label: 'Φ (13 mnd middel)', color: 'var(--s3)' },
      { label: 'Solflekktall (glattet)', color: 'var(--s1)' },
    ],
    render: ({ width, range, pal }) => {
      const top = timeSeries({
        width,
        pal,
        range,
        height: 230,
        yLabel: 'Φ (MV)',
        series: [
          { name: 'Φ månedlig', color: pal.s3, width: 0.8, opacity: 0.45, data: pts(c.t, c.phi) },
          { name: 'Φ 13 mnd', color: pal.s3, width: 2.2, data: pts(c.t, phi13) },
        ],
      });
      const bottom = timeSeries({
        width,
        pal,
        range,
        height: 190,
        yLabel: 'Solflekktall',
        series: [{ name: 'Solflekktall', color: pal.s1, width: 2, data: pts(m.t, m.smoothed) }],
        yDomain: [0, 260],
      });
      return stack(top, bottom);
    },
  };
}

export async function lagScanCosmic(): Promise<ChartInstance> {
  const a = await getJSON('analysis_cosmic.json');
  const s = a.scan_phi_ssn;
  return {
    title: 'Φ mot solflekktall: korrelasjon ved ulike forsinkelser',
    subtitle: `Årlige verdier ${s.period[0]}–${s.period[1]}. ${s.n_tests} tester, ${num(a.n_surrogates, 0)} surrogater. Positiv forsinkelse = solflekktallet leder Φ.`,
    alt: `Korrelasjon mellom årlig solflekktall og Φ for forsinkelser −2 til +3 år. Sterkeste korrelasjon er r = ${num(s.best_r, 2)} ved forsinkelse ${s.best_lag} år (familievis p ${s.p_family < 0.001 ? '< 0,001' : num(s.p_family, 3)}). Φ henger omtrent ett år etter solflekktallet.`,
    sources: ['cosmic', 'silso_monthly'],
    columns: lagColumns(),
    rows: lagRows(s.lags),
    csvName: 'korrelasjon_phi_solflekktall_per_lag',
    render: ({ width, pal }) =>
      lagPlot({ width, pal, sets: [{ name: 'Φ', color: pal.s3, rows: s.lags }], xLabel: 'Forsinkelse (år)' }),
  };
}

// ---------------- Geomagnetisk ----------------
export async function geomagAnnual(): Promise<ChartInstance> {
  const a = await getJSON('analysis_geomag.json');
  const sc = a.scatter as { year: number[]; ssn: number[]; storm_days: number[] };
  const x = sc.year.map((y) => y + 0.5);
  return {
    title: 'Geomagnetiske stormdøgn per år og solflekktall',
    subtitle: 'Stormdøgn = døgn med Kp ≥ 5 (GFZ). Nederst: årlig solflekktall (SILSO).',
    alt: `Antall døgn per år med Kp ≥ 5, ${sc.year[0]}–${last(sc.year)}, og solflekktall. Stormdøgnene følger solsyklusen, men toppene kommer ofte i avtagende fase, og antallet varierer mellom ${Math.min(...sc.storm_days)} og ${Math.max(...sc.storm_days)} døgn per år.`,
    sources: ['gfz_kp', 'silso_monthly'],
    columns: [
      { key: 'year', label: 'År' },
      { key: 'storm_days_kp_ge5', label: 'Døgn med Kp ≥ 5' },
      { key: 'ssn_annual', label: 'Solflekktall (årsmiddel)', digits: 1 },
    ],
    rows: sc.year.map((y, i) => [y, sc.storm_days[i], sc.ssn[i]]),
    rangeCol: 0,
    range: { min: sc.year[0], max: last(sc.year), presets: [50, 25] },
    csvName: 'geomagnetiske_stormdogn_og_solflekktall',
    legend: [
      { label: 'Døgn med Kp ≥ 5', color: 'var(--s2)' },
      { label: 'Solflekktall', color: 'var(--s1)' },
    ],
    render: ({ width, range, pal }) => {
      const r: [number, number] = range ? [range[0], range[1] + 1] : [sc.year[0], last(sc.year) + 1];
      const top = timeSeries({
        width,
        pal,
        range: r,
        height: 240,
        yLabel: 'Stormdøgn per år',
        series: [{ name: 'Stormdøgn', color: pal.s2, kind: 'bar', data: pts(x, sc.storm_days) }],
        yDomain: [0, Math.max(...sc.storm_days) * 1.1],
      });
      const bottom = timeSeries({
        width,
        pal,
        range: r,
        height: 190,
        yLabel: 'Solflekktall',
        series: [{ name: 'Solflekktall', color: pal.s1, width: 2, data: pts(x, sc.ssn) }],
        yDomain: [0, 220],
      });
      return stack(top, bottom);
    },
  };
}

export async function geomagPhase(): Promise<ChartInstance> {
  const a = await getJSON('analysis_geomag.json');
  const p = a.phase_profile;
  const bins = Array.from({ length: p.bins }, (_, i) => `${i * 10}–${(i + 1) * 10} %`);
  return {
    title: 'Geomagnetiske stormer etter fase i solsyklusen',
    subtitle: `Gjennomsnitt over ${p.n_cycles} fullførte sykluser (syklus ${p.cycles[0]}–${last(p.cycles as number[])}). Streker viser ±1 standardavvik mellom syklusene.`,
    alt: `Gjennomsnittlig antall stormdøgn (Kp ≥ 5) per måned fordelt på ti faser av solsyklusen. Aktiviteten er lavest nær minimum og høyest i fase ${p.storm_peak_bin * 10}–${(p.storm_peak_bin + 1) * 10} %, altså etter solflekkmaksimum, i den avtagende fasen.`,
    sources: ['gfz_kp', 'silso_monthly'],
    columns: [
      { key: 'phase', label: 'Fase av syklusen' },
      { key: 'storm_days_per_month', label: 'Stormdøgn per måned', digits: 2 },
      { key: 'storm_sd', label: 'Standardavvik mellom sykluser', digits: 2 },
      { key: 'ap_mean', label: 'ap (gj.snitt)', digits: 2 },
      { key: 'mean_ssn', label: 'Solflekktall (glattet, gj.snitt)', digits: 1 },
    ],
    rows: bins.map((b, i) => [b, p.storm_days[i], p.storm_sd[i], p.ap[i], p.ssn[i]]),
    tableOpen: false,
    csvName: 'geomagnetiske_stormer_per_syklusfase',
    legend: [
      { label: 'Stormdøgn per måned', color: 'var(--s2)' },
      { label: 'Solflekktall (glattet)', color: 'var(--s1)' },
    ],
    render: ({ width, pal }) => {
      const d = bins.map((b, i) => ({
        b,
        v: p.storm_days[i] as number,
        lo: p.storm_days[i] - p.storm_sd[i],
        hi: p.storm_days[i] + p.storm_sd[i],
        ssn: p.ssn[i] as number,
      }));
      const top = Plot.plot({
        ...baseOpts(width, pal, 240),
        x: { label: null, domain: bins, axis: null },
        y: {
          label: 'Stormdøgn per måned',
          grid: false,
          labelAnchor: 'top',
          domain: [0, Math.max(...d.map((q) => q.hi)) * 1.1],
        },
        marks: [
          Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 }),
          Plot.barY(d, { x: 'b', y: 'v', fill: pal.s2 }),
          Plot.ruleX(d, { x: 'b', y1: 'lo', y2: 'hi', stroke: pal.fg, strokeWidth: 1.5 }),
          Plot.ruleY([0], { stroke: pal.muted }),
        ],
      });
      const bottom = Plot.plot({
        ...baseOpts(width, pal, 190),
        x: {
          label: 'Fase av solsyklusen (0 % = minimum, 100 % = neste minimum)',
          domain: bins,
          labelAnchor: 'center',
          tickSize: 0,
        },
        y: { label: 'Solflekktall', grid: false, labelAnchor: 'top', domain: [0, 220] },
        marks: [
          Plot.gridY({ stroke: pal.grid, strokeOpacity: 0.7 }),
          Plot.barY(d, { x: 'b', y: 'ssn', fill: pal.s1 }),
          Plot.ruleY([0], { stroke: pal.muted }),
        ],
      });
      return stack(top, bottom);
    },
  };
}

// ---------------- Maunder / vulkansk forcing ----------------
export async function maunderChart(): Promise<ChartInstance> {
  const a = await getJSON('analysis_maunder.json');
  const s = a.series;
  const x = s.year.map((y: number) => y + 0.5);
  return {
    title: 'Solflekkgrupper og vulkansk sulfatinjeksjon 1600–1900',
    subtitle:
      'Øverst: årlig gruppesolflekktall (to rekonstruksjoner). Nederst: global stratosfærisk sulfatinjeksjon fra vulkanutbrudd (IVI2, Tg svovel).',
    alt: `Gruppesolflekktall 1600–1900 og vulkansk sulfatinjeksjon. Perioden 1645–1715 har svært få registrerte solflekkgrupper. Store vulkanutbrudd (høyest: ${a.ivi2_top_years
      .slice(0, 3)
      .map((e: any) => `${e.year}: ${num(e.global_tg, 0)} Tg`)
      .join(', ')}) opptrer både under og utenfor solminimumene.`,
    sources: ['silso_groups', 'ivi2'],
    columns: [
      { key: 'year', label: 'År' },
      { key: 'gn_backbone', label: 'Gruppetall, backbone', digits: 3 },
      { key: 'gn_hoyt_schatten', label: 'Gruppetall, Hoyt & Schatten', digits: 3 },
      { key: 'ivi2_global_tg', label: 'IVI2 global injeksjon (Tg)', digits: 2 },
    ],
    rows: s.year.map((y: number, i: number) => [y, s.gn_backbone[i], s.gn_hs[i], s.ivi2_global_tg[i]]),
    rangeCol: 0,
    range: { min: 1600, max: 1900, presets: [150] },
    csvName: 'maunder_gruppetall_og_vulkansk_injeksjon',
    legend: [
      { label: 'Gruppetall (backbone)', color: 'var(--s1)' },
      { label: 'Gruppetall (Hoyt & Schatten)', color: 'var(--s2)' },
      { label: 'Vulkansk sulfatinjeksjon', color: 'var(--s4)' },
    ],
    render: ({ width, range, pal }) => {
      const r: [number, number] = range ? [range[0], range[1] + 1] : [1600, 1901];
      const spans = [{ x1: 1645, x2: 1715, label: 'Maunder-minimum' }];
      const top = timeSeries({
        width,
        pal,
        range: r,
        height: 230,
        yLabel: 'Gruppetall',
        series: [
          { name: 'Backbone', color: pal.s1, width: 1.8, data: pts(x, s.gn_backbone) },
          { name: 'Hoyt & Schatten', color: pal.s2, width: 1.8, data: pts(x, s.gn_hs) },
        ],
        spans,
        yDomain: [0, 12],
      });
      const bottom = timeSeries({
        width,
        pal,
        range: r,
        height: 200,
        yLabel: 'Sulfat (Tg S)',
        series: [{ name: 'IVI2', color: pal.s4, kind: 'bar', data: pts(x, s.ivi2_global_tg) }],
        spans: [{ x1: 1645, x2: 1715, label: '' }],
        yDomain: [0, 110],
      });
      return stack(top, bottom);
    },
  };
}

// ---------------- Regionale mønstre ----------------
export async function regionalLag(): Promise<ChartInstance> {
  const a = await getJSON('analysis_regional.json');
  const n = a.scan_nao_djf,
    o = a.scan_oni_djf;
  return {
    title: 'Vinter-NAO og ENSO mot solflekktall: korrelasjon per forsinkelse',
    subtitle: `DJF-gjennomsnitt (desember–februar) ${n.period[0]}–${n.period[1]}, ${a.n_tests} tester totalt, ${num(a.n_surrogates, 0)} surrogater. Fylte punkter = signifikant etter Holm-korreksjon.`,
    alt: `Korrelasjon mellom årlig solflekktall og vinterverdier av NAO og ENSO (ONI) for forsinkelser 0–5 år. Sterkeste: NAO r = ${num(n.best_r, 2)} (forsinkelse ${n.best_lag}, familievis p = ${num(n.p_family, 2)}); ONI r = ${num(o.best_r, 2)} (forsinkelse ${o.best_lag}, familievis p = ${num(o.p_family, 2)}). Ingen er signifikante etter korreksjon.`,
    sources: ['climate_indices', 'silso_monthly'],
    columns: [{ key: 'indeks', label: 'Indeks' }, ...lagColumns()],
    rows: [...lagRows(n.lags, 'NAO (DJF)'), ...lagRows(o.lags, 'ONI (DJF)')],
    csvName: 'nao_enso_mot_solflekktall_per_lag',
    legend: [
      { label: 'NAO (DJF)', color: 'var(--s2)' },
      { label: 'ENSO / ONI (DJF)', color: 'var(--s3)' },
    ],
    render: ({ width, pal }) =>
      lagPlot({
        width,
        pal,
        sets: [
          { name: 'NAO', color: pal.s2, rows: n.lags },
          { name: 'ONI', color: pal.s3, rows: o.lags },
        ],
      }),
  };
}

export async function naoSeries(): Promise<ChartInstance> {
  const a = await getJSON('analysis_regional.json');
  const s = a.nao_series as { year: number[]; ssn: number[]; nao_djf: number[] };
  const x = s.year.map((y) => y + 0.5);
  return {
    title: 'Vinter-NAO (DJF) og solflekktall 1951–2025',
    subtitle: 'NAO-indeksen svinger kraftig fra år til år; solsyklusen forklarer ingen tydelig del av variasjonen.',
    alt: `Søyler: vinterlig NAO-indeks per år ${s.year[0]}–${last(s.year)}. Linje: årlig solflekktall. Det er ingen åpenbar sammenheng mellom de to seriene.`,
    sources: ['climate_indices', 'silso_monthly'],
    columns: [
      { key: 'year', label: 'År' },
      { key: 'nao_djf', label: 'NAO (DJF)', digits: 2 },
      { key: 'ssn', label: 'Solflekktall (årsmiddel)', digits: 1 },
    ],
    rows: s.year.map((y, i) => [y, s.nao_djf[i], s.ssn[i]]),
    csvName: 'nao_djf_og_solflekktall',
    render: ({ width, pal }) => {
      const top = timeSeries({
        width,
        pal,
        height: 220,
        yLabel: 'NAO (DJF)',
        series: [{ name: 'NAO', color: pal.s2, kind: 'bar', data: pts(x, s.nao_djf) }],
        zeroLine: true,
      });
      const bottom = timeSeries({
        width,
        pal,
        height: 180,
        yLabel: 'Solflekktall',
        series: [{ name: 'Solflekktall', color: pal.s1, width: 2, data: pts(x, s.ssn) }],
        yDomain: [0, 220],
      });
      return stack(top, bottom);
    },
  };
}

// ---------------- Påstander uten støtte ----------------
export async function spuriousExample(): Promise<ChartInstance> {
  const a = await getJSON('analysis_spurious.json');
  const e = a.example;
  const z = (v: number[]) => {
    const m = v.reduce((p, q) => p + q, 0) / v.length;
    const sd = Math.sqrt(v.reduce((p, q) => p + (q - m) ** 2, 0) / v.length);
    return v.map((q) => (q - m) / sd);
  };
  const x = e.year.map((y: number) => y + 0.5);
  const zs = z(e.ssn);
  const zr = z(e.random_walk);
  return {
    title: `Det beste treffet blant ${num(e.n_candidates, 0)} tilfeldige serier`,
    subtitle: `Solflekktall ${e.year[0]}–${last(e.year)} mot den tilfeldige vandringen (generert av en datamaskin, uten fysisk kobling) som korrelerte sterkest av ${num(e.n_candidates, 0)} forsøk: r = ${num(e.r, 2)}. Begge standardisert.`,
    alt: `Linjediagram: årlig solflekktall og den av ${num(e.n_candidates, 0)} tilfeldig genererte seriene (tilfeldige vandringer) som korrelerer best med solflekktallet, r = ${num(e.r, 2)}, selv om alle er uavhengige av Solen.`,
    sources: ['silso_monthly'],
    columns: [
      { key: 'year', label: 'År' },
      { key: 'ssn_z', label: 'Solflekktall (z)', digits: 3 },
      { key: 'random_walk_z', label: 'Tilfeldig vandring (z)', digits: 3 },
    ],
    rows: e.year.map((y: number, i: number) => [y, zs[i], zr[i]]),
    csvName: 'tilfeldig_korrelasjon_eksempel',
    legend: [
      { label: 'Solflekktall', color: 'var(--s1)' },
      { label: 'Tilfeldig vandring', color: 'var(--s2)' },
    ],
    render: ({ width, pal }) =>
      timeSeries({
        width,
        pal,
        height: 260,
        yLabel: 'Standardisert verdi (z)',
        series: [
          { name: 'Solflekktall', color: pal.s1, width: 2, data: pts(x, zs) },
          { name: 'Tilfeldig vandring', color: pal.s2, width: 2, data: pts(x, zr) },
        ],
        zeroLine: true,
      }),
  };
}

export async function spuriousRates(): Promise<ChartInstance> {
  const a = await getJSON('analysis_spurious.json');
  const sc = a.scenarios as any[];
  const data = sc.flatMap((s) => [
    { cat: s.name, series: 'Naiv test (N)', v: 100 * s.false_positive_naive },
    { cat: s.name, series: 'Justert for autokorrelasjon (N_eff)', v: 100 * s.false_positive_neff },
    { cat: s.name, series: 'Fase-surrogattest', v: 100 * s.false_positive_surrogate },
  ]);
  return {
    title: 'Hvor ofte gir helt tilfeldige serier «signifikante» resultater?',
    subtitle: `Andel av ${num(sc[0].n_sim, 0)} simuleringer per type (${a.period[0]}–${a.period[1]}, ${sc[0].n} år) der p < 0,05. Forventet ved en korrekt test: 5 %.`,
    alt: `Stolpediagram: falsk-positiv-rate for fire typer tilfeldige serier og tre testmetoder. Den naive testen gir ${num(100 * sc[3].false_positive_naive, 0)} % «signifikante» resultater for to tilfeldige vandringer og ${num(100 * sc[2].false_positive_naive, 0)} % for en tilfeldig vandring mot solflekktallet; surrogattesten gir ${num(100 * sc[3].false_positive_surrogate, 0)} % og ${num(100 * sc[2].false_positive_surrogate, 0)} %.`,
    sources: ['silso_monthly'],
    columns: [
      { key: 'scenario', label: 'Type tilfeldig serie' },
      { key: 'naive', label: 'Naiv test (%)', digits: 1 },
      { key: 'neff', label: 'N_eff-justert (%)', digits: 1 },
      { key: 'surrogate', label: 'Surrogattest (%)', digits: 1 },
      { key: 'share_abs_r_gt_0_3', label: 'Andel med |r| > 0,3 (%)', digits: 1 },
      { key: 'share_abs_r_gt_0_5', label: 'Andel med |r| > 0,5 (%)', digits: 1 },
    ],
    rows: sc.map((s) => [
      s.name,
      100 * s.false_positive_naive,
      100 * s.false_positive_neff,
      100 * s.false_positive_surrogate,
      100 * s.share_abs_r_gt_0_3,
      100 * s.share_abs_r_gt_0_5,
    ]),
    tableOpen: true,
    csvName: 'falsk_positiv_rate_tilfeldige_serier',
    legend: [
      { label: 'Naiv test (N)', color: 'var(--s1)' },
      { label: 'Justert (N_eff)', color: 'var(--s2)' },
      { label: 'Surrogattest', color: 'var(--s3)' },
    ],
    render: ({ width, pal }) =>
      barsByCategory({
        width,
        pal,
        data,
        colors: { 'Naiv test (N)': pal.s1, 'Justert for autokorrelasjon (N_eff)': pal.s2, 'Fase-surrogattest': pal.s3 },
        yLabel: 'Falske positive (%)',
        hline: { y: 5, label: 'Forventet 5 %' },
        height: 300,
        yDomain: [0, 100],
      }),
  };
}
