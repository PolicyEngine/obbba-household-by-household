// Dataset configuration
export const datasets = {
  'tcja-expiration': {
    filename: 'household_tax_income_changes_current_law_baseline.csv',
    label: 'TCJA expiration',
    description: 'Analysis showing impact if TCJA provisions expire'
  },
  'tcja-extension': {
    filename: 'household_tax_income_changes_tcja_baseline.csv',
    label: 'TCJA extension',
    description: 'Analysis showing impact if TCJA provisions are extended'
  }
};

export const defaultDataset = 'tcja-expiration';

// Export DATASETS as an alias for compatibility
export const DATASETS = datasets;