#!/usr/bin/env python3
"""
Extract key characteristics of household 4428 to create MRE.
"""

from policyengine_us import Microsimulation
from policyengine_us.model_api import *
import numpy as np
import sys

# Add the data directory to path to import reforms
sys.path.append('data')
from reforms import current_law_baseline

def extract_characteristics():
    """Extract key characteristics of household 4428."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Use baseline to get original characteristics
    baseline_reform = current_law_baseline()
    sim = Microsimulation(reform=baseline_reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = sim.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    def get_household_value(variable):
        return sim.calculate(variable, map_to="household", period=year).values[household_4428_idx]
    
    # Get person-level data for this household
    person_household = sim.calculate("household_id", map_to="person", period=year).values
    household_mask = person_household == 4428
    
    def get_person_values(variable):
        return sim.calculate(variable, map_to="person", period=year).values[household_mask]
    
    print("\n" + "=" * 60)
    print("HOUSEHOLD 4428 CHARACTERISTICS")
    print("=" * 60)
    
    # Basic demographics
    ages = get_person_values("age")
    is_tax_unit_dependent = get_person_values("is_tax_unit_dependent")
    employment_income = get_person_values("employment_income")
    
    print(f"\nNumber of people: {len(ages)}")
    print(f"Ages: {ages}")
    print(f"Tax unit dependents: {is_tax_unit_dependent}")
    print(f"Employment income by person: {employment_income}")
    
    # Household-level values
    print(f"\nHousehold income: ${get_household_value('household_income'):,.2f}")
    print(f"AGI: ${get_household_value('adjusted_gross_income'):,.2f}")
    print(f"Filing status: {get_household_value('filing_status')}")
    
    # Key deduction components
    print(f"\nDeduction components:")
    print(f"  Medical expenses: ${get_household_value('medical_out_of_pocket_expenses'):,.2f}")
    print(f"  State/local taxes: ${get_household_value('state_and_local_sales_or_income_tax'):,.2f}")
    print(f"  Real estate taxes: ${get_household_value('real_estate_taxes'):,.2f}")
    print(f"  Charitable: ${get_household_value('charitable_cash_donations') + get_household_value('charitable_non_cash_donations'):,.2f}")
    
    # Tax info
    print(f"\nNumber of dependents: {get_household_value('tax_unit_dependents')}")
    print(f"Standard deduction: ${get_household_value('standard_deduction'):,.2f}")
    print(f"Itemized deductions: ${get_household_value('itemized_taxable_income_deductions'):,.2f}")
    
    # State
    state_codes = get_person_values("state_code")
    print(f"\nState codes: {state_codes[0] if len(set(state_codes)) == 1 else state_codes}")
    
    # Create minimal version
    print("\n" + "=" * 60)
    print("MINIMAL VERSION FOR REPRODUCTION:")
    print("- Head: age 70, ~$49k employment income")
    print("- Spouse: age 43")
    print("- 2 children (ages vary in data)")
    print("- Massachusetts residents")
    print("- ~$14k medical expenses")
    print("- ~$2k state/local taxes")
    print("- Minimal charitable/other deductions")
    
if __name__ == "__main__":
    extract_characteristics()