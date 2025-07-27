#!/usr/bin/env python3
"""
Trace CTC refundability under different scenarios.
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

def trace_ctc():
    """Trace CTC refundability."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Stack reforms
    baseline_reform = current_law_baseline()
    with_ctc_reform = baseline_reform
    with_ctc_reform = (with_ctc_reform, senate_finance_tax_rate_reform())
    with_ctc_reform = (with_ctc_reform, senate_finance_sd_reform())
    with_ctc_reform = (with_ctc_reform, senate_finance_exemption_reform())
    with_ctc_reform = (with_ctc_reform, senate_finance_ctc_reform())
    
    print("Creating simulation...")
    sim = Microsimulation(reform=with_ctc_reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = sim.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    # Helper function
    def get_household_value(variable, period=year):
        return sim.calculate(variable, map_to="household", period=period).values[household_4428_idx]
    
    print("\n" + "=" * 60)
    print("CTC REFUNDABILITY ANALYSIS")
    print("=" * 60)
    
    # Get key values
    itemizes = get_household_value("tax_unit_itemizes")
    tax_before_credits = get_household_value("income_tax_before_credits")
    
    # CTC components
    ctc_max = get_household_value("ctc_maximum")
    non_refundable_ctc = get_household_value("non_refundable_ctc")
    refundable_ctc = get_household_value("refundable_ctc")
    total_ctc = get_household_value("ctc")
    
    print(f"\nItemizes: {itemizes}")
    print(f"Tax before credits: ${tax_before_credits:,.2f}")
    print(f"\nCTC breakdown:")
    print(f"  CTC maximum eligible: ${ctc_max:,.2f}")
    print(f"  Non-refundable portion: ${non_refundable_ctc:,.2f}")
    print(f"  Refundable portion: ${refundable_ctc:,.2f}")
    print(f"  Total CTC claimed: ${total_ctc:,.2f}")
    
    # Check if itemizing affects the calculation
    print("\n" + "=" * 60)
    print("HYPOTHESIS CHECK:")
    print("If itemizing increases tax before credits, it could allow")
    print("more of the CTC to be claimed as non-refundable, which")
    print("might be more valuable in certain edge cases.")
    
    # The real answer might be in how tax_liability is calculated
    print("\nBut the real issue is likely in how 'tax_liability' is")
    print("calculated for the itemization decision - it might include")
    print("effects beyond just income tax.")
    
if __name__ == "__main__":
    trace_ctc()