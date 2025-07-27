#!/usr/bin/env python3
"""
Investigate how CTC interacts with itemization decision.
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

def investigate_credits():
    """Investigate how credits affect itemization."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Stack reforms up to just before CTC
    baseline_reform = current_law_baseline()
    pre_ctc_reform = baseline_reform
    pre_ctc_reform = (pre_ctc_reform, senate_finance_tax_rate_reform())
    pre_ctc_reform = (pre_ctc_reform, senate_finance_sd_reform())
    pre_ctc_reform = (pre_ctc_reform, senate_finance_exemption_reform())
    
    # Stack with CTC
    with_ctc_reform = (pre_ctc_reform, senate_finance_ctc_reform())
    
    print("Creating simulations...")
    pre_ctc_sim = Microsimulation(reform=pre_ctc_reform, dataset=dataset_path)
    with_ctc_sim = Microsimulation(reform=with_ctc_reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = pre_ctc_sim.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    # Helper function
    def get_household_value(sim, variable, period=year):
        return sim.calculate(variable, map_to="household", period=period).values[household_4428_idx]
    
    print("\n" + "=" * 60)
    print("TAX AND CREDIT BREAKDOWN")
    print("=" * 60)
    
    # Check tax before credits under each scenario
    scenarios = [
        ("Pre-CTC, Standard", pre_ctc_sim, False),
        ("Pre-CTC, Itemized", pre_ctc_sim, True),
        ("With-CTC, Standard", with_ctc_sim, False),
        ("With-CTC, Itemized", with_ctc_sim, True)
    ]
    
    for scenario_name, sim, should_itemize in scenarios:
        print(f"\n{scenario_name}:")
        
        # We need to trace through the calculation
        actual_itemizes = get_household_value(sim, "tax_unit_itemizes")
        
        if (should_itemize and actual_itemizes) or (not should_itemize and not actual_itemizes):
            # This is the actual scenario
            tax_before_credits = get_household_value(sim, "income_tax_before_credits")
            ctc = get_household_value(sim, "ctc")
            eitc = get_household_value(sim, "eitc")
            other_credits = get_household_value(sim, "income_tax_non_refundable_credits") - ctc
            refundable_ctc = get_household_value(sim, "refundable_ctc")
            income_tax = get_household_value(sim, "income_tax")
            
            print(f"  Tax before credits: ${tax_before_credits:,.2f}")
            print(f"  Non-refundable CTC: ${ctc - refundable_ctc:,.2f}")
            print(f"  Other non-refundable credits: ${other_credits:,.2f}")
            print(f"  Refundable CTC: ${refundable_ctc:,.2f}")
            print(f"  EITC: ${eitc:,.2f}")
            print(f"  Final income tax: ${income_tax:,.2f}")
        else:
            # This is the counterfactual - get from the branching variables
            if should_itemize:
                tax_liability = get_household_value(sim, "tax_liability_if_itemizing")
            else:
                tax_liability = get_household_value(sim, "tax_liability_if_not_itemizing")
            print(f"  (Counterfactual) Tax liability: ${tax_liability:,.2f}")
    
    print("\n" + "=" * 60)
    print("KEY INSIGHT:")
    print("The CTC expansion increases the refundable portion of the credit.")
    print("This might make itemizing more attractive if it reduces tax")
    print("before credits, allowing more of the CTC to be refundable.")
    
if __name__ == "__main__":
    investigate_credits()