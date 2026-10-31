export interface Palette {
  fg: string;
  bg: string;
  muted: string;
  grid: string;
  border: string;
  s1: string;
  s2: string;
  s3: string;
  s4: string;
  s5: string;
  accent: string;
}
export function palette(): Palette {
  const cs = getComputedStyle(document.documentElement);
  const g = (n: string) => cs.getPropertyValue(n).trim();
  return {
    fg: g('--fg'),
    bg: g('--bg'),
    muted: g('--muted'),
    grid: g('--grid'),
    border: g('--border'),
    s1: g('--s1'),
    s2: g('--s2'),
    s3: g('--s3'),
    s4: g('--s4'),
    s5: g('--s5'),
    accent: g('--accent'),
  };
}
