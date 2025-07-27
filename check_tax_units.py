#!/usr/bin/env python3
"""
Check how many tax units are in household 4428.
"""

from policyengine_us import Microsimulation
from policyengine_us.model_api import *
import numpy as np

def check_tax_units():
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    baseline_reform = Reform.from_dict({}, country_id="us")
    sim = Microsimulation(reform=baseline_reform, dataset=dataset_path)
    
    # Get person-level data
    person_household = sim.calculate("household_id", map_to="person", period=year).values
    person_tax_unit = sim.calculate("tax_unit_id", map_to="person", period=year).values
    is_tax_unit_head = sim.calculate("is_tax_unit_head", map_to="person", period=year).values
    
    # Find people in household 4428
    household_mask = person_household == 4428
    tax_units_in_household = person_tax_unit[household_mask]
    heads_in_household = is_tax_unit_head[household_mask]
    
    # Count unique tax units
    unique_tax_units = np.unique(tax_units_in_household)
    
    print(f"Household 4428 has {len(unique_tax_units)} tax unit(s)")
    print(f"Tax unit IDs: {unique_tax_units}")
    print(f"Number of people: {household_mask.sum()}")
    print(f"Number of tax unit heads: {heads_in_household.sum()}")
    
    # Check itemization status for each tax unit
    tax_unit_itemizes = sim.calculate("tax_unit_itemizes", period=year).values
    tax_unit_ids_all = sim.calculate("tax_unit_id", period=year).values
    
    print("\nItemization status by tax unit:")
    for tu_id in unique_tax_units:
        tu_idx = np.where(tax_unit_ids_all == tu_id)[0][0]
        itemizes = tax_unit_itemizes[tu_idx]
        print(f"  Tax unit {tu_id}: itemizes = {bool(itemizes)}")
    
if __name__ == "__main__":
    check_tax_units()