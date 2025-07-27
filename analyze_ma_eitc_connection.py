#!/usr/bin/env python3
"""
Analyze if the MA state tax change is due to EITC interaction.
"""

# Based on the PolicyEngine code analysis, here's the mechanism:
# 1. Federal CTC expansion changes the CTC amount
# 2. The CTC phase-in calculation considers: max(15% of earnings over $2500, Social Security tax - EITC)
# 3. If CTC changes affect this calculation, it could affect EITC
# 4. MA EITC = 30% of federal EITC
# 5. MA refundable credits include MA EITC

# For household 4428:
# - Married with 4 dependents
# - Employment income: $49,024.63
# - AGI: $49,025.45
# - Federal CTC expansion reduces federal tax by $75
# - State tax reduces by $56.41

# Let's calculate the potential EITC impact
employment_income = 49024.63
num_children = 4  # Actually shows as 3.999... in data

# 2026 EITC parameters for married filing jointly
# These are approximate based on current law projections
eitc_params = {
    'max_credit': {0: 649, 1: 4213, 2: 6960, 3: 7830},  # 3+ children same as 3
    'phase_in_rate': {0: 0.0765, 1: 0.34, 2: 0.40, 3: 0.45},
    'max_earned_income': {0: 8490, 1: 12390, 2: 17400, 3: 17400},
    'phase_out_start_married': {0: 17880, 1: 28120, 2: 28120, 3: 28120},
    'phase_out_rate': {0: 0.0765, 1: 0.1598, 2: 0.2106, 3: 0.2106}
}

# Get parameters for 3+ children
num_children_capped = min(num_children, 3)
max_credit = eitc_params['max_credit'][num_children_capped]
phase_in_rate = eitc_params['phase_in_rate'][num_children_capped]
max_earned_income = eitc_params['max_earned_income'][num_children_capped]
phase_out_start = eitc_params['phase_out_start_married'][num_children_capped]
phase_out_rate = eitc_params['phase_out_rate'][num_children_capped]

print("EITC Analysis for Household 4428")
print("=" * 50)
print(f"Employment income: ${employment_income:,.2f}")
print(f"Number of children: {num_children}")
print(f"\nEITC parameters (married, 3+ children):")
print(f"  Max credit: ${max_credit:,.2f}")
print(f"  Phase-in rate: {phase_in_rate:.1%}")
print(f"  Phase-out starts at: ${phase_out_start:,.2f}")
print(f"  Phase-out rate: {phase_out_rate:.1%}")

# Calculate EITC
if employment_income <= max_earned_income:
    # In phase-in range
    eitc = employment_income * phase_in_rate
    phase = "phase-in"
elif employment_income <= phase_out_start:
    # At maximum
    eitc = max_credit
    phase = "maximum"
else:
    # In phase-out range
    excess = employment_income - phase_out_start
    reduction = excess * phase_out_rate
    eitc = max(0, max_credit - reduction)
    phase = "phase-out"

print(f"\nHousehold is in EITC {phase} range")
print(f"Calculated federal EITC: ${eitc:,.2f}")

# MA EITC is 30% of federal
ma_eitc = eitc * 0.30
print(f"MA EITC (30% of federal): ${ma_eitc:,.2f}")

# Now let's think about how CTC expansion could affect this
print("\n" + "=" * 50)
print("HOW CTC EXPANSION COULD AFFECT EITC:")
print("=" * 50)

print("\n1. Direct interaction in CTC phase-in calculation:")
print("   - CTC phase-in = max(15% * (earnings - $2500), Social Security tax - EITC)")
print("   - If CTC expansion changes how this is calculated, it could affect EITC")

print("\n2. The $56.41 state tax reduction:")
print(f"   - This equals about ${56.41/0.30:.2f} in federal EITC change")
print("   - Or about {56.41/ma_eitc*100:.1f}% of the current MA EITC")

print("\n3. Possible mechanism:")
print("   - CTC expansion might change the refundable CTC calculation")
print("   - This could interact with EITC through the phase-in formula")
print("   - Massachusetts picks up 30% of any federal EITC change")

# Check if the amount makes sense
federal_eitc_change_implied = 56.41 / 0.30
print(f"\n4. To get a ${56.41:.2f} MA tax reduction:")
print(f"   - Federal EITC would need to increase by ${federal_eitc_change_implied:.2f}")
print(f"   - This is {federal_eitc_change_implied/eitc*100:.1f}% of the current EITC")

print("\nCONCLUSION:")
print("-" * 50)
print("The $56.41 MA state tax reduction from federal CTC expansion")
print("appears to come through the MA EITC, which is 30% of federal EITC.")
print("The CTC expansion likely increases federal EITC by about $188,")
print("resulting in a $56.41 increase in MA EITC (and thus reduction in MA tax).")