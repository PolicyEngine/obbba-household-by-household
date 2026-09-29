// Browser regression suite for the OBBBA explorer's URLs (e2e/).
//
// Projects:
//   origin-emulated  build/ served by serve-policyengine.js with vercel.json
//                    routing (CI on every PR; E2E_EMULATED=1 starts it)
//   origin-live      https://obbba-household-by-household.vercel.app
//   parent-live      https://www.policyengine.org, which proxies the origin
//   pages-live       the GitHub Pages copy (e2e/pages.spec.js only)
//
// Setup (Playwright is kept out of package-lock.json, like routing-utils):
//   npm install --no-save @playwright/test@1.63.0 @vercel/routing-utils@6.6.0
//   npx playwright install chromium
//   npm run build:policyengine
//   E2E_EMULATED=1 npx playwright test --project=origin-emulated
//   npx playwright test --project=origin-live --project=parent-live --project=pages-live
import { defineConfig } from '@playwright/test';

const PORT = Number(process.env.E2E_PORT ?? 4173);
const explorer = { testIgnore: /pages\.spec\.js/ };

export default defineConfig({
  testDir: 'e2e',
  timeout: 180_000,
  expect: { timeout: 30_000 },
  fullyParallel: true,
  workers: process.env.CI ? 2 : 4,
  // Live hosts occasionally drop a request; the emulated origin never retries.
  retries: 0,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  use: {
    viewport: { width: 1280, height: 900 },
    trace: 'retain-on-failure'
  },
  projects: [
    {
      name: 'origin-emulated',
      ...explorer,
      use: { baseURL: `http://localhost:${PORT}`, host: 'origin' }
    },
    {
      name: 'origin-live',
      ...explorer,
      retries: 1,
      use: { baseURL: 'https://obbba-household-by-household.vercel.app', host: 'origin' }
    },
    {
      name: 'parent-live',
      ...explorer,
      retries: 1,
      use: { baseURL: 'https://www.policyengine.org', host: 'parent' }
    },
    {
      name: 'pages-live',
      testMatch: /pages\.spec\.js/,
      retries: 1,
      use: { baseURL: 'https://policyengine.github.io', host: 'pages' }
    }
  ],
  webServer: process.env.E2E_EMULATED
    ? {
        command: `PORT=${PORT} node serve-policyengine.js`,
        url: `http://localhost:${PORT}/us/obbba-households`,
        reuseExistingServer: !process.env.CI,
        timeout: 60_000
      }
    : undefined
});
