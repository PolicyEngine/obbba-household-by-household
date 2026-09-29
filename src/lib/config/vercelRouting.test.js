import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

// Routing contract for the Vercel origin that policyengine.org proxies.
// The production bundle is built for BASE_PATH=/us/obbba-household-explorer
// (package.json build:policyengine). SvelteKit treats any URL outside the
// base as external and reloads it, so a path outside the base must redirect
// into it, never rewrite to index.html.
// Vitest runs from the repo root (vitest.config.js lives there).
const readJson = (file) => JSON.parse(readFileSync(resolve(process.cwd(), file), 'utf8'));
const vercel = readJson('vercel.json');

const OLD = '/us/obbba-household-explorer';
const NEW = '/us/obbba-households';

const redirectFor = (source) => vercel.redirects.find((r) => r.source === source);

describe('vercel.json routing contract', () => {
  it('serves the app under the compiled base path', () => {
    const pkg = readJson('package.json');
    expect(pkg.scripts['build:policyengine']).toContain(`BASE_PATH=${OLD} `);
    expect(vercel.buildCommand).toBe('npm run build:policyengine');

    const rewrites = Object.fromEntries(vercel.rewrites.map((r) => [r.source, r.destination]));
    expect(rewrites[OLD]).toBe('/index.html');
    expect(rewrites[`${OLD}/explore`]).toBe('/index.html');
    expect(rewrites[`${OLD}/:path*`]).toBe('/:path*');
  });

  it('answers the new slug with a temporary, suffix-preserving redirect to the base', () => {
    // Transitional alias so policyengine.org can proxy /us/obbba-households
    // before the base path moves there. It must stay temporary: the
    // direction flips at the base-path cutover, and a cached permanent
    // redirect would then loop.
    expect(redirectFor(NEW)).toEqual({ source: NEW, destination: OLD, permanent: false });
    expect(redirectFor(`${NEW}/:path*`)).toEqual({
      source: `${NEW}/:path*`,
      destination: `${OLD}/:path*`,
      permanent: false
    });
  });

  it('never rewrites a path outside the compiled base to the app shell', () => {
    for (const rewrite of vercel.rewrites) {
      expect(rewrite.source.startsWith(OLD)).toBe(true);
    }
  });
});
