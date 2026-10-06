#!/usr/bin/env python3
"""
Main script for analyzing tax reform impacts.
Analyzes 2026 tax year using enhanced CPS dataset.
"""

from datetime import datetime
from reforms import obbba_reversal_reform, tcja_reform
from obbba_reforms import get_obbba_provisions
from analysis import calculate_stacked_household_impacts


def main():
    print(f"Tax Reform Impact Analysis")
    print(f"========================")
    print(f"Analysis year: 2026")
    print(f"Dataset: Enhanced CPS 2024")
    print(f"Starting analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    reforms = get_obbba_provisions()

    # Analysis 1: Current Law baseline
    print("=" * 50)
    print("ANALYSIS 1: TCJA Expiration Baseline")
    print("=" * 50)
    baseline_reform = obbba_reversal_reform()

    print(f"Analyzing {len(reforms)} OBBBA components against TCJA expiration baseline:")
    for i, reform_name in enumerate(reforms.keys(), 1):
        print(f"  {i}. {reform_name}")
    print()

    # Calculate household-level impacts with TCJA expiration baseline.
    df_tcja_expiration = calculate_stacked_household_impacts(
        reforms=reforms, baseline_reform=baseline_reform, year=2026
    )

    # Keep the historical filename because the frontend loads this path.
    output_file_tcja_expiration = (
        "household_tax_income_changes_senate_current_law_baseline.csv"
    )
    df_tcja_expiration.to_csv(output_file_tcja_expiration, index=False)
    print(f"\nSaved TCJA expiration results to '{output_file_tcja_expiration}'")
    print(f"Total households analyzed: {len(df_tcja_expiration):,}")

    # Display sample results
    print(f"\nFirst 5 rows of TCJA expiration baseline results:")
    print(df_tcja_expiration.head())

    # Analysis 2: TCJA baseline
    print("\n" + "=" * 50)
    print("ANALYSIS 2: TCJA Baseline")
    print("=" * 50)
    tcja_baseline_reform = (obbba_reversal_reform(), tcja_reform())

    print(f"Analyzing {len(reforms)} OBBBA components against TCJA extension baseline:")
    for i, reform_name in enumerate(reforms.keys(), 1):
        print(f"  {i}. {reform_name}")
    print()

    # Calculate household-level impacts with TCJA extension baseline.
    df_tcja = calculate_stacked_household_impacts(
        reforms=reforms, baseline_reform=tcja_baseline_reform, year=2026
    )

    # Keep the historical filename because the frontend loads this path.
    output_file_tcja = "household_tax_income_changes_senate_tcja_baseline.csv"
    df_tcja.to_csv(output_file_tcja, index=False)
    print(f"\nSaved TCJA extension results to '{output_file_tcja}'")
    print(f"Total households analyzed: {len(df_tcja):,}")

    # Display sample results
    print(f"\nFirst 5 rows of TCJA baseline results:")
    print(df_tcja.head())

    print(f"\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Generated 2 spreadsheets:")
    print(f"  1. {output_file_tcja_expiration} - OBBBA vs TCJA expiration baseline")
    print(f"  2. {output_file_tcja} - OBBBA vs TCJA extension baseline")
    print(f"\nAnalysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
