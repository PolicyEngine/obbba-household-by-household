#!/usr/bin/env python3
"""
Create MRE showing federal CTC reducing MA state tax.
"""

from policyengine_us import Simulation
from policyengine_us.model_api import *

# Key insight: Need income where itemized deductions are close to standard deduction
# and CTC tips the balance to make federal tax equal either way

situation = {
    "people": {
        "parent1": {
            "age": {2026: 45},
            "employment_income": {2026: 35_000},
            "medical_out_of_pocket_expenses": {2026: 5_000},
        },
        "parent2": {
            "age": {2026: 43},
        },
        "child1": {"age": {2026: 13}},
        "child2": {"age": {2026: 10}},
    },
    "tax_units": {
        "tax_unit": {
            "members": ["parent1", "parent2", "child1", "child2"],
            "state_income_tax": {2026: 1_000},  # Add some state tax to itemize
        }
    },
    "households": {
        "household": {
            "members": ["parent1", "parent2", "child1", "child2"],
            "state_code": {2026: "MA"},
        }
    },
}

print("Testing CTC effect on MA tax...")
print("=" * 60)

# Baseline (current law)
sim_baseline = Simulation(situation=situation)
baseline_itemizes = bool(sim_baseline.calculate('tax_unit_itemizes', 2026)[0])
baseline_ma_tax = sim_baseline.calculate('ma_income_tax', 2026)[0]

print(f"\nBASELINE (current law):")
print(f"  Federal itemizes: {baseline_itemizes}")
print(f"  MA state tax: ${baseline_ma_tax:,.2f}")

# With increased CTC
reform_ctc = Reform.from_dict({
    "gov.irs.credits.ctc.amount.base[0].amount": {"2026-01-01": 3_000},
}, country_id="us")

sim_ctc = Simulation(situation=situation, reform=reform_ctc)
ctc_itemizes = bool(sim_ctc.calculate('tax_unit_itemizes', 2026)[0])
ctc_ma_tax = sim_ctc.calculate('ma_income_tax', 2026)[0]

print(f"\nWITH INCREASED CTC:")
print(f"  Federal itemizes: {ctc_itemizes}")
print(f"  MA state tax: ${ctc_ma_tax:,.2f}")

# Check the mechanism
if ctc_itemizes != baseline_itemizes:
    print(f"\n✓ CTC changes itemization: {baseline_itemizes} → {ctc_itemizes}")
    
    if ctc_itemizes:
        med_deduction = sim_ctc.calculate('medical_expense_deduction', 2026)[0]
        ma_exemption = sim_ctc.calculate('ma_part_b_taxable_income_exemption', 2026)[0]
        print(f"  Medical expense deduction: ${med_deduction:,.2f}")
        print(f"  MA Part B exemption: ${ma_exemption:,.2f}")

ma_tax_change = ctc_ma_tax - baseline_ma_tax
if ma_tax_change < 0:
    print(f"\n✓ FEDERAL CTC REDUCES MA TAX BY ${-ma_tax_change:,.2f}")
else:
    print(f"\n✗ No MA tax reduction (change: ${ma_tax_change:,.2f})")

# Show federal tax comparison with CTC
fed_item = sim_ctc.calculate('tax_liability_if_itemizing', 2026)[0]
fed_std = sim_ctc.calculate('tax_liability_if_not_itemizing', 2026)[0]
print(f"\nWith CTC, federal tax comparison:")
print(f"  If itemizing: ${fed_item:,.2f}")
print(f"  If standard: ${fed_std:,.2f}")
print(f"  Difference: ${abs(fed_item - fed_std):,.2f}")