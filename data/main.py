#!/usr/bin/env python3
"""
Main script for analyzing tax reform impacts.
Analyzes 2026 tax year using enhanced CPS dataset.
"""

from datetime import datetime
from reforms import (
    tcja_reform,
    current_law_baseline,
    get_all_reforms,
    get_all_senate_finance_reforms,
)
from analysis import calculate_stacked_household_impacts


def main():
    print(f"Tax Reform Impact Analysis")
    print(f"========================")
    print(f"Analysis year: 2026")
    print(f"Dataset: Enhanced CPS 2024")
    print(f"Starting analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Get reforms
    reforms = get_all_reforms()
    senate_reforms = get_all_senate_finance_reforms()

    # Analysis 1: Current Law baseline
    print("=" * 50)
    print("ANALYSIS 1: Current Law Baseline")
    print("=" * 50)
    baseline_reform = current_law_baseline()

    # print(f"Analyzing {len(reforms)} reform components against Current Law baseline:")
    # for i, reform_name in enumerate(reforms.keys(), 1):
    #     print(f"  {i}. {reform_name}")
    # print()

    # # Calculate household-level impacts with Current Law baseline
    # df_current_law = calculate_stacked_household_impacts(
    #     reforms=reforms, baseline_reform=baseline_reform, year=2026
    # )

    # # Save Current Law baseline results
    # output_file_current_law = "household_tax_income_changes_current_law_baseline.csv"
    # df_current_law.to_csv(output_file_current_law, index=False)
    # print(f"\nSaved Current Law baseline results to '{output_file_current_law}'")
    # print(f"Total households analyzed: {len(df_current_law):,}")

    # # Display sample results
    # print(f"\nFirst 5 rows of Current Law baseline results:")
    # print(df_current_law.head())

    # Senate Finance analysis with Current Law baseline
    print("\n" + "=" * 40)
    print("Senate Finance Tax Reform Impact Analysis (Current Law Baseline)")
    print("=" * 40)
    print(f"Analyzing {len(senate_reforms)} Senate reform components:")
    for i, reform_name in enumerate(senate_reforms.keys(), 1):
        print(f"  {i}. {reform_name}")
    print()
    df_senate_current_law = calculate_stacked_household_impacts(
        reforms=senate_reforms, baseline_reform=baseline_reform, year=2026
    )
    senate_output_file_current_law = (
        "household_tax_income_changes_senate_current_law_baseline.csv"
    )
    df_senate_current_law.to_csv(senate_output_file_current_law, index=False)
    print(
        f"\nSaved Senate Current Law baseline results to '{senate_output_file_current_law}'"
    )
    print(f"Total households analyzed (Senate): {len(df_senate_current_law):,}")
    print(f"\nFirst 5 rows of Senate Current Law baseline results:")
    print(df_senate_current_law.head())

    # Analysis 2: TCJA baseline
    print("\n" + "=" * 50)
    print("ANALYSIS 2: TCJA Baseline")
    print("=" * 50)
    tcja_baseline_reform = tcja_reform()

    print(f"Analyzing {len(reforms)} reform components against TCJA baseline:")
    for i, reform_name in enumerate(reforms.keys(), 1):
        print(f"  {i}. {reform_name}")
    print()

    # Calculate household-level impacts with TCJA baseline
    # df_tcja = calculate_stacked_household_impacts(
    #     reforms=reforms, baseline_reform=tcja_baseline_reform, year=2026
    # )

    # # Save TCJA baseline results
    # output_file_tcja = "household_tax_income_changes_tcja_baseline.csv"
    # df_tcja.to_csv(output_file_tcja, index=False)
    # print(f"\nSaved TCJA baseline results to '{output_file_tcja}'")
    # print(f"Total households analyzed: {len(df_tcja):,}")

    # # Display sample results
    # print(f"\nFirst 5 rows of TCJA baseline results:")
    # print(df_tcja.head())

    # Senate Finance analysis with TCJA baseline
    print("\n" + "=" * 40)
    print("Senate Finance Tax Reform Impact Analysis (TCJA Baseline)")
    print("=" * 40)
    print(f"Analyzing {len(senate_reforms)} Senate reform components:")
    for i, reform_name in enumerate(senate_reforms.keys(), 1):
        print(f"  {i}. {reform_name}")
    print()
    df_senate_tcja = calculate_stacked_household_impacts(
        reforms=senate_reforms, baseline_reform=tcja_baseline_reform, year=2026
    )
    senate_output_file_tcja = "household_tax_income_changes_senate_tcja_baseline.csv"
    df_senate_tcja.to_csv(senate_output_file_tcja, index=False)
    print(f"\nSaved Senate TCJA baseline results to '{senate_output_file_tcja}'")
    print(f"Total households analyzed (Senate): {len(df_senate_tcja):,}")
    print(f"\nFirst 5 rows of Senate TCJA baseline results:")
    print(df_senate_tcja.head())

    print(f"\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Generated 4 spreadsheets:")
    # print(f"  1. {output_file_current_law} - House reforms vs Current Law baseline")
    print(
        f"  2. {senate_output_file_current_law} - Senate reforms vs Current Law baseline"
    )
    # print(f"  3. {output_file_tcja} - House reforms vs TCJA baseline")
    print(f"  4. {senate_output_file_tcja} - Senate reforms vs TCJA baseline")
    print(f"\nAnalysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
