import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import HouseholdProfile from './HouseholdProfile.svelte';

describe('HouseholdProfile', () => {
  const mockHouseholdData = {
    'Household weight': 1000,
    'FIPS': '12345',
    'Household income': 50000,
    'Change in net income after Extension of ACA enhanced subsidies': -1000,
    'Change in net income after SNAP reform': -500,
    'Change in net income after Medicaid reform': -300
  };

  it('displays correct ACA benefit label', () => {
    const { getByText } = render(HouseholdProfile, {
      props: {
        householdData: mockHouseholdData,
        dataset: 'tcja_expiration'
      }
    });

    expect(getByText('ACA premium tax credit eligibility')).toBeTruthy();
  });

  it('displays correct SNAP benefit label', () => {
    const { getByText } = render(HouseholdProfile, {
      props: {
        householdData: mockHouseholdData,
        dataset: 'tcja_expiration'
      }
    });

    expect(getByText('SNAP eligibility')).toBeTruthy();
  });

  it('displays correct Medicaid benefit label', () => {
    const { getByText } = render(HouseholdProfile, {
      props: {
        householdData: mockHouseholdData,
        dataset: 'tcja_expiration'
      }
    });

    expect(getByText('Medicaid eligibility')).toBeTruthy();
  });

  it('displays accurate ACA description', () => {
    const { getByText } = render(HouseholdProfile, {
      props: {
        householdData: mockHouseholdData,
        dataset: 'tcja_expiration'
      }
    });

    expect(getByText('Changes in ACA premium tax credit eligibility based on CBO projections for subsidy participation rates.')).toBeTruthy();
  });

  it('displays accurate SNAP description', () => {
    const { getByText } = render(HouseholdProfile, {
      props: {
        householdData: mockHouseholdData,
        dataset: 'tcja_expiration'
      }
    });

    expect(getByText('Changes in SNAP (food stamp) eligibility based on projected participation rate changes.')).toBeTruthy();
  });

  it('displays accurate Medicaid description', () => {
    const { getByText } = render(HouseholdProfile, {
      props: {
        householdData: mockHouseholdData,
        dataset: 'tcja_expiration'
      }
    });

    expect(getByText('Changes in Medicaid eligibility based on projected participation rate changes.')).toBeTruthy();
  });
});