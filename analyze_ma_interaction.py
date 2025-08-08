#!/usr/bin/env python3
"""
Analyze the specific case of household 4428 to understand MA state tax interaction.
"""

import csv

# Read the data file
with open('static/household_tax_income_changes_senate_current_law_baseline.csv', 'r') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if row['Household ID'] == '4428':
            print("Household 4428 Analysis")
            print("=" * 50)
            print(f"State: {row['State']}")
            print(f"Married: {row['Is Married']}")
            print(f"Number of dependents: {row['Number of Dependents']}")
            print(f"Employment income: ${float(row['Employment income']):,.2f}")
            print(f"Federal AGI: ${float(row['Adjusted gross income']):,.2f}")
            
            print("\nFederal Tax Changes:")
            print("-" * 30)
            
            # Check each reform's impact
            reforms = [
                "Rate adjustments",
                "Standard deduction increase", 
                "Exemption repeal",
                "Child tax credit social security number requirement",
                "Child tax credit expansion",
                "Cap on state and local tax deduction"
            ]
            
            for reform in reforms:
                fed_key = f"Change in Federal tax liability after {reform}"
                state_key = f"Change in State tax liability after {reform}"
                
                if fed_key in row:
                    fed_change = float(row[fed_key])
                    state_change = float(row[state_key])
                    
                    if abs(fed_change) > 0.01 or abs(state_change) > 0.01:
                        print(f"\n{reform}:")
                        print(f"  Federal tax change: ${fed_change:,.2f}")
                        print(f"  State tax change: ${state_change:,.2f}")
            
            print("\nTotal Changes:")
            print("-" * 30)
            print(f"Total federal tax change: ${float(row['Total change in federal tax liability']):,.2f}")
            print(f"Total state tax change: ${float(row['Total change in state tax liability']):,.2f}")
            print(f"Total net income change: ${float(row['Total change in net income']):,.2f}")
            
            break