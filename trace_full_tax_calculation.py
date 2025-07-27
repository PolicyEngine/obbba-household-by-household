#!/usr/bin/env python3
"""
Trace the full tax calculation to understand why itemizing becomes beneficial with CTC.
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

def trace_calculation():
    """Trace full tax calculation."""
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    year = 2026
    
    # Create two simulations: pre-CTC and with-CTC
    baseline_reform = current_law_baseline()
    pre_ctc_reform = baseline_reform
    pre_ctc_reform = (pre_ctc_reform, senate_finance_tax_rate_reform())
    pre_ctc_reform = (pre_ctc_reform, senate_finance_sd_reform())
    pre_ctc_reform = (pre_ctc_reform, senate_finance_exemption_reform())
    
    with_ctc_reform = (pre_ctc_reform, senate_finance_ctc_reform())
    
    print("Creating simulations...")
    pre_ctc_sim = Microsimulation(reform=pre_ctc_reform, dataset=dataset_path)
    with_ctc_sim = Microsimulation(reform=with_ctc_reform, dataset=dataset_path)
    
    # Find household 4428
    household_ids = pre_ctc_sim.calculate("household_id", map_to="household", period=year).values
    household_4428_idx = np.where(household_ids == 4428)[0][0]
    
    def get_value(sim, variable):
        return sim.calculate(variable, map_to="household", period=year).values[household_4428_idx]
    
    # Create branch simulations to force itemization
    print("Creating branch simulations...")
    
    # Get tax unit count
    tax_unit_count = len(pre_ctc_sim.calculate("tax_unit_id", period=year).values)
    
    # Pre-CTC forced to itemize
    pre_ctc_itemize_branch = pre_ctc_sim.get_branch("pre_ctc_itemize")
    pre_ctc_itemize_branch.set_input(
        "tax_unit_itemizes", year, np.ones((tax_unit_count,), dtype=bool)
    )
    
    # With-CTC forced to NOT itemize
    with_ctc_standard_branch = with_ctc_sim.get_branch("with_ctc_standard")
    with_ctc_standard_branch.set_input(
        "tax_unit_itemizes", year, np.zeros((tax_unit_count,), dtype=bool)
    )
    
    print("\n" + "=" * 80)
    print("DETAILED TAX CALCULATION TRACE")
    print("=" * 80)
    
    # Variables to trace
    trace_vars = [
        ("Gross income", "adjusted_gross_income"),
        ("Taxable income deductions", "taxable_income_deductions"),
        ("Taxable income", "taxable_income"),
        ("Tax before credits", "income_tax_before_credits"),
        ("CTC maximum", "ctc_maximum"),
        ("Non-refundable CTC", "non_refundable_ctc"),
        ("Refundable CTC", "refundable_ctc"),
        ("Total CTC", "ctc"),
        ("EITC", "eitc"),
        ("Other credits", "income_tax_non_refundable_credits"),
        ("Income tax", "income_tax"),
        ("Payroll tax", "employee_payroll_tax"),
        ("Self-employment tax", "self_employment_tax"),
    ]
    
    scenarios = [
        ("Pre-CTC, Standard (actual)", pre_ctc_sim),
        ("Pre-CTC, Itemized (forced)", pre_ctc_itemize_branch),
        ("With-CTC, Standard (forced)", with_ctc_standard_branch),
        ("With-CTC, Itemized (actual)", with_ctc_sim),
    ]
    
    results = {}
    
    for scenario_name, sim in scenarios:
        print(f"\n{scenario_name}:")
        print("-" * 40)
        scenario_results = {}
        for label, var in trace_vars:
            try:
                value = get_value(sim, var)
                scenario_results[var] = value
                print(f"  {label:30s} ${value:12,.2f}")
            except:
                print(f"  {label:30s} [Error]")
        results[scenario_name] = scenario_results
    
    # Calculate differences
    print("\n" + "=" * 80)
    print("KEY COMPARISONS")
    print("=" * 80)
    
    # Why does Pre-CTC prefer standard?
    pre_standard = results["Pre-CTC, Standard (actual)"]
    pre_itemized = results["Pre-CTC, Itemized (forced)"]
    
    print("\nPre-CTC: Standard vs Itemized")
    print(f"  Income tax difference: ${pre_itemized['income_tax'] - pre_standard['income_tax']:,.2f}")
    print(f"  (Itemizing would cost ${pre_itemized['income_tax'] - pre_standard['income_tax']:,.2f} more)")
    
    # Why does With-CTC prefer itemized?
    with_standard = results["With-CTC, Standard (forced)"]
    with_itemized = results["With-CTC, Itemized (actual)"]
    
    print("\nWith-CTC: Standard vs Itemized")
    print(f"  Income tax difference: ${with_itemized['income_tax'] - with_standard['income_tax']:,.2f}")
    print(f"  (Itemizing saves ${with_standard['income_tax'] - with_itemized['income_tax']:,.2f})")
    
    # What changed?
    print("\n" + "=" * 80)
    print("WHAT CHANGED WITH CTC REFORM?")
    print("=" * 80)
    
    print("\nComparing itemized scenarios before and after CTC:")
    for label, var in trace_vars:
        if var in pre_itemized and var in with_itemized:
            diff = with_itemized[var] - pre_itemized[var]
            if abs(diff) > 0.01:
                print(f"  {label:30s} changed by ${diff:12,.2f}")
    
if __name__ == "__main__":
    trace_calculation()