// What a visitor sees at the explorer's URLs, through the Vercel origin and
// through policyengine.org (which proxies it). Old slugs must land on
// /us/obbba-households with the path and query intact, on the same host, in
// one document load (SvelteKit reloads forever outside its base).
import {
  BASE,
  HOUSEHOLD,
  HOUSEHOLD_QUERY,
  expect,
  expectAppAssets,
  expectHealthyLoad,
  expectHouseholdSelected,
  test
} from './fixtures.js';

const LEGACY = {
  origin: ['/us/obbba-household-explorer', '/us/obbba-household-by-household'],
  parent: [
    '/us/obbba-household-explorer',
    '/us/obbba-household-by-household',
    '/us/obbba-scatter',
    '/us/obba-household-explorer',
    '/us/ob3-households'
  ]
};

const atExplorerRoot = (url) => [BASE, `${BASE}/`].includes(new URL(url).pathname);

test('serves the explorer at /us/obbba-households', async ({ page, watch }) => {
  await page.goto(BASE, { waitUntil: 'commit' });
  await expect(page.locator('.household-profile h3').first()).toBeVisible({ timeout: 120_000 });
  await expect(page.locator('nav.pe-shell-header')).toContainText('Working paper');
  await expect(page.locator('nav.pe-shell-header')).toContainText('Research');
  expect(atExplorerRoot(page.url())).toBe(true);
  await expectHealthyLoad(page, watch);
  expectAppAssets(watch);
});

for (const host of ['origin', 'parent']) {
  for (const legacy of LEGACY[host]) {
    test(`${host}: ${legacy} with a household link lands on the new slug with it selected`, async ({
      host: target,
      page,
      watch,
      baseURL
    }) => {
      test.skip(target !== host, `${host}-only redirect`);
      await page.goto(`${legacy}?${HOUSEHOLD_QUERY}`, { waitUntil: 'commit' });
      await expectHouseholdSelected(page);
      const url = new URL(page.url());
      expect(url.host).toBe(new URL(baseURL).host);
      expect(atExplorerRoot(url.href)).toBe(true);
      expect(url.searchParams.get('household')).toBe(HOUSEHOLD);
      await expectHealthyLoad(page, watch);
    });
  }
}

test('reloading the URL the app writes (base plus slash) keeps the household', async ({
  page,
  watch
}) => {
  // SvelteKit rewrites the root to `${BASE}/`; both hosts strip the slash.
  await page.goto(`${BASE}/?${HOUSEHOLD_QUERY}`, { waitUntil: 'commit' });
  await expectHouseholdSelected(page);
  await expectHealthyLoad(page, watch);
});

test('an old explore deep link keeps its query, and Back and Explore work', async ({
  page,
  watch
}) => {
  await page.goto(`/us/obbba-household-explorer/explore?household=${HOUSEHOLD}`, {
    waitUntil: 'commit'
  });
  await expect(page.locator('a.back-link')).toBeVisible({ timeout: 60_000 });
  const url = new URL(page.url());
  expect(url.pathname).toBe(`${BASE}/explore`);
  expect(url.search).toBe(`?household=${HOUSEHOLD}`);
  await expectHealthyLoad(page, watch);
  expectAppAssets(watch);

  await page.locator('a.back-link').click();
  await expect.poll(() => atExplorerRoot(page.url())).toBe(true);
  await page.locator('a.explore-link').click();
  await expect.poll(() => new URL(page.url()).pathname).toBe(`${BASE}/explore`);
});

test('the Working paper link opens the embedded manuscript and PDF', async ({
  page,
  watch,
  request
}) => {
  await page.goto(BASE, { waitUntil: 'commit' });
  const paperLink = page.locator('nav.pe-shell-header a', { hasText: 'Working paper' });
  await expect(paperLink).toBeVisible({ timeout: 60_000 });
  await Promise.all([page.waitForURL(/\/paper$/), paperLink.click()]);
  expect(new URL(page.url()).pathname).toBe(`${BASE}/paper`);

  const src = new URL(await page.locator('iframe').evaluate((frame) => frame.src));
  expect(src.pathname).toBe(`${BASE}/paper/web/index.html`);
  await expect(page.frameLocator('iframe').locator('h1').first()).toContainText(
    'One Big Beautiful Bill Act',
    { timeout: 60_000 }
  );

  const pdf = await page.locator('a', { hasText: 'Download PDF' }).evaluate((a) => a.href);
  expect(new URL(pdf).pathname).toBe(`${BASE}/paper/web/index.pdf`);
  const pdfResponse = await request.get(pdf);
  expect(pdfResponse.status()).toBe(200);
  expect(pdfResponse.headers()['content-type']).toMatch(/pdf/);

  await Promise.all([
    page.waitForURL((url) => !url.pathname.includes('/paper')),
    page.locator('a', { hasText: 'Live household explorer' }).click()
  ]);
  expect(atExplorerRoot(page.url())).toBe(true);
  expect(watch.failures).toEqual([]);
});

test('an old paper link with a trailing slash reaches the working wrapper', async ({ page }) => {
  await page.goto('/us/obbba-household-explorer/paper/', { waitUntil: 'commit' });
  await page.waitForURL(new RegExp(`${BASE}/paper$`));
  const src = new URL(await page.locator('iframe').evaluate((frame) => frame.src));
  expect(src.pathname).toBe(`${BASE}/paper/web/index.html`);
  await expect(page.frameLocator('iframe').locator('h1').first()).toContainText(
    'One Big Beautiful Bill Act',
    { timeout: 60_000 }
  );
});
