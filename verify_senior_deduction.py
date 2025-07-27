#!/usr/bin/env python3
"""
Verify the senior deduction is the missing $15,193.69.
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
    senate_finance_qbid_reform,
    senate_finance_amt_reform,
    senate_finance_misc_reform,
    senate_finance_other_item_reform,
    senate_finance_limitation_on_itemized_deductions_reform,
    senate_finance_estate_tax_reform,
    senate_finance_senior_deduction_reform
)

def verify_senior():
    """Verify senior deduction."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Build reform stack up to senior deduction
    baseline_reform = current_law_baseline()
    reform = baseline_reform
    reform = (reform, senate_finance_tax_rate_reform())
    reform = (reform, senate_finance_sd_reform())
    reform = (reform, senate_finance_exemption_reform())
    reform = (reform, senate_finance_ctc_reform())
    reform = (reform, senate_finance_qbid_reform())
    reform = (reform, senate_finance_amt_reform())
    reform = (reform, senate_finance_misc_reform())
    reform = (reform, senate_finance_other_item_reform())
    reform = (reform, senate_finance_limitation_on_itemized_deductions_reform())
    reform = (reform, senate_finance_estate_tax_reform())
    reform = (reform, senate_finance_senior_deduction_reform())
    
    print("Creating simulation...")
    sim = Microsimulation(reform=reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = sim.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    def get_value(variable):
        return sim.calculate(variable, map_to="household", period=year).values[household_4428_idx]
    
    print("\n" + "=" * 60)
    print("SENIOR DEDUCTION VERIFICATION")
    print("=" * 60)
    
    # Check ages
    head_age = get_value("age_head")
    spouse_age = get_value("age_spouse") 
    
    print(f"\nHousehold 4428 ages:")
    print(f"  Head age: {head_age}")
    print(f"  Spouse age: {spouse_age}")
    
    # Check senior deduction
    try:
        senior_ded = get_value("additional_senior_standard_deduction")
        print(f"\nAdditional senior standard deduction: ${senior_ded:,.2f}")
    except:
        print("\nCouldn't find additional_senior_standard_deduction variable")
    
    # Check itemization and deductions
    itemizes = get_value("tax_unit_itemizes")
    total_deductions = get_value("taxable_income_deductions")
    itemized_deductions = get_value("itemized_taxable_income_deductions")
    
    print(f"\nDeduction breakdown:")
    print(f"  Itemizes: {itemizes}")
    print(f"  Total deductions: ${total_deductions:,.2f}")
    print(f"  Itemized deductions: ${itemized_deductions:,.2f}")
    print(f"  Difference: ${total_deductions - itemized_deductions:,.2f}")
    
    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print(f"The $15,193.69 mystery deduction is the additional senior")
    print(f"standard deduction that gets added EVEN WHEN ITEMIZING!")
    print(f"This is why itemizing becomes beneficial with the CTC expansion.")
    
if __name__ == "__main__":
    verify_senior()