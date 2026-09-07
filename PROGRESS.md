# Progress: show taxes and benefits separately per provision

Branch: `provision-tax-benefit-split` (from `origin/main` @ 9c9284a)

## State

Baseline verified before any edit:

- `./node_modules/.bin/vitest --run` -> 18 files, 95 tests, exit 0.
- Household 1009324 (OH, size 10) confirmed in
  `static/household_tax_income_changes_microcosm_buildp.csv`:
  `Change in benefits after Standard Deduction Reform = 55654.736`,
  `Change in federal tax liability after Standard Deduction Reform = -315.47461`,
  `Change in net income after Standard Deduction Reform = 55970.205`.
- Sign identity confirmed on that record for every provision and for the totals:
  `net = -(federal + state) + benefits`. A tax-liability decrease is a gain for the
  household, so "Taxes" is rendered as `-(federal + state)`.
- 70 of 57,240 records (not 68) have a nonzero
  `Change in benefits after Standard Deduction Reform`; 54 of those also have a
  nonzero tax component at that step. Counts identical at strict-nonzero and at
  the |x| > 0.5 threshold this branch uses.

## Done

- (nothing yet)

## Next

1. Extract the provision table + breakdown into `src/lib/components/provisionBreakdown.js`
   (order and descriptions unchanged) with the tax/benefit split derived there.
2. Render the split sub-line, the benefits disclosure sentence, and the headline totals split
   in `HouseholdProfile.svelte`.
3. Tests against the real module using the 1009324 fixture.
4. format / test / validate:data / build:policyengine, then draft PR.
