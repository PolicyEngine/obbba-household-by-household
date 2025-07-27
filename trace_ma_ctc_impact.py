#!/usr/bin/env python3
"""
Trace how federal CTC expansion affects Massachusetts state taxes for household 4428.
"""

from policyengine_us import Microsimulation
from reforms import current_law_baseline, get_all_senate_finance_reforms
import numpy as np

def trace_household_4428():
    """Trace the impact of CTC expansion on MA state taxes for household 4428."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Get baseline and CTC expansion reform
    baseline_reform = current_law_baseline()
    reforms = get_all_senate_finance_reforms()
    
    # Create baseline simulation
    baseline = Microsimulation(reform=baseline_reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = baseline.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    print("=" * 60)
    print("HOUSEHOLD 4428 ANALYSIS - BASELINE")
    print("=" * 60)
    
    # Get baseline values
    baseline_values = {
        "Federal Income Tax": baseline.calculate("income_tax", map_to="household", period=year).values[household_4428_idx],
        "State Income Tax": baseline.calculate("state_income_tax", map_to="household", period=year).values[household_4428_idx],
        "MA Income Tax": baseline.calculate("ma_income_tax", map_to="household", period=year).values[household_4428_idx],
        "Federal AGI": baseline.calculate("adjusted_gross_income", map_to="household", period=year).values[household_4428_idx],
        "MA AGI": baseline.calculate("ma_agi", map_to="household", period=year).values[household_4428_idx],
        "Federal CTC": baseline.calculate("ctc", map_to="household", period=year).values[household_4428_idx],
        "MA Child & Family Credit": baseline.calculate("ma_child_and_family_credit", map_to="household", period=year).values[household_4428_idx],
        "MA Limited Income Credit": baseline.calculate("ma_limited_income_tax_credit", map_to="household", period=year).values[household_4428_idx],
        "MA Refundable Credits": baseline.calculate("ma_refundable_credits", map_to="household", period=year).values[household_4428_idx],
        "MA Non-refundable Credits": baseline.calculate("ma_non_refundable_credits", map_to="household", period=year).values[household_4428_idx],
        "MA Income Tax Before Credits": baseline.calculate("ma_income_tax_before_credits", map_to="household", period=year).values[household_4428_idx],
        "Household Net Income": baseline.calculate("household_net_income_including_health_benefits", map_to="household", period=year).values[household_4428_idx],
    }
    
    for key, value in baseline_values.items():
        print(f"{key:.<35} ${value:,.2f}")
    
    # Now apply CTC expansion
    print("\n" + "=" * 60)
    print("WITH CTC EXPANSION")
    print("=" * 60)
    
    # Stack reforms up to and including CTC expansion
    cumulative_reform = baseline_reform
    for reform_name, reform in reforms.items():
        cumulative_reform = (cumulative_reform, reform)
        if reform_name == "Child tax credit expansion":
            break
    
    # Create reformed simulation
    reformed = Microsimulation(reform=cumulative_reform, dataset=dataset_path)
    
    # Get reformed values
    reformed_values = {
        "Federal Income Tax": reformed.calculate("income_tax", map_to="household", period=year).values[household_4428_idx],
        "State Income Tax": reformed.calculate("state_income_tax", map_to="household", period=year).values[household_4428_idx],
        "MA Income Tax": reformed.calculate("ma_income_tax", map_to="household", period=year).values[household_4428_idx],
        "Federal AGI": reformed.calculate("adjusted_gross_income", map_to="household", period=year).values[household_4428_idx],
        "MA AGI": reformed.calculate("ma_agi", map_to="household", period=year).values[household_4428_idx],
        "Federal CTC": reformed.calculate("ctc", map_to="household", period=year).values[household_4428_idx],
        "MA Child & Family Credit": reformed.calculate("ma_child_and_family_credit", map_to="household", period=year).values[household_4428_idx],
        "MA Limited Income Credit": reformed.calculate("ma_limited_income_tax_credit", map_to="household", period=year).values[household_4428_idx],
        "MA Refundable Credits": reformed.calculate("ma_refundable_credits", map_to="household", period=year).values[household_4428_idx],
        "MA Non-refundable Credits": reformed.calculate("ma_non_refundable_credits", map_to="household", period=year).values[household_4428_idx],
        "MA Income Tax Before Credits": reformed.calculate("ma_income_tax_before_credits", map_to="household", period=year).values[household_4428_idx],
        "Household Net Income": reformed.calculate("household_net_income_including_health_benefits", map_to="household", period=year).values[household_4428_idx],
    }
    
    for key, value in reformed_values.items():
        print(f"{key:.<35} ${value:,.2f}")
    
    # Calculate changes
    print("\n" + "=" * 60)
    print("CHANGES DUE TO CTC EXPANSION")
    print("=" * 60)
    
    for key in baseline_values.keys():
        change = reformed_values[key] - baseline_values[key]
        if abs(change) > 0.01:  # Only show non-zero changes
            print(f"{key:.<35} ${change:,.2f}")
    
    # Try to trace additional MA-specific variables
    print("\n" + "=" * 60)
    print("ADDITIONAL MA TAX COMPONENTS")
    print("=" * 60)
    
    # Check if MA limited income credit is affected
    print("\nMA Limited Income Credit Details:")
    print(f"  Baseline MA AGI: ${baseline_values['MA AGI']:,.2f}")
    print(f"  Reformed MA AGI: ${reformed_values['MA AGI']:,.2f}")
    
    # Get exemption threshold
    exemption_threshold = baseline.calculate("ma_income_tax_exemption_threshold", map_to="household", period=year).values[household_4428_idx]
    print(f"  MA Income Tax Exemption Threshold: ${exemption_threshold:,.2f}")
    
    # Check if household is exempt
    is_exempt_baseline = baseline.calculate("is_ma_income_tax_exempt", map_to="household", period=year).values[household_4428_idx]
    is_exempt_reformed = reformed.calculate("is_ma_income_tax_exempt", map_to="household", period=year).values[household_4428_idx]
    print(f"  Is MA Income Tax Exempt (baseline): {is_exempt_baseline}")
    print(f"  Is MA Income Tax Exempt (reformed): {is_exempt_reformed}")

if __name__ == "__main__":
    trace_household_4428()