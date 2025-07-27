#!/usr/bin/env python3
"""
MRE with closer match to household 4428.
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

def create_household_4428_match():
    """Create a closer match to household 4428."""
    return {
        "people": {
            "p1": {  # age 43
                "age": {2026: 43},
                "employment_income": {2026: 0},
            },
            "p2": {  # age 47 - likely head with income  
                "age": {2026: 47},
                "employment_income": {2026: 25281},
                "medical_out_of_pocket_expenses": {2026: 3902},
                "charitable_cash_donations": {2026: 62},
            },
            "p3": {  # age 23 - adult child with income
                "age": {2026: 23},
                "employment_income": {2026: 27579},
            },
            "p4": {  # age 13 - dependent
                "age": {2026: 13},
            },
            "p5": {  # age 6 - dependent
                "age": {2026: 6},
            },
            "p6": {  # age 4 - dependent
                "age": {2026: 4},
            },
            "p7": {  # age 12 - dependent
                "age": {2026: 12},
            },
        },
        "tax_units": {
            "tax_unit": {
                # Assuming p2 is head, p1 is spouse, and 4 youngest are dependents
                "members": ["p2", "p1", "p4", "p5", "p6", "p7"],
                "state_income_tax": {2026: 1106},
                "real_estate_taxes": {2026: 905},
            },
            # p3 (age 23) files separately
            "tax_unit2": {
                "members": ["p3"],
            }
        },
        "households": {
            "household": {
                "members": ["p1", "p2", "p3", "p4", "p5", "p6", "p7"],
                "state_code": {2026: "MA"},
            }
        },
    }

def test_closer_match():
    situation = create_household_4428_match()
    
    # Test with full reform stack
    baseline_reform = current_law_baseline()
    full_stack = baseline_reform
    full_stack = (full_stack, senate_finance_tax_rate_reform())
    full_stack = (full_stack, senate_finance_sd_reform())
    full_stack = (full_stack, senate_finance_exemption_reform())
    full_stack = (full_stack, senate_finance_ctc_reform())
    
    print("Testing closer match to household 4428...")
    sim = Simulation(situation=situation, reform=full_stack)
    
    # Check main tax unit
    itemizes = sim.calculate("tax_unit_itemizes", 2026)[0]
    deductions = sim.calculate("taxable_income_deductions", 2026)[0]
    tax_if_itemizing = sim.calculate("tax_liability_if_itemizing", 2026)[0]
    tax_if_not_itemizing = sim.calculate("tax_liability_if_not_itemizing", 2026)[0]
    agi = sim.calculate("adjusted_gross_income", 2026)[0]
    
    print(f"\nMain tax unit results:")
    print(f"  AGI: ${agi:,.2f}")
    print(f"  Itemizes: {bool(itemizes)}")
    print(f"  Deductions: ${deductions:,.2f}")
    print(f"  Tax if itemizing: ${tax_if_itemizing:,.2f}")
    print(f"  Tax if NOT itemizing: ${tax_if_not_itemizing:,.2f}")
    print(f"  Should itemize: {tax_if_itemizing < tax_if_not_itemizing}")
    
    if itemizes and not (tax_if_itemizing < tax_if_not_itemizing):
        print("\n*** BUG REPRODUCED! ***")
    
if __name__ == "__main__":
    test_closer_match()