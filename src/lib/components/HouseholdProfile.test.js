import { describe, expect, it, vi, beforeAll } from 'vitest';
import { fireEvent, render } from '@testing-library/svelte';
import { tick } from 'svelte';
import HouseholdProfile from './HouseholdProfile.svelte';
import { getProvisionBreakdown } from './provisionBreakdown.js';

// Household 1009324 (OH, 10 people) from
// static/household_tax_income_changes_microcosm_buildp.csv, verbatim. Almost
// all of its $55,970 standard-deduction gain is a benefits change.
const HOUSEHOLD_1009324 = {
  id: '1009324',
  State: 'OH',
  'Household Size': 10,
  'Age of Head': 56,
  'Is Married': 'False',
  'Number of Dependents': 2,
  'Market Income': 171677.7,
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

// Household 9275325 from static/districts/tcja-extension/district_601.csv,
// verbatim. The district files record a Medicaid participation benefit change
// that their net-income columns omit, so the parts do not add to the headline.
const DISTRICT_HOUSEHOLD_9275325 = {
  'Household ID': '9275325',
  State: 'CA',
  'Change in benefits after Medicaid Takeup Reform': -22373.060546875,
  'Total change in federal tax': 0,
  'Total change in state tax': 0,
  'Total change in net income': 0,
  'Total change in benefits': -22373.060546875
};

// The value span also carries the hover tooltip; read only the headline text.
function headlineValue(row) {
  const clone = row.querySelector('.value.impact').cloneNode(true);
  clone.querySelector('.breakdown-tooltip')?.remove();
  return clone.textContent.trim();
}

function provisionRow(container, name) {
  return [...container.querySelectorAll('.provision-item')].find((item) =>
    item.querySelector('.provision-label')?.textContent.trim().startsWith(name)
  );
}

async function renderExpanded(household) {
  const result = render(HouseholdProfile, { props: { household } });
  await fireEvent.click(result.getByRole('button', { name: /show provisions/i }));
  await tick();
  return result;
}

beforeAll(() => {
  // jsdom has no layout, so the reveal-on-expand scroll is a no-op here.
  Element.prototype.scrollIntoView = vi.fn();
});

describe('HouseholdProfile headline split', () => {
  it('shows the total taxes and benefits under the change in resources', () => {
    const { container } = render(HouseholdProfile, { props: { household: HOUSEHOLD_1009324 } });
    const split = container.querySelector('[data-testid="totals-split"]');

    expect(split).not.toBeNull();
    // -(federal + state) = +$2,061; a tax cut reads as a gain.
    expect(split.textContent).toMatch(/Taxes\s*\+\$2,061/);
    expect(split.textContent).toMatch(/Benefits\s*\+\$55,655/);
  });

  it('states the sign convention once', () => {
    const { container } = render(HouseholdProfile, { props: { household: HOUSEHOLD_1009324 } });
    const notes = container.querySelectorAll('.sign-convention-note');

    expect(notes).toHaveLength(1);
    expect(notes[0].textContent.trim()).toBe(
      'Taxes and benefits are shown as their effect on household resources, so a tax cut is positive. The parts may not add exactly to the total because of rounding.'
    );
  });

  it('omits the totals split when neither total moves', () => {
    const { container } = render(HouseholdProfile, {
      props: {
        household: {
          id: '1',
          State: 'OH',
          'Total change in federal tax liability': 0,
          'Total change in state tax liability': 0,
          'Total change in benefits': 0,
          'Total change in net income': 0
        }
      }
    });

    expect(container.querySelector('[data-testid="totals-split"]')).toBeNull();
    expect(container.querySelector('.sign-convention-note')).toBeNull();
  });

  it('checks the split against the headline it renders when both aliases are present', () => {
    // 'Total change in net income' is 0, so the profile renders the alias
    // (+$1,000); parts adding to $0 must not be drawn under it.
    const { container } = render(HouseholdProfile, {
      props: {
        household: {
          id: '2',
          State: 'OH',
          'Total change in net income': 0,
          'Change in Household Net Income': 1000,
          'Total change in federal tax liability': -100,
          'Total change in benefits': -100
        }
      }
    });

    expect(container.querySelector('[data-testid="totals-split"]')).toBeNull();
  });

  it('omits the totals split under an unparseable headline', () => {
    const { container } = render(HouseholdProfile, {
      props: {
        household: {
          id: '3',
          State: 'OH',
          'Total change in net income': 'NaN',
          'Total change in federal tax liability': -100,
          'Total change in benefits': -100
        }
      }
    });

    expect(container.querySelector('[data-testid="totals-split"]')).toBeNull();
  });

  it('omits the totals split when the parts do not add to the headline', () => {
    const { container } = render(HouseholdProfile, {
      props: { household: DISTRICT_HOUSEHOLD_9275325 }
    });

    expect(container.querySelector('[data-testid="totals-split"]')).toBeNull();
    expect(container.querySelector('.sign-convention-note')).toBeNull();
  });
});

describe('HouseholdProfile provision rows', () => {
  it('splits the standard-deduction row into taxes and benefits', async () => {
    const { container } = await renderExpanded(HOUSEHOLD_1009324);
    const row = provisionRow(container, 'Standard deduction');

    expect(headlineValue(row)).toBe('+$55,970');

    const split = row.querySelector('.component-split');
    expect(split).not.toBeNull();
    expect(split.textContent).toMatch(/Taxes\s*\+\$315/);
    expect(split.textContent).toMatch(/Benefits\s*\+\$55,655/);
  });

  it('leaves the tax-rate row unsplit', async () => {
    const { container } = await renderExpanded(HOUSEHOLD_1009324);
    const row = provisionRow(container, 'Tax rates');

    expect(headlineValue(row)).toBe('+$754');
    expect(row.querySelector('.component-split')).toBeNull();
  });

  it('leaves the CTC expansion row unsplit', async () => {
    const { container } = await renderExpanded(HOUSEHOLD_1009324);
    const row = provisionRow(container, 'CTC expansion');

    expect(headlineValue(row)).toBe('+$2,775');
    expect(row.querySelector('.component-split')).toBeNull();
  });

  it('splits exactly one row across the expanded panel', async () => {
    const { container } = await renderExpanded(HOUSEHOLD_1009324);

    expect(container.querySelectorAll('.provision-item .component-split')).toHaveLength(1);
    expect(container.querySelectorAll('.provision-item')).toHaveLength(3);
  });

  it('splits a participation scenario that moves a tax and benefits', async () => {
    // Household 1002071 from the same export: its SNAP participation step moves
    // a state tax and benefits together.
    const { container } = await renderExpanded({
      id: '1002071',
      State: 'OH',
      'Change in federal tax liability after SNAP Takeup Reform': 0,
      'Change in state tax liability after SNAP Takeup Reform': -902.89648,
      'Change in benefits after SNAP Takeup Reform': -9472.7891,
      'Change in net income after SNAP Takeup Reform': -8569.8906
    });
    const row = provisionRow(container, 'SNAP participation');

    expect(row.querySelector('.component-split').textContent).toMatch(/Taxes\s*\+\$903/);
    expect(row.querySelector('.component-split').textContent).toMatch(/Benefits\s*-\$9,473/);
  });
});

describe('HouseholdProfile participation labels', () => {
  it('labels the ACA result as a participation scenario', () => {
    const provisions = getProvisionBreakdown({
      'Change in net income after ACA Takeup Reform': -6991.0,
      'Change in benefits after ACA Takeup Reform': -6991.0
    });
    const acaProvision = provisions.find((p) => p.name === 'ACA participation');

    expect(acaProvision).toBeDefined();
    expect(acaProvision.description).toContain('reduced-form');
    expect(acaProvision.description).not.toContain('eligibility');
    expect(acaProvision.value).toBe(-6991.0);
    expect(acaProvision.isTaxProvision).toBe(false);
  });

  it('labels the SNAP result as a participation scenario', () => {
    const provisions = getProvisionBreakdown({
      'Change in net income after SNAP Takeup Reform': -500.0,
      'Change in benefits after SNAP Takeup Reform': -500.0
    });
    const snapProvision = provisions.find((p) => p.name === 'SNAP participation');

    expect(snapProvision).toBeDefined();
    expect(snapProvision.description).toContain('reduced-form');
    expect(snapProvision.isTaxProvision).toBe(false);
  });

  it('labels the Medicaid result as a participation scenario', () => {
    const provisions = getProvisionBreakdown({
      'Change in net income after Medicaid Takeup Reform': -1000.0,
      'Change in benefits after Medicaid Takeup Reform': -1000.0
    });
    const medicaidProvision = provisions.find((p) => p.name === 'Medicaid participation');

    expect(medicaidProvision).toBeDefined();
    expect(medicaidProvision.description).toContain('reduced-form');
    expect(medicaidProvision.isTaxProvision).toBe(false);
  });
});
