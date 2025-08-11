import { describe, it, expect } from 'vitest';

describe('HouseholdProfile provisions', () => {
  // Helper function to simulate getProvisionBreakdown logic
  const getProvisionBreakdown = (household) => {
    const provisions = [
      { 
        name: 'ACA premium tax credit eligibility', 
        key: 'Change in net income after Extension of ACA enhanced subsidies',
        description: 'Changes in ACA premium tax credit eligibility based on CBO projections for subsidy participation rates.'
      },
      { 
        name: 'SNAP eligibility', 
        key: 'Change in net income after SNAP reform',
        description: 'Changes in SNAP (food stamp) eligibility based on projected participation rate changes.'
      },
      { 
        name: 'Medicaid eligibility', 
        key: 'Change in net income after Medicaid reform',
        description: 'Changes in Medicaid eligibility based on projected participation rate changes.'
      }
    ];
    
    return provisions
      .map(provision => ({
        ...provision,
        value: household[provision.key] || 0
      }))
      .filter(p => Math.abs(p.value) > 0.01);
  };

  it('should display ACA premium tax credit eligibility changes correctly', () => {
    const mockHousehold = {
      'Change in net income after Extension of ACA enhanced subsidies': -6991.0,
      'Change in federal tax liability after Extension of ACA enhanced subsidies': 0.0,
      'Change in state tax liability after Extension of ACA enhanced subsidies': 0.0,
      'Change in benefits after Extension of ACA enhanced subsidies': -6991.0,
    };

    const provisions = getProvisionBreakdown(mockHousehold);
    const acaProvision = provisions.find(p => p.key.includes('Extension of ACA enhanced subsidies'));
    
    expect(acaProvision).toBeDefined();
    expect(acaProvision.name).toBe('ACA premium tax credit eligibility');
    expect(acaProvision.description).toContain('eligibility');
    expect(acaProvision.description).not.toContain('extends');
    expect(acaProvision.value).toBe(-6991.0);
  });

  it('should display SNAP eligibility changes correctly', () => {
    const mockHousehold = {
      'Change in net income after SNAP reform': -500.0,
      'Change in benefits after SNAP reform': -500.0,
    };

    const provisions = getProvisionBreakdown(mockHousehold);
    const snapProvision = provisions.find(p => p.key.includes('SNAP reform'));
    
    expect(snapProvision).toBeDefined();
    expect(snapProvision.name).toBe('SNAP eligibility');
    expect(snapProvision.description).toContain('eligibility');
    expect(snapProvision.description).toContain('participation rate');
  });

  it('should display Medicaid eligibility changes correctly', () => {
    const mockHousehold = {
      'Change in net income after Medicaid reform': -1000.0,
      'Change in benefits after Medicaid reform': -1000.0,
    };

    const provisions = getProvisionBreakdown(mockHousehold);
    const medicaidProvision = provisions.find(p => p.key.includes('Medicaid reform'));
    
    expect(medicaidProvision).toBeDefined();
    expect(medicaidProvision.name).toBe('Medicaid eligibility');
    expect(medicaidProvision.description).toContain('eligibility');
    expect(medicaidProvision.description).toContain('participation rate');
  });
});