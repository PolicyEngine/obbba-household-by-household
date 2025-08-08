#!/usr/bin/env python3
"""
Analyze why itemizing with lower deductions gives better tax outcome.
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

def analyze_itemization_benefit():
    """Find why itemizing is beneficial despite lower deductions."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Build reform stack
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
    
    def get_value(variable):
        return sim.calculate(variable, map_to="household", period=year).values[household_4428_idx]
    
    # Create branches for forced scenarios
    tax_unit_count = len(sim.calculate("tax_unit_id", period=year).values)
    
    force_standard = sim.get_branch("force_standard")
    force_standard.set_input("tax_unit_itemizes", year, np.zeros((tax_unit_count,), dtype=bool))
    
    print("\n" + "=" * 60)
    print("WHY ITEMIZING IS BETTER WITH CTC REFORM")
    print("=" * 60)
    
    # Compare actual (itemizing) vs forced standard
    scenarios = [
        ("Actual (itemizing)", sim),
        ("Forced standard", force_standard)
    ]
    
    for name, scenario in scenarios:
        print(f"\n{name}:")
        print("-" * 40)
        
        # Tax calculation components
        agi = get_value("adjusted_gross_income")
        deductions = scenario.calculate("taxable_income_deductions", map_to="household", period=year).values[household_4428_idx]
        taxable_income = scenario.calculate("taxable_income", map_to="household", period=year).values[household_4428_idx]
        tax_before_credits = scenario.calculate("income_tax_before_credits", map_to="household", period=year).values[household_4428_idx]
        
        # Credits
        ctc = scenario.calculate("ctc", map_to="household", period=year).values[household_4428_idx]
        non_refundable_ctc = scenario.calculate("non_refundable_ctc", map_to="household", period=year).values[household_4428_idx]
        refundable_ctc = scenario.calculate("refundable_ctc", map_to="household", period=year).values[household_4428_idx]
        eitc = scenario.calculate("eitc", map_to="household", period=year).values[household_4428_idx]
        
        # Final tax
        income_tax = scenario.calculate("income_tax", map_to="household", period=year).values[household_4428_idx]
        
        print(f"  AGI: ${agi:,.2f}")
        print(f"  Deductions: ${deductions:,.2f}")
        print(f"  Taxable income: ${taxable_income:,.2f}")
        print(f"  Tax before credits: ${tax_before_credits:,.2f}")
        print(f"  CTC total: ${ctc:,.2f}")
        print(f"    - Non-refundable: ${non_refundable_ctc:,.2f}")
        print(f"    - Refundable: ${refundable_ctc:,.2f}")
        print(f"  EITC: ${eitc:,.2f}")
        print(f"  Final income tax: ${income_tax:,.2f}")
    
    # Calculate the benefit
    actual_tax = sim.calculate("income_tax", map_to="household", period=year).values[household_4428_idx]
    standard_tax = force_standard.calculate("income_tax", map_to="household", period=year).values[household_4428_idx]
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Tax with itemizing: ${actual_tax:,.2f}")
    print(f"Tax with standard: ${standard_tax:,.2f}")
    print(f"Benefit of itemizing: ${standard_tax - actual_tax:,.2f}")
    
    # The key question: why is the final tax the same when the inputs are different?
    print("\nThe mystery: Why do different paths lead to the same tax?")
    
if __name__ == "__main__":
    analyze_itemization_benefit()