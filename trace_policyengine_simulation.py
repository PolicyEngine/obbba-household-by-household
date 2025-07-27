#!/usr/bin/env python3
"""
Run PolicyEngine simulation to trace how federal CTC expansion affects MA state taxes.
"""

from policyengine_us import Microsimulation
from policyengine_us.model_api import *
import numpy as np
import sys

# Add the data directory to path to import reforms
sys.path.append('data')
from reforms import current_law_baseline, senate_finance_ctc_reform

def trace_household_4428_detailed():
    """Trace the impact of CTC expansion on MA state taxes for household 4428."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Get baseline and CTC expansion reform
    baseline_reform = current_law_baseline()
    ctc_reform = senate_finance_ctc_reform()
    
    # Create baseline simulation
    print("Creating baseline simulation...")
    baseline = Microsimulation(reform=baseline_reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = baseline.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    # Get person indices for household 4428
    person_household_ids = baseline.calculate("household_id", map_to="person", period=year).values
    person_indices = np.where(person_household_ids == 4428)[0]
    
    print(f"Found household 4428 at index {household_4428_idx}")
    print(f"Household contains {len(person_indices)} people")
    
    # Create a function to extract values for household 4428
    def get_household_value(sim, variable, period=year):
        return sim.calculate(variable, map_to="household", period=period).values[household_4428_idx]
    
    def get_person_values(sim, variable, period=year):
        return sim.calculate(variable, map_to="person", period=period).values[person_indices]
    
    print("\n" + "=" * 60)
    print("BASELINE VALUES")
    print("=" * 60)
    
    # Get comprehensive baseline values
    baseline_values = {}
    
    # Federal values
    baseline_values['federal_agi'] = get_household_value(baseline, "adjusted_gross_income")
    baseline_values['federal_gross_income'] = get_household_value(baseline, "irs_gross_income")
    baseline_values['federal_ctc'] = get_household_value(baseline, "ctc")
    baseline_values['federal_eitc'] = get_household_value(baseline, "eitc")
    baseline_values['federal_income_tax'] = get_household_value(baseline, "income_tax")
    
    # MA specific values
    baseline_values['ma_agi'] = get_household_value(baseline, "ma_agi")
    baseline_values['ma_gross_income'] = get_household_value(baseline, "ma_gross_income")
    baseline_values['ma_eitc'] = get_household_value(baseline, "ma_eitc")
    baseline_values['ma_child_family_credit'] = get_household_value(baseline, "ma_child_and_family_credit")
    baseline_values['ma_limited_income_credit'] = get_household_value(baseline, "ma_limited_income_tax_credit")
    baseline_values['ma_income_tax'] = get_household_value(baseline, "ma_income_tax")
    baseline_values['ma_income_tax_before_credits'] = get_household_value(baseline, "ma_income_tax_before_credits")
    baseline_values['ma_refundable_credits'] = get_household_value(baseline, "ma_refundable_credits")
    baseline_values['ma_non_refundable_credits'] = get_household_value(baseline, "ma_non_refundable_credits")
    
    # Additional values to trace
    baseline_values['tax_unit_earned_income'] = get_household_value(baseline, "tax_unit_earned_income")
    baseline_values['employment_income'] = get_household_value(baseline, "irs_employment_income")
    
    # Print baseline values
    for key, value in baseline_values.items():
        print(f"{key:.<40} ${value:,.2f}")
    
    # Check person-level details
    print("\nPerson-level details:")
    ages = get_person_values(baseline, "age")
    is_dependent = get_person_values(baseline, "is_tax_unit_dependent")
    for i, (age, dep) in enumerate(zip(ages, is_dependent)):
        print(f"  Person {i}: Age {age}, Dependent: {dep}")
    
    # Now apply CTC reform
    print("\n" + "=" * 60)
    print("WITH CTC REFORM")
    print("=" * 60)
    
    # Create reformed simulation  
    print("Creating reformed simulation...")
    reformed = Microsimulation(reform=(baseline_reform, ctc_reform), dataset=dataset_path)
    
    # Get reformed values
    reformed_values = {}
    
    # Federal values
    reformed_values['federal_agi'] = get_household_value(reformed, "adjusted_gross_income")
    reformed_values['federal_gross_income'] = get_household_value(reformed, "irs_gross_income")
    reformed_values['federal_ctc'] = get_household_value(reformed, "ctc")
    reformed_values['federal_eitc'] = get_household_value(reformed, "eitc")
    reformed_values['federal_income_tax'] = get_household_value(reformed, "income_tax")
    
    # MA specific values
    reformed_values['ma_agi'] = get_household_value(reformed, "ma_agi")
    reformed_values['ma_gross_income'] = get_household_value(reformed, "ma_gross_income")
    reformed_values['ma_eitc'] = get_household_value(reformed, "ma_eitc")
    reformed_values['ma_child_family_credit'] = get_household_value(reformed, "ma_child_and_family_credit")
    reformed_values['ma_limited_income_credit'] = get_household_value(reformed, "ma_limited_income_tax_credit")
    reformed_values['ma_income_tax'] = get_household_value(reformed, "ma_income_tax")
    reformed_values['ma_income_tax_before_credits'] = get_household_value(reformed, "ma_income_tax_before_credits")
    reformed_values['ma_refundable_credits'] = get_household_value(reformed, "ma_refundable_credits")
    reformed_values['ma_non_refundable_credits'] = get_household_value(reformed, "ma_non_refundable_credits")
    
    # Additional values
    reformed_values['tax_unit_earned_income'] = get_household_value(reformed, "tax_unit_earned_income")
    reformed_values['employment_income'] = get_household_value(reformed, "irs_employment_income")
    
    # Print reformed values
    for key, value in reformed_values.items():
        print(f"{key:.<40} ${value:,.2f}")
    
    # Calculate and display changes
    print("\n" + "=" * 60)
    print("CHANGES DUE TO CTC REFORM")
    print("=" * 60)
    
    for key in baseline_values.keys():
        change = reformed_values[key] - baseline_values[key]
        if abs(change) > 0.01:
            print(f"{key:.<40} ${change:,.2f}")
    
    # Deep dive into MA EITC calculation
    print("\n" + "=" * 60)
    print("MA EITC CALCULATION TRACE")
    print("=" * 60)
    
    print(f"Federal EITC (baseline): ${baseline_values['federal_eitc']:,.2f}")
    print(f"Federal EITC (reformed): ${reformed_values['federal_eitc']:,.2f}")
    print(f"Federal EITC change: ${reformed_values['federal_eitc'] - baseline_values['federal_eitc']:,.2f}")
    print(f"\nMA EITC = Federal EITC * 30%")
    print(f"MA EITC (baseline): ${baseline_values['ma_eitc']:,.2f}")
    print(f"MA EITC (reformed): ${reformed_values['ma_eitc']:,.2f}")
    print(f"MA EITC change: ${reformed_values['ma_eitc'] - baseline_values['ma_eitc']:,.2f}")
    
    # Check if EITC change matches state tax change
    ma_eitc_change = reformed_values['ma_eitc'] - baseline_values['ma_eitc']
    ma_tax_change = reformed_values['ma_income_tax'] - baseline_values['ma_income_tax']
    print(f"\nMA income tax change: ${ma_tax_change:,.2f}")
    print(f"Does MA EITC change explain state tax change? {abs(ma_eitc_change + ma_tax_change) < 0.01}")

if __name__ == "__main__":
    trace_household_4428_detailed()