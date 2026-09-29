// Local stand-in for the Vercel origin that policyengine.org proxies at
// /us/obbba-households.
//
// Serves build/ (from `npm run build:policyengine`) with the routing in
// vercel.json, compiled by @vercel/routing-utils — the same compiler the
// Vercel CLI uses — so local runs and the browser regression suite (e2e/)
// see the same trailing-slash strip, redirects, filesystem precedence and
// rewrites as production, including production's strict matching (no SPA
// fallback: a missing file is a 404, as on Vercel).
//
//   npm install --no-save @vercel/routing-utils@6.6.0
//   npm run build:policyengine
//   npm run serve:policyengine          # PORT=4173 by default
//
// @vercel/routing-utils is installed without saving so that Vercel's
// `npm ci` stays on the committed lockfile; the helper warns if the installed
// version is not the one it was checked against. Beyond vercel.json it
// mirrors two origin behaviours measured with curl: paths with repeated
// slashes 308 to the collapsed path, and methods other than GET/HEAD get 405.
import { createServer } from 'node:http';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { extname, join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROUTING_UTILS_VERSION = '6.6.0';

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.geojson': 'application/geo+json',
  '.csv': 'text/csv; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.pdf': 'application/pdf',
  '.woff2': 'font/woff2',
  '.txt': 'text/plain; charset=utf-8'
};

/** Compiles vercel.json into Vercel's route list. */
export async function compileRoutes(config) {
  let getTransformedRoutes;
  try {
    ({ getTransformedRoutes } = await import('@vercel/routing-utils'));
  } catch (error) {
    if (error?.code !== 'ERR_MODULE_NOT_FOUND') throw error;
    throw new Error(
      `serve-policyengine.js needs @vercel/routing-utils: npm install --no-save @vercel/routing-utils@${ROUTING_UTILS_VERSION}`
    );
  }
  const installed = JSON.parse(
    readFileSync(new URL('./node_modules/@vercel/routing-utils/package.json', import.meta.url), 'utf8')
  ).version;
  if (installed !== ROUTING_UTILS_VERSION) {
    console.warn(
      `@vercel/routing-utils ${installed} is installed; this helper was checked against ${ROUTING_UTILS_VERSION}.`
    );
  }
  const { routes, error } = getTransformedRoutes(config);
  if (error) throw new Error(`vercel.json: ${error.message}`);
  return routes;
}

/** Maps a URL path onto a file in the build directory (or its index.html). */
export function fileLookup(buildDir) {
  const root = resolve(buildDir);
  return (pathname) => {
    let decoded;
    try {
      decoded = decodeURIComponent(pathname);
    } catch {
      return null;
    }
    const candidate = normalize(join(root, decoded));
    if (candidate !== root && !candidate.startsWith(root + '/')) return null;
    for (const path of [candidate, join(candidate, 'index.html')]) {
      if (existsSync(path) && statSync(path).isFile()) return path;
    }
    return null;
  };
}

/**
 * Walks Vercel's compiled routes for one request.
 * Returns {type:'redirect', status, location} | {type:'file', file} | {type:'notFound'}.
 * Supports the route shapes routing-utils emits for this vercel.json
 * (redirects, `handle: filesystem`, rewrites with `check`); anything else
 * throws rather than silently diverging from Vercel.
 */
export function resolveRequest(url, routes, lookup) {
  // Prefix the origin rather than resolving against it: a request target
  // like "//paper" would otherwise parse "paper" as a host.
  const incoming = new URL(`http://localhost${url}`);
  let pathname = incoming.pathname;

  // The origin collapses repeated slashes with a 308 before any routing.
  if (/\/{2,}/.test(pathname)) {
    return {
      type: 'redirect',
      status: 308,
      location: pathname.replace(/\/{2,}/g, '/') + incoming.search
    };
  }

  for (const route of routes) {
    if (route.handle) {
      if (route.handle !== 'filesystem') throw new Error(`Unsupported handle: ${route.handle}`);
      const file = lookup(pathname);
      if (file) return { type: 'file', file };
      continue;
    }
    // Case-sensitive, as the live origin matches (e2e/routes.spec.js pins it).
    const match = new RegExp(route.src).exec(pathname);
    if (!match) continue;
    const fill = (template) => template.replace(/\$(\d+)/g, (_, n) => match[Number(n)] ?? '');

    const location = route.headers?.Location ?? route.headers?.location;
    if (route.status && location) {
      // Vercel carries the request's query string over to the Location.
      const target = new URL(fill(location), 'http://localhost');
      for (const [key, value] of incoming.searchParams) target.searchParams.append(key, value);
      return {
        type: 'redirect',
        status: route.status,
        location: target.pathname + target.search
      };
    }
    if (route.dest) {
      pathname = new URL(fill(route.dest), 'http://localhost').pathname;
      if (route.check) {
        const file = lookup(pathname);
        if (file) return { type: 'file', file };
      }
      // On a miss, routing carries on with the rewritten path.
      continue;
    }
    if (!route.continue) throw new Error(`Unsupported route: ${JSON.stringify(route)}`);
  }

  const file = lookup(pathname);
  return file ? { type: 'file', file } : { type: 'notFound' };
}

export function createHandler({ buildDir, routes }) {
  const lookup = fileLookup(buildDir);
  return (req, res) => {
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.writeHead(405, { Allow: 'GET, HEAD' });
      res.end();
      return;
    }
    const result = resolveRequest(req.url, routes, lookup);
    const cacheControl = { 'Cache-Control': 'public, max-age=0, must-revalidate' };
    if (result.type === 'redirect') {
      res.writeHead(result.status, { ...cacheControl, Location: result.location });
      res.end();
    } else if (result.type === 'file') {
      const type = MIME_TYPES[extname(result.file)] ?? 'application/octet-stream';
      res.writeHead(200, { ...cacheControl, 'Content-Type': type });
      res.end(req.method === 'HEAD' ? undefined : readFileSync(result.file));
    } else {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('The page could not be found');
    }
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const here = fileURLToPath(new URL('.', import.meta.url));
  const config = JSON.parse(readFileSync(join(here, 'vercel.json'), 'utf8'));
  const buildDir = join(here, config.outputDirectory ?? 'build');
  if (!existsSync(join(buildDir, 'index.html'))) {
    console.error(`No build in ${buildDir}. Run "npm run build:policyengine" first.`);
    process.exit(1);
  }
  const routes = await compileRoutes(config);
  const port = Number(process.env.PORT ?? 4173);
  createServer(createHandler({ buildDir, routes })).listen(port, () => {
    const origin = `http://localhost:${port}`;
    console.log(`Serving ${buildDir} with vercel.json routing at ${origin}\n`);
    console.log(`  Explorer:   ${origin}/us/obbba-households`);
    console.log(`  Household:  ${origin}/us/obbba-households?household=39519&baseline=tcja-expiration`);
    console.log(`  Districts:  ${origin}/us/obbba-households/explore`);
    console.log(`  Paper:      ${origin}/us/obbba-households/paper`);
    console.log(`  Old slug:   ${origin}/us/obbba-household-explorer (redirects)`);
  });
}
