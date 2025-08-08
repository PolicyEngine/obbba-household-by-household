#!/usr/bin/env python3
"""
Check if SALT floor is causing the deduction increase.
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

def check_salt_floor():
    """Check SALT floor impact."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Build reform stack up to and including SALT
    baseline_reform = current_law_baseline()
    full_reform = baseline_reform
    full_reform = (full_reform, senate_finance_tax_rate_reform())
    full_reform = (full_reform, senate_finance_sd_reform())
    full_reform = (full_reform, senate_finance_exemption_reform())
    full_reform = (full_reform, senate_finance_ctc_reform())
    # Skip some reforms to get to SALT
    full_reform = (full_reform, senate_finance_salt_reform())
    
    print("Creating simulation...")
    sim = Microsimulation(reform=full_reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = sim.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    def get_value(variable):
        return sim.calculate(variable, map_to="household", period=year).values[household_4428_idx]
    
    print("\n" + "=" * 60)
    print("SALT FLOOR INVESTIGATION")
    print("=" * 60)
    
    # Check itemization and deductions
    itemizes = get_value("tax_unit_itemizes")
    total_deductions = get_value("taxable_income_deductions")
    salt_deduction = get_value("salt_deduction")
    
    print(f"\nItemizes: {itemizes}")
    print(f"Total deductions: ${total_deductions:,.2f}")
    print(f"SALT deduction: ${salt_deduction:,.2f}")
    
    # Check if SALT floor is involved
    try:
        salt_floor = get_value("salt_deduction_floor")
        print(f"SALT deduction floor: ${salt_floor:,.2f}")
    except:
        print("No SALT floor variable found")
    
    # The SALT floor might be adding a minimum deduction
    # The floor amount might be related to the $15,193.69
    
    # Check state and local taxes paid
    state_local_taxes = get_value("state_and_local_tax")
    print(f"\nState and local taxes paid: ${state_local_taxes:,.2f}")
    
    # Theory: The SALT floor guarantees a minimum deduction
    # when itemizing, which could be $15,193.69
    print("\n" + "=" * 60)
    print("THEORY: The SALT reform includes a floor that guarantees")
    print("a minimum deduction when itemizing, explaining the $15,193.69")
    
if __name__ == "__main__":
    check_salt_floor()