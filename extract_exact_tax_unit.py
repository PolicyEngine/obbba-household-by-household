#!/usr/bin/env python3
"""
Extract exact details of tax unit 442801 to understand the issue.
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

def extract_details():
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
    
    print("Tax Unit 442801 Details:")
    print(f"\nIncome:")
    print(f"  AGI: ${get_tu_value('adjusted_gross_income'):,.2f}")
    # print(f"  Wages: ${get_tu_value('tax_unit_wages'):,.2f}")
    
    print(f"\nDeductions:")
    print(f"  Itemizes: {bool(get_tu_value('tax_unit_itemizes'))}")
    print(f"  Total deductions: ${get_tu_value('taxable_income_deductions'):,.2f}")
    print(f"  Standard deduction: ${get_tu_value('standard_deduction'):,.2f}")
    print(f"  Itemized deductions: ${get_tu_value('itemized_taxable_income_deductions'):,.2f}")
    
    # Check what makes up itemized deductions
    print(f"\nItemized components:")
    print(f"  Medical expense: ${get_tu_value('medical_expense_deduction'):,.2f}")
    print(f"  SALT: ${get_tu_value('salt_deduction'):,.2f}")
    print(f"  Charitable: ${get_tu_value('charitable_deduction'):,.2f}")
    
    # Check deductions if itemizing vs not
    print(f"\nDeduction calculations:")
    print(f"  Deductions if itemizing: ${get_tu_value('taxable_income_deductions_if_itemizing'):,.2f}")
    print(f"  Deductions if NOT itemizing: ${get_tu_value('taxable_income_deductions_if_not_itemizing'):,.2f}")
    
    # The key difference
    ded_if_item = get_tu_value('taxable_income_deductions_if_itemizing')
    itemized = get_tu_value('itemized_taxable_income_deductions')
    if ded_if_item != itemized:
        print(f"\n*** KEY FINDING ***")
        print(f"  Deductions if itemizing (${ded_if_item:,.2f}) != Itemized deductions (${itemized:,.2f})")
        print(f"  Extra amount when itemizing: ${ded_if_item - itemized:,.2f}")
    
    # Check senior status
    print(f"\nSenior status:")
    print(f"  Aged head: {get_tu_value('aged_head')}")
    print(f"  Aged spouse: {get_tu_value('aged_spouse')}")
    
if __name__ == "__main__":
    extract_details()