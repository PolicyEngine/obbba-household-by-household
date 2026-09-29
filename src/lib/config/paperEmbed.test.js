import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

// static/paper/index.html wraps the working paper. Its links are relative
// (web/..., ../) so the same file serves on GitHub Pages, the Vercel origin
// and policyengine.org, but the last two strip the trailing slash from
// /paper/. The inline script pins <base> to the paper directory first.
const html = readFileSync(resolve(process.cwd(), 'static/paper/index.html'), 'utf8');
const script = html.match(/<script>\s*(\/\/ Relative links below[\s\S]*?)<\/script>/)[1];

function baseFor(pathname) {
  const appended = [];
  const document = {
    createElement: (tag) => ({ tag }),
    head: { appendChild: (el) => appended.push(el) }
  };
  new Function('location', 'document', script)({ pathname }, document);
  return appended.map((el) => el.href);
}

describe('paper wrapper', () => {
  it.each([
    ['/us/obbba-households/paper', ['/us/obbba-households/paper/']],
    ['/paper', ['/paper/']],
    ['/us/obbba-households/paper/', []],
    ['/obbba-household-by-household/paper/', []],
    ['/us/obbba-households/paper/index.html', []]
  ])('resolves relative links from %s', (pathname, expected) => {
    expect(baseFor(pathname)).toEqual(expected);
  });

  it('pins the base before any relative link is parsed', () => {
    const scriptEnd = html.indexOf('</script>');
    const firstRelative = html.search(/(?:href|src)="(?:web\/|\.\.\/)/);
    expect(scriptEnd).toBeGreaterThan(0);
    expect(scriptEnd).toBeLessThan(firstRelative);
  });

  it('uses one manuscript version everywhere', () => {
    const versions = new Set([...html.matchAll(/web\/index\.html\?v=([\w-]+)/g)].map((m) => m[1]));
    expect(versions.size).toBe(1);
  });

  it('points canonical and og:url at the policyengine.org slug', () => {
    const canonical = 'https://www.policyengine.org/us/obbba-households/paper';
    expect(html).toContain(`<link rel="canonical" href="${canonical}">`);
    expect(html).toContain(`<meta property="og:url" content="${canonical}">`);
    expect(html).not.toContain('obbba-household-explorer');
  });

  it('scrolls to the top in place', () => {
    // With <base> set, a bare "#top" would resolve to another URL and reload.
    expect(html).toMatch(/href="#top" onclick="window\.scrollTo\(0, 0\); return false;"/);
  });
});
