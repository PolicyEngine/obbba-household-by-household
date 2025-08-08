import Papa from 'papaparse';
import { DATASETS } from '../config/datasets.js';

// Map dataset keys to their sample files
const SAMPLE_FILES = {
  'tcja-expiration': {
    micro: 'samples/household_tax_income_changes_senate_current_law_baseline_sample_micro.csv',
    small: 'samples/household_tax_income_changes_senate_current_law_baseline_sample_small.csv',
    medium: 'samples/household_tax_income_changes_senate_current_law_baseline_sample_medium.csv',
    large: 'samples/household_tax_income_changes_senate_current_law_baseline_sample_large.csv',
    full: 'household_tax_income_changes_senate_current_law_baseline.csv'
  },
  'tcja-extension': {
    micro: 'samples/household_tax_income_changes_senate_tcja_baseline_sample_micro.csv',
    small: 'samples/household_tax_income_changes_senate_tcja_baseline_sample_small.csv',
    medium: 'samples/household_tax_income_changes_senate_tcja_baseline_sample_medium.csv',
    large: 'samples/household_tax_income_changes_senate_tcja_baseline_sample_large.csv',
    full: 'household_tax_income_changes_senate_tcja_baseline.csv'
  }
};

// Load a specific sample size for a dataset
export async function loadDatasetSample(datasetKey, sampleSize = 'full') {
  const samples = SAMPLE_FILES[datasetKey];
  if (!samples) {
    throw new Error(`Unknown dataset: ${datasetKey}`);
  }
  
  const filename = samples[sampleSize];
  if (!filename) {
    throw new Error(`Unknown sample size: ${sampleSize}`);
  }
  
  // Handle base path for both dev and production
  const base = import.meta.env.BASE_URL || '/';
  const normalizedBase = base.endsWith('/') ? base : base + '/';
  const url = `${normalizedBase}${filename}`;
  
  console.log(`Loading ${sampleSize} sample from: ${url}`);
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      console.error(`Failed to load CSV from ${url}: ${response.status} ${response.statusText}`);
      throw new Error(`Failed to load CSV: ${response.status} ${response.statusText}`);
    }
    
    const raw = await response.text();
    
    // Parse CSV (samples are small enough to not need workers)
    const result = Papa.parse(raw, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      fastMode: true
    });
    
    if (result.errors.length > 0) {
      console.warn('CSV parsing warnings:', result.errors);
    }
    
    return result.data;
  } catch (error) {
    console.error(`Error loading ${sampleSize} sample:`, error);
    throw error;
  }
}

// Process data with minimal overhead for samples
export function processDataMinimal(rawData) {
  return rawData.map((d, i) => ({
    // Essential fields for visualization
    'Market Income': d['Market Income'] || 0,
    'Total change in net income': d['Total change in net income'] || d['Change in Household Net Income'] || 0,
    'Percentage change in net income': d['Percentage change in net income'] || 0,
    'Household weight': d['Household weight'] || 1,
    id: String(d['Household ID'] || i),
    householdId: d['Household ID'],
    // Basic demographics
    'Number of Dependents': d['Number of Dependents'] || d['Dependents'] || 0,
    'Age of Head': d['Age of Head'] || d['Age'] || 40,
    'Is Married': !!(d['Is Married'] === true || d['Is Married'] === 'True' || d['Is Married'] === 1 || d['Is Married'] === '1'),
  }));
}

// Process data with all fields
export function processDataFull(rawData) {
  return rawData.map((d, i) => ({
    ...d,
    // Ensure consistent types
    'Market Income': Number(d['Market Income']) || 0,
    'Total change in net income': Number(d['Total change in net income'] || d['Change in Household Net Income']) || 0,
    'Percentage change in net income': Number(d['Percentage change in net income']) || 0,
    'Household weight': Number(d['Household weight']) || 1,
    'Number of Dependents': Number(d['Number of Dependents'] || d['Dependents']) || 0,
    'Age of Head': Number(d['Age of Head'] || d['Age']) || 40,
    'Is Married': !!(d['Is Married'] === true || d['Is Married'] === 'True' || d['Is Married'] === 1 || d['Is Married'] === '1'),
    id: String(d['Household ID'] || i),
    householdId: d['Household ID'],
    isAnnotated: false,
    sectionIndex: null
  }));
}

// Ultra-fast progressive loading with pre-computed samples
export async function loadDatasetsUltraFast(onPhaseComplete) {
  const allDatasets = {};
  const startTime = performance.now();
  
  try {
    // PHASE 1: Micro sample (200 rows, ~160KB) - Target: <200ms
    console.log('⚡ PHASE 1: Loading micro samples...');
    const [tcjaExpMicro, tcjaExtMicro] = await Promise.all([
      loadDatasetSample('tcja-expiration', 'micro'),
      loadDatasetSample('tcja-extension', 'micro')
    ]);
    
    console.log(`Micro samples loaded: ${tcjaExpMicro.length} + ${tcjaExtMicro.length} rows`);
    
    allDatasets['tcja-expiration'] = processDataMinimal(tcjaExpMicro);
    allDatasets['tcja-extension'] = processDataMinimal(tcjaExtMicro);
    
    console.log(`Processed datasets: tcja-expiration has ${allDatasets['tcja-expiration'].length} rows`);
    
    const phase1Time = performance.now() - startTime;
    console.log(`✅ PHASE 1 complete in ${phase1Time.toFixed(0)}ms - Instant visualization ready!`);
    onPhaseComplete('micro', allDatasets);
    
    // PHASE 2: Small sample (1000 rows, ~800KB) - Target: <500ms total
    setTimeout(async () => {
      console.log('📊 PHASE 2: Loading small samples...');
      const phase2Start = performance.now();
      
      const [tcjaExpSmall, tcjaExtSmall] = await Promise.all([
        loadDatasetSample('tcja-expiration', 'small'),
        loadDatasetSample('tcja-extension', 'small')
      ]);
      
      allDatasets['tcja-expiration'] = processDataMinimal(tcjaExpSmall);
      allDatasets['tcja-extension'] = processDataMinimal(tcjaExtSmall);
      
      const phase2Time = performance.now() - phase2Start;
      console.log(`✅ PHASE 2 complete in ${phase2Time.toFixed(0)}ms`);
      onPhaseComplete('small', allDatasets);
      
      // PHASE 3: Medium sample (5000 rows, ~4MB) - Target: <2s total
      setTimeout(async () => {
        console.log('🎯 PHASE 3: Loading medium samples...');
        const phase3Start = performance.now();
        
        const [tcjaExpMedium, tcjaExtMedium] = await Promise.all([
          loadDatasetSample('tcja-expiration', 'medium'),
          loadDatasetSample('tcja-extension', 'medium')
        ]);
        
        allDatasets['tcja-expiration'] = processDataFull(tcjaExpMedium);
        allDatasets['tcja-extension'] = processDataFull(tcjaExtMedium);
        
        const phase3Time = performance.now() - phase3Start;
        console.log(`✅ PHASE 3 complete in ${phase3Time.toFixed(0)}ms`);
        onPhaseComplete('medium', allDatasets);
        
        // PHASE 4: Large sample (20000 rows, ~16MB) - Target: <5s total
        setTimeout(async () => {
          console.log('🔧 PHASE 4: Loading large samples...');
          const phase4Start = performance.now();
          
          const [tcjaExpLarge, tcjaExtLarge] = await Promise.all([
            loadDatasetSample('tcja-expiration', 'large'),
            loadDatasetSample('tcja-extension', 'large')
          ]);
          
          allDatasets['tcja-expiration'] = processDataFull(tcjaExpLarge);
          allDatasets['tcja-extension'] = processDataFull(tcjaExtLarge);
          
          const phase4Time = performance.now() - phase4Start;
          console.log(`✅ PHASE 4 complete in ${phase4Time.toFixed(0)}ms`);
          onPhaseComplete('large', allDatasets);
          
          // PHASE 5: Full dataset (41k rows, ~30MB) - Background load
          setTimeout(async () => {
            console.log('🏁 PHASE 5: Loading full datasets in background...');
            const phase5Start = performance.now();
            
            // Load full datasets in parallel with web workers if available
            const loadFullDataset = async (key) => {
              const data = await loadDatasetSample(key, 'full');
              return processDataFull(data);
            };
            
            const [tcjaExpFull, tcjaExtFull] = await Promise.all([
              loadFullDataset('tcja-expiration'),
              loadFullDataset('tcja-extension')
            ]);
            
            allDatasets['tcja-expiration'] = tcjaExpFull;
            allDatasets['tcja-extension'] = tcjaExtFull;
            
            const phase5Time = performance.now() - phase5Start;
            const totalTime = performance.now() - startTime;
            console.log(`✅ PHASE 5 complete in ${phase5Time.toFixed(0)}ms`);
            console.log(`🎉 All data loaded in ${(totalTime / 1000).toFixed(1)}s total`);
            onPhaseComplete('full', allDatasets);
          }, 100);
        }, 100);
      }, 50);
    }, 50);
    
  } catch (error) {
    console.error('Error in progressive loading:', error);
    throw error;
  }
}