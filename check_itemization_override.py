#!/usr/bin/env python3
"""
Check if itemization is being overridden by comparing branch logic.
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

def check_override():
    """Check if itemization decision is overridden."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Test with just CTC reform alone
    baseline_reform = current_law_baseline()
    just_ctc = (baseline_reform, senate_finance_ctc_reform())
    
    print("Creating simulations...")
    print("1. Just CTC reform")
    ctc_only_sim = Microsimulation(reform=just_ctc, dataset=dataset_path)
    
    # Find household 4428
    household_ids = ctc_only_sim.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    def get_value(sim, variable):
        return sim.calculate(variable, map_to="household", period=year).values[household_4428_idx]
    
    # Check itemization with just CTC
    ctc_itemizes = get_value(ctc_only_sim, "tax_unit_itemizes")
    ctc_deductions = get_value(ctc_only_sim, "taxable_income_deductions")
    
    print(f"\nWith just CTC reform:")
    print(f"  Itemizes: {ctc_itemizes}")
    print(f"  Deductions: ${ctc_deductions:,.2f}")
    
    # Now test with each reform added
    reforms_to_test = [
        ("Baseline", baseline_reform),
        ("+ Tax rates", (baseline_reform, senate_finance_tax_rate_reform())),
        ("+ Standard deduction", (baseline_reform, senate_finance_tax_rate_reform(), senate_finance_sd_reform())),
        ("+ Exemption (set to 0)", (baseline_reform, senate_finance_tax_rate_reform(), senate_finance_sd_reform(), senate_finance_exemption_reform())),
        ("+ CTC", (baseline_reform, senate_finance_tax_rate_reform(), senate_finance_sd_reform(), senate_finance_exemption_reform(), senate_finance_ctc_reform())),
    ]
    
    print("\n" + "=" * 60)
    print("TRACING ITEMIZATION DECISION BY REFORM")
    print("=" * 60)
    
    for name, reform_stack in reforms_to_test:
        if isinstance(reform_stack, tuple):
            # Stack the reforms
            stacked = reform_stack[0]
            for r in reform_stack[1:]:
                stacked = (stacked, r)
            sim = Microsimulation(reform=stacked, dataset=dataset_path)
        else:
            sim = Microsimulation(reform=reform_stack, dataset=dataset_path)
        
        itemizes = get_value(sim, "tax_unit_itemizes")
        deductions = get_value(sim, "taxable_income_deductions")
        
        # Get more detail on the decision
        tax_if_item = get_value(sim, "tax_liability_if_itemizing")
        tax_if_not = get_value(sim, "tax_liability_if_not_itemizing")
        
        print(f"\n{name}:")
        print(f"  Itemizes: {itemizes}")
        print(f"  Deductions: ${deductions:,.2f}")
        print(f"  Tax if itemizing: ${tax_if_item:,.2f}")
        print(f"  Tax if NOT itemizing: ${tax_if_not:,.2f}")
        print(f"  Should itemize: {tax_if_item < tax_if_not}")
    
if __name__ == "__main__":
    check_override()