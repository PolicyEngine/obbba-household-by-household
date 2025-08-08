import csv

with open('static/household_tax_income_changes_senate_current_law_baseline.csv', 'r') as f:
    reader = csv.DictReader(f)
    count = 0
    found_households = []
    
    for row in reader:
        ctc_ssn_state = float(row['Change in State tax liability after Child tax credit social security number requirement'])
        ctc_exp_state = float(row['Change in State tax liability after Child tax credit expansion'])
        
        if ctc_ssn_state != 0 or ctc_exp_state != 0:
            household_info = {
                'id': row['Household ID'],
                'state': row['State'],
                'ctc_ssn_state_change': ctc_ssn_state,
                'ctc_exp_state_change': ctc_exp_state,
                'agi': float(row['Adjusted gross income']),
                'num_dependents': int(float(row['Number of Dependents'])),
                'married': row['Is Married'] == 'True',
                'total_state_change': float(row['Total change in state tax liability'])
            }
            found_households.append(household_info)
            count += 1
            
            if count >= 20:
                break
    
    print(f"Found {count} households with state tax changes from CTC policies:\n")
    
    for h in found_households:
        print(f"Household {h['id']} ({h['state']}):")
        print(f"  - Number of dependents: {h['num_dependents']}")
        print(f"  - Married: {h['married']}")
        print(f"  - AGI: ${h['agi']:,.2f}")
        print(f"  - CTC SSN requirement state tax change: ${h['ctc_ssn_state_change']:,.2f}")
        print(f"  - CTC expansion state tax change: ${h['ctc_exp_state_change']:,.2f}")
        print(f"  - Total state tax change: ${h['total_state_change']:,.2f}")
        print()