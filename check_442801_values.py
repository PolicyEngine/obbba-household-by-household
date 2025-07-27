#!/usr/bin/env python3
"""Check exact values for tax unit 442801."""

from policyengine_us import Microsimulation
from policyengine_us.model_api import *
import numpy as np

dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
year = 2026

# Load without reform to get raw values
sim = Microsimulation(dataset=dataset_path)
tax_unit_ids = sim.calculate("tax_unit_id", period=year).values
tu_idx = np.where(tax_unit_ids == 442801)[0][0]

def get_tu_value(var):
    return sim.calculate(var, period=year).values[tu_idx]

print("Tax Unit 442801 characteristics:")
print(f"  Employment income: ${get_tu_value('employment_income'):,.2f}")
print(f"  Medical expenses: ${get_tu_value('medical_out_of_pocket_expenses'):,.2f}")
print(f"  State taxes paid: ${get_tu_value('state_income_tax'):,.2f}")
print(f"  Real estate taxes: ${get_tu_value('real_estate_taxes'):,.2f}")
print(f"  Number of children: {int(get_tu_value('tax_unit_children'))}")
print(f"  Filing status: {get_tu_value('filing_status')}")