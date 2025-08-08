#!/usr/bin/env python3
"""
Demonstrate how federal CTC expansion reduces MA state tax.
"""

from policyengine_us import Simulation
from policyengine_us.model_api import *

print("=" * 70)
print("FEDERAL CTC EXPANSION REDUCES MA STATE TAX")
print("=" * 70)

# Create a family similar to tax unit 442801
situation = {
    "people": {
        "parent1": {
            "age": {2026: 47},
            "employment_income": {2026: 22500},
            "medical_out_of_pocket_expenses": {2026: 3900},
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
            "state_income_tax": {2026: 900},
        }
    },
    "households": {
        "household": {
            "members": ["parent1", "parent2", "child1", "child2", "child3", "child4"],
            "state_code": {2026: "MA"},
        }
    },
}

# Reform stack WITHOUT CTC expansion
reform_no_ctc = Reform.from_dict({
    # Tax rates
    "gov.irs.income.bracket.rates.2": {"2026-01-01": 0.15},
    "gov.irs.income.bracket.rates.3": {"2026-01-01": 0.25},
    # Standard deduction increase
    "gov.irs.deductions.standard.amount.JOINT": {"2026-01-01": 48900},
    # Exemption elimination
    "gov.irs.income.exemption.amount": {"2026-01-01": 0},
}, country_id="us")

sim_no_ctc = Simulation(situation=situation, reform=reform_no_ctc)

print("\nWITHOUT CTC EXPANSION:")
print(f"  Federal itemizes: {bool(sim_no_ctc.calculate('tax_unit_itemizes', 2026)[0])}")
print(f"  MA state tax: ${sim_no_ctc.calculate('ma_income_tax', 2026)[0]:,.2f}")
print(f"  MA Part B exemption: ${sim_no_ctc.calculate('ma_part_b_taxable_income_exemption', 2026)[0]:,.2f}")

# Add CTC expansion
reform_with_ctc = Reform.from_dict({
    # Same as above plus CTC
    "gov.irs.income.bracket.rates.2": {"2026-01-01": 0.15},
    "gov.irs.income.bracket.rates.3": {"2026-01-01": 0.25},
    "gov.irs.deductions.standard.amount.JOINT": {"2026-01-01": 48900},
    "gov.irs.income.exemption.amount": {"2026-01-01": 0},
    # CTC expansion
    "gov.contrib.reconciliation.ctc.in_effect": {"2026-01-01": True},
    "gov.irs.credits.ctc.amount.base[0].amount": {"2026-01-01": 2200},
    "gov.irs.credits.ctc.refundable.individual_max": {"2026-01-01": 1700},
}, country_id="us")

sim_with_ctc = Simulation(situation=situation, reform=reform_with_ctc)

print("\nWITH CTC EXPANSION:")
print(f"  Federal itemizes: {bool(sim_with_ctc.calculate('tax_unit_itemizes', 2026)[0])}")
print(f"  MA state tax: ${sim_with_ctc.calculate('ma_income_tax', 2026)[0]:,.2f}")
print(f"  MA Part B exemption: ${sim_with_ctc.calculate('ma_part_b_taxable_income_exemption', 2026)[0]:,.2f}")

# Compare the two scenarios
ma_tax_no_ctc = sim_no_ctc.calculate('ma_income_tax', 2026)[0]
ma_tax_with_ctc = sim_with_ctc.calculate('ma_income_tax', 2026)[0]

ma_exemption_no_ctc = sim_no_ctc.calculate('ma_part_b_taxable_income_exemption', 2026)[0]
ma_exemption_with_ctc = sim_with_ctc.calculate('ma_part_b_taxable_income_exemption', 2026)[0]

print("\n" + "=" * 70)
print("IMPACT OF CTC EXPANSION:")
print(f"  MA state tax change: ${ma_tax_with_ctc - ma_tax_no_ctc:,.2f}")
print(f"  MA Part B exemption change: ${ma_exemption_with_ctc - ma_exemption_no_ctc:,.2f}")

print(f"\nMECHANISM:")
print(f"1. CTC expansion causes federal itemization")
print(f"2. MA allows itemizers to deduct medical expenses in Part B exemption")
print(f"3. Medical expense deduction: ${sim_with_ctc.calculate('medical_expense_deduction', 2026)[0]:,.2f}")
print(f"4. MA tax rate: 5%")
print(f"5. Tax savings: ${ma_exemption_with_ctc - ma_exemption_no_ctc:,.2f} × 5% = ${(ma_exemption_with_ctc - ma_exemption_no_ctc) * 0.05:,.2f}")

# Additional details
print(f"\nDETAILS:")
print(f"  Federal tax if itemizing: ${sim_with_ctc.calculate('tax_liability_if_itemizing', 2026)[0]:,.2f}")
print(f"  Federal tax if standard: ${sim_with_ctc.calculate('tax_liability_if_not_itemizing', 2026)[0]:,.2f}")
print(f"  -> Same either way, so itemization is rational")