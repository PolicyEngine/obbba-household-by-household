#!/usr/bin/env python3
"""
Check why tax unit 442801 itemizes.
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

def check_decision():
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
    
    # Find tax unit 442801
    tax_unit_ids = sim.calculate("tax_unit_id", period=year).values
    tu_idx = np.where(tax_unit_ids == 442801)[0][0]
    
    def get_tu_value(var):
        return sim.calculate(var, period=year).values[tu_idx]
    
    print("Tax Unit 442801 Itemization Decision:")
    
    # Basic info
    agi = get_tu_value('adjusted_gross_income')
    itemizes = get_tu_value('tax_unit_itemizes')
    deductions = get_tu_value('taxable_income_deductions')
    
    print(f"\nBasic info:")
    print(f"  AGI: ${agi:,.2f}")
    print(f"  Itemizes: {bool(itemizes)} (value: {itemizes})")
    print(f"  Total deductions taken: ${deductions:,.2f}")
    
    # Tax comparison
    tax_if_item = get_tu_value('tax_liability_if_itemizing')
    tax_if_std = get_tu_value('tax_liability_if_not_itemizing')
    income_tax = get_tu_value('income_tax')
    
    print(f"\nTax comparison:")
    print(f"  Tax if itemizing: ${tax_if_item:,.2f}")
    print(f"  Tax if NOT itemizing: ${tax_if_std:,.2f}")
    print(f"  Actual income tax: ${income_tax:,.2f}")
    
    if abs(tax_if_item - tax_if_std) < 0.01:
        print(f"\n→ Tax is the same either way!")
    elif tax_if_item < tax_if_std:
        print(f"\n→ Itemizing saves ${tax_if_std - tax_if_item:,.2f}")
    else:
        print(f"\n→ Standard deduction would save ${tax_if_item - tax_if_std:,.2f}")
        print(f"   BUT the tax unit itemizes anyway!")
    
    # Check taxable income in both scenarios
    print(f"\nTaxable income calculation:")
    print(f"  AGI: ${agi:,.2f}")
    print(f"  - Deductions: ${deductions:,.2f}")
    print(f"  = Taxable income: ${agi - deductions:,.2f}")
    
    # Check if there's something special about the deductions
    standard_ded = get_tu_value('standard_deduction')
    itemized_ded = get_tu_value('itemized_taxable_income_deductions')
    
    if deductions != standard_ded and deductions != itemized_ded:
        print(f"\n*** ANOMALY DETECTED ***")
        print(f"  Total deductions (${deductions:,.2f}) is neither:")
        print(f"    - Standard deduction: ${standard_ded:,.2f}")
        print(f"    - Itemized deductions: ${itemized_ded:,.2f}")

if __name__ == "__main__":
    check_decision()