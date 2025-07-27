#!/usr/bin/env python3
"""
Investigate what makes up the $18,906.70 deduction when itemizing with CTC.
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

def investigate_deduction():
    """Find what makes up the $18,906.70 deduction."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Build the full reform stack
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
    
    print("\n" + "=" * 60)
    print("DEDUCTION COMPONENTS WHEN ITEMIZING WITH CTC")
    print("=" * 60)
    
    # Check itemization status
    itemizes = get_value("tax_unit_itemizes")
    print(f"\nItemizes: {itemizes}")
    
    # Total deductions
    total_deductions = get_value("taxable_income_deductions")
    print(f"Total taxable income deductions: ${total_deductions:,.2f}")
    
    # Components
    deductions_if_itemizing = get_value("taxable_income_deductions_if_itemizing")
    itemized_deductions = get_value("itemized_taxable_income_deductions")
    
    print(f"\nDeductions if itemizing: ${deductions_if_itemizing:,.2f}")
    print(f"Itemized deductions: ${itemized_deductions:,.2f}")
    
    # The difference must be other deductions available when itemizing
    difference = deductions_if_itemizing - itemized_deductions
    print(f"Other deductions when itemizing: ${difference:,.2f}")
    
    # Check QBI deduction
    qbi = get_value("qualified_business_income_deduction")
    print(f"\nQBI deduction: ${qbi:,.2f}")
    
    # Check if it's related to charitable deduction
    charitable = get_value("charitable_deduction")
    print(f"Charitable deduction: ${charitable:,.2f}")
    
    # Check salt deduction  
    salt = get_value("salt_deduction")
    print(f"SALT deduction: ${salt:,.2f}")
    
    # Check medical expense deduction
    medical = get_value("medical_expense_deduction")
    print(f"Medical expense deduction: ${medical:,.2f}")
    
    # Check for other deductions
    print("\n" + "=" * 60)
    print("SEARCHING FOR THE MISSING $15,193.69...")
    
    # It's likely the dependent exemption that was reinstated
    # Check if there's a personal exemption
    try:
        personal_exemption = get_value("exemptions")
        print(f"\nPersonal/dependent exemptions: ${personal_exemption:,.2f}")
    except:
        print("\nNo 'exemptions' variable found")
    
    # The senate_finance_exemption_reform sets exemption to 0
    # So it must be something else
    
    # Check what adds up to deductions_if_itemizing
    print("\nLet me check the formula for taxable_income_deductions_if_itemizing...")
    
if __name__ == "__main__":
    investigate_deduction()