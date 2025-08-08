#!/usr/bin/env python3
"""
Find what causes the $56.41 MA state tax change for household 4428.
"""

import csv
import json

# First, let's analyze all households with MA state tax changes from CTC expansion
households_with_ma_ctc_impact = []

with open('static/household_tax_income_changes_senate_current_law_baseline.csv', 'r') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        state = row['State']
        ctc_state_change = float(row['Change in State tax liability after Child tax credit expansion'])
        
        if state == 'MA' and abs(ctc_state_change) > 0.01:
            households_with_ma_ctc_impact.append({
                'id': row['Household ID'],
                'agi': float(row['Adjusted gross income']),
                'married': row['Is Married'] == 'True',
                'dependents': int(float(row['Number of Dependents'])),
                'employment_income': float(row['Employment income']),
                'federal_ctc_change': float(row['Change in Federal tax liability after Child tax credit expansion']),
                'state_ctc_change': ctc_state_change,
                'total_state_change': float(row['Total change in state tax liability']),
            })

# Sort by state tax change magnitude
households_with_ma_ctc_impact.sort(key=lambda x: abs(x['state_ctc_change']), reverse=True)

print(f"Found {len(households_with_ma_ctc_impact)} Massachusetts households affected by federal CTC expansion")
print("\nTop 10 households by state tax change magnitude:")
print("-" * 80)
print(f"{'ID':>8} {'AGI':>12} {'Married':>8} {'Deps':>5} {'Fed CTC Δ':>12} {'State CTC Δ':>12}")
print("-" * 80)

for h in households_with_ma_ctc_impact[:10]:
    print(f"{h['id']:>8} ${h['agi']:>11,.0f} {str(h['married']):>8} {h['dependents']:>5} "
          f"${h['federal_ctc_change']:>11,.2f} ${h['state_ctc_change']:>11,.2f}")

# Look for patterns
print("\n\nAnalyzing patterns:")
print("-" * 50)

# Check if all affected households have dependents
all_have_deps = all(h['dependents'] > 0 for h in households_with_ma_ctc_impact)
print(f"All affected households have dependents: {all_have_deps}")

# Check AGI ranges
agis = [h['agi'] for h in households_with_ma_ctc_impact]
print(f"AGI range: ${min(agis):,.0f} - ${max(agis):,.0f}")

# Check if there's a correlation between federal and state changes
fed_changes = [h['federal_ctc_change'] for h in households_with_ma_ctc_impact]
state_changes = [h['state_ctc_change'] for h in households_with_ma_ctc_impact]

# Calculate rough correlation direction
positive_correlation = sum(1 for f, s in zip(fed_changes, state_changes) if f * s < 0) # opposite signs
print(f"Cases where federal decrease leads to state decrease: {positive_correlation} out of {len(households_with_ma_ctc_impact)}")

# Save detailed results for household 4428
for h in households_with_ma_ctc_impact:
    if h['id'] == '4428':
        print(f"\n\nHousehold 4428 details:")
        print(json.dumps(h, indent=2))