#!/usr/bin/env python3
"""
Run PolicyEngine simulation with cumulative reforms to match the data generation.
"""

from policyengine_us import Microsimulation
from policyengine_us.model_api import *
import numpy as np
import sys

# Add the data directory to path to import reforms
sys.path.append('data')
from reforms import current_law_baseline, get_all_senate_finance_reforms

def trace_household_4428_cumulative():
    """Trace the impact of CTC expansion with cumulative reforms."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Get baseline
    baseline_reform = current_law_baseline()
    
    # Get all senate finance reforms
    all_reforms = get_all_senate_finance_reforms()
    
    # Create baseline simulation
    print("Creating baseline simulation...")
    baseline = Microsimulation(reform=baseline_reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = baseline.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    # Helper function
    def get_household_value(sim, variable, period=year):
        return sim.calculate(variable, map_to="household", period=period).values[household_4428_idx]
    
    # Get baseline MA state tax
    baseline_ma_tax = get_household_value(baseline, "ma_income_tax")
    baseline_fed_tax = get_household_value(baseline, "income_tax")
    
    print(f"\nBaseline taxes:")
    print(f"  Federal: ${baseline_fed_tax:,.2f}")
    print(f"  MA State: ${baseline_ma_tax:,.2f}")
    
    # Now apply reforms cumulatively, tracking state tax at each step
    cumulative_reform = baseline_reform
    previous_ma_tax = baseline_ma_tax
    previous_fed_tax = baseline_fed_tax
    
    print("\nApplying reforms cumulatively:")
    print("-" * 60)
    
    for reform_name, reform in all_reforms.items():
        # Stack the reform
        cumulative_reform = (cumulative_reform, reform)
        
        # Create new simulation
        sim = Microsimulation(reform=cumulative_reform, dataset=dataset_path)
        
        # Get new values
        new_ma_tax = get_household_value(sim, "ma_income_tax")
        new_fed_tax = get_household_value(sim, "income_tax")
        
        # Calculate changes
        ma_change = new_ma_tax - previous_ma_tax
        fed_change = new_fed_tax - previous_fed_tax
        
        # Only print if there's a change
        if abs(ma_change) > 0.01 or abs(fed_change) > 0.01:
            print(f"\nAfter {reform_name}:")
            print(f"  Federal tax change: ${fed_change:,.2f}")
            print(f"  MA tax change: ${ma_change:,.2f}")
            print(f"  Cumulative MA tax: ${new_ma_tax:,.2f}")
            
            # If this is the CTC reform, get more details
            if reform_name == "CTC Reform":
                print("\n  Detailed values at CTC Reform:")
                print(f"    Federal CTC: ${get_household_value(sim, 'ctc'):,.2f}")
                print(f"    Federal EITC: ${get_household_value(sim, 'eitc'):,.2f}")
                print(f"    MA EITC: ${get_household_value(sim, 'ma_eitc'):,.2f}")
                print(f"    MA AGI: ${get_household_value(sim, 'ma_agi'):,.2f}")
                print(f"    MA Limited Income Credit: ${get_household_value(sim, 'ma_limited_income_tax_credit'):,.2f}")
        
        # Update previous values
        previous_ma_tax = new_ma_tax
        previous_fed_tax = new_fed_tax
        
        # Stop after CTC Reform to match the data
        if reform_name == "CTC Reform":
            break
    
    print("\n" + "=" * 60)
    print("FINAL RESULT:")
    print(f"Total MA tax change from baseline to CTC Reform: ${new_ma_tax - baseline_ma_tax:,.2f}")
    print(f"Expected from data file: $-56.41")
    print(f"Match: {abs((new_ma_tax - baseline_ma_tax) - (-56.41)) < 0.01}")

if __name__ == "__main__":
    trace_household_4428_cumulative()