import { defineConfig } from 'vite';
import fs from 'node:fs';
import path from 'node:path';

const base = (process.env.VITE_BASE || '/sun/').replace(/\/?$/, '/');
const listFile = path.resolve(__dirname, 'scripts/pages.generated.json');
const pages: string[] = fs.existsSync(listFile) ? JSON.parse(fs.readFileSync(listFile, 'utf8')) : ['index.html'];

export default defineConfig({
  base,
  build: {
    outDir: 'dist',
    target: 'es2022',
    chunkSizeWarningLimit: 700,
    rollupOptions: {
      input: Object.fromEntries(
        pages.map((p) => [
          p
            .replace(/\/?index\.html$/, '')
            .replace(/\.html$/, '')
            .replace(/\//g, '-') || 'home',
          path.resolve(__dirname, p),
        ]),
      ),
    },
  },
  server: { port: 5173 },
});
