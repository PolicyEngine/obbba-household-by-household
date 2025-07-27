#!/usr/bin/env python3
"""
Check tax liabilities to understand itemization decision.
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

def check_tax_liabilities():
    """Check tax liabilities under different scenarios."""
    
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
    print("TAX LIABILITY COMPARISON FOR ITEMIZATION DECISION")
    print("=" * 60)
    
    # Pre-CTC scenario
    print("\nPre-CTC Reform:")
    pre_tax_if_itemizing = get_household_value(pre_ctc_sim, "tax_liability_if_itemizing")
    pre_tax_if_not_itemizing = get_household_value(pre_ctc_sim, "tax_liability_if_not_itemizing")
    pre_itemizes = get_household_value(pre_ctc_sim, "tax_unit_itemizes")
    
    print(f"  Tax liability if itemizing: ${pre_tax_if_itemizing:,.2f}")
    print(f"  Tax liability if NOT itemizing: ${pre_tax_if_not_itemizing:,.2f}")
    print(f"  Difference: ${pre_tax_if_itemizing - pre_tax_if_not_itemizing:,.2f}")
    print(f"  Decision: {'Itemize' if pre_itemizes else 'Standard deduction'}")
    
    # With-CTC scenario
    print("\nWith-CTC Reform:")
    with_tax_if_itemizing = get_household_value(with_ctc_sim, "tax_liability_if_itemizing")
    with_tax_if_not_itemizing = get_household_value(with_ctc_sim, "tax_liability_if_not_itemizing")
    with_itemizes = get_household_value(with_ctc_sim, "tax_unit_itemizes")
    
    print(f"  Tax liability if itemizing: ${with_tax_if_itemizing:,.2f}")
    print(f"  Tax liability if NOT itemizing: ${with_tax_if_not_itemizing:,.2f}")
    print(f"  Difference: ${with_tax_if_itemizing - with_tax_if_not_itemizing:,.2f}")
    print(f"  Decision: {'Itemize' if with_itemizes else 'Standard deduction'}")
    
    # Check what's included in deductions when itemizing
    print("\n" + "=" * 60)
    print("DEDUCTIONS BREAKDOWN")
    print("=" * 60)
    
    # Check QBI deduction
    pre_qbi = get_household_value(pre_ctc_sim, "qualified_business_income_deduction")
    with_qbi = get_household_value(with_ctc_sim, "qualified_business_income_deduction")
    
    print(f"\nQBI Deduction:")
    print(f"  Pre-CTC: ${pre_qbi:,.2f}")
    print(f"  With-CTC: ${with_qbi:,.2f}")
    
    # Check total deductions if itemizing vs not
    pre_ded_if_item = get_household_value(pre_ctc_sim, "taxable_income_deductions_if_itemizing")
    pre_ded_if_not = get_household_value(pre_ctc_sim, "taxable_income_deductions_if_not_itemizing")
    
    with_ded_if_item = get_household_value(with_ctc_sim, "taxable_income_deductions_if_itemizing")
    with_ded_if_not = get_household_value(with_ctc_sim, "taxable_income_deductions_if_not_itemizing")
    
    print("\nTotal deductions comparison:")
    print(f"Pre-CTC:")
    print(f"  If itemizing: ${pre_ded_if_item:,.2f}")
    print(f"  If not itemizing: ${pre_ded_if_not:,.2f}")
    print(f"With-CTC:")
    print(f"  If itemizing: ${with_ded_if_item:,.2f}")
    print(f"  If not itemizing: ${with_ded_if_not:,.2f}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS:")
    print("The itemization decision is based on which results in lower tax liability.")
    print("Even if itemized deductions are lower than standard, itemizing might")
    print("still be beneficial if it allows access to other deductions or benefits.")
    
if __name__ == "__main__":
    check_tax_liabilities()