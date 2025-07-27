#!/usr/bin/env python3
"""
Find the missing deduction component.
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

def find_deduction():
    """Find the missing deduction."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Build both reform stacks
    baseline_reform = current_law_baseline()
    
    # Without CTC
    pre_ctc_reform = baseline_reform
    pre_ctc_reform = (pre_ctc_reform, senate_finance_tax_rate_reform())
    pre_ctc_reform = (pre_ctc_reform, senate_finance_sd_reform())
    pre_ctc_reform = (pre_ctc_reform, senate_finance_exemption_reform())
    
    # With CTC  
    with_ctc_reform = (pre_ctc_reform, senate_finance_ctc_reform())
    
    print("Creating simulations...")
    pre_sim = Microsimulation(reform=pre_ctc_reform, dataset=dataset_path)
    with_sim = Microsimulation(reform=with_ctc_reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = pre_sim.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    def get_value(sim, variable):
        return sim.calculate(variable, map_to="household", period=year).values[household_4428_idx]
    
    # Force both to itemize for comparison
    tax_unit_count = len(pre_sim.calculate("tax_unit_id", period=year).values)
    
    pre_itemize = pre_sim.get_branch("pre_itemize")
    pre_itemize.set_input("tax_unit_itemizes", year, np.ones((tax_unit_count,), dtype=bool))
    
    with_itemize = with_sim.get_branch("with_itemize") 
    with_itemize.set_input("tax_unit_itemizes", year, np.ones((tax_unit_count,), dtype=bool))
    
    print("\n" + "=" * 60)
    print("DEDUCTION MYSTERY")
    print("=" * 60)
    
    # Compare taxable income deductions when both itemize
    pre_ded = get_value(pre_itemize, "taxable_income_deductions")
    with_ded = get_value(with_itemize, "taxable_income_deductions")
    
    print(f"\nWhen itemizing:")
    print(f"  Pre-CTC deductions: ${pre_ded:,.2f}")
    print(f"  With-CTC deductions: ${with_ded:,.2f}")
    print(f"  Difference: ${with_ded - pre_ded:,.2f}")
    
    # Check if it's in adjusted gross income
    pre_agi = get_value(pre_itemize, "adjusted_gross_income")
    with_agi = get_value(with_itemize, "adjusted_gross_income")
    
    print(f"\nAGI:")
    print(f"  Pre-CTC: ${pre_agi:,.2f}")
    print(f"  With-CTC: ${with_agi:,.2f}")
    
    # Maybe it's a dependent exemption that got reinstated?
    # Check number of dependents
    try:
        num_deps = get_value(pre_sim, "tax_unit_dependents")
        print(f"\nNumber of dependents: {num_deps}")
    except:
        pass
    
    # The $15,193.69 is suspiciously close to 4 * $3,800 = $15,200
    # Could this be personal exemptions sneaking back in?
    
    # Check if there's a parameter that got changed
    print("\nThe $15,193.69 difference is suspiciously close to:")
    print(f"  4 people * $3,800 = $15,200")
    print("\nThis suggests personal exemptions might be involved despite")
    print("the exemption reform setting them to 0...")
    
    # Check taxable income directly
    pre_ti = get_value(pre_itemize, "taxable_income")
    with_ti = get_value(with_itemize, "taxable_income")
    
    print(f"\nTaxable income:")
    print(f"  Pre-CTC: ${pre_ti:,.2f}")
    print(f"  With-CTC: ${with_ti:,.2f}")
    print(f"  Difference: ${with_ti - pre_ti:,.2f}")
    
if __name__ == "__main__":
    find_deduction()