import { describe, expect, it } from 'vitest';
import {
  PARTICIPATION_START,
  PROVISIONS,
  RECONCILIATION_TOLERANCE,
  SPLIT_THRESHOLD,
  getProvisionBreakdown,
  getTotalsSplit,
  selectTotalsHeadline
} from './provisionBreakdown.js';

// Household 1009324 (OH, 10 people) from
// static/household_tax_income_changes_microcosm_buildp.csv, verbatim. Its
// standard-deduction step is almost entirely a benefits change, which is the
// case the split exists to surface.
const HOUSEHOLD_1009324 = {
  id: '1009324',
  State: 'OH',
  'Household Size': 10,
  'Baseline Net Income': 177020.42,
  'Change in federal tax liability after Tax Rate Reform': -754.27344,
  'Change in state tax liability after Tax Rate Reform': 0,
  'Change in benefits after Tax Rate Reform': 0,
  'Change in net income after Tax Rate Reform': 754.28125,
  'Change in federal tax liability after Standard Deduction Reform': -315.47461,
  'Change in state tax liability after Standard Deduction Reform': 0,
  'Change in benefits after Standard Deduction Reform': 55654.736,
  'Change in net income after Standard Deduction Reform': 55970.205,
  'Change in federal tax liability after CTC Expansion': -2775.0002,
  'Change in state tax liability after CTC Expansion': 0,
  'Change in benefits after CTC Expansion': 0,
  'Change in net income after CTC Expansion': 2775,
  'Total change in federal tax liability': -2060.5032,
  'Total change in state tax liability': 0,
  'Total change in benefits': 55654.736,
  'Total change in net income': 57715.251,
  'Percentage change in net income': 32.603725
};

// Household 1002071 from the same file: the SNAP participation scenario moves
// both a state tax and benefits, so it splits without being a tax provision.
const HOUSEHOLD_1002071 = {
  id: '1002071',
  'Change in federal tax liability after SNAP Takeup Reform': 0,
  'Change in state tax liability after SNAP Takeup Reform': -902.89648,
  'Change in benefits after SNAP Takeup Reform': -9472.7891,
  'Change in net income after SNAP Takeup Reform': -8569.8906
};

const byName = (rows, name) => rows.find((row) => row.name === name);

describe('PROVISIONS', () => {
  it('keeps the paper forward-stacking order and the tax/participation boundary', () => {
    expect(PROVISIONS).toHaveLength(21);
    expect(PROVISIONS[0].name).toBe('Tax rates');
    expect(PROVISIONS[1].name).toBe('Standard deduction');
    expect(PARTICIPATION_START).toBe(18);
    expect(PROVISIONS[PARTICIPATION_START - 1].name).toBe('Auto loan interest deduction');
    expect(PROVISIONS.slice(PARTICIPATION_START).map((p) => p.name)).toEqual([
      'SNAP participation',
      'ACA participation',
      'Medicaid participation'
    ]);
  });
});

describe('getProvisionBreakdown', () => {
  it('returns nothing without a household', () => {
    expect(getProvisionBreakdown(null)).toEqual([]);
    expect(getProvisionBreakdown(undefined)).toEqual([]);
  });

  it('splits household 1009324 standard deduction into tax and benefits', () => {
    const row = byName(getProvisionBreakdown(HOUSEHOLD_1009324), 'Standard deduction');

    expect(row.value).toBeCloseTo(55970.205, 3);
    // -(federal + state): the $315 federal cut is a gain for the household.
    expect(row.taxChange).toBeCloseTo(315.47461, 5);
    expect(row.benefitsChange).toBeCloseTo(55654.736, 3);
    expect(row.showSplit).toBe(true);
    expect(row.isTaxProvision).toBe(true);
  });

  it('shows no split for household 1009324 tax rates, which is tax only', () => {
    const row = byName(getProvisionBreakdown(HOUSEHOLD_1009324), 'Tax rates');

    expect(row.value).toBeCloseTo(754.28125, 5);
    expect(row.taxChange).toBeCloseTo(754.27344, 5);
    expect(row.benefitsChange).toBe(0);
    expect(row.showSplit).toBe(false);
  });

  it('shows no split for household 1009324 CTC expansion, which is tax only', () => {
    const row = byName(getProvisionBreakdown(HOUSEHOLD_1009324), 'CTC expansion');

    expect(row.value).toBeCloseTo(2775, 5);
    expect(row.taxChange).toBeCloseTo(2775.0002, 5);
    expect(row.benefitsChange).toBe(0);
    expect(row.showSplit).toBe(false);
  });

  it('reconciles each row: value equals tax plus benefits', () => {
    for (const row of getProvisionBreakdown(HOUSEHOLD_1009324)) {
      expect(row.taxChange + row.benefitsChange).toBeCloseTo(row.value, 1);
    }
  });

  it('keeps rows in the stacking order and drops untouched provisions', () => {
    const rows = getProvisionBreakdown(HOUSEHOLD_1009324);

    expect(rows.map((row) => row.name)).toEqual([
      'Tax rates',
      'Standard deduction',
      'CTC expansion'
    ]);
    expect(rows.map((row) => row.index)).toEqual([0, 1, 4]);
  });

  it('splits a participation scenario that moves a tax and benefits', () => {
    const row = byName(getProvisionBreakdown(HOUSEHOLD_1002071), 'SNAP participation');

    expect(row.taxChange).toBeCloseTo(902.89648, 5);
    expect(row.benefitsChange).toBeCloseTo(-9472.7891, 4);
    expect(row.showSplit).toBe(true);
    expect(row.isTaxProvision).toBe(false);
  });

  it('ignores components below the split threshold', () => {
    const rows = getProvisionBreakdown({
      'Change in federal tax liability after Tax Rate Reform': -1000,
      'Change in benefits after Tax Rate Reform': 0.4,
      'Change in net income after Tax Rate Reform': 1000.4
    });

    expect(SPLIT_THRESHOLD).toBe(0.5);
    expect(rows[0].benefitsChange).toBe(0.4);
    expect(rows[0].showSplit).toBe(false);
  });

  it('reads the district column vocabulary, which omits "liability"', () => {
    const row = byName(
      getProvisionBreakdown({
        'Change in federal tax after Standard Deduction Reform': -200,
        'Change in state tax after Standard Deduction Reform': -50,
        'Change in benefits after Standard Deduction Reform': 800,
        'Change in net income after Standard Deduction Reform': 1050
      }),
      'Standard deduction'
    );

    expect(row.taxChange).toBe(250);
    expect(row.benefitsChange).toBe(800);
    expect(row.showSplit).toBe(true);
  });

  it('parses numeric strings, as PapaParse leaves them when typing is off', () => {
    const row = byName(
      getProvisionBreakdown({
        'Change in federal tax liability after Standard Deduction Reform': '-315.47461',
        'Change in benefits after Standard Deduction Reform': '55654.736',
        'Change in net income after Standard Deduction Reform': 55970.205
      }),
      'Standard deduction'
    );

    expect(row.taxChange).toBeCloseTo(315.47461, 5);
    expect(row.benefitsChange).toBeCloseTo(55654.736, 3);
    expect(row.showSplit).toBe(true);
  });
});

describe('getTotalsSplit', () => {
  it('is inert without a household', () => {
    expect(getTotalsSplit(null)).toEqual({
      federalChange: 0,
      stateChange: 0,
      taxChange: 0,
      benefitsChange: 0,
      netChange: 0,
      showSplit: false
    });
  });

  it('splits household 1009324 totals and reconciles with the headline', () => {
    const totals = getTotalsSplit(HOUSEHOLD_1009324);

    expect(totals.taxChange).toBeCloseTo(2060.5032, 4);
    expect(totals.benefitsChange).toBeCloseTo(55654.736, 3);
    expect(totals.showSplit).toBe(true);
    expect(totals.taxChange + totals.benefitsChange).toBeCloseTo(
      HOUSEHOLD_1009324['Total change in net income'],
      1
    );
  });

  it('shows the split when only one side moves', () => {
    expect(
      getTotalsSplit({
        'Total change in federal tax liability': -1200,
        'Total change in net income': 1200
      }).showSplit
    ).toBe(true);
    expect(
      getTotalsSplit({
        'Total change in benefits': -1200,
        'Total change in net income': -1200
      }).showSplit
    ).toBe(true);
  });

  it('hides the split when nothing moves', () => {
    expect(
      getTotalsSplit({
        'Total change in federal tax liability': 0,
        'Total change in state tax liability': 0,
        'Total change in benefits': 0
      }).showSplit
    ).toBe(false);
  });

  it('reads the district total columns', () => {
    const totals = getTotalsSplit({
      'Total change in federal tax': -900,
      'Total change in state tax': 100,
      'Total change in benefits': 250,
      'Total change in net income': 1050
    });

    expect(totals.taxChange).toBe(800);
    expect(totals.benefitsChange).toBe(250);
    expect(totals.netChange).toBe(1050);
    expect(totals.showSplit).toBe(true);
  });
});

// Households 9275325 and 9275596 from static/districts/tcja-extension/
// district_601.csv, verbatim. The district files record a Medicaid
// participation benefit change that their net-income columns omit, so a split
// would contradict the headline it sits under.
const DISTRICT_9275325 = {
  'Household ID': '9275325',
  State: 'CA',
  'Change in benefits after Medicaid Takeup Reform': -22373.060546875,
  'Total change in federal tax': 0,
  'Total change in state tax': 0,
  'Total change in net income': 0,
  'Total change in benefits': -22373.060546875
};
const DISTRICT_9275596 = {
  'Household ID': '9275596',
  State: 'CA',
  'Change in federal tax after Tax Rate Reform': -5,
  'Change in net income after Tax Rate Reform': 5,
  'Change in federal tax after Standard Deduction Reform': -304,
  'Change in net income after Standard Deduction Reform': 304,
  'Change in benefits after Medicaid Takeup Reform': -22373.060546875,
  'Total change in federal tax': -309,
  'Total change in state tax': 0,
  'Total change in net income': 309,
  'Total change in benefits': -22373.060546875
};

describe('reconciliation guard', () => {
  it('uses the tolerance the export validator enforces', () => {
    expect(RECONCILIATION_TOLERANCE).toBe(1.25);
  });

  it('hides a totals split whose parts add to $22,373 less than a $0 headline', () => {
    const totals = getTotalsSplit(DISTRICT_9275325);

    expect(totals.benefitsChange).toBeCloseTo(-22373.06, 2);
    expect(totals.netChange).toBe(0);
    expect(totals.showSplit).toBe(false);
  });

  it('hides a totals split whose parts contradict a +$309 headline', () => {
    const totals = getTotalsSplit(DISTRICT_9275596);

    expect(totals.taxChange).toBe(309);
    expect(totals.showSplit).toBe(false);
    // Its tax-only provision rows are unaffected: nothing to split.
    const rows = getProvisionBreakdown(DISTRICT_9275596);
    expect(rows.map((row) => row.name)).toEqual(['Tax rates', 'Standard deduction']);
    expect(rows.every((row) => !row.showSplit)).toBe(true);
  });

  it('hides a provision split whose parts do not add to its value', () => {
    const [row] = getProvisionBreakdown({
      'Change in federal tax liability after Standard Deduction Reform': -1000,
      'Change in benefits after Standard Deduction Reform': 500,
      'Change in net income after Standard Deduction Reform': 1000
    });

    expect(row.showSplit).toBe(false);
  });

  it('hides a totals split when a missing tax column would read as zero', () => {
    expect(
      getTotalsSplit({ 'Total change in benefits': 20, 'Total change in net income': 100 })
        .showSplit
    ).toBe(false);
  });

  it('reads the totals headline exactly as the profile renders it', () => {
    // The profile renders `a || b || 0`, so a zero primary falls through.
    expect(
      selectTotalsHeadline({
        'Total change in net income': 0,
        'Change in Household Net Income': 1000
      })
    ).toBe(1000);
    expect(selectTotalsHeadline({ 'Total change in net income': '57715.251' })).toBe('57715.251');
    expect(selectTotalsHeadline({})).toBe(0);
  });

  it('hides a totals split checked against a headline the profile would not render', () => {
    const totals = getTotalsSplit({
      'Total change in net income': 0,
      'Change in Household Net Income': 1000,
      'Total change in federal tax liability': -100,
      'Total change in benefits': -100
    });

    expect(totals.netChange).toBe(1000);
    expect(totals.showSplit).toBe(false);
  });

  it('hides a totals split under a missing or unparseable headline', () => {
    const parts = {
      'Total change in federal tax liability': -100,
      'Total change in benefits': -100
    };

    expect(getTotalsSplit({ ...parts, 'Total change in net income': 'NaN' }).showSplit).toBe(false);
    expect(getTotalsSplit({ ...parts, 'Total change in net income': 'n/a' }).showSplit).toBe(false);
    expect(getTotalsSplit({ ...parts, 'Total change in net income': NaN }).showSplit).toBe(false);
    // Both columns absent: the profile falls back to $0, which is not data.
    expect(getTotalsSplit(parts).showSplit).toBe(false);
  });

  it('keeps a split whose residual is within the tolerance and drops one just past it', () => {
    const split = (residual) =>
      getProvisionBreakdown({
        'Change in federal tax liability after Standard Deduction Reform': -1000,
        'Change in benefits after Standard Deduction Reform': 500,
        'Change in net income after Standard Deduction Reform': 1500 + residual
      })[0].showSplit;

    expect(split(1.25)).toBe(true);
    expect(split(-1.25)).toBe(true);
    expect(split(1.26)).toBe(false);
    expect(split(-1.26)).toBe(false);
  });
});

describe('numeric coercion', () => {
  it('returns a numeric value even from the string-typed preview parse', () => {
    const [row] = getProvisionBreakdown({
      'Change in federal tax liability after Tax Rate Reform': '-754.27344',
      'Change in net income after Tax Rate Reform': '754.28125'
    });

    expect(typeof row.value).toBe('number');
    expect(row.value).toBeCloseTo(754.28125, 5);
  });

  it('drops a provision whose only value is an unparseable string', () => {
    expect(getProvisionBreakdown({ 'Change in net income after Tax Rate Reform': 'n/a' })).toEqual(
      []
    );
  });
});
