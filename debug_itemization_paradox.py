#!/usr/bin/env python3
"""
Debug the paradox: Why does household switch to itemizing when itemized < standard?
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

def debug_itemization():
    """Debug the itemization paradox."""
    
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
    print("ITEMIZATION PARADOX INVESTIGATION")
    print("=" * 60)
    
    # Check the actual deduction taken
    pre_deduction_taken = get_household_value(pre_ctc_sim, "taxable_income_deductions")
    with_deduction_taken = get_household_value(with_ctc_sim, "taxable_income_deductions")
    
    print(f"\nActual deduction taken:")
    print(f"  Pre-CTC: ${pre_deduction_taken:,.2f}")
    print(f"  With-CTC: ${with_deduction_taken:,.2f}")
    
    # Check filing status
    filing_status = get_household_value(pre_ctc_sim, "filing_status")
    print(f"\nFiling status: {filing_status}")
    
    # Check if qbid is involved
    pre_qbid = get_household_value(pre_ctc_sim, "qualified_business_income_deduction")
    with_qbid = get_household_value(with_ctc_sim, "qualified_business_income_deduction")
    
    print(f"\nQualified Business Income Deduction:")
    print(f"  Pre-CTC: ${pre_qbid:,.2f}")
    print(f"  With-CTC: ${with_qbid:,.2f}")
    
    # Check if there are any errors in the tax calculation
    pre_tax_before_credits = get_household_value(pre_ctc_sim, "income_tax_before_credits")
    with_tax_before_credits = get_household_value(with_ctc_sim, "income_tax_before_credits")
    
    print(f"\nFederal tax before credits:")
    print(f"  Pre-CTC: ${pre_tax_before_credits:,.2f}")
    print(f"  With-CTC: ${with_tax_before_credits:,.2f}")
    
    # The itemization decision should be based on which gives lower taxable income
    pre_taxable_income = get_household_value(pre_ctc_sim, "taxable_income")
    with_taxable_income = get_household_value(with_ctc_sim, "taxable_income")
    
    print(f"\nTaxable income:")
    print(f"  Pre-CTC: ${pre_taxable_income:,.2f}")
    print(f"  With-CTC: ${with_taxable_income:,.2f}")
    
    # Check if this is a calculation error
    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print("The household is switching to itemizing even though itemized deductions")
    print("are much lower than the standard deduction. This suggests:")
    print("1. There's a bug in the itemization decision logic, OR")
    print("2. The CTC reform is changing something that affects the itemization calculation")
    print("3. This is a data artifact from how reforms are stacked in the simulation")
    
if __name__ == "__main__":
    debug_itemization()