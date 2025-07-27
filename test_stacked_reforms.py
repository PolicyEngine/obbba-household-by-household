#!/usr/bin/env python3
"""
Test stacked reforms to isolate the CTC effect on MA state taxes.
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

def test_stacked_reforms():
    """Test reforms stacked up to just before CTC, then with CTC."""
    
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
    print("COMPARISON: Pre-CTC vs With-CTC")
    print("=" * 60)
    
    # Variables to check
    variables = [
        "income_tax",
        "ma_income_tax",
        "ctc",
        "eitc",
        "ma_eitc",
        "ma_agi",
        "ma_gross_income",
        "ma_part_b_agi",
        "ma_part_b_gross_income",
        "ma_limited_income_tax_credit",
        "ma_income_tax_before_credits",
        "ma_refundable_credits",
        "refundable_ctc",
        "non_refundable_ctc"
    ]
    
    print(f"{'Variable':<35} {'Pre-CTC':>15} {'With-CTC':>15} {'Change':>15}")
    print("-" * 85)
    
    for var in variables:
        try:
            pre_val = get_household_value(pre_ctc_sim, var)
            with_val = get_household_value(with_ctc_sim, var)
            change = with_val - pre_val
            if abs(change) > 0.01:
                print(f"{var:<35} ${pre_val:>14,.2f} ${with_val:>14,.2f} ${change:>14,.2f}")
        except:
            pass
    
    # Check if MA has any add-back provisions
    print("\n" + "=" * 60)
    print("CHECKING FOR MA ADD-BACKS")
    print("=" * 60)
    
    # Check federal deductions that MA disallows
    print("\nMA might add back certain federal deductions or credits.")
    print("Let's check if refundable CTC affects MA income calculations...")
    
    # Get more detailed MA income components
    pre_ctc_ma_part_b_gross = get_household_value(pre_ctc_sim, "ma_part_b_gross_income")
    with_ctc_ma_part_b_gross = get_household_value(with_ctc_sim, "ma_part_b_gross_income")
    
    print(f"\nMA Part B Gross Income:")
    print(f"  Pre-CTC: ${pre_ctc_ma_part_b_gross:,.2f}")
    print(f"  With-CTC: ${with_ctc_ma_part_b_gross:,.2f}")
    print(f"  Change: ${with_ctc_ma_part_b_gross - pre_ctc_ma_part_b_gross:,.2f}")
    
    # Check if the federal refundable CTC amount matches the state tax change
    refundable_ctc_change = get_household_value(with_ctc_sim, "refundable_ctc") - get_household_value(pre_ctc_sim, "refundable_ctc")
    ma_tax_change = get_household_value(with_ctc_sim, "ma_income_tax") - get_household_value(pre_ctc_sim, "ma_income_tax")
    
    print(f"\nRefundable CTC change: ${refundable_ctc_change:,.2f}")
    print(f"MA tax change: ${ma_tax_change:,.2f}")
    print(f"Expected MA tax change from data: $-56.41")
    
    # Check MA taxable income
    for income_type in ["ma_part_a_taxable_income", "ma_part_b_taxable_income", "ma_part_c_taxable_income"]:
        try:
            pre_val = get_household_value(pre_ctc_sim, income_type)
            with_val = get_household_value(with_ctc_sim, income_type)
            change = with_val - pre_val
            if abs(change) > 0.01:
                print(f"\n{income_type}:")
                print(f"  Pre-CTC: ${pre_val:,.2f}")
                print(f"  With-CTC: ${with_val:,.2f}")
                print(f"  Change: ${change:,.2f}")
        except:
            pass

if __name__ == "__main__":
    test_stacked_reforms()