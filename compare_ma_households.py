#!/usr/bin/env python3
"""
Compare the two MA households affected by CTC expansion.
"""

import csv

with open('static/household_tax_income_changes_senate_current_law_baseline.csv', 'r') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if row['Household ID'] in ['4428', '93476']:
            print(f"\nHousehold {row['Household ID']}:")
            print(f"  State: {row['State']}")
            print(f"  AGI: ${float(row['Adjusted gross income']):,.2f}")
            print(f"  Employment income: ${float(row['Employment income']):,.2f}")
            print(f"  Self-employment income: ${float(row['Self-employment income']):,.2f}")
            print(f"  Number of dependents: {row['Number of Dependents']}")
            print(f"  Married: {row['Is Married']}")
            print(f"  Fed CTC expansion change: ${float(row['Change in Federal tax liability after Child tax credit expansion']):,.2f}")
            print(f"  State CTC expansion change: ${float(row['Change in State tax liability after Child tax credit expansion']):,.2f}")
            
            # Check if it's related to EITC
            print(f"\n  Income components that might affect EITC:")
            print(f"    Capital gains: ${float(row['Capital gains']):,.2f}")
            print(f"    Investment income: ${float(row['Taxable interest income']) + float(row['Dividend income']):,.2f}")
            
            print(f"\n  Other significant changes:")
            for reform in ['Standard deduction increase', 'Exemption repeal', 'Cap on state and local tax deduction']:
                fed_key = f'Change in Federal tax liability after {reform}'
                state_key = f'Change in State tax liability after {reform}'
                if fed_key in row:
                    fed = float(row[fed_key])
                    state = float(row[state_key])
                    if abs(fed) > 0.01 or abs(state) > 0.01:
                        print(f"    {reform}: Fed ${fed:,.2f}, State ${state:,.2f}")