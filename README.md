# OBBBA Household Explorer

An interactive record-level view of how 21 modeled provisions of the One Big Beautiful Bill Act change household resources in 2026.

The national story uses the same certified Microcosm Build P results as the [OBBBA paper](https://github.com/PolicyEngine/obbba-paper):

- 57,240 modeled public-use household records, weighted to represent 124.6 million US households
- PolicyEngine 5.0.1 and PolicyEngine US 1.764.6
- OBBBA compared with a TCJA-expiration counterfactual
- Cash net income plus Medicaid, CHIP, and enrollee-assigned ACA premium tax credits valued at program cost
- Forward-order marginal contributions from 18 tax provisions and three reduced-form participation scenarios

The national data reproduce the paper's 2026 headline estimates: a $546.1 billion increase in household resources, or $4,384 per household; 82.8% of households gain more than $1 and 3.6% lose more than $1.

These are modeled records, not identifiable families. Their assigned household IDs exist only to support reproducible links. The district route remains on the predecessor district-target-calibrated data; Microcosm Build P's district assignments are not used for district estimates.

## Deep links

Use the `household` query parameter to open a record. The optional `baseline=tcja-expiration` parameter is retained for compatibility.

```text
https://www.policyengine.org/us/obbba-households?household=1026679&baseline=tcja-expiration
```

Links that request the retired `tcja-extension` dataset fall back to the paper-consistent TCJA-expiration baseline.

## Development

```bash
npm ci
npm run dev
```

Build the multizone path served by PolicyEngine (`/us/obbba-households`) and serve it locally with the production routing from `vercel.json`:

```bash
npm install --no-save @vercel/routing-utils@6.6.0
npm run build:policyengine
npm run serve:policyengine
```

See [POLICYENGINE_DEPLOYMENT.md](POLICYENGINE_DEPLOYMENT.md) for how policyengine.org serves the app, the old-slug redirects, and rollback order.

Run tests and the generated-data contract:

```bash
npm test -- --run
npm run validate:data
```

## Rebuilding the Microcosm export

The exporter reads the paper's committed household-level result frames and performs one lightweight metadata simulation for profile fields. It refuses to run unless the exact certified model and data bundle are active.

```bash
VIRTUAL_ENV=../obbba-paper/.venv-pe501 uv run --active --no-sync \
  python data/export_microcosm_explorer.py \
  --paper-root ../obbba-paper \
  --profile-cache /tmp/obbba_microcosm_profile.parquet \
  --output static/household_tax_income_changes_microcosm_buildp.csv \
  --manifest-output static/household_tax_income_changes_microcosm_buildp.manifest.json

node scripts/generate-minimal-1000.js
```

The manifest records the release build ID, certified input dataset SHA-256, model versions, resource definition, provision order, and weighted headline checks.
