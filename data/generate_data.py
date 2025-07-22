#!/usr/bin/env python3
"""
Generate tax reform data files for OBBBA Scatter visualization.
This generates both the original wide format and the optimized format.
"""

from datetime import datetime
import shutil
from reforms import (
    tcja_reform,
    current_law_baseline,
    get_all_senate_finance_reforms,
)
from analysis import calculate_stacked_household_impacts
from analysis_optimized import calculate_stacked_household_impacts_optimized


def main():
    print(f"Tax Reform Data Generation")
    print(f"=========================")
    print(f"Analysis year: 2026")
    print(f"Dataset: Enhanced CPS 2024")
    print(f"Starting analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Use the passed Senate Finance reforms
    reforms = get_all_senate_finance_reforms()
    
    # Analysis 1: Current Law baseline (TCJA expiration)
    print("=" * 50)
    print("ANALYSIS 1: Current Law Baseline (TCJA Expiration)")
    print("=" * 50)
    baseline_reform = current_law_baseline()
    
    print(f"Analyzing {len(reforms)} reform components:")
    for i, reform_name in enumerate(reforms.keys(), 1):
        print(f"  {i}. {reform_name}")
    print()
    
    # Generate optimized format
    print("\nGenerating optimized format...")
    households_df, provisions_df = calculate_stacked_household_impacts_optimized(
        reforms=reforms, 
        baseline_reform=baseline_reform, 
        year=2026
    )
    
    # Save optimized results
    households_file = "households_tcja_expiration.csv"
    provisions_file = "provisions_tcja_expiration.csv"
    
    households_df.to_csv(households_file, index=False)
    provisions_df.to_csv(provisions_file, index=False)
    
    print(f"\nSaved optimized results:")
    print(f"  - {households_file}")
    print(f"  - {provisions_file}")
    
    # Generate original wide format
    print("\nGenerating original wide format...")
    wide_df = calculate_stacked_household_impacts(
        reforms=reforms,
        baseline_reform=baseline_reform,
        year=2026
    )
    
    # Save with new name (without "senate")
    wide_file = "household_tax_income_changes_current_law_baseline.csv"
    wide_df.to_csv(wide_file, index=False)
    print(f"  - {wide_file}")
    
    # Analysis 2: TCJA baseline (TCJA extension)
    print("\n" + "=" * 50)
    print("ANALYSIS 2: TCJA Baseline (TCJA Extension)")
    print("=" * 50)
    tcja_baseline_reform = tcja_reform()
    
    # Generate optimized format
    print("\nGenerating optimized format...")
    households_df_tcja, provisions_df_tcja = calculate_stacked_household_impacts_optimized(
        reforms=reforms,
        baseline_reform=tcja_baseline_reform,
        year=2026
    )
    
    # Save optimized results
    households_file_tcja = "households_tcja_extension.csv"
    provisions_file_tcja = "provisions_tcja_extension.csv"
    
    households_df_tcja.to_csv(households_file_tcja, index=False)
    provisions_df_tcja.to_csv(provisions_file_tcja, index=False)
    
    print(f"\nSaved optimized results:")
    print(f"  - {households_file_tcja}")
    print(f"  - {provisions_file_tcja}")
    
    # Generate original wide format
    print("\nGenerating original wide format...")
    wide_df_tcja = calculate_stacked_household_impacts(
        reforms=reforms,
        baseline_reform=tcja_baseline_reform,
        year=2026
    )
    
    # Save with new name (without "senate")
    wide_file_tcja = "household_tax_income_changes_tcja_baseline.csv"
    wide_df_tcja.to_csv(wide_file_tcja, index=False)
    print(f"  - {wide_file_tcja}")
    
    # Summary
    import os
    print(f"\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    total_size = 0
    for f in [households_file, provisions_file, wide_file, 
              households_file_tcja, provisions_file_tcja, wide_file_tcja]:
        size = os.path.getsize(f) / 1024 / 1024
        total_size += size
        print(f"{f}: {size:.1f} MB")
    
    print(f"\nTotal size: {total_size:.1f} MB")
    print(f"\nAnalysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Copy to static directory
    print("\nCopying files to ../static/...")
    for f in [households_file, provisions_file, wide_file,
              households_file_tcja, provisions_file_tcja, wide_file_tcja]:
        shutil.copy(f, "../static/")
    print("Files copied successfully!")


if __name__ == "__main__":
    main()