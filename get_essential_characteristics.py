#!/usr/bin/env python3
"""
Get essential characteristics to create MRE.
"""

from policyengine_us import Microsimulation
from policyengine_us.model_api import *
import numpy as np
import sys

sys.path.append('data')
from reforms import current_law_baseline

def get_essentials():
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    baseline_reform = current_law_baseline()
    sim = Microsimulation(reform=baseline_reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = sim.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    def get_value(variable):
        return sim.calculate(variable, map_to="household", period=year).values[household_4428_idx]
    
    print("Key characteristics:")
    print(f"AGI: ${get_value('adjusted_gross_income'):,.2f}")
    print(f"Medical expenses: ${get_value('medical_out_of_pocket_expenses'):,.2f}")
    print(f"SALT deduction: ${get_value('salt_deduction'):,.2f}")
    print(f"Charitable deduction: ${get_value('charitable_deduction'):,.2f}")
    print(f"Standard deduction: ${get_value('standard_deduction'):,.2f}")
    print(f"Itemized deductions: ${get_value('itemized_taxable_income_deductions'):,.2f}")
    print(f"Number of dependents: {get_value('tax_unit_dependents')}")
    print(f"EITC: ${get_value('eitc'):,.2f}")
    print(f"State: MA")
    
if __name__ == "__main__":
    get_essentials()