# Serving the explorer on policyengine.org

The explorer lives at **https://www.policyengine.org/us/obbba-households**. policyengine.org (PolicyEngine/policyengine-app-v2, `website/`) proxies that path to this app's Vercel deployment, https://obbba-household-by-household.vercel.app/us/obbba-households, as a path-mounted multizone route (`website/src/data/appZoneRoutes.ts`). The proxy does not inject the parent site shell, so `src/routes/+layout.svelte` renders the PolicyEngine header and footer itself.

## Base path

SvelteKit is built with `BASE_PATH=/us/obbba-households` (`npm run build:policyengine`, which Vercel runs). The public path and the proxied path must match: SvelteKit treats any URL outside its base as external and reloads it, so serving this bundle under any other path loops.

Other builds:
- GitHub Pages (`deploy.yml`) uses `/obbba-household-by-household` and serves https://policyengine.github.io/obbba-household-by-household/.
- `npm run dev` uses the same default.

## Routing (`vercel.json`)

| Request | Response |
|---|---|
| `/` and `/index.html` | 307 to `/us/obbba-households` |
| `/us/obbba-household-explorer[/*]`, `/us/obbba-household-by-household[/*]` (old slugs) | 307 to `/us/obbba-households[/*]`, query kept |
| Any path ending in `/` | 308 to the same path without it (`trailingSlash: false`, as policyengine.org does) |
| `/us/obbba-households`, `/explore`, `/explore/*` | the SPA shell (`index.html`) |
| `/us/obbba-households/*` | the file under `build/`; a missing file is a 404 |

policyengine.org sends the old slugs to the new one with its own permanent 308s (`website/next.config.ts`). It also redirects `/us/obbba-scatter`, the `/us/obba-household-explorer` typo, the `/us/research/obbba-household-*` forms, and the temporary `/us/ob3-households` alias.

`src/app.html` also carries a guard. If the page is ever served outside the base anyway, the guard moves it under the base before SvelteKit starts, keeping the old-slug suffix, the query and the hash.

## Paper

The working paper lives at `/us/obbba-households/paper`: a wrapper, `static/paper/index.html`, around the manuscript in `static/paper/web/`. Both hosts strip the trailing slash, so the wrapper pins `<base>` to the paper directory before any of its relative links are parsed.

## Local serving

`serve-policyengine.js` serves `build/` with the routing above. It compiles `vercel.json` with `@vercel/routing-utils`, the compiler the Vercel CLI uses. It deliberately has no SPA fallback, so it 404s wherever Vercel would.

```bash
npm install --no-save @vercel/routing-utils@6.6.0   # kept out of package-lock.json
npm run build:policyengine
npm run serve:policyengine                          # http://localhost:4173/us/obbba-households
```

`./test-policyengine-build.sh` does all three steps.

## Rollback floors

Fix forward where possible. If you must roll back:

- **Keep the parent route.** Never revert or Instant-Rollback policyengine.org below the release that proxies `/us/obbba-households` (policyengine-app-v2#1226) while this app serves that base. The old URLs redirect there.
- **Keep this app on the new base.** Never take this app below the base-path move (#250) while policyengine.org 308s the old slugs (policyengine-app-v2#1178). The earlier deployment 307s the new slug back to the old one, and the two redirects would loop.
- **Order matters.** Roll back policyengine.org's redirects first, confirm that's live, then this app.
