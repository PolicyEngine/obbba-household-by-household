import numpy as np
from policyengine_core.reforms import Reform


def current_law_baseline():
    """
    Returns a baseline with no reforms (current law).
    This represents the default PolicyEngine US baseline for 2026.
    """
    return Reform.from_dict({})


def tcja_reform():

    return Reform.from_dict(
        {
            "gov.irs.income.bracket.rates.2": {"2026-01-01.2100-12-31": 0.12},
            "gov.irs.income.bracket.rates.3": {"2026-01-01.2100-12-31": 0.22},
            "gov.irs.income.bracket.rates.4": {"2026-01-01.2100-12-31": 0.24},
            "gov.irs.income.bracket.rates.5": {"2026-01-01.2100-12-31": 0.32},
            "gov.irs.income.bracket.rates.7": {"2026-01-01.2100-12-31": 0.37},
            "gov.irs.deductions.qbi.max.rate": {"2026-01-01.2100-12-31": 0.2},
            "gov.irs.income.exemption.amount": {"2026-01-01.2100-12-31": 0},
            "gov.irs.deductions.qbi.max.w2_wages.rate": {"2026-01-01.2100-12-31": 0.5},
            "gov.irs.deductions.standard.amount.JOINT": {
                "2026-01-01.2026-12-31": 30300,
            },
            "gov.irs.credits.ctc.amount.base[0].amount": {
                "2026-01-01.2100-12-31": 2000
            },
            "gov.irs.deductions.standard.amount.SINGLE": {
                "2026-01-01.2026-12-31": 15150,
            },
            "gov.irs.income.amt.exemption.amount.JOINT": {
                "2026-01-01.2026-12-31": 139100,
            },
            "gov.irs.income.bracket.thresholds.3.JOINT": {
                "2026-01-01.2026-12-31": 208300,
            },
            "gov.irs.income.bracket.thresholds.4.JOINT": {
                "2026-01-01.2026-12-31": 397650,
            },
            "gov.irs.income.bracket.thresholds.5.JOINT": {
                "2026-01-01.2026-12-31": 512950,
            },
            "gov.irs.income.bracket.thresholds.6.JOINT": {
                "2026-01-01.2026-12-31": 769450,
            },
            "gov.irs.credits.ctc.amount.adult_dependent": {
                "2026-01-01.2100-12-31": 500
            },
            "gov.irs.income.amt.exemption.amount.SINGLE": {
                "2026-01-01.2026-12-31": 89400,
            },
            "gov.irs.income.bracket.thresholds.3.SINGLE": {
                "2026-01-01.2026-12-31": 104900,
            },
            "gov.irs.income.bracket.thresholds.4.SINGLE": {
                "2026-01-01.2026-12-31": 198800,
            },
            "gov.irs.income.bracket.thresholds.5.SINGLE": {
                "2026-01-01.2026-12-31": 256450,
            },
            "gov.irs.income.bracket.thresholds.6.SINGLE": {
                "2026-01-01.2026-12-31": 641200,
            },
            "gov.irs.deductions.itemized.casualty.active": {
                "2026-01-01.2100-12-31": False
            },
            "gov.irs.deductions.standard.amount.SEPARATE": {
                "2026-01-01.2026-12-31": 15150,
            },
            "gov.irs.deductions.qbi.max.w2_wages.alt_rate": {
                "2026-01-01.2100-12-31": 0.25
            },
            "gov.irs.deductions.qbi.phase_out.start.JOINT": {
                "2026-01-01.2026-12-31": 409800,
            },
            "gov.irs.income.amt.exemption.amount.SEPARATE": {
                "2026-01-01.2026-12-31": 69500,
            },
            "gov.irs.income.bracket.thresholds.3.SEPARATE": {
                "2026-01-01.2026-12-31": 104900,
            },
            "gov.irs.income.bracket.thresholds.4.SEPARATE": {
                "2026-01-01.2026-12-31": 198800,
            },
            "gov.irs.income.bracket.thresholds.5.SEPARATE": {
                "2026-01-01.2026-12-31": 256450,
            },
            "gov.irs.income.bracket.thresholds.6.SEPARATE": {
                "2026-01-01.2026-12-31": 384700,
            },
            "gov.irs.credits.ctc.phase_out.threshold.JOINT": {
                "2026-01-01.2100-12-31": 400000
            },
            "gov.irs.credits.ctc.refundable.individual_max": {
                "2026-01-01.2026-12-31": 1800,
            },
            "gov.irs.deductions.qbi.phase_out.length.JOINT": {
                "2026-01-01.2100-12-31": 100000
            },
            "gov.irs.deductions.qbi.phase_out.start.SINGLE": {
                "2026-01-01.2026-12-31": 204900,
            },
            "gov.irs.credits.ctc.phase_out.threshold.SINGLE": {
                "2026-01-01.2100-12-31": 200000
            },
            "gov.irs.deductions.qbi.phase_out.length.SINGLE": {
                "2026-01-01.2100-12-31": 50000
            },
            "gov.irs.deductions.itemized.charity.ceiling.all": {
                "2026-01-01.2100-12-31": 0.6
            },
            "gov.irs.deductions.itemized.limitation.agi_rate": {
                "2026-01-01.2100-12-31": np.inf
            },
            "gov.irs.deductions.qbi.phase_out.start.SEPARATE": {
                "2026-01-01.2026-12-31": 204900,
            },
            "gov.irs.credits.ctc.phase_out.threshold.SEPARATE": {
                "2026-01-01.2100-12-31": 200000
            },
            "gov.irs.deductions.qbi.phase_out.length.SEPARATE": {
                "2026-01-01.2100-12-31": 50000
            },
            "gov.irs.credits.ctc.refundable.phase_in.threshold": {
                "2026-01-01.2100-12-31": 2500
            },
            "gov.irs.deductions.qbi.max.business_property.rate": {
                "2026-01-01.2100-12-31": 0.025
            },
            "gov.irs.income.amt.exemption.phase_out.start.JOINT": {
                "2026-01-01.2026-12-31": 1271900,
            },
            "gov.irs.deductions.standard.amount.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 30300,
            },
            "gov.irs.income.amt.exemption.phase_out.start.SINGLE": {
                "2026-01-01.2026-12-31": 635900,
            },
            "gov.irs.deductions.standard.amount.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 22700,
            },
            "gov.irs.income.amt.exemption.amount.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 139100,
            },
            "gov.irs.income.bracket.thresholds.3.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 208300,
            },
            "gov.irs.income.bracket.thresholds.4.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 397650,
            },
            "gov.irs.income.bracket.thresholds.5.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 512950,
            },
            "gov.irs.income.bracket.thresholds.6.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 769450,
            },
            "gov.irs.income.amt.exemption.amount.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 89400,
            },
            "gov.irs.income.amt.exemption.phase_out.start.SEPARATE": {
                "2026-01-01.2026-12-31": 635900,
            },
            "gov.irs.income.bracket.thresholds.3.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 104900,
            },
            "gov.irs.income.bracket.thresholds.4.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 198800,
            },
            "gov.irs.income.bracket.thresholds.5.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 256486,
            },
            "gov.irs.income.bracket.thresholds.6.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 641200,
            },
            "gov.irs.deductions.qbi.phase_out.start.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 409800,
            },
            "gov.irs.credits.ctc.phase_out.threshold.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 400000
            },
            "gov.irs.deductions.qbi.phase_out.length.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 100000
            },
            "gov.irs.deductions.qbi.phase_out.start.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 204900,
            },
            "gov.irs.credits.ctc.phase_out.threshold.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 200000
            },
            "gov.irs.deductions.qbi.phase_out.length.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 50000
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.JOINT": {
                "2026-01-01.2100-12-31": 10000
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SINGLE": {
                "2026-01-01.2100-12-31": 10000
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SEPARATE": {
                "2026-01-01.2100-12-31": 5000
            },
            "gov.irs.income.amt.exemption.phase_out.start.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 1271900,
            },
            "gov.irs.deductions.itemized.reduction.applies": {
                "2026-01-01.2100-12-31": False
            },
            "gov.irs.deductions.itemized.reduction.agi_threshold.SINGLE": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.irs.income.amt.exemption.phase_out.start.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 635900,
            },
            "gov.irs.deductions.itemized.reduction.agi_threshold.JOINT": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.irs.deductions.itemized.reduction.agi_threshold.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 10_000
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 10_000
            },
            "gov.irs.deductions.itemized.reduction.agi_threshold.SEPARATE": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.irs.deductions.itemized.reduction.agi_threshold.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 0
            },
            "gov.irs.credits.estate.base": {
                "2026-01-01.2026-12-31": 14200000,
            },
            "gov.irs.income.amt.exemption.separate_limit": {
                "2026-01-01.2026-12-31": 913900,
            },
            "gov.irs.deductions.itemized.misc.applies": {
                "2026-01-01.2100-12-31": False
            },
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
            "gov.aca.ptc_phase_out_rate[0].amount": {"2026-01-01.2100-12-31": 0},
            "gov.aca.ptc_phase_out_rate[1].amount": {"2025-01-01.2100-12-31": 0},
            "gov.aca.ptc_phase_out_rate[2].amount": {"2026-01-01.2100-12-31": 0},
            "gov.aca.ptc_phase_out_rate[3].amount": {"2026-01-01.2100-12-31": 0.02},
            "gov.aca.ptc_phase_out_rate[4].amount": {"2026-01-01.2100-12-31": 0.04},
            "gov.aca.ptc_phase_out_rate[5].amount": {"2026-01-01.2100-12-31": 0.06},
            "gov.aca.ptc_phase_out_rate[6].amount": {"2026-01-01.2100-12-31": 0.085},
            "gov.aca.ptc_income_eligibility[2].amount": {"2026-01-01.2100-12-31": True},
            "gov.aca.ptc_phase_out_rate[1].threshold": {"2026-01-01.2100-12-31": 0},
        },
        country_id="us",
    )


def hr1_tax_rate_reform():
    return Reform.from_dict(
        {
            "gov.irs.income.bracket.rates.2": {"2026-01-01.2100-12-31": 0.12},
            "gov.irs.income.bracket.rates.3": {"2026-01-01.2100-12-31": 0.22},
            "gov.irs.income.bracket.rates.4": {"2026-01-01.2100-12-31": 0.24},
            "gov.irs.income.bracket.rates.5": {"2026-01-01.2100-12-31": 0.32},
            "gov.irs.income.bracket.rates.7": {"2026-01-01.2100-12-31": 0.37},
            "gov.irs.income.bracket.thresholds.3.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 104900,
            },
            "gov.irs.income.bracket.thresholds.4.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 198800,
            },
            "gov.irs.income.bracket.thresholds.5.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 256486,
            },
            "gov.irs.income.bracket.thresholds.6.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 643950,
            },
            "gov.irs.income.bracket.thresholds.3.JOINT": {
                "2026-01-01.2026-12-31": 208300,
            },
            "gov.irs.income.bracket.thresholds.4.JOINT": {
                "2026-01-01.2026-12-31": 397650,
            },
            "gov.irs.income.bracket.thresholds.5.JOINT": {
                "2026-01-01.2026-12-31": 512950,
            },
            "gov.irs.income.bracket.thresholds.6.JOINT": {
                "2026-01-01.2026-12-31": 772750,
            },
            "gov.irs.income.bracket.thresholds.3.SEPARATE": {
                "2026-01-01.2026-12-31": 104900,
            },
            "gov.irs.income.bracket.thresholds.4.SEPARATE": {
                "2026-01-01.2026-12-31": 198800,
            },
            "gov.irs.income.bracket.thresholds.5.SEPARATE": {
                "2026-01-01.2026-12-31": 256450,
            },
            "gov.irs.income.bracket.thresholds.6.SEPARATE": {
                "2026-01-01.2026-12-31": 386350,
            },
            "gov.irs.income.bracket.thresholds.3.SINGLE": {
                "2026-01-01.2026-12-31": 105475,
            },
            "gov.irs.income.bracket.thresholds.4.SINGLE": {
                "2026-01-01.2026-12-31": 198800,
            },
            "gov.irs.income.bracket.thresholds.5.SINGLE": {
                "2026-01-01.2026-12-31": 256450,
            },
            "gov.irs.income.bracket.thresholds.6.SINGLE": {
                "2026-01-01.2026-12-31": 643950,
            },
            "gov.irs.income.bracket.thresholds.3.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 208300,
            },
            "gov.irs.income.bracket.thresholds.4.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 397650,
            },
            "gov.irs.income.bracket.thresholds.5.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 512950,
            },
            "gov.irs.income.bracket.thresholds.6.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 772750,
            },
        },
        country_id="us",
    )


def hr1_sd_reform():
    return Reform.from_dict(
        {
            "gov.irs.deductions.standard.amount.JOINT": {
                "2026-01-01.2026-12-31": 32300,
            },
            "gov.irs.deductions.standard.amount.SINGLE": {
                "2026-01-01.2026-12-31": 16150,
            },
            "gov.irs.deductions.standard.amount.SEPARATE": {
                "2026-01-01.2026-12-31": 16150,
            },
            "gov.irs.deductions.standard.amount.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 32300,
            },
            "gov.irs.deductions.standard.amount.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 24400,
            },
        },
        country_id="us",
    )


def hr1_exemption_reform():
    return Reform.from_dict(
        {"gov.irs.income.exemption.amount": {"2026-01-01.2100-12-31": 0}},
        country_id="us",
    )


def hr1_ctc_reform():
    return Reform.from_dict(
        {
            "gov.contrib.reconciliation.ctc.in_effect": {"2025-01-01.2100-12-31": True},
            "gov.irs.credits.ctc.amount.base[0].amount": {
                "2025-01-01.2028-12-31": 2500
            },
            "gov.irs.credits.ctc.amount.adult_dependent": {
                "2026-01-01.2100-12-31": 500
            },
            "gov.irs.credits.ctc.phase_out.threshold.JOINT": {
                "2026-01-01.2100-12-31": 400000
            },
            "gov.irs.credits.ctc.refundable.individual_max": {
                "2026-01-01.2026-12-31": 1700
            },
            "gov.irs.credits.ctc.phase_out.threshold.SINGLE": {
                "2026-01-01.2100-12-31": 200000
            },
            "gov.irs.credits.ctc.phase_out.threshold.SEPARATE": {
                "2026-01-01.2100-12-31": 200000
            },
            "gov.irs.credits.ctc.refundable.phase_in.threshold": {
                "2026-01-01.2100-12-31": 2500
            },
            "gov.irs.credits.ctc.phase_out.threshold.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 400000
            },
            "gov.irs.credits.ctc.phase_out.threshold.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 200000
            },
        },
        country_id="us",
    )


def hr1_qbi_reform():
    return Reform.from_dict(
        {
            "gov.irs.deductions.qbi.max.rate": {"2026-01-01.2100-12-31": 0.23},
            "gov.irs.deductions.qbi.max.w2_wages.rate": {"2026-01-01.2100-12-31": 0.5},
            "gov.contrib.reconciliation.qbid.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            "gov.irs.deductions.qbi.max.w2_wages.alt_rate": {
                "2026-01-01.2035-12-31": 0.25
            },
            "gov.irs.deductions.qbi.phase_out.start.JOINT": {
                "2026-01-01.2026-12-31": 400600,
            },
            "gov.irs.deductions.qbi.phase_out.start.SINGLE": {
                "2026-01-01.2026-12-31": 200300,
            },
            "gov.irs.deductions.qbi.phase_out.start.SEPARATE": {
                "2026-01-01.2026-12-31": 200300,
            },
            "gov.irs.deductions.qbi.max.business_property.rate": {
                "2026-01-01.2100-12-31": 0.025
            },
            "gov.irs.deductions.qbi.phase_out.start.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 400600,
            },
            "gov.irs.deductions.qbi.phase_out.start.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 200300,
            },
        },
        country_id="us",
    )


def hr1_estate_tax_reform():
    return Reform.from_dict(
        {
            "gov.irs.credits.estate.base": {
                "2026-01-01.2026-12-31": 15000000,
            }
        },
        country_id="us",
    )


def hr1_amt_reform():
    return Reform.from_dict(
        {
            "gov.irs.income.amt.exemption.amount.JOINT": {
                "2026-01-01.2026-12-31": 109400,
            },
            "gov.irs.income.amt.exemption.amount.SINGLE": {
                "2026-01-01.2026-12-31": 70300,
            },
            "gov.irs.income.amt.exemption.separate_limit": {
                "2026-01-01.2026-12-31": 718800,
            },
            "gov.irs.income.amt.exemption.amount.SEPARATE": {
                "2026-01-01.2026-12-31": 54700,
            },
            "gov.irs.income.amt.exemption.phase_out.start.JOINT": {
                "2026-01-01.2026-12-31": 1000000,
            },
            "gov.irs.income.amt.exemption.phase_out.start.SINGLE": {
                "2026-01-01.2026-12-31": 500000,
            },
            "gov.irs.income.amt.exemption.amount.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 109400,
            },
            "gov.irs.income.amt.exemption.amount.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 70300,
            },
            "gov.irs.income.amt.exemption.phase_out.start.SEPARATE": {
                "2026-01-01.2026-12-31": 500000,
            },
            "gov.irs.income.amt.exemption.phase_out.start.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 1000000,
            },
        },
        country_id="us",
    )


def hr1_misc_reform():
    return Reform.from_dict(
        {"gov.irs.deductions.itemized.misc.applies": {"2026-01-01.2100-12-31": False}},
        country_id="us",
    )


def hr1_other_item_reform():
    return Reform.from_dict(
        {
            "gov.irs.deductions.itemized.interest.mortgage.cap.JOINT": {
                "2026-01-01.2100-12-31": 750000
            },
            "gov.irs.deductions.itemized.interest.mortgage.cap.SINGLE": {
                "2026-01-01.2100-12-31": 750000
            },
            "gov.irs.deductions.itemized.interest.mortgage.cap.SEPARATE": {
                "2026-01-01.2100-12-31": 375000
            },
            "gov.irs.deductions.itemized.charity.non_itemizers_amount.JOINT": {
                "2025-01-01.2028-12-31": 300
            },
            "gov.irs.deductions.itemized.charity.non_itemizers_amount.SINGLE": {
                "2025-01-01.2028-12-31": 150
            },
            "gov.irs.deductions.itemized.charity.non_itemizers_amount.SEPARATE": {
                "2025-01-01.2028-12-31": 150
            },
            "gov.irs.deductions.itemized.interest.mortgage.cap.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 750000
            },
            "gov.irs.deductions.itemized.interest.mortgage.cap.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 750000
            },
            "gov.irs.deductions.itemized.charity.non_itemizers_amount.SURVIVING_SPOUSE": {
                "2025-01-01.2028-12-31": 150
            },
            "gov.irs.deductions.itemized.charity.non_itemizers_amount.HEAD_OF_HOUSEHOLD": {
                "2025-01-01.2028-12-31": 150
            },
            "gov.irs.deductions.itemized.casualty.active": {
                "2026-01-01.2100-12-31": False
            },
        },
        country_id="us",
    )


def hr1_limitation_on_itemized_deductions_reform():
    return Reform.from_dict(
        {
            "gov.contrib.reconciliation.pease.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            "gov.contrib.reconciliation.pease.amended_structure.in_effect": {
                "2026-01-01.2100-12-31": True
            },
        },
        country_id="us",
    )


def hr1_tip_reform():
    return Reform.from_dict(
        {
            "gov.contrib.reconciliation.tip_income_exempt.in_effect": {
                "2025-01-01.2028-12-31": True
            }
        },
        country_id="us",
    )


def hr1_overtime_reform():
    return Reform.from_dict(
        {
            "gov.contrib.reconciliation.overtime_income_exempt.in_effect": {
                "2025-01-01.2028-12-31": True
            }
        },
        country_id="us",
    )


def hr1_senior_deduction_reform():
    return Reform.from_dict(
        {
            "gov.contrib.reconciliation.additional_senior_standard_deduction.in_effect": {
                "2025-01-01.2028-12-31": True
            },
        },
        country_id="us",
    )


def hr1_auto_loan_reform():
    return Reform.from_dict(
        {
            "gov.contrib.reconciliation.auto_loan_interest_ald.in_effect": {
                "2025-01-01.2028-12-31": True
            }
        },
        country_id="us",
    )


def hr1_salt_reform():
    return Reform.from_dict(
        {
            "gov.contrib.salt_phase_out.rate": {"2025-01-01.2100-12-31": 0.3},
            "gov.contrib.salt_phase_out.in_effect": {"2025-01-01.2100-12-31": True},
            "gov.contrib.salt_phase_out.floor.applies": {"2025-01-01.2100-12-31": True},
            "gov.contrib.salt_phase_out.threshold.JOINT": {
                "2026-01-01.2026-12-31": 505000,
            },
            "gov.contrib.salt_phase_out.threshold.SINGLE": {
                "2026-01-01.2026-12-31": 505000,
            },
            "gov.contrib.salt_phase_out.threshold.SEPARATE": {
                "2026-01-01.2026-12-31": 252500,
            },
            "gov.contrib.salt_phase_out.threshold.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 505000,
            },
            "gov.contrib.salt_phase_out.threshold.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 505000,
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.JOINT": {
                "2026-01-01.2026-12-31": 40400,
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SINGLE": {
                "2026-01-01.2026-12-31": 40400,
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SEPARATE": {
                "2026-01-01.2026-12-31": 20200,
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 40400,
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 40400,
            },
        },
        country_id="us",
    )


def aca_enhanced_subsidies_reform():
    return Reform.from_dict(
        {
            "gov.aca.ptc_phase_out_rate[0].amount": {"2026-01-01.2100-12-31": 0.02},
            "gov.aca.ptc_phase_out_rate[1].threshold": {"2026-01-01.2100-12-31": 1.33},
            "gov.aca.ptc_phase_out_rate[1].amount": {"2025-01-01.2100-12-31": 0.03},
            "gov.aca.ptc_phase_out_rate[2].amount": {"2026-01-01.2100-12-31": 0.04},
            "gov.aca.ptc_phase_out_rate[3].amount": {"2026-01-01.2100-12-31": 0.063},
            "gov.aca.ptc_phase_out_rate[4].amount": {"2026-01-01.2100-12-31": 0.0805},
            "gov.aca.ptc_phase_out_rate[5].amount": {"2026-01-01.2100-12-31": 0.095},
            "gov.aca.ptc_phase_out_rate[6].amount": {"2026-01-01.2100-12-31": 0.095},
            "gov.aca.ptc_income_eligibility[2].amount": {
                "2026-01-01.2100-12-31": False
            },
        },
        country_id="us",
    )


def snap_takeup_reform():
    return Reform.from_dict(
        {
            "gov.usda.snap.takeup_rate": {"2026-01-01.2028-12-31": 0.775},
        },
        country_id="us",
    )


def aca_takeup_reform():
    return Reform.from_dict(
        {
            "gov.aca.takeup_rate": {"2026-01-01.2028-12-31": 0.63},
        },
        country_id="us",
    )


def medicaid_takeup_reform():
    return Reform.from_dict(
        {
            "gov.hhs.medicaid.takeup_rate": {"2026-01-01.2028-12-31": 0.92},
        },
        country_id="us",
    )


def get_all_reforms():
    """Get dictionary of all reform components."""
    return {
        "Tax Rate Reform": hr1_tax_rate_reform(),
        "Standard Deduction Reform": hr1_sd_reform(),
        "Exemption Reform": hr1_exemption_reform(),
        "CTC Reform": hr1_ctc_reform(),
        "QBID Reform": hr1_qbi_reform(),
        "AMT Reform": hr1_amt_reform(),
        "Miscellaneous Reform": hr1_misc_reform(),
        "Other Itemized Deductions Reform": hr1_other_item_reform(),
        "Limitation on Itemized Deductions Reform": hr1_limitation_on_itemized_deductions_reform(),
        "Estate Tax Reform": hr1_estate_tax_reform(),
        "Senior Deduction Reform": hr1_senior_deduction_reform(),
        "Tip Income Exempt": hr1_tip_reform(),
        "Overtime Income Exempt": hr1_overtime_reform(),
        "Auto Loan Interest ALD": hr1_auto_loan_reform(),
        "SALT Reform": hr1_salt_reform(),
        "ACA Enhanced Subsidies Reform": aca_enhanced_subsidies_reform(),
        "SNAP Takeup Reform": snap_takeup_reform(),
        "ACA Takeup Reform": aca_takeup_reform(),
        "Medicaid Takeup Reform": medicaid_takeup_reform(),
    }


def senate_finance_tax_rate_reform():
    return Reform.from_dict(
        {
            "gov.irs.income.bracket.rates.2": {"2026-01-01.2100-12-31": 0.12},
            "gov.irs.income.bracket.rates.3": {"2026-01-01.2100-12-31": 0.22},
            "gov.irs.income.bracket.rates.4": {"2026-01-01.2100-12-31": 0.24},
            "gov.irs.income.bracket.rates.5": {"2026-01-01.2100-12-31": 0.32},
            "gov.irs.income.bracket.rates.7": {"2026-01-01.2100-12-31": 0.37},
            "gov.irs.income.bracket.thresholds.1.JOINT": {
                "2026-01-01.2100-12-31": 23850
            },
            "gov.irs.income.bracket.thresholds.2.JOINT": {
                "2026-01-01.2100-12-31": 96950
            },
            "gov.irs.income.bracket.thresholds.3.JOINT": {
                "2026-01-01.2026-12-31": 208300,
                "2027-01-01.2027-12-31": 213400,
                "2028-01-01.2028-12-31": 217850,
                "2029-01-01.2029-12-31": 222200,
                "2030-01-01.2030-12-31": 226650,
                "2031-01-01.2031-12-31": 231100,
                "2032-01-01.2032-12-31": 235650,
                "2033-01-01.2033-12-31": 240300,
                "2034-01-01.2034-12-31": 245100,
                "2035-01-01.2036-12-31": 249950,
            },
            "gov.irs.income.bracket.thresholds.4.JOINT": {
                "2026-01-01.2026-12-31": 397650,
                "2027-01-01.2027-12-31": 407450,
                "2028-01-01.2028-12-31": 415900,
                "2029-01-01.2029-12-31": 424250,
                "2030-01-01.2030-12-31": 432700,
                "2031-01-01.2031-12-31": 441250,
                "2032-01-01.2032-12-31": 449900,
                "2033-01-01.2033-12-31": 458800,
                "2034-01-01.2034-12-31": 467950,
                "2035-01-01.2036-12-31": 477150,
            },
            "gov.irs.income.bracket.thresholds.5.JOINT": {
                "2026-01-01.2026-12-31": 512950,
                "2027-01-01.2027-12-31": 525600,
                "2028-01-01.2028-12-31": 536500,
                "2029-01-01.2029-12-31": 547200,
                "2030-01-01.2030-12-31": 558100,
                "2031-01-01.2031-12-31": 569150,
                "2032-01-01.2032-12-31": 580350,
                "2033-01-01.2033-12-31": 591800,
                "2034-01-01.2034-12-31": 603550,
                "2035-01-01.2037-12-31": 615500,
            },
            "gov.irs.income.bracket.thresholds.6.JOINT": {
                "2026-01-01.2026-12-31": 772750,
                "2027-01-01.2027-12-31": 791800,
                "2028-01-01.2028-12-31": 808200,
                "2029-01-01.2029-12-31": 824400,
                "2030-01-01.2030-12-31": 840800,
                "2031-01-01.2031-12-31": 857400,
                "2032-01-01.2032-12-31": 874250,
                "2033-01-01.2033-12-31": 891550,
                "2034-01-01.2034-12-31": 909300,
                "2035-01-01.2036-12-31": 927250,
            },
            "gov.irs.income.bracket.thresholds.1.SINGLE": {
                "2026-01-01.2100-12-31": 11925
            },
            "gov.irs.income.bracket.thresholds.2.SINGLE": {
                "2026-01-01.2100-12-31": 48475
            },
            "gov.irs.income.bracket.thresholds.3.SINGLE": {
                "2026-01-01.2026-12-31": 104900,
                "2027-01-01.2027-12-31": 107500,
                "2028-01-01.2028-12-31": 109700,
                "2029-01-01.2029-12-31": 111900,
                "2030-01-01.2030-12-31": 114150,
                "2031-01-01.2031-12-31": 116400,
                "2032-01-01.2032-12-31": 118700,
                "2033-01-01.2033-12-31": 121050,
                "2034-01-01.2034-12-31": 123450,
                "2035-01-01.2036-12-31": 125900,
            },
            "gov.irs.income.bracket.thresholds.4.SINGLE": {
                "2026-01-01.2026-12-31": 198800,
                "2027-01-01.2027-12-31": 203700,
                "2028-01-01.2028-12-31": 207950,
                "2029-01-01.2029-12-31": 212100,
                "2030-01-01.2030-12-31": 216350,
                "2031-01-01.2031-12-31": 220600,
                "2032-01-01.2032-12-31": 224950,
                "2033-01-01.2033-12-31": 229400,
                "2034-01-01.2034-12-31": 233950,
                "2035-01-01.2036-12-31": 238550,
            },
            "gov.irs.income.bracket.thresholds.5.SINGLE": {
                "2026-01-01.2026-12-31": 256450,
                "2027-01-01.2027-12-31": 262800,
                "2028-01-01.2028-12-31": 268250,
                "2029-01-01.2029-12-31": 273600,
                "2030-01-01.2030-12-31": 279050,
                "2031-01-01.2031-12-31": 284550,
                "2032-01-01.2032-12-31": 290150,
                "2033-01-01.2033-12-31": 295900,
                "2034-01-01.2034-12-31": 301750,
                "2035-01-01.2100-12-31": 307750,
            },
            "gov.irs.income.bracket.thresholds.6.SINGLE": {
                "2026-01-01.2026-12-31": 643950,
                "2027-01-01.2027-12-31": 659800,
                "2028-01-01.2028-12-31": 673500,
                "2029-01-01.2029-12-31": 687000,
                "2030-01-01.2030-12-31": 700650,
                "2031-01-01.2031-12-31": 714500,
                "2032-01-01.2032-12-31": 728550,
                "2033-01-01.2033-12-31": 742950,
                "2034-01-01.2034-12-31": 757750,
                "2035-01-01.2036-12-31": 772700,
            },
            "gov.irs.income.bracket.thresholds.1.SEPARATE": {
                "2026-01-01.2100-12-31": 11925
            },
            "gov.irs.income.bracket.thresholds.2.SEPARATE": {
                "2026-01-01.2100-12-31": 48475
            },
            "gov.irs.income.bracket.thresholds.3.SEPARATE": {
                "2026-01-01.2026-12-31": 104900,
                "2027-01-01.2027-12-31": 107500,
                "2028-01-01.2028-12-31": 109700,
                "2029-01-01.2029-12-31": 111900,
                "2030-01-01.2030-12-31": 114150,
                "2031-01-01.2031-12-31": 116400,
                "2032-01-01.2032-12-31": 118700,
                "2033-01-01.2033-12-31": 121050,
                "2034-01-01.2034-12-31": 123450,
                "2035-01-01.2036-12-31": 125900,
            },
            "gov.irs.income.bracket.thresholds.4.SEPARATE": {
                "2026-01-01.2026-12-31": 198800,
                "2027-01-01.2027-12-31": 203700,
                "2028-01-01.2028-12-31": 207950,
                "2029-01-01.2029-12-31": 212100,
                "2030-01-01.2030-12-31": 216350,
                "2031-01-01.2031-12-31": 220600,
                "2032-01-01.2032-12-31": 224950,
                "2033-01-01.2033-12-31": 229400,
                "2034-01-01.2034-12-31": 233950,
                "2035-01-01.2036-12-31": 238550,
            },
            "gov.irs.income.bracket.thresholds.5.SEPARATE": {
                "2026-01-01.2026-12-31": 256450,
                "2027-01-01.2027-12-31": 262800,
                "2028-01-01.2028-12-31": 268250,
                "2029-01-01.2029-12-31": 273600,
                "2030-01-01.2030-12-31": 279050,
                "2031-01-01.2031-12-31": 284550,
                "2032-01-01.2032-12-31": 290150,
                "2033-01-01.2033-12-31": 295900,
                "2034-01-01.2034-12-31": 301750,
                "2035-01-01.2100-12-31": 307750,
            },
            "gov.irs.income.bracket.thresholds.6.SEPARATE": {
                "2026-01-01.2026-12-31": 386350,
                "2027-01-01.2027-12-31": 395900,
                "2028-01-01.2028-12-31": 404100,
                "2029-01-01.2029-12-31": 412200,
                "2030-01-01.2030-12-31": 420400,
                "2031-01-01.2031-12-31": 428700,
                "2032-01-01.2032-12-31": 437100,
                "2033-01-01.2033-12-31": 445750,
                "2034-01-01.2034-12-31": 454650,
                "2035-01-01.2036-12-31": 463600,
            },
            "gov.irs.income.bracket.thresholds.1.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 23850
            },
            "gov.irs.income.bracket.thresholds.2.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 96950
            },
            "gov.irs.income.bracket.thresholds.3.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 208300,
                "2027-01-01.2027-12-31": 213400,
                "2028-01-01.2028-12-31": 217850,
                "2029-01-01.2029-12-31": 222200,
                "2030-01-01.2030-12-31": 226650,
                "2031-01-01.2031-12-31": 231100,
                "2032-01-01.2032-12-31": 235650,
                "2033-01-01.2033-12-31": 240300,
                "2034-01-01.2034-12-31": 245100,
                "2035-01-01.2036-12-31": 249950,
            },
            "gov.irs.income.bracket.thresholds.4.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 397650,
                "2027-01-01.2027-12-31": 407450,
                "2028-01-01.2028-12-31": 415900,
                "2029-01-01.2029-12-31": 424250,
                "2030-01-01.2030-12-31": 432700,
                "2031-01-01.2031-12-31": 441250,
                "2032-01-01.2032-12-31": 449900,
                "2033-01-01.2033-12-31": 458800,
                "2034-01-01.2034-12-31": 467950,
                "2035-01-01.2036-12-31": 477150,
            },
            "gov.irs.income.bracket.thresholds.5.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 512950,
                "2027-01-01.2027-12-31": 525600,
                "2028-01-01.2028-12-31": 536500,
                "2029-01-01.2029-12-31": 547200,
                "2030-01-01.2030-12-31": 558100,
                "2031-01-01.2031-12-31": 569150,
                "2032-01-01.2032-12-31": 580350,
                "2033-01-01.2033-12-31": 591800,
                "2034-01-01.2034-12-31": 603550,
                "2035-01-01.2037-12-31": 615500,
            },
            "gov.irs.income.bracket.thresholds.6.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 772750,
                "2027-01-01.2027-12-31": 791800,
                "2028-01-01.2028-12-31": 808200,
                "2029-01-01.2029-12-31": 824400,
                "2030-01-01.2030-12-31": 840800,
                "2031-01-01.2031-12-31": 857400,
                "2032-01-01.2032-12-31": 874250,
                "2033-01-01.2033-12-31": 891550,
                "2034-01-01.2034-12-31": 909300,
                "2035-01-01.2036-12-31": 927300,
            },
            "gov.irs.income.bracket.thresholds.1.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 17000
            },
            "gov.irs.income.bracket.thresholds.2.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 64850
            },
            "gov.irs.income.bracket.thresholds.3.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 104900,
                "2027-01-01.2027-12-31": 107500,
                "2028-01-01.2028-12-31": 109700,
                "2029-01-01.2029-12-31": 111900,
                "2030-01-01.2030-12-31": 114150,
                "2031-01-01.2031-12-31": 116400,
                "2032-01-01.2032-12-31": 118700,
                "2033-01-01.2033-12-31": 121050,
                "2034-01-01.2034-12-31": 123450,
                "2035-01-01.2036-12-31": 125900,
            },
            "gov.irs.income.bracket.thresholds.4.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 198800,
                "2027-01-01.2027-12-31": 203700,
                "2028-01-01.2028-12-31": 207950,
                "2029-01-01.2029-12-31": 212100,
                "2030-01-01.2030-12-31": 216350,
                "2031-01-01.2031-12-31": 220600,
                "2032-01-01.2032-12-31": 224950,
                "2033-01-01.2033-12-31": 229400,
                "2034-01-01.2034-12-31": 233950,
                "2035-01-01.2036-12-31": 238550,
            },
            "gov.irs.income.bracket.thresholds.5.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 256486,
                "2027-01-01.2027-12-31": 262806,
                "2028-01-01.2028-12-31": 268250,
                "2029-01-01.2029-12-31": 273621,
                "2030-01-01.2030-12-31": 279065,
                "2031-01-01.2031-12-31": 284584,
                "2032-01-01.2032-12-31": 290175,
                "2033-01-01.2033-12-31": 295914,
                "2034-01-01.2034-12-31": 301800,
                "2035-01-01.2036-12-31": 307759,
            },
            "gov.irs.income.bracket.thresholds.6.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 643950,
                "2027-01-01.2027-12-31": 659800,
                "2028-01-01.2028-12-31": 673500,
                "2029-01-01.2029-12-31": 687000,
                "2030-01-01.2030-12-31": 700650,
                "2031-01-01.2031-12-31": 714500,
                "2032-01-01.2032-12-31": 728550,
                "2033-01-01.2033-12-31": 742950,
                "2034-01-01.2034-12-31": 757750,
                "2035-01-01.2036-12-31": 772700,
            },
        },
        country_id="us",
    )


def senate_finance_sd_reform():
    return Reform.from_dict(
        {
            "gov.irs.deductions.standard.amount.JOINT": {
                "2025-01-01.2025-12-31": 31500,
                "2026-01-01.2026-12-31": 32600,
                "2027-01-01.2027-12-31": 33400,
                "2028-01-01.2028-12-31": 34100,
                "2029-01-01.2029-12-31": 34800,
                "2030-01-01.2030-12-31": 35500,
                "2031-01-01.2031-12-31": 36200,
                "2032-01-01.2032-12-31": 36900,
                "2033-01-01.2033-12-31": 37700,
                "2034-01-01.2034-12-31": 38400,
                "2035-01-01.2100-12-31": 39200,
            },
            "gov.irs.deductions.standard.amount.SINGLE": {
                "2025-01-01.2025-12-31": 15750,
                "2026-01-01.2026-12-31": 16300,
                "2027-01-01.2027-12-31": 16700,
                "2028-01-01.2028-12-31": 17050,
                "2029-01-01.2029-12-31": 17400,
                "2030-01-01.2030-12-31": 17750,
                "2031-01-01.2031-12-31": 18100,
                "2032-01-01.2032-12-31": 18450,
                "2033-01-01.2033-12-31": 18850,
                "2034-01-01.2034-12-31": 19200,
                "2035-01-01.2100-12-31": 19600,
            },
            "gov.irs.deductions.standard.amount.SEPARATE": {
                "2025-01-01.2025-12-31": 15750,
                "2026-01-01.2026-12-31": 16300,
                "2027-01-01.2027-12-31": 16700,
                "2028-01-01.2028-12-31": 17050,
                "2029-01-01.2029-12-31": 17400,
                "2030-01-01.2030-12-31": 17750,
                "2031-01-01.2031-12-31": 18100,
                "2032-01-01.2032-12-31": 18450,
                "2033-01-01.2033-12-31": 18850,
                "2034-01-01.2034-12-31": 19200,
                "2035-01-01.2100-12-31": 19600,
            },
            "gov.irs.deductions.standard.amount.SURVIVING_SPOUSE": {
                "2025-01-01.2025-12-31": 31500,
                "2026-01-01.2026-12-31": 32600,
                "2027-01-01.2027-12-31": 33400,
                "2028-01-01.2028-12-31": 34100,
                "2029-01-01.2029-12-31": 34800,
                "2030-01-01.2030-12-31": 35500,
                "2031-01-01.2031-12-31": 36200,
                "2032-01-01.2032-12-31": 36900,
                "2033-01-01.2033-12-31": 37700,
                "2034-01-01.2034-12-31": 38400,
                "2035-01-01.2100-12-31": 39200,
            },
            "gov.irs.deductions.standard.amount.HEAD_OF_HOUSEHOLD": {
                "2025-01-01.2025-12-31": 23625,
                "2026-01-01.2026-12-31": 24500,
                "2027-01-01.2027-12-31": 25100,
                "2028-01-01.2028-12-31": 25600,
                "2029-01-01.2029-12-31": 26150,
                "2030-01-01.2030-12-31": 26650,
                "2031-01-01.2031-12-31": 27200,
                "2032-01-01.2032-12-31": 27700,
                "2033-01-01.2033-12-31": 28250,
                "2034-01-01.2034-12-31": 28800,
                "2035-01-01.2100-12-31": 29400,
            },
        },
        country_id="us",
    )


def senate_finance_amt_reform():
    return Reform.from_dict(
        {
            "gov.irs.income.amt.exemption.amount.JOINT": {
                "2026-01-01.2026-12-31": 139000,
                "2027-01-01.2027-12-31": 142500,
                "2028-01-01.2028-12-31": 145500,
                "2029-01-01.2029-12-31": 148400,
                "2030-01-01.2030-12-31": 151300,
                "2031-01-01.2031-12-31": 154300,
                "2032-01-01.2032-12-31": 157400,
                "2033-01-01.2033-12-31": 160500,
                "2034-01-01.2034-12-31": 163700,
                "2035-01-01.2100-12-31": 166900,
            },
            "gov.irs.income.amt.exemption.amount.SINGLE": {
                "2026-01-01.2026-12-31": 89400,
                "2027-01-01.2027-12-31": 91700,
                "2028-01-01.2028-12-31": 93500,
                "2029-01-01.2029-12-31": 95400,
                "2030-01-01.2030-12-31": 97300,
                "2031-01-01.2031-12-31": 99200,
                "2032-01-01.2032-12-31": 101200,
                "2033-01-01.2033-12-31": 103200,
                "2034-01-01.2034-12-31": 105300,
                "2035-01-01.2100-12-31": 107300,
            },
            "gov.irs.income.amt.exemption.phase_out.rate": {
                "2026-01-01.2100-12-31": 0.5
            },
            "gov.irs.income.amt.exemption.separate_limit": {
                "2026-01-01.2026-12-31": 639200,
                "2027-01-01.2027-12-31": 662750,
                "2028-01-01.2028-12-31": 676350,
                "2029-01-01.2029-12-31": 689950,
                "2030-01-01.2030-12-31": 703750,
                "2031-01-01.2031-12-31": 717650,
                "2032-01-01.2032-12-31": 731700,
                "2033-01-01.2033-12-31": 746100,
                "2034-01-01.2034-12-31": 760950,
                "2035-01-01.2100-12-31": 776150,
            },
            "gov.irs.income.amt.exemption.amount.SEPARATE": {
                "2026-01-01.2026-12-31": 69600,
                "2027-01-01.2027-12-31": 71300,
                "2028-01-01.2028-12-31": 72700,
                "2029-01-01.2029-12-31": 74200,
                "2030-01-01.2030-12-31": 75700,
                "2031-01-01.2031-12-31": 77200,
                "2032-01-01.2032-12-31": 78700,
                "2033-01-01.2033-12-31": 80200,
                "2034-01-01.2034-12-31": 81800,
                "2035-01-01.2100-12-31": 83500,
            },
            "gov.irs.income.amt.exemption.phase_out.start.JOINT": {
                "2026-01-01.2026-12-31": 1000000,
                "2027-01-01.2027-12-31": 1040300,
                "2028-01-01.2028-12-31": 1061900,
                "2029-01-01.2029-12-31": 1083100,
                "2030-01-01.2030-12-31": 1104700,
                "2031-01-01.2031-12-31": 1126500,
                "2032-01-01.2032-12-31": 1148600,
                "2033-01-01.2033-12-31": 1171400,
                "2034-01-01.2034-12-31": 1194700,
                "2035-01-01.2100-12-31": 1218300,
            },
            "gov.irs.income.amt.exemption.phase_out.start.SINGLE": {
                "2026-01-01.2026-12-31": 500000,
                "2027-01-01.2027-12-31": 520150,
                "2028-01-01.2028-12-31": 530950,
                "2029-01-01.2029-12-31": 541550,
                "2030-01-01.2030-12-31": 552350,
                "2031-01-01.2031-12-31": 563250,
                "2032-01-01.2032-12-31": 574300,
                "2033-01-01.2033-12-31": 585700,
                "2034-01-01.2034-12-31": 597350,
                "2035-01-01.2100-12-31": 609150,
            },
            "gov.irs.income.amt.exemption.amount.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 139100,
                "2027-01-01.2027-12-31": 142500,
                "2028-01-01.2028-12-31": 145500,
                "2029-01-01.2029-12-31": 148400,
                "2030-01-01.2030-12-31": 151300,
                "2031-01-01.2031-12-31": 154300,
                "2032-01-01.2032-12-31": 157400,
                "2033-01-01.2033-12-31": 160500,
                "2034-01-01.2034-12-31": 163700,
                "2035-01-01.2100-12-31": 166900,
            },
            "gov.irs.income.amt.exemption.amount.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 89400,
                "2027-01-01.2027-12-31": 91700,
                "2028-01-01.2028-12-31": 93600,
                "2029-01-01.2029-12-31": 95400,
                "2030-01-01.2030-12-31": 97300,
                "2031-01-01.2031-12-31": 99200,
                "2032-01-01.2032-12-31": 101200,
                "2033-01-01.2033-12-31": 103200,
                "2034-01-01.2034-12-31": 105300,
                "2035-01-01.2100-12-31": 107300,
            },
            "gov.irs.income.amt.exemption.phase_out.start.SEPARATE": {
                "2026-01-01.2026-12-31": 500000,
                "2027-01-01.2027-12-31": 520150,
                "2028-01-01.2028-12-31": 530950,
                "2029-01-01.2029-12-31": 541550,
                "2030-01-01.2030-12-31": 552350,
                "2031-01-01.2031-12-31": 563250,
                "2032-01-01.2032-12-31": 574300,
                "2033-01-01.2033-12-31": 585700,
                "2034-01-01.2034-12-31": 597350,
                "2035-01-01.2100-12-31": 609150,
            },
            "gov.irs.income.amt.exemption.phase_out.start.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 1000000,
                "2027-01-01.2027-12-31": 1040300,
                "2028-01-01.2028-12-31": 1061900,
                "2029-01-01.2029-12-31": 1083100,
                "2030-01-01.2030-12-31": 1104700,
                "2031-01-01.2031-12-31": 1126500,
                "2032-01-01.2032-12-31": 1148600,
                "2033-01-01.2033-12-31": 1171400,
                "2034-01-01.2034-12-31": 1194700,
                "2035-01-01.2100-12-31": 1218300,
            },
            "gov.irs.income.amt.exemption.phase_out.start.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 500000,
                "2027-01-01.2027-12-31": 520150,
                "2028-01-01.2028-12-31": 530950,
                "2029-01-01.2029-12-31": 541550,
                "2030-01-01.2030-12-31": 552350,
                "2031-01-01.2031-12-31": 563250,
                "2032-01-01.2032-12-31": 574300,
                "2033-01-01.2033-12-31": 585700,
                "2034-01-01.2034-12-31": 597350,
                "2035-01-01.2100-12-31": 609150,
            },
        },
        country_id="us",
    )


def senate_finance_salt_reform():
    return Reform.from_dict(
        {
            "gov.contrib.salt_phase_out.rate": {"2025-01-01.2100-12-31": 0.3},
            "gov.contrib.salt_phase_out.in_effect": {"2025-01-01.2029-12-31": True},
            "gov.contrib.salt_phase_out.floor.applies": {"2025-01-01.2029-12-31": True},
            "gov.contrib.salt_phase_out.threshold.JOINT": {
                "2025-01-01.2025-12-31": 500000,
                "2026-01-01.2026-12-31": 505000,
                "2027-01-01.2027-12-31": 510050,
                "2028-01-01.2028-12-31": 515151,
                "2029-01-01.2029-12-31": 520302,
                "2030-01-01.2030-12-31": 525505,
                "2031-01-01.2031-12-31": 530760,
                "2032-01-01.2032-12-31": 536069,
                "2033-01-01.2100-12-31": 541428,
            },
            "gov.contrib.salt_phase_out.threshold.SINGLE": {
                "2025-01-01.2025-12-31": 500000,
                "2026-01-01.2026-12-31": 505000,
                "2027-01-01.2027-12-31": 510050,
                "2028-01-01.2028-12-31": 515151,
                "2029-01-01.2029-12-31": 520302,
                "2030-01-01.2030-12-31": 525505,
                "2031-01-01.2031-12-31": 530760,
                "2032-01-01.2032-12-31": 536068,
                "2033-01-01.2100-12-31": 541428,
            },
            "gov.contrib.salt_phase_out.threshold.SEPARATE": {
                "2025-01-01.2025-12-31": 250000,
                "2026-01-01.2026-12-31": 252500,
                "2027-01-01.2027-12-31": 255025,
                "2028-01-01.2028-12-31": 257575,
                "2029-01-01.2029-12-31": 260151,
                "2030-01-01.2030-12-31": 262753,
                "2031-01-01.2031-12-31": 265380,
                "2032-01-01.2032-12-31": 268034,
                "2033-01-01.2100-12-31": 270714,
            },
            "gov.contrib.salt_phase_out.threshold.SURVIVING_SPOUSE": {
                "2025-01-01.2025-12-31": 500000,
                "2026-01-01.2026-12-31": 505000,
                "2027-01-01.2027-12-31": 510050,
                "2028-01-01.2028-12-31": 515151,
                "2029-01-01.2029-12-31": 520302,
                "2030-01-01.2030-12-31": 525505,
                "2031-01-01.2031-12-31": 530760,
                "2032-01-01.2032-12-31": 536068,
                "2033-01-01.2100-12-31": 541428,
            },
            "gov.contrib.salt_phase_out.threshold.HEAD_OF_HOUSEHOLD": {
                "2025-01-01.2025-12-31": 500000,
                "2026-01-01.2026-12-31": 505000,
                "2027-01-01.2027-12-31": 510050,
                "2028-01-01.2028-12-31": 515151,
                "2029-01-01.2029-12-31": 520302,
                "2030-01-01.2030-12-31": 525505,
                "2031-01-01.2031-12-31": 530760,
                "2032-01-01.2032-12-31": 536068,
                "2033-01-01.2100-12-31": 541428,
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.JOINT": {
                "2025-01-01.2025-12-31": 40000,
                "2026-01-01.2026-12-31": 40400,
                "2027-01-01.2027-12-31": 40804,
                "2028-01-01.2028-12-31": 41212,
                "2029-01-01.2029-12-31": 41624,
                "2030-01-01.2100-12-31": 10000,
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SINGLE": {
                "2025-01-01.2025-12-31": 40000,
                "2026-01-01.2026-12-31": 40400,
                "2027-01-01.2027-12-31": 40804,
                "2028-01-01.2028-12-31": 41212,
                "2029-01-01.2029-12-31": 41624,
                "2030-01-01.2100-12-31": 10000,
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SEPARATE": {
                "2025-01-01.2025-12-31": 20000,
                "2026-01-01.2026-12-31": 20200,
                "2027-01-01.2027-12-31": 20402,
                "2028-01-01.2028-12-31": 20606,
                "2029-01-01.2029-12-31": 20812,
                "2030-01-01.2100-12-31": 5000,
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SURVIVING_SPOUSE": {
                "2025-01-01.2025-12-31": 40000,
                "2026-01-01.2026-12-31": 40400,
                "2027-01-01.2027-12-31": 40804,
                "2028-01-01.2028-12-31": 41212,
                "2029-01-01.2029-12-31": 41624,
                "2030-01-01.2100-12-31": 10000,
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.HEAD_OF_HOUSEHOLD": {
                "2025-01-01.2025-12-31": 40000,
                "2026-01-01.2026-12-31": 40400,
                "2027-01-01.2027-12-31": 40804,
                "2028-01-01.2028-12-31": 41212,
                "2029-01-01.2029-12-31": 41624,
                "2030-01-01.2100-12-31": 10000,
            },
        },
        country_id="us",
    )


def senate_finance_exemption_reform():
    """Personal exemption reform from Senate Finance package."""
    return Reform.from_dict(
        {"gov.irs.income.exemption.amount": {"2026-01-01.2100-12-31": 0}},
        country_id="us",
    )


def senate_finance_ctc_ssn_reform():
    """Child Tax Credit reforms from Senate Finance package."""
    return Reform.from_dict(
        {
            "gov.contrib.reconciliation.ctc.in_effect": {"2025-01-01.2100-12-31": True},
            "gov.contrib.reconciliation.ctc.one_person_ssn_req": {
                "2025-01-01.2100-12-31": True
            },
        },
        country_id="us",
    )


def senate_finance_ctc_expansion_reform():
    """Child Tax Credit reforms from Senate Finance package."""
    return Reform.from_dict(
        {
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
            "gov.irs.credits.ctc.refundable.individual_max": {
                "2026-01-01.2026-12-31": 1700,
                "2027-01-01.2028-12-31": 1800,
                "2029-01-01.2031-12-31": 1900,
                "2032-01-01.2033-12-31": 2000,
                "2034-01-01.2100-12-31": 2100,
            },
            "gov.irs.credits.ctc.phase_out.threshold.SINGLE": {
                "2026-01-01.2100-12-31": 200000
            },
            "gov.irs.credits.ctc.phase_out.threshold.SEPARATE": {
                "2026-01-01.2100-12-31": 200000
            },
            "gov.irs.credits.ctc.refundable.phase_in.threshold": {
                "2026-01-01.2100-12-31": 2500
            },
            "gov.irs.credits.ctc.phase_out.threshold.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 400000
            },
            "gov.irs.credits.ctc.phase_out.threshold.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 200000
            },
        },
        country_id="us",
    )

def senate_finance_qbid_reform():
    """Qualified Business Income Deduction reform from Senate Finance package."""
    return Reform.from_dict(
        {
            "gov.irs.deductions.qbi.max.rate": {"2026-01-01.2100-12-31": 0.2},
            "gov.irs.deductions.qbi.max.w2_wages.rate": {"2026-01-01.2100-12-31": 0.5},
            "gov.irs.deductions.qbi.max.w2_wages.alt_rate": {
                "2026-01-01.2100-12-31": 0.25
            },
            "gov.irs.deductions.qbi.phase_out.start.JOINT": {
                "2026-01-01.2026-12-31": 400600
            },
            "gov.irs.deductions.qbi.phase_out.length.JOINT": {
                "2026-01-01.2026-12-31": 150000
            },
            "gov.irs.deductions.qbi.phase_out.start.SINGLE": {
                "2026-01-01.2026-12-31": 200300
            },
            "gov.irs.deductions.qbi.phase_out.length.SINGLE": {
                "2026-01-01.2026-12-31": 75000
            },
            "gov.irs.deductions.qbi.phase_out.start.SEPARATE": {
                "2026-01-01.2026-12-31": 200300
            },
            "gov.irs.deductions.qbi.phase_out.length.SEPARATE": {
                "2026-01-01.2026-12-31": 75000
            },
            "gov.irs.deductions.qbi.max.business_property.rate": {
                "2026-01-01.2100-12-31": 0.025
            },
            "gov.irs.deductions.qbi.phase_out.start.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 400600
            },
            "gov.irs.deductions.qbi.phase_out.length.SURVIVING_SPOUSE": {
                "2026-01-01.2026-12-31": 150000
            },
            "gov.irs.deductions.qbi.phase_out.start.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 200300
            },
            "gov.contrib.reconciliation.qbid.deduction_floor.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            "gov.irs.deductions.qbi.phase_out.length.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2026-12-31": 75000
            },
        },
        country_id="us",
    )


def senate_finance_estate_tax_reform():
    """Estate tax reform from Senate Finance package."""
    return Reform.from_dict(
        {
            "gov.irs.credits.estate.base": {
                "2026-01-01.2026-12-31": 15000000,
                "2027-01-01.2027-12-31": 15600000,
                "2028-01-01.2028-12-31": 15930000,
                "2029-01-01.2029-12-31": 16250000,
                "2030-01-01.2030-12-31": 16570000,
                "2031-01-01.2031-12-31": 16900000,
                "2032-01-01.2032-12-31": 17230000,
                "2033-01-01.2033-12-31": 17570000,
                "2034-01-01.2034-12-31": 17920000,
                "2035-01-01.2100-12-31": 18270000,
            }
        },
        country_id="us",
    )


def senate_finance_misc_reform():
    """Miscellaneous itemized deduction reform from Senate Finance package."""
    return Reform.from_dict(
        {"gov.irs.deductions.itemized.misc.applies": {"2026-01-01.2100-12-31": False}},
        country_id="us",
    )

def senate_finance_charitable_ded_reform():
    """Other itemized deductions reforms from Senate Finance package."""
    return Reform.from_dict(
        {
            "gov.irs.deductions.itemized.charity.non_itemizers_amount.JOINT": {
                "2026-01-01.2100-12-31": 2000
            },
            "gov.irs.deductions.itemized.charity.non_itemizers_amount.SINGLE": {
                "2026-01-01.2100-12-31": 1000
            },
            "gov.irs.deductions.itemized.charity.non_itemizers_amount.SEPARATE": {
                "2026-01-01.2100-12-31": 1000
            },
            "gov.irs.deductions.itemized.charity.non_itemizers_amount.SURVIVING_SPOUSE": {
                "2026-01-01.2100-12-31": 1000
            },
            "gov.irs.deductions.itemized.charity.non_itemizers_amount.HEAD_OF_HOUSEHOLD": {
                "2026-01-01.2100-12-31": 1000
            },
            "gov.irs.deductions.itemized.charity.ceiling.all": {
                "2026-01-01.2100-12-31": 0.6
            },
            "gov.irs.deductions.itemized.charity.ceiling.non_cash": {
                "2026-01-01.2100-12-31": 0.5
            },
            "gov.contrib.reconciliation.charitable_donations.in_effect": {
                "2026-01-01.2100-12-31": True
            },
        },
        country_id="us",
    )

def senate_finance_casualty_loss_reform():
    """Other itemized deductions reforms from Senate Finance package."""
    return Reform.from_dict(
        {
            "gov.irs.deductions.itemized.casualty.active": {
                "2026-01-01.2100-12-31": False
            },
        },
        country_id="us",
    )

def senate_finance_pease_repeal_reform():
    """PEASE repeal reform from Senate Finance package."""
    return Reform.from_dict(
        {"gov.irs.deductions.itemized.reduction.applies": {"2026-01-01.2100-12-31": False}},
        country_id="us",
    )




def senate_finance_limitation_on_itemized_deductions_reform():
    """Limitation on itemized deductions reform from Senate Finance package."""
    return Reform.from_dict(
        {"gov.contrib.reconciliation.pease.in_effect": {"2026-01-01.2100-12-31": True}},
        country_id="us",
    )


def senate_finance_tip_reform():
    """Tip income exemption reform from Senate Finance package."""
    return Reform.from_dict(
        {
            "gov.contrib.reconciliation.tip_income_exempt.cap.JOINT": {
                "2025-01-01.2100-12-31": 25000
            },
            "gov.contrib.reconciliation.tip_income_exempt.in_effect": {
                "2025-01-01.2028-12-31": True
            },
            "gov.contrib.reconciliation.tip_income_exempt.cap.SINGLE": {
                "2025-01-01.2100-12-31": 25000
            },
            "gov.contrib.reconciliation.tip_income_exempt.cap.SEPARATE": {
                "2025-01-01.2100-12-31": 25000
            },
            "gov.contrib.reconciliation.tip_income_exempt.phase_out.applies": {
                "2025-01-01.2028-12-31": True
            },
            "gov.contrib.reconciliation.tip_income_exempt.cap.SURVIVING_SPOUSE": {
                "2025-01-01.2100-12-31": 25000
            },
            "gov.contrib.reconciliation.tip_income_exempt.cap.HEAD_OF_HOUSEHOLD": {
                "2025-01-01.2100-12-31": 25000
            },
            "gov.contrib.reconciliation.tip_income_exempt.phase_out.start.SURVIVING_SPOUSE": {
                "2025-01-01.2100-12-31": 150000
            },
        },
        country_id="us",
    )


def senate_finance_overtime_reform():
    """Overtime income exemption reform from Senate Finance package."""
    return Reform.from_dict(
        {
            "gov.contrib.reconciliation.overtime_income_exempt.cap.JOINT": {
                "2025-01-01.2100-12-31": 25000
            },
            "gov.contrib.reconciliation.overtime_income_exempt.in_effect": {
                "2025-01-01.2028-12-31": True
            },
            "gov.contrib.reconciliation.overtime_income_exempt.cap.SINGLE": {
                "2025-01-01.2100-12-31": 12500
            },
            "gov.contrib.reconciliation.overtime_income_exempt.cap.SEPARATE": {
                "2025-01-01.2100-12-31": 12500
            },
            "gov.contrib.reconciliation.overtime_income_exempt.phase_out.applies": {
                "2025-01-01.2028-12-31": True
            },
            "gov.contrib.reconciliation.overtime_income_exempt.cap.SURVIVING_SPOUSE": {
                "2025-01-01.2100-12-31": 12500
            },
            "gov.contrib.reconciliation.overtime_income_exempt.cap.HEAD_OF_HOUSEHOLD": {
                "2025-01-01.2100-12-31": 12500
            },
            "gov.contrib.reconciliation.overtime_income_exempt.phase_out.start.SURVIVING_SPOUSE": {
                "2025-01-01.2100-12-31": 150000
            },
        },
        country_id="us",
    )


def senate_finance_senior_deduction_reform():
    """Additional senior standard deduction reform from Senate Finance package."""
    return Reform.from_dict(
        {
            "gov.contrib.reconciliation.additional_senior_standard_deduction.amount": {
                "2025-01-01.2100-12-31": 6000
            },
            "gov.contrib.reconciliation.additional_senior_standard_deduction.in_effect": {
                "2025-01-01.2028-12-31": True
            },
            "gov.contrib.reconciliation.additional_senior_standard_deduction.rate.joint[1].rate": {
                "2025-01-01.2100-12-31": 0.06
            },
            "gov.contrib.reconciliation.additional_senior_standard_deduction.rate.other[1].rate": {
                "2025-01-01.2100-12-31": 0.06
            },
        },
        country_id="us",
    )


def senate_finance_auto_loan_reform():
    """Auto loan interest deduction reform from Senate Finance package."""
    return Reform.from_dict(
        {
            "gov.contrib.reconciliation.auto_loan_interest_ald.in_effect": {
                "2025-01-01.2028-12-31": True
            },
            "gov.contrib.reconciliation.auto_loan_interest_ald.senate_version.applies": {
                "2025-01-01.2100-12-31": True
            },
        },
        country_id="us",
    )


def senate_finance_cdcc_reform():
    """Child and Dependent Care Credit reform from Senate Finance package."""
    return Reform.from_dict(
        {
            "gov.irs.credits.cdcc.phase_out.max": {"2026-01-01.2100-12-31": 0.5},
            "gov.irs.credits.cdcc.phase_out.min": {"2026-01-01.2100-12-31": 0.35},
            "gov.contrib.reconciliation.cdcc.in_effect": {
                "2026-01-01.2100-12-31": True
            },
            "gov.contrib.reconciliation.cdcc.phase_out.second_start.SURVIVING_SPOUSE": {
                "2025-01-01.2100-12-31": 75000
            },
            "gov.contrib.reconciliation.cdcc.phase_out.second_increment.SURVIVING_SPOUSE": {
                "2025-01-01.2100-12-31": 2000
            },
        },
        country_id="us",
    )


def senate_finance_aca_enhanced_subsidies_reform():
    return Reform.from_dict(
        {
            "gov.aca.ptc_phase_out_rate[0].amount": {"2026-01-01.2100-12-31": 0.02},
            "gov.aca.ptc_phase_out_rate[1].threshold": {"2026-01-01.2100-12-31": 1.33},
            "gov.aca.ptc_phase_out_rate[1].amount": {"2025-01-01.2100-12-31": 0.03},
            "gov.aca.ptc_phase_out_rate[2].amount": {"2026-01-01.2100-12-31": 0.04},
            "gov.aca.ptc_phase_out_rate[3].amount": {"2026-01-01.2100-12-31": 0.063},
            "gov.aca.ptc_phase_out_rate[4].amount": {"2026-01-01.2100-12-31": 0.0805},
            "gov.aca.ptc_phase_out_rate[5].amount": {"2026-01-01.2100-12-31": 0.095},
            "gov.aca.ptc_phase_out_rate[6].amount": {"2026-01-01.2100-12-31": 0.095},
            "gov.aca.ptc_income_eligibility[2].amount": {
                "2026-01-01.2100-12-31": False
            },
        },
        country_id="us",
    )


def senate_finance_snap_takeup_reform():
    return Reform.from_dict(
        {
            "gov.usda.snap.takeup_rate": {"2026-01-01.2028-12-31": 0.775},
        },
        country_id="us",
    )


def senate_finance_aca_takeup_reform():
    return Reform.from_dict(
        {
            "gov.aca.takeup_rate": {"2026-01-01.2028-12-31": 0.655},
        },
        country_id="us",
    )


def senate_finance_medicaid_takeup_reform():
    return Reform.from_dict(
        {
            "gov.hhs.medicaid.takeup_rate": {"2026-01-01.2028-12-31": 0.92},
        },
        country_id="us",
    )


def get_all_senate_finance_reforms():
    """Get dictionary of all Senate Finance reform components."""
    return {
        "Tax Rate Reform": senate_finance_tax_rate_reform(),
        "Standard Deduction Reform": senate_finance_sd_reform(),
        "Exemption Reform": senate_finance_exemption_reform(),
        "Child tax credit social security number requirement": senate_finance_ctc_ssn_reform(),
        "Child tax credit expansion": senate_finance_ctc_expansion_reform(),
        "Qualified business interest deduction reform": senate_finance_qbid_reform(),
        "Alternative minimum tax reform": senate_finance_amt_reform(),
        "Miscellaneous deduction reform": senate_finance_misc_reform(),
        "Charitable deductions reform": senate_finance_charitable_ded_reform(),
        "Casualty loss deduction repeal": senate_finance_casualty_loss_reform(),
        "Pease repeal": senate_finance_pease_repeal_reform(),
        "Limitation on itemized deductions reform": senate_finance_limitation_on_itemized_deductions_reform(),
        "Estate tax reform": senate_finance_estate_tax_reform(),
        "New senior deduction": senate_finance_senior_deduction_reform(),
        "Tip exemption": senate_finance_tip_reform(),
        "Overtime exemption": senate_finance_overtime_reform(),
        "Auto loan interest deduction": senate_finance_auto_loan_reform(),
        "Cap on state and local tax deduction": senate_finance_salt_reform(),
        "Child and dependent care credit reform": senate_finance_cdcc_reform(),
        "Extension of ACA enhanced subsidies": senate_finance_aca_enhanced_subsidies_reform(),
        "SNAP reform": senate_finance_snap_takeup_reform(),
        "ACA reform": senate_finance_aca_takeup_reform(),
        "Medicaid reform": senate_finance_medicaid_takeup_reform(),
    }
