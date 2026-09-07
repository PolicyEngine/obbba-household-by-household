# Progress: show taxes and benefits separately per provision

Branch: `provision-tax-benefit-split` (from `origin/main` @ 9c9284a)

## State

Complete. All gates green; draft PR open.

## Verified facts

- Sign identity. The exported net-income column satisfies
  `net = -(federal + state) + benefits`. Confirmed two ways: arithmetically on
  household 1009324's every nonzero provision and on its totals, and by
  `scripts/validate-microcosm-data.js:167`, which already asserts
  `resource - (-federal - state + benefits)` across the whole file and passes
  with a maximum residual of $1.20. A tax-liability decrease is therefore a
  gain for the household, and `taxChange = -(federal + state)`.
- Household 1009324 (OH, size 10), standard-deduction step:
  federal `-315.47461`, state `0`, benefits `55654.736`, net `55970.205`.
- 70 of 57,240 records have a nonzero `Change in benefits after Standard
  Deduction Reform` (the brief said 68); 54 of those also move a tax component
  at that step. Counts are identical at strict-nonzero and at the |x| > 0.5
  threshold this branch uses. `Exemption Reform` moves benefits for 6 records;
  `SNAP Takeup Reform` moves both tax and benefits for 7.
- The eighteen tax provisions are `PROVISIONS[0..17]`; the three participation
  scenarios are `PROVISIONS[18..20]`. Asserted in the test suite so a reorder
  fails loudly rather than silently mislabeling the disclosure.

## Done

1. `src/lib/components/provisionBreakdown.js` — the provision table moved out of
   the component byte-for-byte (order and descriptions untouched), plus
   `getProvisionBreakdown`, `getTotalsSplit`, the $0.50 threshold, and the two
   disclosure strings.
2. `HouseholdProfile.svelte` — split sub-line under each provision headline when
   both components clear the threshold; the disclosure sentence under a tax
   provision that moves benefits; the same split under the headline total; one
   line stating the sign convention above every split it governs.
3. Tests — `provisionBreakdown.test.js` (19 cases) against household 1009324's
   and 1002071's real CSV values; `HouseholdProfile.test.js` (11 cases)
   rewritten to mount the component and assert the rendered DOM instead of
   re-implementing the logic it was meant to test.
4. Browser check at 1280 / 390 / 320 px against the PolicyEngine-path bundle:
   the split, the disclosure, and the sign note all render, and
   `document.documentElement.scrollWidth === clientWidth` at every width.

## Gates

| command | exit |
| --- | --- |
| `npx prettier --write "src/**/*.{js,svelte,json,css}"` | 0 (touches only the 17 files already prettier-dirty on `main`; reverted) |
| `npx vitest --run` | 0 — 19 files, 122 tests |
| `node scripts/validate-microcosm-data.js` | 0 |
| `BASE_PATH=/us/obbba-household-explorer npx vite build` | 0 |
| `npx svelte-check --threshold warning` | 0 — 0 errors, 14 warnings, all pre-existing |

## Not done

- The prettier check exits 1 both on this branch and on `main`: 17 files under
  `src/` have never been prettier-clean. CI runs that step with `|| true`, so it
  does not gate. Fixing it is a repo-wide reformat and belongs in its own PR.
- The export carries one `Change in benefits after <provision>` column per
  provision, with no per-program split, so which of Medicaid, CHIP, or
  marketplace credits moves at a given step is not verifiable from the committed
  data. The disclosure sentence is the brief's mandated wording and is hedged
  accordingly.
