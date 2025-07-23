#!/usr/bin/env python3
"""
Optimized main script for generating tax reform data in efficient format.
"""

from datetime import datetime
from reforms import (
    tcja_reform,
    current_law_baseline,
    get_all_senate_finance_reforms,
)
from analysis_optimized import calculate_stacked_household_impacts_optimized


def main():
    print(f"Optimized Tax Reform Data Generation")
    print(f"===================================")
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
    
    # Calculate household-level impacts with Current Law baseline
    households_df, provisions_df = calculate_stacked_household_impacts_optimized(
        reforms=reforms, 
        baseline_reform=baseline_reform, 
        year=2026
    )
    
    # Save results
    households_file = "households_tcja_expiration.csv"
    provisions_file = "provisions_tcja_expiration.csv"
    
    households_df.to_csv(households_file, index=False)
    provisions_df.to_csv(provisions_file, index=False)
    
    print(f"\nSaved optimized results:")
    print(f"  - {households_file} ({households_df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB in memory)")
    print(f"  - {provisions_file} ({provisions_df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB in memory)")
    
    # Check file sizes
    import os
    households_size = os.path.getsize(households_file) / 1024 / 1024
    provisions_size = os.path.getsize(provisions_file) / 1024 / 1024
    print(f"\nFile sizes:")
    print(f"  - {households_file}: {households_size:.1f} MB")
    print(f"  - {provisions_file}: {provisions_size:.1f} MB")
    print(f"  - Total: {households_size + provisions_size:.1f} MB")
    
    # Analysis 2: TCJA baseline (TCJA extension)
    print("\n" + "=" * 50)
    print("ANALYSIS 2: TCJA Baseline (TCJA Extension)")
    print("=" * 50)
    tcja_baseline_reform = tcja_reform()
    
    # Calculate household-level impacts with TCJA baseline
    households_df_tcja, provisions_df_tcja = calculate_stacked_household_impacts_optimized(
        reforms=reforms,
        baseline_reform=tcja_baseline_reform,
        year=2026
    )
    
    # Save results
    households_file_tcja = "households_tcja_extension.csv"
    provisions_file_tcja = "provisions_tcja_extension.csv"
    
    households_df_tcja.to_csv(households_file_tcja, index=False)
    provisions_df_tcja.to_csv(provisions_file_tcja, index=False)
    
    print(f"\nSaved optimized results:")
    print(f"  - {households_file_tcja} ({households_df_tcja.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB in memory)")
    print(f"  - {provisions_file_tcja} ({provisions_df_tcja.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB in memory)")
    
    # Check file sizes
    households_size_tcja = os.path.getsize(households_file_tcja) / 1024 / 1024
    provisions_size_tcja = os.path.getsize(provisions_file_tcja) / 1024 / 1024
    print(f"\nFile sizes:")
    print(f"  - {households_file_tcja}: {households_size_tcja:.1f} MB")
    print(f"  - {provisions_file_tcja}: {provisions_size_tcja:.1f} MB")
    print(f"  - Total: {households_size_tcja + provisions_size_tcja:.1f} MB")
    
    # Compare with original format estimate
    print(f"\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    original_size_estimate = len(households_df) * 150 * 8 / 1024 / 1024  # ~150 columns, 8 bytes per value
    optimized_size = (households_size + provisions_size + households_size_tcja + provisions_size_tcja)
    reduction = (1 - optimized_size / (original_size_estimate * 2)) * 100
    
    print(f"Original format estimate: {original_size_estimate * 2:.1f} MB (2 files)")
    print(f"Optimized format actual: {optimized_size:.1f} MB (4 files)")
    print(f"Size reduction: {reduction:.0f}%")
    print(f"\nAnalysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()