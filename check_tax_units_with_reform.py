#!/usr/bin/env python3
"""
Check tax unit itemization with the reform stack.
"""

from policyengine_us import Microsimulation
from policyengine_us.model_api import *
import numpy as np
import sys

sys.path.append('data')
from reforms import (
    current_law_baseline,
    senate_finance_tax_rate_reform,
    senate_finance_sd_reform,
    senate_finance_exemption_reform,
    senate_finance_ctc_reform
)

def check_with_reform():
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Build reform stack
    baseline_reform = current_law_baseline()
    reform = baseline_reform
    reform = (reform, senate_finance_tax_rate_reform())
    reform = (reform, senate_finance_sd_reform())
    reform = (reform, senate_finance_exemption_reform())
    reform = (reform, senate_finance_ctc_reform())
    
    sim = Microsimulation(reform=reform, dataset=dataset_path)
    
    # Get tax unit info
    tax_unit_ids = sim.calculate("tax_unit_id", period=year).values
    tax_unit_itemizes = sim.calculate("tax_unit_itemizes", period=year).values
    tax_if_item = sim.calculate("tax_liability_if_itemizing", period=year).values
    tax_if_std = sim.calculate("tax_liability_if_not_itemizing", period=year).values
    
    # Find the two tax units
    tu1_idx = np.where(tax_unit_ids == 442801)[0][0]
    tu2_idx = np.where(tax_unit_ids == 442802)[0][0]
    
    print("With CTC reform:")
    print("\nTax unit 442801:")
    print(f"  Itemizes: {bool(tax_unit_itemizes[tu1_idx])}")
    print(f"  Tax if itemizing: ${tax_if_item[tu1_idx]:,.2f}")
    print(f"  Tax if standard: ${tax_if_std[tu1_idx]:,.2f}")
    print(f"  Should itemize: {tax_if_item[tu1_idx] < tax_if_std[tu1_idx]}")
    
    print("\nTax unit 442802:")
    print(f"  Itemizes: {bool(tax_unit_itemizes[tu2_idx])}")
    print(f"  Tax if itemizing: ${tax_if_item[tu2_idx]:,.2f}")
    print(f"  Tax if standard: ${tax_if_std[tu2_idx]:,.2f}")
    print(f"  Should itemize: {tax_if_item[tu2_idx] < tax_if_std[tu2_idx]}")
    
    # Get more details about each tax unit
    print("\n" + "=" * 60)
    print("TAX UNIT DETAILS")
    
    # Map person-level data
    person_tax_unit = sim.calculate("tax_unit_id", map_to="person", period=year).values
    person_age = sim.calculate("age", map_to="person", period=year).values
    person_income = sim.calculate("employment_income", map_to="person", period=year).values
    
    for tu_id in [442801, 442802]:
        people_in_tu = person_tax_unit == tu_id
        ages = person_age[people_in_tu]
        incomes = person_income[people_in_tu]
        print(f"\nTax unit {tu_id}:")
        print(f"  Number of people: {people_in_tu.sum()}")
        print(f"  Ages: {ages}")
        print(f"  Employment incomes: {incomes}")

if __name__ == "__main__":
    check_with_reform()