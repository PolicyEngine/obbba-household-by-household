#!/usr/bin/env python3
"""
Create MRE showing federal CTC reducing MA state tax.
"""

from policyengine_us import Simulation
from policyengine_us.model_api import *

# The key is finding a tax unit where:
# 1. Without CTC: Standard deduction is better than itemizing
# 2. With CTC: Federal tax becomes equal either way, triggering itemization
# 3. Itemization allows MA medical expense deduction

# Let me try with specific values that should work
situation = {
    "people": {
        "parent1": {
            "age": {2026: 45},
            "employment_income": {2026: 17_237},
            "medical_out_of_pocket_expenses": {2026: 3_339},
        },
        "parent2": {
            "age": {2026: 43},
        },
        "child1": {"age": {2026: 13}},
        "child2": {"age": {2026: 12}},
        "child3": {"age": {2026: 6}},
        "child4": {"age": {2026: 4}},
    },
    "tax_units": {
        "tax_unit": {
            "members": ["parent1", "parent2", "child1", "child2", "child3", "child4"],
        }
    },
    "households": {
        "household": {
            "members": ["parent1", "parent2", "child1", "child2", "child3", "child4"],
            "state_code": {2026: "MA"},
        }
    },
}

print("Demonstrating federal CTC reducing MA state tax")
print("=" * 60)

# Test different scenarios to find the effect
scenarios = [
    ("Current Law", {}),
    ("Higher Standard Deduction", {
        "gov.irs.deductions.standard.amount.JOINT": {"2026-01-01": 48_900},
    }),
    ("Senate Finance (no CTC)", {
        "gov.irs.income.bracket.rates.2": {"2026-01-01": 0.15},
        "gov.irs.income.bracket.rates.3": {"2026-01-01": 0.25},
        "gov.irs.deductions.standard.amount.JOINT": {"2026-01-01": 48_900},
        "gov.irs.income.exemption.amount": {"2026-01-01": 0},
    }),
    ("Senate Finance + CTC", {
        "gov.irs.income.bracket.rates.2": {"2026-01-01": 0.15},
        "gov.irs.income.bracket.rates.3": {"2026-01-01": 0.25},
        "gov.irs.deductions.standard.amount.JOINT": {"2026-01-01": 48_900},
        "gov.irs.income.exemption.amount": {"2026-01-01": 0},
        "gov.contrib.reconciliation.ctc.in_effect": {"2026-01-01": True},
        "gov.irs.credits.ctc.amount.base[0].amount": {"2026-01-01": 2_200},
    }),
]

results = []
for name, reform_dict in scenarios:
    if reform_dict:
        reform = Reform.from_dict(reform_dict, country_id="us")
        sim = Simulation(situation=situation, reform=reform)
    else:
        sim = Simulation(situation=situation)
    
    itemizes = bool(sim.calculate('tax_unit_itemizes', 2026)[0])
    ma_tax = sim.calculate('ma_income_tax', 2026)[0]
    fed_item = sim.calculate('tax_liability_if_itemizing', 2026)[0]
    fed_std = sim.calculate('tax_liability_if_not_itemizing', 2026)[0]
    
    results.append({
        'name': name,
        'itemizes': itemizes,
        'ma_tax': ma_tax,
        'fed_diff': fed_item - fed_std
    })
    
    print(f"\n{name}:")
    print(f"  Itemizes: {itemizes}")
    print(f"  MA tax: ${ma_tax:,.2f}")
    print(f"  Fed tax diff (item - std): ${fed_item - fed_std:,.2f}")

# Check for the effect
print("\n" + "="*60)
print("ANALYSIS:")

# Compare Senate Finance without and with CTC
sf_no_ctc = results[2]
sf_with_ctc = results[3]

if sf_no_ctc['itemizes'] != sf_with_ctc['itemizes']:
    print(f"\n✓ CTC changes itemization: {sf_no_ctc['itemizes']} → {sf_with_ctc['itemizes']}")
    
ma_tax_change = sf_with_ctc['ma_tax'] - sf_no_ctc['ma_tax']
if ma_tax_change < 0:
    print(f"✓ MA tax reduced by ${-ma_tax_change:,.2f}")
    print(f"\nThis happens because:")
    print(f"1. CTC makes federal tax difference smaller: ${sf_no_ctc['fed_diff']:,.2f} → ${sf_with_ctc['fed_diff']:,.2f}")
    print(f"2. If itemization is triggered, MA allows medical expense deduction")
else:
    print(f"✗ MA tax not reduced (change: ${ma_tax_change:,.2f})")

# The issue is that PolicyEngine uses < not <=, so equal taxes don't trigger itemization
if abs(sf_with_ctc['fed_diff']) < 1:
    print(f"\nNOTE: Federal taxes are essentially equal (${sf_with_ctc['fed_diff']:,.2f} difference)")
    print("but PolicyEngine doesn't itemize because it uses < not <= in the comparison.")