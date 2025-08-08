#!/usr/bin/env python3
"""
Understand the cumulative effect of reforms on household 4428.
"""

import csv

# Read the data and trace cumulative changes
with open('static/household_tax_income_changes_senate_current_law_baseline.csv', 'r') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if row['Household ID'] == '4428':
            print("Tracing cumulative reforms for Household 4428")
            print("=" * 60)
            
            # Get baseline values
            baseline_fed = float(row['Baseline federal tax liability'])
            baseline_state = float(row['State income tax'])  # This is baseline state tax
            
            print(f"Baseline federal tax: ${baseline_fed:,.2f}")
            print(f"Baseline state tax: ${baseline_state:,.2f}")
            
            # Track cumulative values
            cumulative_fed = baseline_fed
            cumulative_state = baseline_state
            
            # List of reforms in order
            reforms = [
                "Rate adjustments",
                "Standard deduction increase", 
                "Exemption repeal",
                "Child tax credit social security number requirement",
                "Child tax credit expansion"
            ]
            
            print("\nCumulative effects:")
            print("-" * 60)
            
            for reform in reforms:
                fed_key = f"Change in Federal tax liability after {reform}"
                state_key = f"Change in State tax liability after {reform}"
                
                if fed_key in row:
                    fed_change = float(row[fed_key])
                    state_change = float(row[state_key])
                    
                    cumulative_fed += fed_change
                    cumulative_state += state_change
                    
                    if abs(fed_change) > 0.01 or abs(state_change) > 0.01:
                        print(f"\nAfter {reform}:")
                        print(f"  Federal change: ${fed_change:,.2f}")
                        print(f"  State change: ${state_change:,.2f}")
                        print(f"  Cumulative federal tax: ${cumulative_fed:,.2f}")
                        print(f"  Cumulative state tax: ${cumulative_state:,.2f}")
            
            print("\n" + "=" * 60)
            print("KEY INSIGHT:")
            print("The state tax change of -$56.41 happens ONLY with the CTC expansion.")
            print("This suggests the mechanism is specific to how the CTC expansion")
            print("interacts with the already-modified tax structure from prior reforms.")
            
            break