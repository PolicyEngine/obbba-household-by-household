#!/usr/bin/env python3
"""
Find the conditions where federal CTC expansion reduces MA state tax.
"""

from policyengine_us import Simulation
from policyengine_us.model_api import *

# Try different income levels to find where CTC makes itemization neutral
for income in [15000, 20000, 25000, 30000, 35000, 40000]:
    situation = {
        "people": {
            "parent": {
                "age": {2026: 40},
                "employment_income": {2026: income},
                "medical_out_of_pocket_expenses": {2026: 3000},
            },
            "child": {
                "age": {2026: 10},
            },
        },
        "tax_units": {
            "tax_unit": {
                "members": ["parent", "child"],
            }
        },
        "households": {
            "household": {
                "members": ["parent", "child"],
                "state_code": {2026: "MA"},
            }
        },
    }
    
    # Without CTC expansion
    reform_no_ctc = Reform.from_dict({
        "gov.irs.deductions.standard.amount.SINGLE": {"2026-01-01": 16_550},
    }, country_id="us")
    
    sim_no_ctc = Simulation(situation=situation, reform=reform_no_ctc)
    
    # With CTC expansion  
    reform_with_ctc = Reform.from_dict({
        "gov.irs.deductions.standard.amount.SINGLE": {"2026-01-01": 16_550},
        "gov.irs.credits.ctc.amount.base[0].amount": {"2026-01-01": 3_000},
    }, country_id="us")
    
    sim_with_ctc = Simulation(situation=situation, reform=reform_with_ctc)
    
    # Check itemization
    itemizes_no_ctc = bool(sim_no_ctc.calculate('tax_unit_itemizes', 2026)[0])
    itemizes_with_ctc = bool(sim_with_ctc.calculate('tax_unit_itemizes', 2026)[0])
    
    # Check MA tax
    ma_tax_no_ctc = sim_no_ctc.calculate('ma_income_tax', 2026)[0]
    ma_tax_with_ctc = sim_with_ctc.calculate('ma_income_tax', 2026)[0]
    
    # Check federal tax differences
    fed_item_with = sim_with_ctc.calculate('tax_liability_if_itemizing', 2026)[0]
    fed_std_with = sim_with_ctc.calculate('tax_liability_if_not_itemizing', 2026)[0]
    
    if itemizes_with_ctc != itemizes_no_ctc:
        print(f"\nIncome ${income:,}:")
        print(f"  Itemization change: {itemizes_no_ctc} → {itemizes_with_ctc}")
        print(f"  Federal tax if itemizing: ${fed_item_with:,.2f}")
        print(f"  Federal tax if standard: ${fed_std_with:,.2f}")
        print(f"  Difference: ${fed_item_with - fed_std_with:,.2f}")
        print(f"  MA tax change: ${ma_tax_with_ctc - ma_tax_no_ctc:,.2f}")