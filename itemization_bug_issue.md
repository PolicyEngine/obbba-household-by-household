# Household itemizes despite worse tax outcome when CTC reform is applied

## Description

When applying the Senate Finance CTC reform (as part of a reform stack), certain households make irrational itemization decisions. Specifically, household 4428 from the enhanced_cps_2024 dataset chooses to itemize deductions even though it results in $1,789.27 worse tax liability compared to taking the standard deduction.

## Minimal Reproducible Example

```python
from policyengine_us import Microsimulation
from policyengine_us.model_api import *
import numpy as np

# Dataset and household ID that demonstrates the bug
DATASET_PATH = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
HOUSEHOLD_ID = 4428
YEAR = 2026

# Build reform stack that triggers the bug
baseline_reform = Reform.from_dict({}, country_id="us")

# Senate Finance tax rate reform
tax_rate_reform = Reform.from_dict({
    "gov.irs.income.bracket.rates.2": {"2026-01-01.2100-12-31": 0.15},
    "gov.irs.income.bracket.rates.3": {"2026-01-01.2100-12-31": 0.25},
    "gov.irs.income.bracket.rates.4": {"2026-01-01.2100-12-31": 0.28},
    "gov.irs.income.bracket.rates.5": {"2026-01-01.2100-12-31": 0.28},
    "gov.irs.income.bracket.rates.6": {"2026-01-01.2100-12-31": 0.35},
}, country_id="us")

# Senate Finance standard deduction reform  
sd_reform = Reform.from_dict({
    "gov.irs.deductions.standard.amount.JOINT": {"2026-01-01.2026-12-31": 48900},
    "gov.irs.deductions.standard.amount.SINGLE": {"2026-01-01.2026-12-31": 36950},
    "gov.irs.deductions.standard.amount.HEAD_OF_HOUSEHOLD": {"2026-01-01.2026-12-31": 42150},
}, country_id="us")

# Senate Finance exemption reform (sets to 0)
exemption_reform = Reform.from_dict({
    "gov.irs.income.exemption.amount": {"2026-01-01.2100-12-31": 0}
}, country_id="us")

# Senate Finance CTC reform
ctc_reform = Reform.from_dict({
    "gov.contrib.reconciliation.ctc.in_effect": {"2025-01-01.2100-12-31": True},
    "gov.irs.credits.ctc.amount.base[0].amount": {"2026-01-01.2026-12-31": 2200},
    "gov.irs.credits.ctc.refundable.individual_max": {"2026-01-01.2026-12-31": 1700},
}, country_id="us")

# Stack the reforms
reform_with_bug = baseline_reform
reform_with_bug = (reform_with_bug, tax_rate_reform)
reform_with_bug = (reform_with_bug, sd_reform)
reform_with_bug = (reform_with_bug, exemption_reform)
reform_with_bug = (reform_with_bug, ctc_reform)

# Create simulation
sim = Microsimulation(reform=reform_with_bug, dataset=DATASET_PATH)

# Find the household
household_ids = sim.calculate("household_id", map_to="household", period=YEAR).values
household_idx = np.where(household_ids == HOUSEHOLD_ID)[0][0]

def get_value(variable):
    return sim.calculate(variable, map_to="household", period=YEAR).values[household_idx]

# Demonstrate the bug
itemizes = get_value("tax_unit_itemizes")
tax_if_itemizing = get_value("tax_liability_if_itemizing")  
tax_if_not_itemizing = get_value("tax_liability_if_not_itemizing")

print(f"Household {HOUSEHOLD_ID} itemization decision:")
print(f"  Actually itemizes: {bool(itemizes)}")
print(f"  Tax if itemizing: ${tax_if_itemizing:,.2f}")
print(f"  Tax if NOT itemizing: ${tax_if_not_itemizing:,.2f}")
print(f"  Should itemize: {tax_if_itemizing < tax_if_not_itemizing}")

# Output:
# Household 4428 itemization decision:
#   Actually itemizes: True
#   Tax if itemizing: $-8,817.22
#   Tax if NOT itemizing: $-10,606.49
#   Should itemize: False
```

## Expected Behavior

The household should choose NOT to itemize since the standard deduction results in lower tax liability (-$10,606.49 is better than -$8,817.22).

## Actual Behavior  

The household itemizes despite it resulting in $1,789.27 worse tax outcome.

## Additional Context

1. **The bug only occurs with CTC reform**: Without the CTC reform in the stack, the household correctly chooses the standard deduction.

2. **Deduction amounts are unusual**: When itemizing, the household gets $18,906.70 in total deductions, which includes only $3,713.01 in itemized deductions. The extra $15,193.69 appears to come from subsequent reforms in the stack that modify deduction calculations.

3. **State tax impact**: This erroneous itemization triggers Massachusetts to apply the medical expense exemption for itemizers, affecting state tax calculations.

4. **Household characteristics**:
   - State: Massachusetts
   - AGI: $49,025.45  
   - Number of dependents: 3
   - Medical expenses: $3,901.80

## Environment

- PolicyEngine US version: [latest]
- Python version: 3.13
- Dataset: enhanced_cps_2024.h5

## Potential Root Cause

The itemization decision logic (`tax_unit_itemizes`) appears to be making an incorrect choice when certain reforms are stacked. The comparison of `tax_liability_if_itemizing` vs `tax_liability_if_not_itemizing` should prevent this, but the household itemizes anyway.