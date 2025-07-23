import Papa from 'papaparse';

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

// Load a specific sample
async function loadSample(datasetKey, sampleSize) {
  const samples = SAMPLE_FILES[datasetKey];
  if (!samples) throw new Error(`Unknown dataset: ${datasetKey}`);
  
  const filename = samples[sampleSize];
  if (!filename) throw new Error(`Unknown sample size: ${sampleSize}`);
  
  const base = import.meta.env.BASE_URL || '/';
  const normalizedBase = base.endsWith('/') ? base : base + '/';
  const url = `${normalizedBase}${filename}`;
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load ${sampleSize} sample: ${response.status}`);
  }
  
  const raw = await response.text();
  const result = Papa.parse(raw, {
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
    fastMode: true
  });
  
  return result.data;
}

// Minimal data processing
function processData(rawData) {
  return rawData.map((d, i) => ({
    'Market Income': d['Market Income'] || 0,
    'Total change in net income': d['Total change in net income'] || d['Change in Household Net Income'] || 0,
    'Percentage change in net income': d['Percentage change in net income'] || 0,
    'Household weight': d['Household weight'] || 1,
    id: String(d['Household ID'] || i),
    householdId: d['Household ID'],
    'Number of Dependents': d['Number of Dependents'] || d['Dependents'] || 0,
    'Age of Head': d['Age of Head'] || d['Age'] || 40,
    'Is Married': !!(d['Is Married'] === true || d['Is Married'] === 'True' || d['Is Married'] === 1 || d['Is Married'] === '1'),
    ...d // Include all other fields
  }));
}

// Ultra-fast single dataset loading with immediate display
export async function loadDatasetUltraFast(selectedDataset, onUpdate) {
  const startTime = performance.now();
  const otherDataset = selectedDataset === 'tcja-expiration' ? 'tcja-extension' : 'tcja-expiration';
  
  try {
    // PHASE 1: Load micro sample of selected dataset ONLY (target: <100ms)
    console.log(`⚡ Loading ${selectedDataset} micro sample...`);
    const microData = await loadSample(selectedDataset, 'micro');
    const processedMicro = processData(microData);
    
    const phase1Time = performance.now() - startTime;
    console.log(`✅ Micro sample ready in ${phase1Time.toFixed(0)}ms - ${processedMicro.length} dots visible!`);
    
    // Return data immediately
    onUpdate({
      [selectedDataset]: processedMicro,
      phase: 'micro',
      isComplete: false
    });
    
    // PHASE 2: Load small sample (no delay)
    const smallData = await loadSample(selectedDataset, 'small');
    const processedSmall = processData(smallData);
    
    const phase2Time = performance.now() - startTime;
    console.log(`✅ Small sample ready in ${phase2Time.toFixed(0)}ms - ${processedSmall.length} dots`);
    
    onUpdate({
      [selectedDataset]: processedSmall,
      phase: 'small',
      isComplete: false
    });
    
    // PHASE 3: Load medium sample
    const mediumData = await loadSample(selectedDataset, 'medium');
    const processedMedium = processData(mediumData);
    
    const phase3Time = performance.now() - startTime;
    console.log(`✅ Medium sample ready in ${phase3Time.toFixed(0)}ms - ${processedMedium.length} dots`);
    
    onUpdate({
      [selectedDataset]: processedMedium,
      phase: 'medium',
      isComplete: false
    });
    
    // PHASE 4: Load other dataset's micro sample (for instant switching)
    const otherMicroData = await loadSample(otherDataset, 'micro');
    const processedOtherMicro = processData(otherMicroData);
    
    onUpdate({
      [selectedDataset]: processedMedium,
      [otherDataset]: processedOtherMicro,
      phase: 'medium-with-other',
      isComplete: false
    });
    
    // PHASE 5: Load large samples in parallel
    const [largeData, otherSmallData] = await Promise.all([
      loadSample(selectedDataset, 'large'),
      loadSample(otherDataset, 'small')
    ]);
    
    const processedLarge = processData(largeData);
    const processedOtherSmall = processData(otherSmallData);
    
    const phase5Time = performance.now() - startTime;
    console.log(`✅ Large samples ready in ${phase5Time.toFixed(0)}ms`);
    
    onUpdate({
      [selectedDataset]: processedLarge,
      [otherDataset]: processedOtherSmall,
      phase: 'large',
      isComplete: false
    });
    
    // PHASE 6: Load full datasets in background
    const [fullData, otherMediumData] = await Promise.all([
      loadSample(selectedDataset, 'full'),
      loadSample(otherDataset, 'medium')
    ]);
    
    const processedFull = processData(fullData);
    const processedOtherMedium = processData(otherMediumData);
    
    onUpdate({
      [selectedDataset]: processedFull,
      [otherDataset]: processedOtherMedium,
      phase: 'full-partial',
      isComplete: false
    });
    
    // PHASE 7: Complete other dataset
    const [otherLargeData] = await Promise.all([
      loadSample(otherDataset, 'large')
    ]);
    
    const processedOtherLarge = processData(otherLargeData);
    
    onUpdate({
      [selectedDataset]: processedFull,
      [otherDataset]: processedOtherLarge,
      phase: 'full-near-complete',
      isComplete: false
    });
    
    // PHASE 8: Final - load other full dataset
    const otherFullData = await loadSample(otherDataset, 'full');
    const processedOtherFull = processData(otherFullData);
    
    const totalTime = performance.now() - startTime;
    console.log(`🎉 All data loaded in ${(totalTime / 1000).toFixed(1)}s`);
    
    onUpdate({
      [selectedDataset]: processedFull,
      [otherDataset]: processedOtherFull,
      phase: 'complete',
      isComplete: true
    });
    
  } catch (error) {
    console.error('Error loading data:', error);
    throw error;
  }
}