// The GitHub Pages copy (base /obbba-household-by-household) shares
// src/app.html and the paper wrapper with the policyengine.org build; the
// out-of-base guard and the <base> pin must leave it working.
import {
  HOUSEHOLD_QUERY,
  expect,
  expectHealthyLoad,
  expectHouseholdSelected,
  test
} from './fixtures.js';

const PAGES_BASE = '/obbba-household-by-household';

test('the GitHub Pages copy selects a linked household in one load', async ({ page, watch }) => {
  await page.goto(`${PAGES_BASE}/?${HOUSEHOLD_QUERY}`, { waitUntil: 'commit' });
  await expectHouseholdSelected(page);
  expect(new URL(page.url()).pathname).toBe(`${PAGES_BASE}/`);
  await expectHealthyLoad(page, watch);
});

test('the GitHub Pages copy embeds the working paper', async ({ page }) => {
  await page.goto(`${PAGES_BASE}/paper/`, { waitUntil: 'commit' });
  await expect(page.frameLocator('iframe').locator('h1').first()).toContainText(
    'One Big Beautiful Bill Act',
    { timeout: 60_000 }
  );
});
