// Brukergrensesnitt-tekster hentes fra content/<språk>/ui.json (språkvelger kan legges til senere).
const files = import.meta.glob('../../content/*/ui.json', { eager: true, import: 'default' }) as Record<string, any>;
const lang = (import.meta.env.VITE_LANG as string | undefined) ?? 'nb';
const key = Object.keys(files).find((k) => k.includes(`/${lang}/`)) ?? Object.keys(files)[0];
export const ui = files[key] as any;
export const tpl = (s: string, vars: Record<string, string | number>) =>
  s.replace(/\{(\w+)\}/g, (_, k) => String(vars[k] ?? ''));
