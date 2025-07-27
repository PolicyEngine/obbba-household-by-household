#!/usr/bin/env python3
"""
Investigate why MA Part B taxable income decreases with CTC expansion.
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

def investigate_ma_part_b():
    """Investigate MA Part B taxable income calculation."""
    
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
    print("MA PART B TAXABLE INCOME CALCULATION")
    print("=" * 60)
    
    # MA Part B taxable income = MA Part B AGI - MA Part B deductions
    
    # Check Part B AGI
    pre_part_b_agi = get_household_value(pre_ctc_sim, "ma_part_b_agi")
    with_part_b_agi = get_household_value(with_ctc_sim, "ma_part_b_agi")
    
    print(f"MA Part B AGI:")
    print(f"  Pre-CTC: ${pre_part_b_agi:,.2f}")
    print(f"  With-CTC: ${with_part_b_agi:,.2f}")
    print(f"  Change: ${with_part_b_agi - pre_part_b_agi:,.2f}")
    
    # Check Part B deductions
    pre_part_b_deductions = get_household_value(pre_ctc_sim, "ma_part_b_taxable_income_deductions")
    with_part_b_deductions = get_household_value(with_ctc_sim, "ma_part_b_taxable_income_deductions")
    
    print(f"\nMA Part B Deductions:")
    print(f"  Pre-CTC: ${pre_part_b_deductions:,.2f}")
    print(f"  With-CTC: ${with_part_b_deductions:,.2f}")
    print(f"  Change: ${with_part_b_deductions - pre_part_b_deductions:,.2f}")
    
    # Check Part B exemption
    pre_part_b_exemption = get_household_value(pre_ctc_sim, "ma_part_b_taxable_income_exemption")
    with_part_b_exemption = get_household_value(with_ctc_sim, "ma_part_b_taxable_income_exemption")
    
    print(f"\nMA Part B Exemption:")
    print(f"  Pre-CTC: ${pre_part_b_exemption:,.2f}")
    print(f"  With-CTC: ${with_part_b_exemption:,.2f}")
    print(f"  Change: ${with_part_b_exemption - pre_part_b_exemption:,.2f}")
    
    # Check Part B taxable income before exemption
    pre_part_b_before_exemption = get_household_value(pre_ctc_sim, "ma_part_b_taxable_income_before_exemption")
    with_part_b_before_exemption = get_household_value(with_ctc_sim, "ma_part_b_taxable_income_before_exemption")
    
    print(f"\nMA Part B Taxable Income Before Exemption:")
    print(f"  Pre-CTC: ${pre_part_b_before_exemption:,.2f}")
    print(f"  With-CTC: ${with_part_b_before_exemption:,.2f}")
    print(f"  Change: ${with_part_b_before_exemption - pre_part_b_before_exemption:,.2f}")
    
    # Final Part B taxable income
    pre_part_b_taxable = get_household_value(pre_ctc_sim, "ma_part_b_taxable_income")
    with_part_b_taxable = get_household_value(with_ctc_sim, "ma_part_b_taxable_income")
    
    print(f"\nMA Part B Taxable Income (Final):")
    print(f"  Pre-CTC: ${pre_part_b_taxable:,.2f}")
    print(f"  With-CTC: ${with_part_b_taxable:,.2f}")
    print(f"  Change: ${with_part_b_taxable - pre_part_b_taxable:,.2f}")
    
    # Calculate effective tax rate
    taxable_income_change = with_part_b_taxable - pre_part_b_taxable
    ma_tax_change = get_household_value(with_ctc_sim, "ma_income_tax") - get_household_value(pre_ctc_sim, "ma_income_tax")
    
    print(f"\nEFFECT ON MA TAX:")
    print(f"  Taxable income change: ${taxable_income_change:,.2f}")
    print(f"  MA tax change: ${ma_tax_change:,.2f}")
    print(f"  Effective rate: {ma_tax_change / taxable_income_change * 100:.1f}%")
    
    # Check if this is related to federal itemized deductions
    pre_itemizes = get_household_value(pre_ctc_sim, "tax_unit_itemizes")
    with_itemizes = get_household_value(with_ctc_sim, "tax_unit_itemizes")
    
    print(f"\nItemization status:")
    print(f"  Pre-CTC: {pre_itemizes}")
    print(f"  With-CTC: {with_itemizes}")

if __name__ == "__main__":
    investigate_ma_part_b()