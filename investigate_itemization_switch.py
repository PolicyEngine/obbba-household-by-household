#!/usr/bin/env python3
"""
Investigate why CTC expansion causes itemization switch.
"""

from policyengine_us import Microsimulation
from policyengine_us.model_api import *
import numpy as np
import sys

# Add the data directory to path to import reforms
sys.path.append('data')
from reforms import (
    current_law_baseline,
    senate_finance_tax_rate_reform,
    senate_finance_sd_reform,
    senate_finance_exemption_reform,
    senate_finance_ctc_reform
)

def investigate_itemization():
    """Investigate why CTC causes itemization switch."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Get baseline
    baseline_reform = current_law_baseline()
    
    # Stack reforms up to just before CTC
    pre_ctc_reform = baseline_reform
    pre_ctc_reform = (pre_ctc_reform, senate_finance_tax_rate_reform())
    pre_ctc_reform = (pre_ctc_reform, senate_finance_sd_reform())
    pre_ctc_reform = (pre_ctc_reform, senate_finance_exemption_reform())
    
    # Stack with CTC
    with_ctc_reform = (pre_ctc_reform, senate_finance_ctc_reform())
    
    print("Creating simulations...")
    pre_ctc_sim = Microsimulation(reform=pre_ctc_reform, dataset=dataset_path)
    with_ctc_sim = Microsimulation(reform=with_ctc_reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = pre_ctc_sim.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    # Helper function
    def get_household_value(sim, variable, period=year):
        return sim.calculate(variable, map_to="household", period=period).values[household_4428_idx]
    
    print("\n" + "=" * 60)
    print("ITEMIZATION DECISION ANALYSIS")
    print("=" * 60)
    
    # Check itemization status
    pre_itemizes = get_household_value(pre_ctc_sim, "tax_unit_itemizes")
    with_itemizes = get_household_value(with_ctc_sim, "tax_unit_itemizes")
    
    print(f"\nItemization status:")
    print(f"  Pre-CTC: {'Yes' if pre_itemizes else 'No'}")
    print(f"  With-CTC: {'Yes' if with_itemizes else 'No'}")
    
    # Check standard deduction vs itemized deductions
    pre_standard = get_household_value(pre_ctc_sim, "standard_deduction")
    with_standard = get_household_value(with_ctc_sim, "standard_deduction")
    
    pre_itemized = get_household_value(pre_ctc_sim, "itemized_taxable_income_deductions")
    with_itemized = get_household_value(with_ctc_sim, "itemized_taxable_income_deductions")
    
    print(f"\nStandard deduction:")
    print(f"  Pre-CTC: ${pre_standard:,.2f}")
    print(f"  With-CTC: ${with_standard:,.2f}")
    
    print(f"\nItemized deductions:")
    print(f"  Pre-CTC: ${pre_itemized:,.2f}")
    print(f"  With-CTC: ${with_itemized:,.2f}")
    
    # Check components of itemized deductions
    itemized_components = [
        "medical_expense_deduction",
        "salt_deduction",
        "qualified_interest_deduction",
        "charitable_deduction"
    ]
    
    print("\nItemized deduction components:")
    for component in itemized_components:
        pre_val = get_household_value(pre_ctc_sim, component)
        with_val = get_household_value(with_ctc_sim, component)
        if pre_val > 0 or with_val > 0:
            print(f"\n{component}:")
            print(f"  Pre-CTC: ${pre_val:,.2f}")
            print(f"  With-CTC: ${with_val:,.2f}")
            print(f"  Change: ${with_val - pre_val:,.2f}")
    
    # Check AGI - this might affect medical expense deduction
    pre_agi = get_household_value(pre_ctc_sim, "adjusted_gross_income")
    with_agi = get_household_value(with_ctc_sim, "adjusted_gross_income")
    
    print(f"\nAdjusted Gross Income:")
    print(f"  Pre-CTC: ${pre_agi:,.2f}")
    print(f"  With-CTC: ${with_agi:,.2f}")
    print(f"  Change: ${with_agi - pre_agi:,.2f}")
    
    # Check taxable income
    pre_taxable = get_household_value(pre_ctc_sim, "taxable_income")
    with_taxable = get_household_value(with_ctc_sim, "taxable_income")
    
    print(f"\nTaxable income:")
    print(f"  Pre-CTC: ${pre_taxable:,.2f}")
    print(f"  With-CTC: ${with_taxable:,.2f}")
    print(f"  Change: ${with_taxable - pre_taxable:,.2f}")
    
    # Check CTC amounts
    pre_ctc = get_household_value(pre_ctc_sim, "ctc")
    with_ctc = get_household_value(with_ctc_sim, "ctc")
    
    print(f"\nChild Tax Credit:")
    print(f"  Pre-CTC: ${pre_ctc:,.2f}")
    print(f"  With-CTC: ${with_ctc:,.2f}")
    print(f"  Change: ${with_ctc - pre_ctc:,.2f}")
    
    # Check if there's something about the CTC reform that affects income
    print("\n" + "=" * 60)
    print("HYPOTHESIS: The CTC reform might be changing something other than just the credit amount.")
    print("Let's check what the senate_finance_ctc_reform actually does...")
    
if __name__ == "__main__":
    investigate_itemization()