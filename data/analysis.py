"""
Core analysis functions for tax reform impact calculations.
"""

import pandas as pd
import numpy as np
from policyengine_us import Microsimulation


def calculate_stacked_household_impacts(reforms, baseline_reform, year):
    """
    Calculate tax and income changes for each household after each reform is stacked.

    Parameters:
    -----------
    reforms : dict
        Dictionary of reform names to Reform objects
    baseline_reform : Reform
        The baseline reform to compare against
    year : int
        Tax year to analyze

    Returns:
    --------
    pd.DataFrame
        DataFrame with household impacts
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
    household_size = baseline.calculate(
        "household_size", map_to="household", period=year
    ).values
    num_dependents = baseline.calculate(
        "tax_unit_dependents", map_to="household", period=year
    ).values
    employment_income = baseline.calculate(
        "irs_employment_income", map_to="household", period=year
    ).values
    self_employment_income = baseline.calculate(
        "self_employment_income", map_to="household", period=year
    ).values
    capital_gains = baseline.calculate(
        "capital_gains", map_to="household", period=year
    ).values
    property_taxes = baseline.calculate(
        "real_estate_taxes", map_to="household", period=year
    ).values
    state_income_tax = baseline.calculate(
        "state_income_tax", map_to="household", period=year
    ).values
    tip_income = baseline.calculate(
        "tip_income", map_to="household", period=year
    ).values
    overtime_income = baseline.calculate(
        "fsla_overtime_premium", map_to="household", period=year
    ).values
    auto_loan_interest = baseline.calculate(
        "auto_loan_interest", map_to="household", period=year
    ).values
    household_weight = baseline.calculate(
        "household_weight", map_to="household", period=year
    ).values
    gross_income = baseline.calculate(
        "irs_gross_income", map_to="household", period=year
    ).values
    agi = baseline.calculate(
        "adjusted_gross_income", map_to="household", period=year
    ).values
    social_security_benefits = baseline.calculate(
        "social_security", map_to="household", period=year
    ).values
    dividend_income = baseline.calculate(
        "dividend_income", map_to="household", period=year
    ).values
    farm_income = baseline.calculate(
        "farm_income", map_to="household", period=year
    ).values
    taxable_interest_income = baseline.calculate(
        "taxable_interest_income", map_to="household", period=year
    ).values
    rental_income = baseline.calculate(
        "rental_income", map_to="household", period=year
    ).values
    taxable_unemployment_compensation = baseline.calculate(
        "taxable_unemployment_compensation", map_to="household", period=year
    ).values
    household_market_income = baseline.calculate(
        "household_market_income", map_to="household", period=year
    ).values
    miscellaneous_income = baseline.calculate(
        "miscellaneous_income", map_to="household", period=year
    ).values
    taxable_retirement_distributions = baseline.calculate(
        "taxable_retirement_distributions", map_to="household", period=year
    ).values
    taxable_pension_income = baseline.calculate(
        "taxable_pension_income", map_to="household", period=year
    ).values
    taxable_social_security = baseline.calculate(
        "taxable_social_security", map_to="household", period=year
    ).values

    # Get person-level values
    age = baseline.calculate("age", map_to="person", period=year).values
    person_household = baseline.calculate(
        "household_id", map_to="person", period=year
    ).values
    is_head = baseline.calculate(
        "is_tax_unit_head", map_to="person", period=year
    ).values
    is_spouse = baseline.calculate(
        "is_tax_unit_spouse", map_to="person", period=year
    ).values
    is_dependent = baseline.calculate(
        "is_tax_unit_dependent", map_to="person", period=year
    ).values
    tax_unit_id = baseline.calculate("tax_unit_id", map_to="person", period=year).values
    is_married = baseline.calculate("is_married", map_to="person", period=year).values
    # Add ssn_card_type
    ssn_card_type = baseline.calculate(
        "ssn_card_type", map_to="person", period=year
    ).values

    # Create a DataFrame with person-level data
    person_df = pd.DataFrame(
        {
            "household_id": person_household,
            "tax_unit_id": tax_unit_id,
            "age": age,
            "is_dependent": is_dependent,
            "is_head": is_head,
            "is_spouse": is_spouse,
            "is_married": is_married,
            "ssn_card_type": ssn_card_type,
        }
    )

    # Count tax units per household
    tax_units_per_household = (
        person_df[person_df["is_head"]].groupby("household_id")["tax_unit_id"].nunique()
    )
    num_tax_units = tax_units_per_household.reindex(household_id).fillna(1).values

    # Identify the first tax unit in each household
    # First, get all tax unit heads and sort by household_id and tax_unit_id
    tax_unit_heads = person_df[person_df["is_head"]].sort_values(
        ["household_id", "tax_unit_id"]
    )
    first_tax_unit_per_household = tax_unit_heads.groupby("household_id")[
        "tax_unit_id"
    ].first()

    # Create a mapping of household_id to first tax_unit_id
    first_tax_unit_map = first_tax_unit_per_household.to_dict()

    # Filter person_df to only include people from the first tax unit in each household
    person_df["is_first_tax_unit"] = person_df.apply(
        lambda row: row["tax_unit_id"] == first_tax_unit_map.get(row["household_id"]),
        axis=1,
    )

    # Now get ages only from the first tax unit
    first_tu_df = person_df[person_df["is_first_tax_unit"]]

    # Get married status from first tax unit only
    # Use the head's married status from the first tax unit
    married_status = (
        first_tu_df[first_tu_df["is_head"]]
        .groupby("household_id")["is_married"]
        .first()
    )
    is_married = married_status.reindex(household_id).fillna(False).values.astype(bool)

    # Get head ages (from first tax unit only)
    head_ages = (
        first_tu_df[first_tu_df["is_head"]].groupby("household_id")["age"].first()
    )
    age_head = head_ages.reindex(household_id).values

    # Get spouse ages (from first tax unit only)
    spouse_ages = (
        first_tu_df[first_tu_df["is_spouse"]].groupby("household_id")["age"].first()
    )
    age_spouse = spouse_ages.reindex(household_id).values

    # Fill missing spouse ages with 40 only if married
    age_spouse = np.where(
        pd.isna(age_spouse) & is_married,  # If age is NaN AND household is married
        40,  # Fill with 40
        age_spouse,  # Otherwise keep original value (including NaN)
    )

    # Get dependent ages (from first tax unit only)
    dependents_df = first_tu_df[first_tu_df["is_dependent"]].copy()
    dependents_df["dep_rank"] = dependents_df.groupby("household_id")["age"].rank(
        method="first"
    )

    # Determine max number of dependents (in first tax units)
    max_dependents = (
        int(dependents_df.groupby("household_id").size().max())
        if len(dependents_df) > 0
        else 0
    )

    # Create a dictionary to hold dependent age columns
    dependent_age_columns = {}

    # Create each dependent age column
    for i in range(max_dependents):
        # Get the i-th dependent for each household
        ith_dependent = (
            dependents_df[dependents_df["dep_rank"] == i + 1]
            .groupby("household_id")["age"]
            .first()
        )
        dependent_age_columns[f"Age of Dependent {i+1}"] = ith_dependent.reindex(
            household_id
        ).values

    # Fill NA values with 10 only for households that have that many dependents
    for i in range(max_dependents):
        col_name = f"Age of Dependent {i+1}"
        # Only fill with 10 if the household has at least i+1 dependents
        mask = pd.isna(dependent_age_columns[col_name]) & (num_dependents > i)
        dependent_age_columns[col_name] = np.where(
            mask,
            10,  # Fill with 10
            dependent_age_columns[col_name],  # Keep original value (including NaN)
        )

    # --- SSN Card Type household counts ---
    # CITIZEN or NON_CITIZEN_VALID_EAD
    ssn_citizen_ead = (
        person_df[person_df["ssn_card_type"].isin(["CITIZEN", "NON_CITIZEN_VALID_EAD"])]
        .groupby("household_id")
        .size()
    )
    # OTHER_NON_CITIZEN or NONE
    ssn_other_none = (
        person_df[person_df["ssn_card_type"].isin(["OTHER_NON_CITIZEN", "NONE"])]
        .groupby("household_id")
        .size()
    )
    # Reindex to all households, fill missing with 0
    ssn_citizen_ead = ssn_citizen_ead.reindex(household_id, fill_value=0).values
    ssn_other_none = ssn_other_none.reindex(household_id, fill_value=0).values

    # Initialize results dictionary
    results = {
        "Household ID": household_id,
        "State": state,
        "Household Size": household_size,
        "Number of Tax Units": num_tax_units,
        "Age of Head": age_head,
        "Age of Spouse": age_spouse,
        **dependent_age_columns,  # Add dependent ages from first tax unit
        "Number of Dependents": num_dependents,
        "Is Married": is_married,
        "Num with SSN Card (Citizen/EAD)": ssn_citizen_ead,
        "Num with SSN Card (Other/None)": ssn_other_none,
        "Employment Income": employment_income,
        "Self-Employment Income": self_employment_income,
        "Capital Gains": capital_gains,
        "Dividend Income": dividend_income,
        "Farm Income": farm_income,
        "Taxable Interest Income": taxable_interest_income,
        "Rental Income": rental_income,
        "Taxable Unemployment Compensation": taxable_unemployment_compensation,
        "Miscellaneous Income": miscellaneous_income,
        "Taxable Retirement Distributions": taxable_retirement_distributions,
        "Taxable Pension Income": taxable_pension_income,
        "Taxable Social Security": taxable_social_security,
        "Property Taxes": property_taxes,
        "State Income Tax": state_income_tax,
        "Tip Income": tip_income,
        "Overtime Income": overtime_income,
        "Auto Loan Interest": auto_loan_interest,
        "Social Security Benefits": social_security_benefits,
        "Gross Income": gross_income,
        "Adjusted Gross Income": agi,
        "Market Income": household_market_income,
        "Baseline Federal Tax Liability": baseline_income_tax,
        "Baseline Net Income": baseline_net_income,
        "Baseline Benefits": baseline_benefits,
        "Baseline Medicaid": medicaid_benefits,
        "Baseline ACA PTC": ptc_benefits,
        "Baseline CHIP": chip_benefits,
        "Baseline Total Benefits": total_benefits,
        "Household Weight": household_weight,
    }

    # Track cumulative values
    cumulative_reform = baseline_reform
    previous_income_tax = baseline_income_tax.copy()
    previous_state_income_tax = state_income_tax.copy()
    previous_net_income = baseline_net_income.copy()
    previous_total_benefits = total_benefits.copy()

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
        reformed_state_income_tax = reformed.calculate(
            "state_income_tax", map_to="household", period=year
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

        # Calculate incremental changes (from previous state)
        tax_change = reformed_income_tax - previous_income_tax
        state_tax_change = reformed_state_income_tax - previous_state_income_tax
        benefits_change = reformed_total_benefits - previous_total_benefits
        net_income_change = reformed_net_income - previous_net_income

        # Store results
        results[f"Change in federal tax liability after {reform_name}"] = tax_change
        results[f"Change in state tax liability after {reform_name}"] = state_tax_change
        results[f"Change in benefits after {reform_name}"] = benefits_change
        results[f"Change in net income after {reform_name}"] = net_income_change

        # Update previous values for next iteration
        previous_income_tax = reformed_income_tax.copy()
        previous_state_income_tax = reformed_state_income_tax.copy()
        previous_total_benefits = reformed_total_benefits.copy()
        previous_net_income = reformed_net_income.copy()

    # Add final total changes (from baseline to fully reformed)
    results[f"Total change in federal tax liability"] = (
        previous_income_tax - baseline_income_tax
    )
    results[f"Total change in state tax liability"] = (
        previous_state_income_tax - state_income_tax
    )
    results[f"Total change in benefits"] = previous_total_benefits - total_benefits
    results[f"Total change in net income"] = previous_net_income - baseline_net_income

    # Calculate percentage changes
    # For tax: handle cases where baseline tax is zero or negative
    pct_tax_change = np.zeros_like(baseline_income_tax)
    mask = baseline_income_tax != 0
    pct_tax_change[mask] = (
        results[f"Total change in federal tax liability"][mask]
        / np.abs(baseline_income_tax[mask])
    ) * 100

    results[f"Percentage change in federal tax liability"] = pct_tax_change

    # For net income: handle cases where baseline net income is zero
    pct_net_income_change = np.zeros_like(baseline_net_income)
    mask = baseline_net_income != 0
    pct_net_income_change[mask] = (
        results[f"Total change in net income"][mask] / np.abs(baseline_net_income[mask])
    ) * 100

    results[f"Percentage change in net income"] = pct_net_income_change

    # Calculate percentage changes for state tax
    pct_state_tax_change = np.zeros_like(state_income_tax)
    mask = state_income_tax != 0
    pct_state_tax_change[mask] = (
        results[f"Total change in state tax liability"][mask]
        / np.abs(state_income_tax[mask])
    ) * 100

    results[f"Percentage change in state tax liability"] = pct_state_tax_change

    # For benefits: handle cases where baseline benefits is zero
    pct_benefits_change = np.zeros_like(total_benefits)
    mask = total_benefits != 0
    pct_benefits_change[mask] = (
        results[f"Total change in benefits"][mask] / np.abs(total_benefits[mask])
    ) * 100

    results[f"Percentage change in benefits"] = pct_benefits_change

    # Create DataFrame
    df = pd.DataFrame(results)

    return df
