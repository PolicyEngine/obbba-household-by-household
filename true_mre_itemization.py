#!/usr/bin/env python3
"""
True minimal reproducible example showing itemization calculation issue.
"""

from policyengine_us import Simulation
from policyengine_us.model_api import *

def create_mre():
    """Create minimal scenario that reproduces the issue."""
    
    # Create a simplified version of tax unit 442801
    situation = {
        "people": {
            "parent1": {
                "age": {2026: 47},
                "employment_income": {2026: 25280},
                "medical_out_of_pocket_expenses": {2026: 3900},
                "charitable_cash_donations": {2026: 60},
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
                "state_income_tax": {2026: 1100},
            }
        },
        "households": {
            "household": {
                "members": ["parent1", "parent2", "child1", "child2", "child3", "child4"],
                "state_code": {2026: "MA"},
            }
        },
    }
    
    # Create reform
    reform = Reform.from_dict({
        # Tax rates
        "gov.irs.income.bracket.rates.2": {"2026-01-01": 0.15},
        "gov.irs.income.bracket.rates.3": {"2026-01-01": 0.25},
        "gov.irs.income.bracket.rates.4": {"2026-01-01": 0.28},
        # Standard deduction
        "gov.irs.deductions.standard.amount.JOINT": {"2026-01-01": 48900},
        "gov.irs.deductions.standard.amount.SINGLE": {"2026-01-01": 36950},
        "gov.irs.deductions.standard.amount.HEAD_OF_HOUSEHOLD": {"2026-01-01": 42150},
        # Exemption elimination
        "gov.irs.income.exemption.amount": {"2026-01-01": 0},
        # CTC reform
        "gov.contrib.reconciliation.ctc.in_effect": {"2026-01-01": True},
        "gov.irs.credits.ctc.amount.base[0].amount": {"2026-01-01": 2200},
        "gov.irs.credits.ctc.refundable.individual_max": {"2026-01-01": 1700},
    }, country_id="us")
    
    return situation, reform

def test_issue():
    """Test the itemization issue."""
    
    situation, reform = create_mre()
    
    print("Testing synthetic tax unit similar to 442801...\n")
    
    # Test with reform
    sim = Simulation(situation=situation, reform=reform)
    
    itemizes = sim.calculate("tax_unit_itemizes", 2026)[0]
    deductions = sim.calculate("taxable_income_deductions", 2026)[0]
    tax_if_item = sim.calculate("tax_liability_if_itemizing", 2026)[0]
    tax_if_std = sim.calculate("tax_liability_if_not_itemizing", 2026)[0]
    
    print("Results:")
    print(f"  Itemizes: {bool(itemizes)}")
    print(f"  Total deductions: ${deductions:,.2f}")
    print(f"  Tax if itemizing: ${tax_if_item:,.2f}")
    print(f"  Tax if standard: ${tax_if_std:,.2f}")
    print(f"  Difference: ${abs(tax_if_item - tax_if_std):,.2f}")
    
    # Get more details
    agi = sim.calculate("adjusted_gross_income", 2026)[0]
    itemized_ded = sim.calculate("itemized_taxable_income_deductions", 2026)[0]
    standard_ded = sim.calculate("standard_deduction", 2026)[0]
    
    print(f"\nDetails:")
    print(f"  AGI: ${agi:,.2f}")
    print(f"  Itemized deductions: ${itemized_ded:,.2f}")
    print(f"  Standard deduction: ${standard_ded:,.2f}")
    
    # Check components if itemizing
    if deductions != standard_ded and deductions != itemized_ded:
        print(f"\nDeduction mystery:")
        print(f"  Total deductions: ${deductions:,.2f}")
        print(f"  Neither standard (${standard_ded:,.2f}) nor itemized (${itemized_ded:,.2f})")
        print(f"  Extra amount: ${deductions - itemized_ded:,.2f}")

if __name__ == "__main__":
    test_issue()