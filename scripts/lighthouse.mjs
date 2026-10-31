// Kjører Lighthouse mot forsiden (mobil-profil) på en lokal preview-server og skriver lighthouse/forside.json.
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import lighthouse from 'lighthouse';
import { launch } from 'chrome-launcher';

const server = spawn('npx', ['vite', 'preview', '--port', '4173', '--strictPort'], { stdio: 'ignore' });
await new Promise((r) => setTimeout(r, 3000));
const chrome = await launch({ chromePath: process.env.CHROMIUM_PATH, chromeFlags: ['--headless', '--no-sandbox'] });
try {
  const res = await lighthouse('http://localhost:4173/sun/', { port: chrome.port, output: 'json', onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'] });
  const scores = Object.fromEntries(Object.entries(res.lhr.categories).map(([k, v]) => [k, Math.round(v.score * 100)]));
  fs.mkdirSync('lighthouse', { recursive: true });
  fs.writeFileSync('lighthouse/forside.json', JSON.stringify({ url: 'forsiden (mobil-profil)', scores, fetchTime: res.lhr.fetchTime }, null, 2));
  console.log(scores);
  const failed = res.lhr.categories.performance.score * 100 < 90 || res.lhr.categories.accessibility.score * 100 < 95;
  process.exitCode = failed ? 1 : 0;
} finally {
  await chrome.kill();
  server.kill();
}
