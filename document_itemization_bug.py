#!/usr/bin/env python3
"""
Document the itemization bug with household 4428 from enhanced_cps_2024.

This demonstrates a bug where the CTC reform causes a household to itemize
even though it results in worse tax outcomes.
"""

from policyengine_us import Microsimulation
from policyengine_us.model_api import *
import numpy as np
import sys

sys.path.append('data')
from reforms import (
    current_law_baseline,
    senate_finance_tax_rate_reform,
    senate_finance_sd_reform,
    senate_finance_exemption_reform,
    senate_finance_ctc_reform
)

# Dataset and household ID
DATASET_PATH = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
HOUSEHOLD_ID = 4428
YEAR = 2026

def demonstrate_bug():
    """Demonstrate the itemization bug."""
    
    # Build reform stack that triggers the bug
    baseline_reform = current_law_baseline()
    reform_with_bug = baseline_reform
    reform_with_bug = (reform_with_bug, senate_finance_tax_rate_reform())
    reform_with_bug = (reform_with_bug, senate_finance_sd_reform())
    reform_with_bug = (reform_with_bug, senate_finance_exemption_reform())
    reform_with_bug = (reform_with_bug, senate_finance_ctc_reform())
    
    # Create simulation
    print(f"Loading household {HOUSEHOLD_ID} from enhanced CPS 2024...")
    sim = Microsimulation(reform=reform_with_bug, dataset=DATASET_PATH)
    
    # Find the household
    household_ids = sim.calculate("household_id", map_to="household", period=YEAR).values
    household_idx = np.where(household_ids == HOUSEHOLD_ID)[0][0]
    
    def get_value(variable):
        return sim.calculate(variable, map_to="household", period=YEAR).values[household_idx]
    
    print("\n" + "=" * 70)
    print("ITEMIZATION BUG DEMONSTRATION")
    print("=" * 70)
    
    # Get key values
    itemizes = get_value("tax_unit_itemizes")
    deductions = get_value("taxable_income_deductions")
    tax_if_itemizing = get_value("tax_liability_if_itemizing")
    tax_if_not_itemizing = get_value("tax_liability_if_not_itemizing")
    
    # Display the bug
    print(f"\nHousehold {HOUSEHOLD_ID} itemization decision:")
    print(f"  Actually itemizes: {bool(itemizes)} (value: {itemizes})")
    print(f"  Deductions taken: ${deductions:,.2f}")
    print(f"\n  Tax liability comparison:")
    print(f"    If itemizing: ${tax_if_itemizing:,.2f}")
    print(f"    If NOT itemizing: ${tax_if_not_itemizing:,.2f}")
    print(f"    Optimal choice: {'Itemize' if tax_if_itemizing < tax_if_not_itemizing else 'Standard deduction'}")
    
    if itemizes and not (tax_if_itemizing < tax_if_not_itemizing):
        print("\n*** BUG CONFIRMED ***")
        print("The household itemizes despite having WORSE tax liability!")
        print(f"They pay ${tax_if_itemizing - tax_if_not_itemizing:,.2f} MORE by itemizing.")
    
    # Show impact on MA taxes
    ma_tax = get_value("ma_income_tax")
    print(f"\nMassachusetts state tax: ${ma_tax:,.2f}")
    
    # Test without CTC to confirm it's the trigger
    print("\n" + "=" * 70)
    print("CONFIRMING CTC REFORM IS THE TRIGGER")
    print("=" * 70)
    
    reform_no_ctc = baseline_reform
    reform_no_ctc = (reform_no_ctc, senate_finance_tax_rate_reform())
    reform_no_ctc = (reform_no_ctc, senate_finance_sd_reform())
    reform_no_ctc = (reform_no_ctc, senate_finance_exemption_reform())
    # Skip CTC reform
    
    sim_no_ctc = Microsimulation(reform=reform_no_ctc, dataset=DATASET_PATH)
    itemizes_no_ctc = sim_no_ctc.calculate("tax_unit_itemizes", map_to="household", period=YEAR).values[household_idx]
    
    print(f"\nWithout CTC reform:")
    print(f"  Itemizes: {bool(itemizes_no_ctc)}")
    
    if not itemizes_no_ctc and itemizes:
        print("\n*** CONFIRMED: CTC reform triggers the erroneous itemization ***")

    # Additional details
    print("\n" + "=" * 70)
    print("ADDITIONAL DETAILS")
    print("=" * 70)
    
    print(f"\nWhen itemizing (actual behavior):")
    print(f"  Total deductions: ${deductions:,.2f}")
    print(f"  Itemized deductions component: ${get_value('itemized_taxable_income_deductions'):,.2f}")
    print(f"  Difference: ${deductions - get_value('itemized_taxable_income_deductions'):,.2f}")
    
    print(f"\nHousehold characteristics:")
    print(f"  State: Massachusetts")
    print(f"  AGI: ${get_value('adjusted_gross_income'):,.2f}")
    print(f"  Number of dependents: {int(get_value('tax_unit_dependents'))}")
    print(f"  Medical expenses: ${get_value('medical_out_of_pocket_expenses'):,.2f}")
    
if __name__ == "__main__":
    demonstrate_bug()