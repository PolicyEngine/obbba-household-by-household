// Dataset configuration
export const datasets = {
  'tcja-expiration': {
    filename: 'household_tax_income_changes_senate_current_law_baseline.csv',
    label: 'TCJA Expiration',
    description: 'Analysis showing impact if TCJA provisions expire'
  },
  'tcja-extension': {
    filename: 'household_tax_income_changes_senate_tcja_baseline.csv',
    label: 'TCJA Extension',
    description: 'Analysis showing impact if TCJA provisions are extended'
  }
};

export const defaultDataset = 'tcja-expiration';