import Papa from 'papaparse';

// Map old column names to new shorter names
const COLUMN_MAPPING = {
  'id': 'Household ID',
  'state': 'State', 
  'household_weight': 'Household Weight',
  'market_income': 'Market Income',
  'baseline_net_income': 'Baseline Net Income',
  'total_change_net_income': 'Total Change in Net Income',
  'pct_change_net_income': 'Percentage Change in Net Income',
  'household_size': 'Household Size',
  'num_dependents': 'Number of Dependents',
  'age_head': 'Age of Head',
  'age_spouse': 'Age of Spouse',
  'is_married': 'Is Married'
};

// Map provision names to expected column format
const PROVISION_COLUMN_FORMAT = {
  'Rate Adjustment': 'Change in Net income after Rate Adjustments',
  'Standard Deduction Increase': 'Change in Net income after Standard deduction increase',
  'Exemption Repeal': 'Change in Net income after Exemption Reform',
  'Child Tax Credit Social Security Number Requirement': 'Change in Net income after Child Tax Credit Social Security Number Requirement',
  'Child Tax Credit Expansion': 'Change in Net income after Child Tax Credit Expansion',
  'Qualified Business Income Deduction Reform': 'Change in Net income after Qualified Business Interest Deduction Reform',
  'Alternative Minimum Tax Reform': 'Change in Net income after Alternative Minimum Tax Reform',
  'Miscellaneous Deductions Reform': 'Change in Net income after Miscellaneous Deduction Reform',
  'Charitable Deductions Reform': 'Change in Net income after Charitable Deductions Reform',
  'Casualty Loss Deductions Repeal': 'Change in Net income after Casualty Loss Deductions Repeal',
  'Pease Repeal': 'Change in Net income after Pease Repeal',
  'Limitation on Itemized Deductions Reform': 'Change in Net income after Limitation on Itemized Deductions Reform',
  'Estate Tax Reform': 'Change in Net income after Estate Tax Reform',
  'New Senior Deduction': 'Change in Net income after New Senior Deduction',
  'Tip Exemption': 'Change in Net income after Tip Exemption',
  'Overtime Exemption': 'Change in Net income after Overtime Exemption',
  'Auto Loan Interest Deduction': 'Change in Net income after Auto Loan Interest Deduction',
  'Cap on State and Local Tax Deduction': 'Change in Net income after Cap on state and local tax deduction',
  'Child and Dependent Care Credit Reform': 'Change in Net income after Child and dependent care credit reform',
  'Extension of ACA Enhanced Subsidies': 'Change in Net income after Extension of ACA Enhanced Subsidies',
  'SNAP Reform': 'Change in Net income after SNAP Reform',
  'Medicaid Reform': 'Change in Net income after Medicaid Reform'
};

// Load CSV file
async function loadCSV(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load CSV: ${response.status} ${response.statusText}`);
  }
  
  const raw = await response.text();
  const result = Papa.parse(raw, {
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true
  });
  
  if (result.errors.length > 0) {
    console.warn('CSV parsing warnings:', result.errors);
  }
  
  return result.data;
}

// Convert optimized format back to original format
function mergeHouseholdsAndProvisions(households, provisions) {
  // Create a map of household_id -> provision impacts
  const provisionMap = new Map();
  
  provisions.forEach(p => {
    const householdId = String(p.household_id);
    if (!provisionMap.has(householdId)) {
      provisionMap.set(householdId, []);
    }
    provisionMap.get(householdId).push(p);
  });
  
  // Convert households to original format
  return households.map(h => {
    // Map basic fields
    const household = {};
    
    // Map columns using COLUMN_MAPPING
    Object.entries(COLUMN_MAPPING).forEach(([newName, oldName]) => {
      if (h.hasOwnProperty(newName)) {
        household[oldName] = h[newName];
      }
    });
    
    // Convert id to string for consistency
    household['Household ID'] = String(h.id);
    
    // Add provision columns (initialize all to 0)
    Object.values(PROVISION_COLUMN_FORMAT).forEach(colName => {
      household[colName] = 0;
    });
    
    // Fill in actual provision values
    const householdProvisions = provisionMap.get(String(h.id)) || [];
    householdProvisions.forEach(p => {
      const columnName = PROVISION_COLUMN_FORMAT[p.provision];
      if (columnName) {
        household[columnName] = p.net_income_change;
      }
    });
    
    // Add some calculated/missing fields
    household['Gross Income'] = h.market_income; // Use market income as gross income
    household['Dependents'] = h.num_dependents; // Alternative name
    
    return household;
  });
}

// Load optimized dataset
export async function loadOptimizedDataset(datasetKey) {
  const base = import.meta.env.BASE_URL || '/';
  const normalizedBase = base.endsWith('/') ? base : base + '/';
  
  // Map dataset keys to file prefixes
  const filePrefixes = {
    'tcja-expiration': 'tcja_expiration',
    'tcja-extension': 'tcja_extension'
  };
  
  const prefix = filePrefixes[datasetKey];
  if (!prefix) {
    throw new Error(`Unknown dataset: ${datasetKey}`);
  }
  
  try {
    // Load both files in parallel
    const [households, provisions] = await Promise.all([
      loadCSV(`${normalizedBase}households_${prefix}.csv`),
      loadCSV(`${normalizedBase}provisions_${prefix}.csv`)
    ]);
    
    // Merge and convert to original format
    return mergeHouseholdsAndProvisions(households, provisions);
  } catch (error) {
    console.error('Error loading optimized data:', error);
    throw error;
  }
}

// Check if optimized files exist
export async function hasOptimizedFiles() {
  const base = import.meta.env.BASE_URL || '/';
  const normalizedBase = base.endsWith('/') ? base : base + '/';
  
  try {
    // Try to fetch just the headers to check if files exist
    const response = await fetch(`${normalizedBase}households_tcja_expiration.csv`, {
      method: 'HEAD'
    });
    return response.ok;
  } catch {
    return false;
  }
}

// Export functions that match the original dataLoader interface
export { loadOptimizedDataset as loadDataset };
export { processData, buildHouseholdMap } from './dataLoader.js';

// Load all datasets with optimized format
export async function loadDatasets() {
  try {
    const [tcjaExpiration, tcjaExtension] = await Promise.all([
      loadOptimizedDataset('tcja-expiration'),
      loadOptimizedDataset('tcja-extension')
    ]);
    
    const { processData } = await import('./dataLoader.js');
    
    return {
      'tcja-expiration': processData(tcjaExpiration),
      'tcja-extension': processData(tcjaExtension)
    };
  } catch (error) {
    console.error('Failed to load optimized datasets:', error);
    throw new Error('Failed to load datasets');
  }
}

// Load datasets progressively
export async function loadDatasetsProgressive(onFirstDatasetLoaded, onSecondDatasetLoaded) {
  const allDatasets = {};
  const { processData } = await import('./dataLoader.js');
  
  try {
    // Load TCJA expiration first
    console.log('Loading primary dataset (TCJA expiration) - optimized format...');
    const tcjaExpiration = await loadOptimizedDataset('tcja-expiration');
    allDatasets['tcja-expiration'] = processData(tcjaExpiration);
    
    // Notify that first dataset is ready
    if (onFirstDatasetLoaded) {
      onFirstDatasetLoaded(allDatasets);
    }
    
    // Load TCJA extension in the background
    console.log('Loading secondary dataset (TCJA extension) in background - optimized format...');
    loadOptimizedDataset('tcja-extension')
      .then(tcjaExtension => {
        allDatasets['tcja-extension'] = processData(tcjaExtension);
        console.log('Secondary dataset loaded successfully');
        
        if (onSecondDatasetLoaded) {
          onSecondDatasetLoaded(allDatasets);
        }
      })
      .catch(error => {
        console.error('Failed to load secondary dataset:', error);
      });
    
    return allDatasets;
  } catch (error) {
    console.error('Failed to load primary dataset:', error);
    throw new Error('Failed to load primary dataset');
  }
}