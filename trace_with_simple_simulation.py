#!/usr/bin/env python3
"""
Simplified tracing of how federal CTC affects MA state taxes.
"""

import sys
sys.path.append('data')

# Try a different approach - analyze the data we already have
import csv
import json

# First, let's look at all the reforms and their impacts on household 4428
with open('static/household_tax_income_changes_senate_current_law_baseline.csv', 'r') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if row['Household ID'] == '4428':
            print("Analyzing Household 4428 - Full Reform Impacts")
            print("=" * 60)
            
            # Get all reform columns
            reform_impacts = {}
            for col in row.keys():
                if "Change in" in col and "after" in col:
                    reform_impacts[col] = float(row[col])
            
            # Group by reform
            reforms_by_name = {}
            for col, value in reform_impacts.items():
                if abs(value) > 0.01:  # Only non-zero changes
                    # Extract reform name
                    parts = col.split(" after ")
                    if len(parts) == 2:
                        metric = parts[0]
                        reform = parts[1]
                        
                        if reform not in reforms_by_name:
                            reforms_by_name[reform] = {}
                        
                        reforms_by_name[reform][metric] = value
            
            # Focus on CTC expansion
            ctc_expansion = reforms_by_name.get("Child tax credit expansion", {})
            
            print("\nChild Tax Credit Expansion impacts:")
            for metric, value in ctc_expansion.items():
                print(f"  {metric}: ${value:,.2f}")
            
            # Now let's think about what could cause this
            print("\n" + "=" * 60)
            print("ANALYSIS OF MECHANISM:")
            print("=" * 60)
            
            # The only way federal CTC can affect MA state taxes is through:
            # 1. MA EITC (30% of federal EITC)
            # 2. Some other MA credit that uses federal values
            # 3. MA AGI calculation that includes federal adjustments
            
            # Check if it's exactly 30% of something
            state_change = ctc_expansion.get("Change in State tax liability", 0)
            implied_federal_credit_change = state_change / 0.30
            
            print(f"\nIf this is through MA EITC (30% match):")
            print(f"  State tax change: ${state_change:,.2f}")
            print(f"  Implied federal EITC change: ${implied_federal_credit_change:,.2f}")
            
            # But CTC shouldn't increase EITC...
            print("\nBUT: Federal CTC expansion should NOT increase federal EITC")
            print("In fact, it might DECREASE EITC due to interaction effects")
            
            print("\nPOSSIBLE EXPLANATIONS:")
            print("1. Computational artifact from stacked reforms")
            print("2. Complex interaction through refundable credit calculations")
            print("3. Error in data generation or recording")
            
            # Check if other households show similar patterns
            break

# Now check all MA households with CTC impacts
print("\n" + "=" * 60)
print("ALL MA HOUSEHOLDS WITH CTC STATE TAX IMPACTS:")
print("=" * 60)

ma_ctc_impacts = []
with open('static/household_tax_income_changes_senate_current_law_baseline.csv', 'r') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if row['State'] == 'MA':
            state_ctc_change = float(row['Change in State tax liability after Child tax credit expansion'])
            if abs(state_ctc_change) > 0.01:
                ma_ctc_impacts.append({
                    'id': row['Household ID'],
                    'state_change': state_ctc_change,
                    'federal_change': float(row['Change in Federal tax liability after Child tax credit expansion']),
                    'has_dependents': int(float(row['Number of Dependents'])) > 0,
                    'agi': float(row['Adjusted gross income'])
                })

print(f"Found {len(ma_ctc_impacts)} MA households affected")
for h in ma_ctc_impacts:
    print(f"  Household {h['id']}: State ${h['state_change']:,.2f}, Federal ${h['federal_change']:,.2f}, AGI ${h['agi']:,.0f}")