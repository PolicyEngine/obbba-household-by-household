#!/usr/bin/env python3
"""
Create MRE with the specific Senate Finance reforms.
"""

from policyengine_us import Simulation
from policyengine_us.model_api import *

# Try to replicate conditions similar to household 4428
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

print("Testing Senate Finance reforms effect on MA tax...")
print("=" * 60)

# Step 1: Apply tax rate + standard deduction + exemption reforms (no CTC)
reform_no_ctc = Reform.from_dict({
    "gov.irs.income.bracket.rates.2": {"2026-01-01": 0.15},
    "gov.irs.income.bracket.rates.3": {"2026-01-01": 0.25},
    "gov.irs.income.bracket.rates.4": {"2026-01-01": 0.28},
    "gov.irs.deductions.standard.amount.JOINT": {"2026-01-01": 48_900},
    "gov.irs.income.exemption.amount": {"2026-01-01": 0},
}, country_id="us")

sim_no_ctc = Simulation(situation=situation, reform=reform_no_ctc)

# Calculate state income tax that will be used for itemization
state_tax = sim_no_ctc.calculate('state_income_tax', 2026)[0]
print(f"\nState income tax calculated: ${state_tax:,.2f}")

# Now update situation with calculated state tax
situation["tax_units"]["tax_unit"]["state_income_tax"] = {2026: state_tax}

# Re-run with state tax included
sim_no_ctc = Simulation(situation=situation, reform=reform_no_ctc)
no_ctc_itemizes = bool(sim_no_ctc.calculate('tax_unit_itemizes', 2026)[0])
no_ctc_ma_tax = sim_no_ctc.calculate('ma_income_tax', 2026)[0]

print(f"\nWITHOUT CTC EXPANSION:")
print(f"  Federal itemizes: {no_ctc_itemizes}")
print(f"  MA state tax: ${no_ctc_ma_tax:,.2f}")

# Show deductions
print(f"\n  Deduction details:")
print(f"    Medical expense deduction: ${sim_no_ctc.calculate('medical_expense_deduction', 2026)[0]:,.2f}")
print(f"    SALT deduction: ${sim_no_ctc.calculate('salt_deduction', 2026)[0]:,.2f}")
print(f"    Total itemized: ${sim_no_ctc.calculate('itemized_taxable_income_deductions', 2026)[0]:,.2f}")
print(f"    Standard deduction: ${sim_no_ctc.calculate('standard_deduction', 2026)[0]:,.2f}")

# Step 2: Add CTC expansion
reform_with_ctc = Reform.from_dict({
    "gov.irs.income.bracket.rates.2": {"2026-01-01": 0.15},
    "gov.irs.income.bracket.rates.3": {"2026-01-01": 0.25},
    "gov.irs.income.bracket.rates.4": {"2026-01-01": 0.28},
    "gov.irs.deductions.standard.amount.JOINT": {"2026-01-01": 48_900},
    "gov.irs.income.exemption.amount": {"2026-01-01": 0},
    # CTC expansion
    "gov.contrib.reconciliation.ctc.in_effect": {"2026-01-01": True},
    "gov.irs.credits.ctc.amount.base[0].amount": {"2026-01-01": 2_200},
}, country_id="us")

sim_with_ctc = Simulation(situation=situation, reform=reform_with_ctc)
with_ctc_itemizes = bool(sim_with_ctc.calculate('tax_unit_itemizes', 2026)[0])
with_ctc_ma_tax = sim_with_ctc.calculate('ma_income_tax', 2026)[0]

print(f"\nWITH CTC EXPANSION:")
print(f"  Federal itemizes: {with_ctc_itemizes}")
print(f"  MA state tax: ${with_ctc_ma_tax:,.2f}")

# Check federal tax comparison
fed_item = sim_with_ctc.calculate('tax_liability_if_itemizing', 2026)[0]
fed_std = sim_with_ctc.calculate('tax_liability_if_not_itemizing', 2026)[0]
print(f"\n  Federal tax comparison:")
print(f"    If itemizing: ${fed_item:,.2f}")
print(f"    If standard: ${fed_std:,.2f}")
print(f"    Difference: ${fed_item - fed_std:,.2f}")

# Result
ma_tax_change = with_ctc_ma_tax - no_ctc_ma_tax
print(f"\n{'='*60}")
if ma_tax_change < 0:
    print(f"✓ FEDERAL CTC REDUCES MA TAX BY ${-ma_tax_change:,.2f}")
    print(f"\nMechanism:")
    print(f"1. CTC makes federal tax nearly equal either way")
    print(f"2. Itemization status: {no_ctc_itemizes} → {with_ctc_itemizes}")
    if with_ctc_itemizes:
        med_ded = sim_with_ctc.calculate('medical_expense_deduction', 2026)[0]
        print(f"3. Medical expense deduction allowed: ${med_ded:,.2f}")
        print(f"4. MA tax savings: ${-ma_tax_change:,.2f}")
else:
    print(f"✗ No MA tax reduction")