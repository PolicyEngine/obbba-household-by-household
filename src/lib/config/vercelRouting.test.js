import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it, vi } from 'vitest';

// Routing contract for the Vercel origin that policyengine.org proxies.
// The production bundle is built for BASE_PATH=/us/obbba-households
// (package.json build:policyengine). SvelteKit treats any URL outside the
// base as external and reloads it, so a path outside the base must redirect
// into it, never rewrite to index.html.
// Vitest runs from the repo root (vitest.config.js lives there).
const read = (file) => readFileSync(resolve(process.cwd(), file), 'utf8');
const vercel = JSON.parse(read('vercel.json'));

const BASE = '/us/obbba-households';
const LEGACY = ['/us/obbba-household-explorer', '/us/obbba-household-by-household'];

const inBase = (path) => path === BASE || path.startsWith(`${BASE}/`);
const redirectFor = (source) => vercel.redirects.find((r) => r.source === source);

describe('vercel.json routing contract', () => {
  it('serves the app under the compiled base path', () => {
    const pkg = JSON.parse(read('package.json'));
    expect(pkg.scripts['build:policyengine']).toContain(`BASE_PATH=${BASE} `);
    expect(pkg.scripts['preview:policyengine']).toContain(`BASE_PATH=${BASE} `);
    expect(vercel.buildCommand).toBe('npm run build:policyengine');

    const rewrites = Object.fromEntries(vercel.rewrites.map((r) => [r.source, r.destination]));
    expect(rewrites[BASE]).toBe('/index.html');
    expect(rewrites[`${BASE}/explore`]).toBe('/index.html');
    expect(rewrites[`${BASE}/explore/:path*`]).toBe('/index.html');
    expect(rewrites[`${BASE}/:path*`]).toBe('/:path*');
  });

  it('matches the catch-all rewrite last', () => {
    // Rewrites are first-match: the static-file catch-all must not shadow the
    // SPA routes.
    expect(vercel.rewrites.at(-1).source).toBe(`${BASE}/:path*`);
    expect(
      vercel.rewrites.filter((r) => r.source.endsWith('/:path*') && r.destination === '/:path*')
    ).toHaveLength(1);
  });

  it('never rewrites a path outside the compiled base to the app shell', () => {
    for (const rewrite of vercel.rewrites) {
      expect(inBase(rewrite.source)).toBe(true);
    }
  });

  it('redirects only into the base, and never from inside it', () => {
    // Together these rule out redirect loops.
    for (const redirect of vercel.redirects) {
      expect(inBase(redirect.destination.replace('/:path*', ''))).toBe(true);
      expect(inBase(redirect.source)).toBe(false);
    }
  });

  it('redirects the root to the base', () => {
    expect(redirectFor('/')).toEqual({ source: '/', destination: BASE, permanent: false });
  });

  it('redirects /index.html into the base instead of serving the app outside it', () => {
    // Vercel would otherwise serve the SPA shell from the filesystem at
    // /index.html, outside the base, where SvelteKit reloads forever.
    expect(redirectFor('/index.html')).toEqual({
      source: '/index.html',
      destination: BASE,
      permanent: false
    });
  });

  it.each(LEGACY)('redirects %s to the base, keeping the suffix', (legacy) => {
    // Temporary on the origin so a rollback can never meet a browser-cached
    // redirect; policyengine.org carries the permanent one.
    expect(redirectFor(legacy)).toEqual({ source: legacy, destination: BASE, permanent: false });
    expect(redirectFor(`${legacy}/:path*`)).toEqual({
      source: `${legacy}/:path*`,
      destination: `${BASE}/:path*`,
      permanent: false
    });
  });

  it('strips trailing slashes like policyengine.org does', () => {
    expect(vercel.trailingSlash).toBe(false);
  });
});

describe('out-of-base guard in src/app.html', () => {
  // Runs the inline guard against a stub location, the way a browser would
  // before SvelteKit starts. SvelteKit substitutes %sveltekit.assets% with the
  // base path in the SPA fallback page (build/index.html).
  const html = read('src/app.html');
  const guard = html.match(
    /<script>\s*(\/\/ SvelteKit reloads any URL outside[\s\S]*?)<\/script>/
  )[1];

  const run = (pathname, { search = '', hash = '', base = BASE } = {}) => {
    const location = { pathname, search, hash, replace: vi.fn() };
    new Function('location', guard.replaceAll('%sveltekit.assets%', base))(location);
    return location.replace.mock.calls.map(([url]) => url);
  };

  it('runs before SvelteKit boots and reads the base from the build', () => {
    expect(html.indexOf(guard)).toBeLessThan(html.indexOf('%sveltekit.head%'));
    expect(guard).toContain("'%sveltekit.assets%'");
  });

  it.each([
    ['/us/obbba-household-explorer', '', '', '/us/obbba-households'],
    ['/us/obbba-household-explorer/', '', '', '/us/obbba-households/'],
    [
      '/us/obbba-household-explorer/explore',
      '?household=8&baseline=tcja-expiration',
      '#map',
      '/us/obbba-households/explore?household=8&baseline=tcja-expiration#map'
    ],
    ['/us/obbba-household-by-household', '?household=8', '', '/us/obbba-households?household=8'],
    ['/index.html', '?household=8', '', '/us/obbba-households?household=8'],
    ['/', '', '', '/us/obbba-households'],
    ['/us/obbba-household-explorerx/explore', '', '', '/us/obbba-households']
  ])('moves %s%s%s under the base', (pathname, search, hash, expected) => {
    expect(run(pathname, { search, hash })).toEqual([expected]);
  });

  it.each(['/us/obbba-households', '/us/obbba-households/', '/us/obbba-households/explore'])(
    'leaves %s alone',
    (pathname) => {
      expect(run(pathname, { search: '?household=8' })).toEqual([]);
    }
  );

  it('leaves the GitHub Pages build alone', () => {
    const base = '/obbba-household-by-household';
    expect(run('/obbba-household-by-household/', { base })).toEqual([]);
    expect(run('/obbba-household-by-household/explore', { base })).toEqual([]);
  });

  it('does nothing if the assets path is ever relative', () => {
    // paths.relative makes %sveltekit.assets% relative in prerendered pages.
    expect(run('/us/obbba-household-explorer', { base: '.' })).toEqual([]);
  });
});
