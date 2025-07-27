#!/usr/bin/env python3
"""
Debug the CTC calculation to understand the paradox.
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

def debug_ctc():
    """Debug CTC calculation."""
    
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
    
    # Check the actual itemization decision
    itemizes = sim.calculate("tax_unit_itemizes", map_to="household", period=year).values[household_4428_idx]
    
    print(f"\nHousehold 4428 itemizes: {itemizes}")
    
    # Check tax liabilities used for decision
    tax_if_itemizing = sim.calculate("tax_liability_if_itemizing", map_to="household", period=year).values[household_4428_idx]
    tax_if_not_itemizing = sim.calculate("tax_liability_if_not_itemizing", map_to="household", period=year).values[household_4428_idx]
    
    print(f"\nTax liability comparison:")
    print(f"  If itemizing: ${tax_if_itemizing:,.2f}")
    print(f"  If NOT itemizing: ${tax_if_not_itemizing:,.2f}")
    print(f"  Difference: ${tax_if_itemizing - tax_if_not_itemizing:,.2f}")
    print(f"  Decision: {'Itemize' if tax_if_itemizing < tax_if_not_itemizing else 'Standard'}")
    
    # Something is wrong if they're choosing to itemize when it results in the same tax
    print("\n" + "=" * 60)
    print("ERROR IN LOGIC:")
    print("The household is choosing to itemize even though both options")
    print("result in the same final tax. This suggests:")
    print("1. The branch simulations aren't calculating correctly, OR")
    print("2. There's a floating point comparison issue, OR")
    print("3. The tax_liability variables include something beyond income_tax")
    
if __name__ == "__main__":
    debug_ctc()