"""
OBBBA provision reforms for district-level analysis.

These reforms revert parameters from TCJA expiration (obbba_reversal baseline)
back to OBBBA/current law values. Stack these on top of obbba_reversal_reform()
to build up OBBBA impact incrementally.

2026 values are audited against PolicyEngine 4.4.4 current law, with statutory
effective windows from Public Law 119-21 where relevant. PolicyEngine-US
previously carried many of these as gov.contrib.reconciliation reforms before
moving them into current policy.

Usage:
    baseline = obbba_reversal_reform()  # TCJA expiration
    reforms = get_obbba_provisions()     # Stack these to get back to OBBBA
"""

from policyengine_core.reforms import Reform


OBBBA_SNAP_ELIGIBLE_IMMIGRATION_STATUSES = [
    "CITIZEN",
    "LEGAL_PERMANENT_RESIDENT",
    "CUBAN_HAITIAN_ENTRANT",
]

OBBBA_ACA_INELIGIBLE_IMMIGRATION_STATUSES = [
    "DACA",
    "UNDOCUMENTED",
    "TPS",
    "REFUGEE",
    "ASYLEE",
    "DEPORTATION_WITHHELD",
    "PAROLED_ONE_YEAR",
]


def obbba_tax_rate_reform():
    """
    OBBBA tax rate provisions.
    Reverts rates AND thresholds from TCJA expiration back to TCJA/OBBBA values.
    """
    return Reform.from_dict({
        # Tax rates
        "gov.irs.income.bracket.rates.2": {"2026-01-01.2100-12-31": 0.12},
        "gov.irs.income.bracket.rates.3": {"2026-01-01.2100-12-31": 0.22},
        "gov.irs.income.bracket.rates.4": {"2026-01-01.2100-12-31": 0.24},
        "gov.irs.income.bracket.rates.5": {"2026-01-01.2100-12-31": 0.32},
        "gov.irs.income.bracket.rates.7": {"2026-01-01.2100-12-31": 0.37},
        # Bracket thresholds - JOINT (from PolicyEngine 2026 defaults)
        "gov.irs.income.bracket.thresholds.1.JOINT": {"2026-01-01.2026-12-31": 24800},
        "gov.irs.income.bracket.thresholds.2.JOINT": {"2026-01-01.2026-12-31": 100800},
        "gov.irs.income.bracket.thresholds.3.JOINT": {"2026-01-01.2026-12-31": 211400},
        "gov.irs.income.bracket.thresholds.4.JOINT": {"2026-01-01.2026-12-31": 403550},
        "gov.irs.income.bracket.thresholds.5.JOINT": {"2026-01-01.2026-12-31": 512450},
        "gov.irs.income.bracket.thresholds.6.JOINT": {"2026-01-01.2026-12-31": 768700},
        # Bracket thresholds - SINGLE
        "gov.irs.income.bracket.thresholds.1.SINGLE": {"2026-01-01.2026-12-31": 12400},
        "gov.irs.income.bracket.thresholds.2.SINGLE": {"2026-01-01.2026-12-31": 50400},
        "gov.irs.income.bracket.thresholds.3.SINGLE": {"2026-01-01.2026-12-31": 105700},
        "gov.irs.income.bracket.thresholds.4.SINGLE": {"2026-01-01.2026-12-31": 201775},
        "gov.irs.income.bracket.thresholds.5.SINGLE": {"2026-01-01.2026-12-31": 256225},
        "gov.irs.income.bracket.thresholds.6.SINGLE": {"2026-01-01.2026-12-31": 640600},
        # Bracket thresholds - SEPARATE
        "gov.irs.income.bracket.thresholds.1.SEPARATE": {"2026-01-01.2026-12-31": 12400},
        "gov.irs.income.bracket.thresholds.2.SEPARATE": {"2026-01-01.2026-12-31": 50400},
        "gov.irs.income.bracket.thresholds.3.SEPARATE": {"2026-01-01.2026-12-31": 105700},
        "gov.irs.income.bracket.thresholds.4.SEPARATE": {"2026-01-01.2026-12-31": 201775},
        "gov.irs.income.bracket.thresholds.5.SEPARATE": {"2026-01-01.2026-12-31": 256225},
        "gov.irs.income.bracket.thresholds.6.SEPARATE": {"2026-01-01.2026-12-31": 384350},
        # Bracket thresholds - HEAD_OF_HOUSEHOLD
        "gov.irs.income.bracket.thresholds.1.HEAD_OF_HOUSEHOLD": {"2026-01-01.2026-12-31": 17700},
        "gov.irs.income.bracket.thresholds.2.HEAD_OF_HOUSEHOLD": {"2026-01-01.2026-12-31": 67450},
        "gov.irs.income.bracket.thresholds.3.HEAD_OF_HOUSEHOLD": {"2026-01-01.2026-12-31": 105700},
        "gov.irs.income.bracket.thresholds.4.HEAD_OF_HOUSEHOLD": {"2026-01-01.2026-12-31": 201750},
        "gov.irs.income.bracket.thresholds.5.HEAD_OF_HOUSEHOLD": {"2026-01-01.2026-12-31": 256200},
        "gov.irs.income.bracket.thresholds.6.HEAD_OF_HOUSEHOLD": {"2026-01-01.2026-12-31": 640600},
        # Bracket thresholds - SURVIVING_SPOUSE
        "gov.irs.income.bracket.thresholds.1.SURVIVING_SPOUSE": {"2026-01-01.2026-12-31": 24800},
        "gov.irs.income.bracket.thresholds.2.SURVIVING_SPOUSE": {"2026-01-01.2026-12-31": 100800},
        "gov.irs.income.bracket.thresholds.3.SURVIVING_SPOUSE": {"2026-01-01.2026-12-31": 211400},
        "gov.irs.income.bracket.thresholds.4.SURVIVING_SPOUSE": {"2026-01-01.2026-12-31": 403550},
        "gov.irs.income.bracket.thresholds.5.SURVIVING_SPOUSE": {"2026-01-01.2026-12-31": 512450},
        "gov.irs.income.bracket.thresholds.6.SURVIVING_SPOUSE": {"2026-01-01.2026-12-31": 768700},
    }, country_id="us")


def obbba_standard_deduction_reform():
    """
    OBBBA standard deduction provisions.
    Reverts to higher TCJA/OBBBA standard deduction amounts.
    """
    return Reform.from_dict({
        "gov.irs.deductions.standard.amount.JOINT": {
            "2026-01-01.2026-12-31": 32200,
        },
        "gov.irs.deductions.standard.amount.SINGLE": {
            "2026-01-01.2026-12-31": 16100,
        },
        "gov.irs.deductions.standard.amount.SEPARATE": {
            "2026-01-01.2026-12-31": 16100,
        },
        "gov.irs.deductions.standard.amount.HEAD_OF_HOUSEHOLD": {
            "2026-01-01.2026-12-31": 24150,
        },
        "gov.irs.deductions.standard.amount.SURVIVING_SPOUSE": {
            "2026-01-01.2026-12-31": 32200,
        },
    }, country_id="us")


def obbba_exemption_reform():
    """
    OBBBA personal exemption provisions.
    Suspends personal exemptions while preserving the statutory amount.
    """
    return Reform.from_dict({
        "gov.irs.income.exemption.suspended": {"2026-01-01.2100-12-31": True},
    }, country_id="us")


def obbba_ctc_ssn_reform():
    """
    OBBBA Child Tax Credit SSN requirement.
    Requires valid SSN for CTC eligibility.
    """
    return Reform.from_dict({
        "gov.irs.credits.ctc.adult_ssn_requirement_applies": {
            "2026-01-01.2100-12-31": True
        },
    }, country_id="us")


def obbba_ctc_expansion_reform():
    """
    OBBBA Child Tax Credit expansion provisions.
    Increased CTC amount, higher phase-out thresholds, adult dependent credit.
    """
    return Reform.from_dict({
        "gov.irs.credits.ctc.amount.base[0].amount": {
            "2025-01-01.2026-12-31": 2200,
            "2027-01-01.2028-12-31": 2300,
            "2029-01-01.2030-12-31": 2400,
            "2031-01-01.2032-12-31": 2500,
            "2033-01-01.2034-12-31": 2600,
            "2035-01-01.2100-12-31": 2700,
        },
        "gov.irs.credits.ctc.amount.adult_dependent": {
            "2026-01-01.2100-12-31": 500
        },
        "gov.irs.credits.ctc.phase_out.threshold.JOINT": {
            "2026-01-01.2100-12-31": 400000
        },
        "gov.irs.credits.ctc.phase_out.threshold.SINGLE": {
            "2026-01-01.2100-12-31": 200000
        },
        "gov.irs.credits.ctc.phase_out.threshold.SEPARATE": {
            "2026-01-01.2100-12-31": 200000
        },
        "gov.irs.credits.ctc.phase_out.threshold.HEAD_OF_HOUSEHOLD": {
            "2026-01-01.2100-12-31": 200000
        },
        "gov.irs.credits.ctc.phase_out.threshold.SURVIVING_SPOUSE": {
            "2026-01-01.2100-12-31": 400000
        },
        "gov.irs.credits.ctc.refundable.individual_max": {
            "2026-01-01.2026-12-31": 1700,
            "2027-01-01.2028-12-31": 1800,
            "2029-01-01.2031-12-31": 1900,
            "2032-01-01.2033-12-31": 2000,
            "2034-01-01.2100-12-31": 2100,
        },
        "gov.irs.credits.ctc.refundable.phase_in.threshold": {
            "2026-01-01.2100-12-31": 2500
        },
    }, country_id="us")


def obbba_cdcc_reform():
    """
    OBBBA Child and Dependent Care Credit provisions.
    Reverts to OBBBA CDCC values.
    """
    return Reform.from_dict({
        "gov.irs.credits.cdcc.phase_out.max": {
            "2026-01-01.2100-12-31": 0.5
        },
        "gov.irs.credits.cdcc.phase_out.min": {
            "2026-01-01.2100-12-31": 0.35
        },
        "gov.irs.credits.cdcc.phase_out.amended_structure.applies": {
            "2026-01-01.2100-12-31": True
        },
    }, country_id="us")


def obbba_qbi_reform():
    """
    OBBBA Qualified Business Income Deduction provisions.
    Reverts to TCJA/OBBBA QBI deduction including phase-out lengths and floor.
    """
    return Reform.from_dict({
        "gov.irs.deductions.qbi.max.rate": {"2026-01-01.2100-12-31": 0.2},
        "gov.irs.deductions.qbi.max.w2_wages.rate": {"2026-01-01.2100-12-31": 0.5},
        "gov.irs.deductions.qbi.max.w2_wages.alt_rate": {"2026-01-01.2100-12-31": 0.25},
        "gov.irs.deductions.qbi.max.business_property.rate": {"2026-01-01.2100-12-31": 0.025},
        "gov.irs.deductions.qbi.phase_out.length.JOINT": {"2026-01-01.2100-12-31": 150000},
        "gov.irs.deductions.qbi.phase_out.length.SINGLE": {"2026-01-01.2100-12-31": 75000},
        "gov.irs.deductions.qbi.phase_out.length.SEPARATE": {"2026-01-01.2100-12-31": 75000},
        "gov.irs.deductions.qbi.phase_out.length.HEAD_OF_HOUSEHOLD": {"2026-01-01.2100-12-31": 75000},
        "gov.irs.deductions.qbi.phase_out.length.SURVIVING_SPOUSE": {"2026-01-01.2100-12-31": 150000},
        # QBI deduction floor (OBBBA provision)
        "gov.irs.deductions.qbi.deduction_floor.in_effect": {"2026-01-01.2100-12-31": True},
        "gov.irs.deductions.qbi.deduction_floor.amount[1].amount": {"2026-01-01.2100-12-31": 400},
    }, country_id="us")


def obbba_amt_reform():
    """
    OBBBA Alternative Minimum Tax provisions.
    Reverts to higher TCJA/OBBBA AMT exemptions.
    """
    return Reform.from_dict({
        "gov.irs.income.amt.exemption.amount.JOINT": {
            "2026-01-01.2026-12-31": 140200,
        },
        "gov.irs.income.amt.exemption.amount.SINGLE": {
            "2026-01-01.2026-12-31": 90100,
        },
        "gov.irs.income.amt.exemption.amount.SEPARATE": {
            "2026-01-01.2026-12-31": 70100,
        },
        "gov.irs.income.amt.exemption.amount.HEAD_OF_HOUSEHOLD": {
            "2026-01-01.2026-12-31": 90100,
        },
        "gov.irs.income.amt.exemption.amount.SURVIVING_SPOUSE": {
            "2026-01-01.2026-12-31": 140200,
        },
        "gov.irs.income.amt.exemption.phase_out.start.JOINT": {
            "2026-01-01.2026-12-31": 1000000,
        },
        "gov.irs.income.amt.exemption.phase_out.start.SINGLE": {
            "2026-01-01.2026-12-31": 500000,
        },
        "gov.irs.income.amt.exemption.phase_out.start.SEPARATE": {
            "2026-01-01.2026-12-31": 500000,
        },
        "gov.irs.income.amt.exemption.phase_out.start.HEAD_OF_HOUSEHOLD": {
            "2026-01-01.2026-12-31": 500000,
        },
        "gov.irs.income.amt.exemption.phase_out.start.SURVIVING_SPOUSE": {
            "2026-01-01.2026-12-31": 1000000,
        },
        "gov.irs.income.amt.exemption.phase_out.rate": {
            "2026-01-01.2100-12-31": 0.5,
        },
    }, country_id="us")


def obbba_salt_reform():
    """
    OBBBA SALT cap provisions.
    Reverts to OBBBA SALT cap (higher than TCJA $10K) with phase-out.
    """
    return Reform.from_dict({
        "gov.irs.deductions.itemized.salt_and_real_estate.cap.JOINT": {
            "2026-01-01.2026-12-31": 40400
        },
        "gov.irs.deductions.itemized.salt_and_real_estate.cap.SINGLE": {
            "2026-01-01.2026-12-31": 40400
        },
        "gov.irs.deductions.itemized.salt_and_real_estate.cap.SEPARATE": {
            "2026-01-01.2026-12-31": 20200
        },
        "gov.irs.deductions.itemized.salt_and_real_estate.cap.HEAD_OF_HOUSEHOLD": {
            "2026-01-01.2026-12-31": 40400
        },
        "gov.irs.deductions.itemized.salt_and_real_estate.cap.SURVIVING_SPOUSE": {
            "2026-01-01.2026-12-31": 40400
        },
        # SALT phase-out parameters (OBBBA provision)
        "gov.irs.deductions.itemized.salt_and_real_estate.phase_out.in_effect": {
            "2026-01-01.2100-12-31": True
        },
        "gov.irs.deductions.itemized.salt_and_real_estate.phase_out.floor.applies": {
            "2026-01-01.2100-12-31": True
        },
    }, country_id="us")


def obbba_tip_income_reform():
    """
    OBBBA tip income exemption.
    Sets tip income deduction cap (new OBBBA provision).
    """
    return Reform.from_dict({
        "gov.irs.deductions.tip_income.cap": {
            "2025-01-01.2028-12-31": 25000
        },
    }, country_id="us")


def obbba_overtime_reform():
    """
    OBBBA overtime income exemption.
    Sets overtime income deduction cap (new OBBBA provision).
    """
    return Reform.from_dict({
        "gov.irs.deductions.overtime_income.cap.JOINT": {
            "2025-01-01.2028-12-31": 25000
        },
        "gov.irs.deductions.overtime_income.cap.SINGLE": {
            "2025-01-01.2028-12-31": 12500
        },
        "gov.irs.deductions.overtime_income.cap.SEPARATE": {
            "2025-01-01.2028-12-31": 12500
        },
        "gov.irs.deductions.overtime_income.cap.HEAD_OF_HOUSEHOLD": {
            "2025-01-01.2028-12-31": 12500
        },
        "gov.irs.deductions.overtime_income.cap.SURVIVING_SPOUSE": {
            "2025-01-01.2028-12-31": 12500
        },
    }, country_id="us")


def obbba_senior_deduction_reform():
    """
    OBBBA senior standard deduction addition.
    Sets additional senior deduction (new OBBBA provision).
    """
    return Reform.from_dict({
        "gov.irs.deductions.senior_deduction.amount": {
            "2025-01-01.2028-12-31": 6000
        },
    }, country_id="us")


def obbba_auto_loan_reform():
    """
    OBBBA auto loan interest deduction.
    Sets auto loan interest deduction cap (new OBBBA provision).
    """
    return Reform.from_dict({
        "gov.irs.deductions.auto_loan_interest.cap": {
            "2025-01-01.2028-12-31": 10000
        },
    }, country_id="us")


def obbba_misc_reform():
    """
    OBBBA miscellaneous itemized deductions.
    Disables misc itemized deductions (TCJA/OBBBA provision).
    """
    return Reform.from_dict({
        "gov.irs.deductions.itemized.misc.applies": {
            "2026-01-01.2100-12-31": False
        },
    }, country_id="us")


def obbba_casualty_reform():
    """
    OBBBA casualty loss deduction repeal.
    Disables casualty deductions (TCJA/OBBBA provision).
    """
    return Reform.from_dict({
        "gov.irs.deductions.itemized.casualty.active": {
            "2026-01-01.2100-12-31": False
        },
    }, country_id="us")


def obbba_other_item_reform():
    """
    OBBBA other itemized deduction provisions.
    Mortgage interest cap and charity deductions for non-itemizers (all filing statuses).
    """
    return Reform.from_dict({
        "gov.irs.deductions.itemized.interest.mortgage.cap.JOINT": {
            "2026-01-01.2100-12-31": 750000
        },
        "gov.irs.deductions.itemized.interest.mortgage.cap.SINGLE": {
            "2026-01-01.2100-12-31": 750000
        },
        "gov.irs.deductions.itemized.interest.mortgage.cap.SEPARATE": {
            "2026-01-01.2100-12-31": 375000
        },
        "gov.irs.deductions.itemized.interest.mortgage.cap.SURVIVING_SPOUSE": {
            "2026-01-01.2100-12-31": 750000
        },
        "gov.irs.deductions.itemized.interest.mortgage.cap.HEAD_OF_HOUSEHOLD": {
            "2026-01-01.2100-12-31": 750000
        },
        # Charity non-itemizers - all filing statuses (OBBBA provision: $2,000/$1,000)
        "gov.irs.deductions.itemized.charity.non_itemizers_amount.JOINT": {
            "2026-01-01.2100-12-31": 2000
        },
        "gov.irs.deductions.itemized.charity.non_itemizers_amount.SINGLE": {
            "2026-01-01.2100-12-31": 1000
        },
        "gov.irs.deductions.itemized.charity.non_itemizers_amount.SEPARATE": {
            "2026-01-01.2100-12-31": 1000
        },
        "gov.irs.deductions.itemized.charity.non_itemizers_amount.HEAD_OF_HOUSEHOLD": {
            "2026-01-01.2100-12-31": 1000
        },
        "gov.irs.deductions.itemized.charity.non_itemizers_amount.SURVIVING_SPOUSE": {
            "2026-01-01.2100-12-31": 1000
        },
        "gov.irs.deductions.itemized.charity.floor.applies": {
            "2026-01-01.2100-12-31": True
        },
    }, country_id="us")


def obbba_limitation_on_itemized_reform():
    """
    OBBBA limitation on itemized deductions.
    Restores the OBBB itemized deduction limitation structure.
    """
    return Reform.from_dict({
        "gov.irs.deductions.itemized.limitation.applies": {
            "2026-01-01.2100-12-31": True
        },
        "gov.irs.deductions.itemized.limitation.obbb.applies": {
            "2026-01-01.2100-12-31": True
        },
    }, country_id="us")


def obbba_estate_tax_reform():
    """
    OBBBA estate tax provisions.
    Sets estate tax base to $15M (OBBBA provision).
    """
    return Reform.from_dict({
        "gov.irs.credits.estate.base": {
            "2026-01-01.2026-12-31": 15000000,
        },
    }, country_id="us")


def obbba_snap_immigration_reform():
    """
    OBBBA SNAP immigration eligibility restrictions.
    """
    return Reform.from_dict({
        "gov.usda.snap.eligibility.eligible_immigration_statuses": {
            "2025-07-01.2100-12-31": OBBBA_SNAP_ELIGIBLE_IMMIGRATION_STATUSES
        },
    }, country_id="us")


def obbba_snap_abawd_reform():
    """
    OBBBA SNAP ABAWD work requirement changes.
    """
    return Reform.from_dict({
        "gov.usda.snap.work_requirements.abawd.in_effect": {
            "2025-07-04.2100-12-31": True
        },
        "gov.states.ca.cdss.snap.work_requirements.abawd.hr1_in_effect": {
            "2026-06-01.2100-12-31": True
        },
    }, country_id="us")


def obbba_medicaid_immigration_reform():
    """
    OBBBA Medicaid immigration eligibility restrictions.
    """
    return Reform.from_dict({
        "gov.hhs.medicaid.eligibility.eligible_immigration_statuses": {
            "2026-10-01.2100-12-31": OBBBA_SNAP_ELIGIBLE_IMMIGRATION_STATUSES
        },
    }, country_id="us")


def obbba_medicaid_work_requirement_reform():
    """
    OBBBA Medicaid work requirement.
    """
    return Reform.from_dict({
        "gov.hhs.medicaid.eligibility.work_requirements.applies": {
            "2027-01-01.2100-12-31": True
        },
    }, country_id="us")


def obbba_aca_immigration_reform():
    """
    OBBBA ACA premium tax credit immigration eligibility restrictions.
    """
    return Reform.from_dict({
        "gov.aca.ineligible_immigration_statuses": {
            "2027-01-01.2100-12-31": OBBBA_ACA_INELIGIBLE_IMMIGRATION_STATUSES
        },
    }, country_id="us")


def get_obbba_provisions():
    """
    Get dictionary of all OBBBA provision reforms.
    Stack these on top of obbba_reversal_reform() baseline.

    This matches get_all_reforms() in reforms.py for consistency with national analysis.
    Includes all parameters needed to restore OBBBA from TCJA expiration baseline.
    """
    return {
        "Tax Rate Reform": obbba_tax_rate_reform(),
        "Standard Deduction Reform": obbba_standard_deduction_reform(),
        "Exemption Reform": obbba_exemption_reform(),
        "CTC SSN Requirement": obbba_ctc_ssn_reform(),
        "CTC Expansion": obbba_ctc_expansion_reform(),
        "CDCC Reform": obbba_cdcc_reform(),
        "QBI Deduction Reform": obbba_qbi_reform(),
        "AMT Reform": obbba_amt_reform(),
        "Miscellaneous Reform": obbba_misc_reform(),
        "Casualty Loss Repeal": obbba_casualty_reform(),
        "Other Itemized Deductions Reform": obbba_other_item_reform(),
        "Limitation on Itemized Deductions Reform": obbba_limitation_on_itemized_reform(),
        "Estate Tax Reform": obbba_estate_tax_reform(),
        "SALT Cap Reform": obbba_salt_reform(),
        "Tip Income Exemption": obbba_tip_income_reform(),
        "Overtime Exemption": obbba_overtime_reform(),
        "Senior Deduction": obbba_senior_deduction_reform(),
        "Auto Loan Interest": obbba_auto_loan_reform(),
        "SNAP Immigration Eligibility": obbba_snap_immigration_reform(),
        "SNAP ABAWD Work Requirements": obbba_snap_abawd_reform(),
        "Medicaid Immigration Eligibility": obbba_medicaid_immigration_reform(),
        "Medicaid Work Requirements": obbba_medicaid_work_requirement_reform(),
        "ACA Immigration Eligibility": obbba_aca_immigration_reform(),
    }
