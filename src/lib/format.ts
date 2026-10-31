const nf = new Map<string, Intl.NumberFormat>();
export function num(v: number | null | undefined, digits = 0, group = true): string {
  if (v === null || v === undefined || !Number.isFinite(v)) return '–';
  const key = `${digits}-${group}`;
  let f = nf.get(key);
  if (!f) {
    f = new Intl.NumberFormat('nb-NO', { minimumFractionDigits: digits, maximumFractionDigits: digits, useGrouping: group });
    nf.set(key, f);
  }
  return f.format(v);
}
export const signed = (v: number, digits = 2) => (v > 0 ? '+' : '') + num(v, digits);
export function pval(p: number): string {
  if (p < 0.001) return '< 0,001';
  return num(p, p < 0.01 ? 3 : 2);
}
const MONTHS = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'desember'];
export function isoDate(s: string): string {
  const d = new Date(s.slice(0, 10) + 'T00:00:00Z');
  return `${d.getUTCDate()}. ${MONTHS[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}
export function decYear(t: number): string {
  const y = Math.floor(t + 1e-9);
  const m = Math.min(11, Math.floor((t - y) * 12 + 1e-6));
  return `${MONTHS[m]} ${y}`;
}
export const yearTick = (d: number) => String(d);
