#!/usr/bin/env python3
"""
Debug the actual calculation without forcing itemization.
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
    senate_finance_ctc_reform,
    senate_finance_salt_reform
)

def debug_calculation():
    """Debug the actual calculation."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Build reform WITHOUT exemption reform to test
    baseline_reform = current_law_baseline()
    test_reform = baseline_reform
    test_reform = (test_reform, senate_finance_tax_rate_reform())
    test_reform = (test_reform, senate_finance_sd_reform())
    # Skip exemption reform
    test_reform = (test_reform, senate_finance_ctc_reform())
    
    # Also build with exemption reform
    with_exemption = baseline_reform
    with_exemption = (with_exemption, senate_finance_tax_rate_reform())
    with_exemption = (with_exemption, senate_finance_sd_reform())
    with_exemption = (with_exemption, senate_finance_exemption_reform())
    with_exemption = (with_exemption, senate_finance_ctc_reform())
    
    print("Creating simulations...")
    test_sim = Microsimulation(reform=test_reform, dataset=dataset_path)
    with_ex_sim = Microsimulation(reform=with_exemption, dataset=dataset_path)
    
    # Find household 4428
    household_ids = test_sim.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    def get_value(sim, variable):
        return sim.calculate(variable, map_to="household", period=year).values[household_4428_idx]
    
    print("\n" + "=" * 60)
    print("TESTING EXEMPTION REFORM IMPACT")
    print("=" * 60)
    
    # Check exemptions
    print("\nWithout exemption reform:")
    test_itemizes = get_value(test_sim, "tax_unit_itemizes")
    test_deductions = get_value(test_sim, "taxable_income_deductions")
    test_exemptions = get_value(test_sim, "exemptions")
    
    print(f"  Itemizes: {test_itemizes}")
    print(f"  Taxable income deductions: ${test_deductions:,.2f}")
    print(f"  Exemptions: ${test_exemptions:,.2f}")
    
    print("\nWith exemption reform:")
    with_itemizes = get_value(with_ex_sim, "tax_unit_itemizes")
    with_deductions = get_value(with_ex_sim, "taxable_income_deductions")
    with_exemptions = get_value(with_ex_sim, "exemptions")
    
    print(f"  Itemizes: {with_itemizes}")
    print(f"  Taxable income deductions: ${with_deductions:,.2f}")
    print(f"  Exemptions: ${with_exemptions:,.2f}")
    
    # The mystery might be that exemptions are being included in deductions
    # when itemizing under certain conditions
    
    print("\n" + "=" * 60)
    print("HYPOTHESIS: The $18,906.70 might be $3,713.01 (itemized) + $15,193.69")
    print("And $15,193.69 ≈ 4 * $3,800 personal exemptions")
    
    # Check if SALT reform is involved
    print("\nLet me also check if SALT reform is part of the stack...")
    
    # Actually, let's check the order of reforms in the data generation
    
if __name__ == "__main__":
    debug_calculation()