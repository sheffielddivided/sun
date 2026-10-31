const cache = new Map<string, Promise<any>>();
export function getJSON<T = any>(name: string): Promise<T> {
  let p = cache.get(name);
  if (!p) {
    p = fetch(`${import.meta.env.BASE_URL}data/${name}`).then((r) => {
      if (!r.ok) throw new Error(`${name}: HTTP ${r.status}`);
      return r.json();
    });
    cache.set(name, p);
  }
  return p as Promise<T>;
}
export interface SourceEntry {
  id: string;
  name: string;
  provider: string;
  homepage: string;
  urls: string[];
  license: string;
  citation: string;
  status: 'ok' | 'stale' | 'failed';
  fetched_at: string | null;
  last_point: string | null;
}
export interface Manifest {
  generated_at: string | null;
  sources: Record<string, SourceEntry>;
}
export const getManifest = () => getJSON<Manifest>('manifest.json');

export type Num = number | null;
/** Fjern null/NaN og returner punktlister {x, y}. */
export function pts(xs: Num[], ys: Num[]): { x: number; y: number }[] {
  const out: { x: number; y: number }[] = [];
  for (let i = 0; i < xs.length; i++) {
    const x = xs[i];
    const y = ys[i];
    if (x !== null && y !== null && Number.isFinite(x) && Number.isFinite(y)) out.push({ x, y });
  }
  return out;
}
export function last<T>(a: T[]): T {
  return a[a.length - 1];
}
