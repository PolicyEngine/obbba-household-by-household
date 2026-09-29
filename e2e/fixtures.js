import { test as base, expect } from '@playwright/test';

export const BASE = '/us/obbba-households';
// Absent from the 1,000-row instant sample, so selecting it proves the full
// dataset loaded and the household parameter was applied.
export const HOUSEHOLD = '39519';
export const HOUSEHOLD_QUERY = `household=${HOUSEHOLD}&baseline=tcja-expiration`;

// Analytics must never count test traffic (the CRM reads GA page views and
// tool_engaged events by slug).
const ANALYTICS = /googletagmanager\.com|google-analytics\.com|analytics\.google\.com/;

export const test = base.extend({
  host: ['origin', { option: true }],

  context: async ({ context }, use) => {
    await context.route(ANALYTICS, (route) => route.fulfill({ status: 204, body: '' }));
    await use(context);
  },

  // Records what a page load did on the host under test.
  watch: async ({ page, baseURL }, use) => {
    const origin = new URL(baseURL).origin;
    const record = { documents: [], assets: [], failures: [], errors: [] };
    page.on('request', (request) => {
      // One entry per navigation the page started; redirect hops share it.
      if (
        request.isNavigationRequest() &&
        request.frame() === page.mainFrame() &&
        !request.redirectedFrom()
      ) {
        record.documents.push(request.url());
      }
    });
    page.on('response', (response) => {
      const url = new URL(response.url());
      if (url.origin !== origin) return;
      const type = response.request().resourceType();
      if (type === 'script' || type === 'stylesheet' || url.pathname.includes('/_app/')) {
        record.assets.push({
          path: url.pathname,
          status: response.status(),
          contentType: response.headers()['content-type'] ?? ''
        });
      }
      if (response.status() >= 400) record.failures.push(`${response.status()} ${url.pathname}`);
    });
    page.on('pageerror', (error) => record.errors.push(String(error)));
    await use(record);
  }
});

export { expect };

/** The redirect hops a response went through, as paths with queries. */
export function hops(response) {
  const chain = [];
  for (let request = response.request(); request; request = request.redirectedFrom()) {
    const url = new URL(request.url());
    chain.unshift(url.pathname + url.search);
  }
  return chain;
}

export async function expectHouseholdSelected(page) {
  await expect(
    page.locator('.household-profile h3', { hasText: `Household #${HOUSEHOLD}` }).first()
  ).toBeVisible({ timeout: 120_000 });
}

/** JS and CSS all load, with the right type, from under the base path. */
export function expectAppAssets(watch) {
  const scripts = watch.assets.filter((a) => a.path.endsWith('.js'));
  const styles = watch.assets.filter((a) => a.path.endsWith('.css'));
  expect(scripts.length).toBeGreaterThan(0);
  expect(styles.length).toBeGreaterThan(0);
  for (const asset of watch.assets) {
    expect(asset.status, asset.path).toBe(200);
    expect(asset.path, 'assets load from under the base').toMatch(
      new RegExp(`^${BASE}/_app/(immutable/|version\\.json$)`)
    );
    if (asset.path.endsWith('.js')) expect(asset.contentType, asset.path).toMatch(/javascript/);
    if (asset.path.endsWith('.css')) expect(asset.contentType, asset.path).toMatch(/css/);
  }
}

/** Settles, then asserts one document load, no errors and no failed requests. */
export async function expectHealthyLoad(page, watch) {
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(2_000); // a reload loop would show up here
  expect(watch.documents, 'one document load, no reload loop').toHaveLength(1);
  expect(watch.errors, 'no uncaught page errors').toEqual([]);
  expect(watch.failures, 'no failed requests on the host').toEqual([]);
}
