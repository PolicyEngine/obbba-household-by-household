#!/usr/bin/env python3
"""
Minimal reproducible example of the itemization bug.
Uses the Simulation class for single-household testing.
"""

from policyengine_us import Simulation
from policyengine_us.model_api import *
import sys

sys.path.append('data')
from reforms import (
    current_law_baseline,
    senate_finance_tax_rate_reform,
    senate_finance_sd_reform,
    senate_finance_exemption_reform,
    senate_finance_ctc_reform
)

def create_test_situation():
    """Create a test household similar to 4428."""
    return {
        "people": {
            "head": {
                "age": {2026: 70},
                "employment_income": {2026: 25000},
                "medical_out_of_pocket_expenses": {2026: 3900},
                "charitable_cash_donations": {2026: 60},
            },
            "spouse": {  
                "age": {2026: 43},
                "employment_income": {2026: 24000},
            },
            "child1": {
                "age": {2026: 12},
            },
            "child2": {
                "age": {2026: 10},
            },
            "child3": {
                "age": {2026: 8},
            },
            "child4": {
                "age": {2026: 6},
            },
        },
        "tax_units": {
            "tax_unit": {
                "members": ["head", "spouse", "child1", "child2", "child3", "child4"],
                "state_income_tax": {2026: 1100},
            }
        },
        "households": {
            "household": {
                "members": ["head", "spouse", "child1", "child2", "child3", "child4"],
                "state_code": {2026: "MA"},
            }
        },
    }

def test_bug():
    """Test the itemization bug."""
    
    situation = create_test_situation()
    
    # Test with full reform stack
    baseline_reform = current_law_baseline()
    full_stack = baseline_reform
    full_stack = (full_stack, senate_finance_tax_rate_reform())
    full_stack = (full_stack, senate_finance_sd_reform())
    full_stack = (full_stack, senate_finance_exemption_reform())
    full_stack = (full_stack, senate_finance_ctc_reform())
    
    print("Testing with full reform stack including CTC...")
    sim = Simulation(situation=situation, reform=full_stack)
    
    itemizes = sim.calculate("tax_unit_itemizes", 2026)[0]
    deductions = sim.calculate("taxable_income_deductions", 2026)[0]
    tax_if_itemizing = sim.calculate("tax_liability_if_itemizing", 2026)[0]
    tax_if_not_itemizing = sim.calculate("tax_liability_if_not_itemizing", 2026)[0]
    ma_tax = sim.calculate("ma_income_tax", 2026)[0]
    
    print(f"\nResults:")
    print(f"  Itemizes: {bool(itemizes)}")
    print(f"  Deductions: ${deductions:,.2f}")
    print(f"  Tax if itemizing: ${tax_if_itemizing:,.2f}")
    print(f"  Tax if NOT itemizing: ${tax_if_not_itemizing:,.2f}")
    print(f"  Should itemize: {tax_if_itemizing < tax_if_not_itemizing}")
    print(f"  MA state tax: ${ma_tax:,.2f}")
    
    if itemizes and not (tax_if_itemizing < tax_if_not_itemizing):
        print("\n*** BUG CONFIRMED: Household itemizes despite worse outcome! ***")
    
    # Test without CTC
    print("\n" + "=" * 60)
    print("Testing WITHOUT CTC reform...")
    
    no_ctc_stack = baseline_reform
    no_ctc_stack = (no_ctc_stack, senate_finance_tax_rate_reform())
    no_ctc_stack = (no_ctc_stack, senate_finance_sd_reform())
    no_ctc_stack = (no_ctc_stack, senate_finance_exemption_reform())
    
    sim2 = Simulation(situation=situation, reform=no_ctc_stack)
    itemizes2 = sim2.calculate("tax_unit_itemizes", 2026)[0]
    
    print(f"\nItemizes without CTC reform: {bool(itemizes2)}")
    
    if not itemizes2 and itemizes:
        print("\nCONFIRMED: CTC reform triggers the erroneous itemization!")

if __name__ == "__main__":
    test_bug()