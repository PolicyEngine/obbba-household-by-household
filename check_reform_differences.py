#!/usr/bin/env python3
"""
Check if the reforms match between what we're simulating and what was used to generate the data.
"""

import sys
sys.path.append('data')
from reforms import senate_finance_ctc_reform, get_all_senate_finance_reforms

# Show what's in the CTC reform
ctc_reform = senate_finance_ctc_reform()
print("CTC Reform parameters:")
print(ctc_reform.to_dict())

print("\n" + "=" * 60)
print("Order of reforms in get_all_senate_finance_reforms:")
all_reforms = get_all_senate_finance_reforms()
for i, (name, reform) in enumerate(all_reforms.items()):
    print(f"{i+1}. {name}")
    if name == "CTC Reform":
        print("   ^ This is what affects household 4428")

print("\n" + "=" * 60)
print("The data generation script applies these reforms CUMULATIVELY")
print("So the CTC Reform is applied on top of:")
print("- Tax Rate Reform")
print("- Standard Deduction Reform") 
print("- Exemption Reform")
print("\nThis cumulative application might create interactions that don't")
print("exist when applying the CTC reform in isolation.")