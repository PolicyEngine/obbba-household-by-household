"""
Optimized analysis functions for tax reform impact calculations.
Outputs data in a more efficient format with separate files for households and provisions.
"""

import pandas as pd
import numpy as np
from policyengine_us import Microsimulation


def calculate_stacked_household_impacts_optimized(reforms, baseline_reform, year):
    """
    Calculate tax and income changes for each household in an optimized format.
    
    Returns:
    --------
    tuple of (households_df, provisions_df)
        households_df: Core household data and totals
        provisions_df: Long format of non-zero provision impacts
    """
    
    dataset_path = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    
    # Calculate baseline values
    print("Calculating baseline values...")
    baseline = Microsimulation(reform=baseline_reform, dataset=dataset_path)
    
    # Get household-level baseline values
    baseline_income_tax = baseline.calculate(
        "income_tax", map_to="household", period=year
    ).values
    baseline_net_income = baseline.calculate(
        "household_net_income_including_health_benefits",
        map_to="household",
        period=year,
    ).values
    
    # Get Benefit values
    baseline_benefits = baseline.calculate(
        "household_benefits", map_to="household", period=year
    ).values
    medicaid_benefits = baseline.calculate(
        "medicaid", map_to="household", period=year
    ).values
    ptc_benefits = baseline.calculate("aca_ptc", map_to="household", period=year).values
    chip_benefits = baseline.calculate("chip", map_to="household", period=year).values
    total_benefits = (
        medicaid_benefits + ptc_benefits + chip_benefits + baseline_benefits
    )
    
    # Get household-level characteristics
    household_id = baseline.calculate(
        "household_id", map_to="household", period=year
    ).values
    state = baseline.calculate("state_code", map_to="household", period=year).values
    household_weight = baseline.calculate(
        "household_weight", map_to="household", period=year
    ).values
    gross_income = baseline.calculate(
        "irs_gross_income", map_to="household", period=year
    ).values
    
    # Get person-level data for demographics
    person_df = pd.DataFrame({
        "household_id": baseline.calculate("household_id", period=year).values,
        "age": baseline.calculate("age", period=year).values,
        "is_tax_unit_head": baseline.calculate("is_tax_unit_head", period=year).values,
        "is_tax_unit_spouse": baseline.calculate("is_tax_unit_spouse", period=year).values,
        "is_tax_unit_dependent": baseline.calculate("is_tax_unit_dependent", period=year).values,
    })
    
    # Calculate household demographics
    household_demo = person_df.groupby("household_id").agg({
        "age": ["count", "max"],  # count for size, max for oldest person
        "is_tax_unit_head": "sum",
        "is_tax_unit_spouse": "sum", 
        "is_tax_unit_dependent": "sum"
    })
    household_demo.columns = ["size", "max_age", "num_heads", "num_spouses", "num_dependents"]
    
    # Get head and spouse ages
    head_ages = person_df[person_df["is_tax_unit_head"] == True].groupby("household_id")["age"].first()
    spouse_ages = person_df[person_df["is_tax_unit_spouse"] == True].groupby("household_id")["age"].first()
    
    # Track cumulative values
    cumulative_reform = baseline_reform
    previous_net_income = baseline_net_income.copy()
    previous_income_tax = baseline_income_tax.copy()
    previous_total_benefits = total_benefits.copy()
    
    # Collect provision impacts
    provision_impacts = []
    
    # Apply each reform sequentially
    for reform_name, reform in reforms.items():
        print(f"Processing {reform_name}...")
        
        # Stack the reform
        cumulative_reform = (cumulative_reform, reform)
        
        # Calculate with cumulative reforms
        reformed = Microsimulation(reform=cumulative_reform, dataset=dataset_path)
        
        # Get reformed values
        reformed_income_tax = reformed.calculate(
            "income_tax", map_to="household", period=year
        ).values
        reformed_net_income = reformed.calculate(
            "household_net_income_including_health_benefits",
            map_to="household",
            period=year,
        ).values
        reformed_benefits = reformed.calculate(
            "household_benefits", map_to="household", period=year
        ).values
        reformed_medicaid = reformed.calculate(
            "medicaid", map_to="household", period=year
        ).values
        reformed_ptc = reformed.calculate(
            "aca_ptc", map_to="household", period=year
        ).values
        reformed_chip = reformed.calculate(
            "chip", map_to="household", period=year
        ).values
        reformed_total_benefits = (
            reformed_medicaid + reformed_ptc + reformed_chip + reformed_benefits
        )
        
        # Calculate incremental changes
        net_income_change = reformed_net_income - previous_net_income
        tax_change = reformed_income_tax - previous_income_tax
        benefits_change = reformed_total_benefits - previous_total_benefits
        
        # Store non-zero impacts
        non_zero_mask = (
            (np.abs(net_income_change) > 0.5) |  # At least 50 cents change
            (np.abs(tax_change) > 0.5) |
            (np.abs(benefits_change) > 0.5)
        )
        
        if np.any(non_zero_mask):
            affected_households = household_id[non_zero_mask]
            for i, hh_id in enumerate(affected_households):
                idx = np.where(household_id == hh_id)[0][0]
                provision_impacts.append({
                    "household_id": int(hh_id),
                    "provision": reform_name,
                    "net_income_change": round(net_income_change[idx], 2),
                    "tax_change": round(tax_change[idx], 2),
                    "benefit_change": round(benefits_change[idx], 2)
                })
        
        # Update previous values for next iteration
        previous_income_tax = reformed_income_tax.copy()
        previous_total_benefits = reformed_total_benefits.copy()
        previous_net_income = reformed_net_income.copy()
    
    # Calculate total changes
    total_net_income_change = previous_net_income - baseline_net_income
    total_tax_change = previous_income_tax - baseline_income_tax
    total_benefits_change = previous_total_benefits - total_benefits
    
    # Calculate percentage changes
    pct_net_income_change = np.zeros_like(baseline_net_income)
    mask = baseline_net_income != 0
    pct_net_income_change[mask] = (
        total_net_income_change[mask] / np.abs(baseline_net_income[mask])
    ) * 100
    
    # Create households dataframe
    households_df = pd.DataFrame({
        "id": household_id.astype(int),
        "state": state,
        "household_weight": np.round(household_weight, 2),
        "market_income": np.round(gross_income, 0).astype(int),
        "baseline_net_income": np.round(baseline_net_income, 0).astype(int),
        "total_change_net_income": np.round(total_net_income_change, 0).astype(int),
        "pct_change_net_income": np.round(pct_net_income_change, 2),
        "total_change_tax": np.round(total_tax_change, 0).astype(int),
        "total_change_benefits": np.round(total_benefits_change, 0).astype(int),
    })
    
    # Add demographics
    households_df["household_size"] = household_demo["size"].reindex(household_id).fillna(1).astype(int).values
    households_df["num_dependents"] = household_demo["num_dependents"].reindex(household_id).fillna(0).astype(int).values
    households_df["age_head"] = head_ages.reindex(household_id).fillna(40).astype(int).values
    households_df["age_spouse"] = spouse_ages.reindex(household_id).values
    households_df["is_married"] = ~pd.isna(households_df["age_spouse"])
    
    # Create provisions dataframe
    provisions_df = pd.DataFrame(provision_impacts)
    
    print(f"Households: {len(households_df):,}")
    print(f"Non-zero provision impacts: {len(provisions_df):,}")
    print(f"Average provisions per affected household: {len(provisions_df) / len(households_df[households_df['total_change_net_income'] != 0]):.1f}")
    
    return households_df, provisions_df