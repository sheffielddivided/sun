import { defineConfig, devices } from '@playwright/test';

// Lokalt kan nettleseren peke på en forhåndsinstallert Chromium (CHROMIUM_PATH); i CI brukes `npx playwright install chromium`.
const executablePath = process.env.CHROMIUM_PATH || undefined;

export default defineConfig({
  testDir: 'tests',
  timeout: 60_000,
  fullyParallel: true,
  reporter: [['list']],
  use: {
    baseURL: 'http://localhost:4173',
    launchOptions: executablePath ? { executablePath, args: ['--no-sandbox'] } : { args: ['--no-sandbox'] },
  },
  projects: [
    {
      name: 'desktop',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: executablePath ? { executablePath, args: ['--no-sandbox'] } : { args: ['--no-sandbox'] },
      },
    },
    {
      name: 'mobile',
      use: {
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
        launchOptions: executablePath ? { executablePath, args: ['--no-sandbox'] } : { args: ['--no-sandbox'] },
      },
    },
  ],
  webServer: {
    command: 'npm run preview',
    url: 'http://localhost:4173/sun/',
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
