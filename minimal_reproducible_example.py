#!/usr/bin/env python3
"""
Minimal reproducible example of the itemization bug.
"""

from policyengine_us import Microsimulation
from policyengine_us.model_api import *
import pandas as pd
import sys

sys.path.append('data')
from reforms import (
    current_law_baseline,
    senate_finance_tax_rate_reform,
    senate_finance_sd_reform,
    senate_finance_exemption_reform,
    senate_finance_ctc_reform
)

def create_minimal_household():
    """Create a minimal household similar to 4428."""
    return {
        "people": {
            "person1": {  # Head
                "age": {2026: 70},
                "employment_income": {2026: 25000},
            },
            "person2": {  # Spouse  
                "age": {2026: 43},
                "employment_income": {2026: 24000},
            },
            "child1": {
                "age": {2026: 12},
                "employment_income": {2026: 0},
            },
            "child2": {
                "age": {2026: 10},
                "employment_income": {2026: 0},
            },
            "child3": {
                "age": {2026: 8},
                "employment_income": {2026: 0},
            },
            "child4": {
                "age": {2026: 6},
                "employment_income": {2026: 0},
            },
        },
        "tax_units": {
            "tax_unit": {
                "members": ["person1", "person2", "child1", "child2", "child3", "child4"],
                "medical_out_of_pocket_expenses": {2026: 3900},
                "state_income_tax": {2026: 1100},
                "charitable_cash_donations": {2026: 60},
            }
        },
        "households": {
            "household": {
                "members": ["person1", "person2", "child1", "child2", "child3", "child4"],
                "state_code": {2026: "MA"},
            }
        },
    }

def test_itemization_bug():
    """Test the itemization bug with minimal example."""
    
    situation = create_minimal_household()
    year = 2026
    
    # Build reform stack
    baseline_reform = current_law_baseline()
    reform_stack = baseline_reform
    reform_stack = (reform_stack, senate_finance_tax_rate_reform())
    reform_stack = (reform_stack, senate_finance_sd_reform())
    reform_stack = (reform_stack, senate_finance_exemption_reform())
    reform_stack = (reform_stack, senate_finance_ctc_reform())
    
    print("Creating simulation with minimal household...")
    sim = Microsimulation(reform=reform_stack, situation=situation)
    
    # Check itemization decision
    itemizes = sim.calculate("tax_unit_itemizes", period=year).values[0]
    deductions = sim.calculate("taxable_income_deductions", period=year).values[0]
    
    # Check decision logic
    tax_if_itemizing = sim.calculate("tax_liability_if_itemizing", period=year).values[0]
    tax_if_not_itemizing = sim.calculate("tax_liability_if_not_itemizing", period=year).values[0]
    
    # Check MA state tax
    ma_tax = sim.calculate("ma_income_tax", period=year).values[0]
    
    print("\n" + "=" * 60)
    print("ITEMIZATION BUG REPRODUCTION")
    print("=" * 60)
    
    print(f"\nItemization decision:")
    print(f"  Actually itemizes: {itemizes}")
    print(f"  Tax if itemizing: ${tax_if_itemizing:,.2f}")
    print(f"  Tax if NOT itemizing: ${tax_if_not_itemizing:,.2f}")
    print(f"  Should itemize: {tax_if_itemizing < tax_if_not_itemizing}")
    
    print(f"\nDeductions taken: ${deductions:,.2f}")
    print(f"MA state tax: ${ma_tax:,.2f}")
    
    if itemizes and not (tax_if_itemizing < tax_if_not_itemizing):
        print("\n*** BUG CONFIRMED ***")
        print("Household itemizes despite it being worse for taxes!")
    
    # Test without CTC reform
    print("\n" + "=" * 60)
    print("TESTING WITHOUT CTC REFORM")
    print("=" * 60)
    
    no_ctc_stack = baseline_reform
    no_ctc_stack = (no_ctc_stack, senate_finance_tax_rate_reform())
    no_ctc_stack = (no_ctc_stack, senate_finance_sd_reform())
    no_ctc_stack = (no_ctc_stack, senate_finance_exemption_reform())
    # Skip CTC reform
    
    sim_no_ctc = Microsimulation(reform=no_ctc_stack, situation=situation)
    itemizes_no_ctc = sim_no_ctc.calculate("tax_unit_itemizes", period=year).values[0]
    print(f"\nItemizes without CTC reform: {itemizes_no_ctc}")
    
if __name__ == "__main__":
    test_itemization_bug()