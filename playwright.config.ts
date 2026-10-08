import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/browser',
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: 'http://127.0.0.1:3100',
    headless: true,
    screenshot: 'only-on-failure',
    ...(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {}),
  },
  webServer: [
    {
      command: 'pnpm --filter @nexusai/api exec tsx src/server.ts',
      url: 'http://127.0.0.1:4100/health/ready',
      env: {
        NODE_ENV: 'test',
        API_PORT: '4100',
        API_HOST: '127.0.0.1',
        WEB_ORIGIN: 'http://127.0.0.1:3100',
      },
      reuseExistingServer: false,
    },
    {
      command: 'pnpm --filter @nexusai/web exec next dev --hostname 127.0.0.1 -p 3100',
      url: 'http://127.0.0.1:3100',
      env: { NODE_ENV: 'development', NEXT_PUBLIC_API_ORIGIN: 'http://127.0.0.1:4100' },
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
