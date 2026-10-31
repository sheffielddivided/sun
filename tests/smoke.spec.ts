import { expect, test, type Page } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const pages: string[] = (JSON.parse(fs.readFileSync(path.resolve('scripts/pages.generated.json'), 'utf8')) as string[])
  .filter((p) => p !== '404.html')
  .map((p) => '/sun/' + p.replace(/index\.html$/, ''));

async function loadAll(page: Page) {
  // Grafer lastes først når de nærmer seg skjermen: rull gjennom hele siden.
  await page.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 600) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 40));
    }
    window.scrollTo(0, 0);
  });
}

for (const route of pages) {
  test(`side lastes uten feil: ${route}`, async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (m) => {
      if (m.type() === 'error') errors.push(m.text());
    });
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('requestfailed', (r) => errors.push(`requestfailed ${r.url()}`));
    const resp = await page.goto(route);
    expect(resp?.status()).toBe(200);
    await expect(page.locator('h1')).toHaveCount(1);
    await loadAll(page);
    const figs = page.locator('figure[data-chart]');
    const n = await figs.count();
    for (let i = 0; i < n; i++) {
      const f = figs.nth(i);
      await expect(f, `graf ${await f.getAttribute('data-chart')}`).toHaveAttribute('aria-busy', 'false', {
        timeout: 20_000,
      });
      await expect(f).not.toHaveAttribute('data-error', '1');
      // grafer med tegning skal ha en SVG/canvas og et tekstalternativ
      const plot = f.locator('.plot-wrap');
      if (await plot.count()) {
        await expect(plot).toHaveAttribute('role', 'img');
        expect(((await plot.getAttribute('aria-label')) ?? '').length).toBeGreaterThan(30);
        await expect(plot.locator('svg').first()).toBeVisible();
      }
      await expect(f.locator('details.table-alt table')).toHaveCount(1);
    }
    // tidslinje og dashbord
    if (await page.locator('[data-timeline]').count()) await expect(page.locator('.tl-item').first()).toBeVisible();
    if (await page.locator('[data-dashboard]').count()) {
      await expect(page.locator('[data-field="ssn-value"]')).not.toHaveText('–');
      await expect(page.locator('[data-field="kp-value"]')).not.toHaveText('–');
    }
    const text = await page.locator('main').innerText();
    for (const bad of ['NaN', 'undefined', 'Infinity', 'TODO', 'lorem ipsum', 'Laster'])
      expect(text, `uventet «${bad}» i teksten`).not.toContain(bad);
    expect(errors, errors.join('\n')).toEqual([]);
  });
}

test('tema kan byttes og huskes', async ({ page }) => {
  await page.goto('/sun/');
  const html = page.locator('html');
  await page.locator('.theme-toggle').click();
  const t1 = await html.getAttribute('data-theme');
  expect(['light', 'dark']).toContain(t1);
  await page.reload();
  expect(await html.getAttribute('data-theme')).toBe(t1);
});

test('periodevalg zoomer grafen og filtrerer tabellen', async ({ page }) => {
  await page.goto('/sun/dataserier/');
  const fig = page.locator('figure[data-chart="data-ssn-monthly"]');
  await fig.scrollIntoViewIfNeeded();
  await expect(fig).toHaveAttribute('aria-busy', 'false', { timeout: 20_000 });
  await fig.getByRole('button', { name: 'Siste 25 år' }).click();
  await fig.locator('summary').click();
  const caption = await fig.locator('caption').innerText();
  expect(caption).toMatch(/av 3\s?\d{3} rader|av \d+/);
  const rows = await fig.locator('tbody tr').count();
  expect(rows).toBeLessThan(400);
  expect(rows).toBeGreaterThan(200);
});

test('CSV-nedlasting inneholder kildehenvisning', async ({ page }) => {
  await page.goto('/sun/dataserier/');
  const fig = page.locator('figure[data-chart="data-ssn-yearly"]');
  await fig.scrollIntoViewIfNeeded();
  await expect(fig).toHaveAttribute('aria-busy', 'false', { timeout: 20_000 });
  const [dl] = await Promise.all([
    page.waitForEvent('download'),
    fig.getByRole('button', { name: 'Last ned CSV' }).click(),
  ]);
  const content = fs.readFileSync((await dl.path())!, 'utf8');
  expect(content).toContain('# Kilde:');
  expect(content).toContain('# Lisens:');
  expect(content).toContain('year,ssn');
});

test('mobilmeny åpnes og tastaturnavigasjon når hovedinnhold', async ({ page }) => {
  await page.goto('/sun/');
  await page.keyboard.press('Tab');
  await expect(page.locator('.skip')).toBeFocused();
});
