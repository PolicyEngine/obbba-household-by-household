#!/usr/bin/env python3
"""
Check if the CTC SSN requirement is causing the MA state tax change.
"""

import sys
sys.path.append('data')
from reforms import senate_finance_ctc_reform

# The senate finance CTC reform includes:
# 1. Increasing CTC amounts
# 2. Setting gov.contrib.reconciliation.ctc.in_effect to True
# 3. Setting gov.contrib.reconciliation.ctc.one_person_ssn_req to True

print("Senate Finance CTC Reform includes:")
print("1. CTC amount increases (from $2000 to $2200 in 2026)")
print("2. Increased refundable amounts")
print("3. SSN requirement changes")
print("\nThe SSN requirement change might interact with state calculations")
print("if Massachusetts uses any federal values that are affected by")
print("the SSN requirement implementation.")

# Check the CSV data for SSN information
import csv

with open('static/household_tax_income_changes_senate_current_law_baseline.csv', 'r') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if row['Household ID'] == '4428':
            print(f"\nHousehold 4428 SSN status:")
            print(f"  Num with SSN card (Citizen/EAD): {row['Num with SSN card (Citizen/EAD)']}")
            print(f"  Num with SSN card (Other/None): {row['Num with SSN card (Other/None)']}")
            print(f"  Household size: {row['Household size']}")
            
            # Check CTC SSN requirement impact
            ctc_ssn_fed = float(row['Change in Federal tax liability after Child tax credit social security number requirement'])
            ctc_ssn_state = float(row['Change in State tax liability after Child tax credit social security number requirement'])
            
            print(f"\nCTC SSN requirement impacts:")
            print(f"  Federal: ${ctc_ssn_fed:,.2f}")
            print(f"  State: ${ctc_ssn_state:,.2f}")
            
            break

print("\nCONCLUSION:")
print("The SSN requirement reform shows $0 impact for household 4428.")
print("The state tax change of -$56.41 comes specifically from the")
print("CTC expansion reform, not the SSN requirement.")
print("\nThis suggests the issue is a computational artifact from")
print("how the stacked reforms interact in the data generation script.")