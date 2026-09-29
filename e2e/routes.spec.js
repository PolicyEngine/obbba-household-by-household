// HTTP route tables, one request per row with redirects not followed. The
// origin table runs against both serve-policyengine.js (origin-emulated) and
// the live Vercel origin (origin-live), so the local helper cannot drift
// from what Vercel does.
import { BASE, expect, test } from './fixtures.js';

const HQ = 'household=39519&baseline=tcja-expiration';

// [path, status, Location (path + query) or content type]
const ORIGIN = [
  ['/', 307, BASE],
  ['/index.html', 307, BASE],
  ['/index.html?household=8', 307, `${BASE}?household=8`],
  [BASE, 200, 'text/html'],
  [`${BASE}?${HQ}`, 200, 'text/html'],
  [`${BASE}/`, 308, BASE],
  [`${BASE}/explore`, 200, 'text/html'],
  [`${BASE}/explore/`, 308, `${BASE}/explore`],
  ['/us/obbba-household-explorer', 307, BASE],
  [`/us/obbba-household-explorer?${HQ}`, 307, `${BASE}?${HQ}`],
  ['/us/obbba-household-explorer/', 308, '/us/obbba-household-explorer'],
  [`/us/obbba-household-explorer/explore?${HQ}`, 307, `${BASE}/explore?${HQ}`],
  ['/us/obbba-household-explorer/paper', 307, `${BASE}/paper`],
  ['/us/obbba-household-by-household', 307, BASE],
  ['/us/obbba-household-by-household/explore', 307, `${BASE}/explore`],
  ['/US/OBBBA-HOUSEHOLD-EXPLORER', 404, null],
  [`${BASE}/paper`, 200, 'text/html'],
  [`${BASE}/paper/`, 308, `${BASE}/paper`],
  [`${BASE}/paper/index.html`, 200, 'text/html'],
  [`${BASE}/paper/web/index.html?v=r2-20260830`, 200, 'text/html'],
  [`${BASE}/paper/web/index.pdf`, 200, 'application/pdf'],
  [`${BASE}/favicon.svg`, 200, 'image/svg+xml'],
  [`${BASE}/policyengine-white.svg`, 200, 'image/svg+xml'],
  [`${BASE}/provision_impacts.json`, 200, 'json'],
  [`${BASE}/_app/version.json`, 200, 'json'],
  [`${BASE}/no-such-file.js`, 404, null],
  ['/us/explore', 404, null],
  // The origin collapses repeated slashes before routing.
  ['//paper', 308, '/paper'],
  [`${BASE}//paper`, 308, `${BASE}/paper`],
  ['/us//obbba-households?x=1', 308, `${BASE}?x=1`]
];

// policyengine.org: old slugs redirect once, permanently, before the proxy.
const PARENT = [
  [BASE, 200, 'text/html'],
  [`${BASE}/`, 308, BASE],
  [`${BASE}/explore`, 200, 'text/html'],
  [`${BASE}/paper`, 200, 'text/html'],
  [`${BASE}/paper/web/index.pdf`, 200, 'application/pdf'],
  ['/us/obbba-household-explorer', 308, BASE],
  [`/us/obbba-household-explorer?${HQ}`, 308, `${BASE}?${HQ}`],
  [`/us/obbba-household-explorer/explore?${HQ}`, 308, `${BASE}/explore?${HQ}`],
  ['/us/obbba-household-explorer/paper', 308, `${BASE}/paper`],
  ['/us/obbba-household-explorer/', 308, '/us/obbba-household-explorer'],
  ['/us/obbba-household-by-household', 308, BASE],
  [`/us/obbba-household-by-household/explore?${HQ}`, 308, `${BASE}/explore?${HQ}`],
  ['/us/obbba-scatter', 308, BASE],
  ['/us/obbba-scatter/explore', 308, `${BASE}/explore`],
  ['/us/obba-household-explorer', 308, BASE],
  ['/us/research/obbba-household-explorer', 308, BASE],
  ['/us/research/obbba-household-by-household', 308, BASE],
  ['/us/ob3-households', 307, BASE],
  [`/us/ob3-households/explore?${HQ}`, 307, `${BASE}/explore?${HQ}`]
];

const TABLES = { origin: ORIGIN, parent: PARENT };

test('the origin only answers GET and HEAD', async ({ host, request }) => {
  test.skip(host !== 'origin', 'origin behaviour');
  expect((await request.post(BASE, { maxRedirects: 0 })).status()).toBe(405);
  expect((await request.head(`${BASE}/paper/web/index.pdf`)).status()).toBe(200);
});

for (const [host, table] of Object.entries(TABLES)) {
  test.describe(`${host} routes`, () => {
    for (const [path, status, expected] of table) {
      test(`${path} → ${status}${expected ? ` ${expected}` : ''}`, async ({
        host: target,
        request,
        baseURL
      }) => {
        test.skip(target !== host, `${host} table`);
        // Absolute, so "//paper" is a path and not a protocol-relative URL.
        const response = await request.get(new URL(baseURL).origin + path, { maxRedirects: 0 });
        expect(response.status()).toBe(status);
        if (status >= 300 && status < 400) {
          const location = new URL(response.headers().location, baseURL);
          expect(location.origin, 'redirects stay on the host').toBe(new URL(baseURL).origin);
          expect(location.pathname + location.search).toBe(expected);
          expect(response.headers()['cache-control'] ?? '').not.toMatch(/max-age=[1-9]/);
        } else if (expected) {
          expect(response.headers()['content-type']).toContain(expected);
        }
      });
    }
  });
}
