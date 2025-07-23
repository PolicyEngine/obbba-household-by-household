import Papa from 'papaparse';

// Load minimal visualization data
export async function loadInstantVisualization(onUpdate) {
  const startTime = performance.now();
  
  try {
    // Load minimal CSV with only visualization columns
    const base = import.meta.env.BASE_URL || '/';
    const normalizedBase = base.endsWith('/') ? base : base + '/';
    const url = `${normalizedBase}household_tax_income_changes_senate_current_law_baseline_minimal.csv`;
    
    console.log('⚡ Loading minimal visualization data...');
    const loadStart = performance.now();
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to load minimal data: ${response.status}`);
    }
    
    const fetchTime = performance.now() - loadStart;
    console.log(`  ✓ Fetched 1.4MB in ${fetchTime.toFixed(0)}ms`);
    
    const text = await response.text();
    const textTime = performance.now() - loadStart - fetchTime;
    console.log(`  ✓ Read text in ${textTime.toFixed(0)}ms`);
    
    // Parse CSV
    const parseStart = performance.now();
    const result = Papa.parse(text, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      fastMode: true
    });
    
    const parseTime = performance.now() - parseStart;
    console.log(`  ✓ Parsed ${result.data.length} rows in ${parseTime.toFixed(0)}ms`);
    
    // Process data minimally
    const processStart = performance.now();
    const data = result.data.map((d, i) => ({
      id: String(d['Household ID'] || i),
      householdId: d['Household ID'],
      'Market Income': d['Market Income'] || 0,
      'Total change in net income': d['Total change in net income'] || 0,
      'Household weight': d['Household weight'] || 1,
      // Calculate percentage for color (approximate)
      'Percentage change in net income': d['Market Income'] > 0 
        ? (d['Total change in net income'] / d['Market Income']) * 100 
        : 0
    }));
    
    const processTime = performance.now() - processStart;
    console.log(`  ✓ Processed data in ${processTime.toFixed(0)}ms`);
    
    const totalTime = performance.now() - startTime;
    console.log(`🎉 Visualization ready in ${totalTime.toFixed(0)}ms!`);
    
    // Return data immediately for starfield animation
    onUpdate({
      visualData: data,
      phase: 'instant',
      isComplete: false
    });
    
  } catch (error) {
    console.error('Error loading instant visualization:', error);
    throw error;
  }
}

// Load full dataset in background
export async function loadFullDataBackground(datasetKey, onUpdate) {
  try {
    const base = import.meta.env.BASE_URL || '/';
    const normalizedBase = base.endsWith('/') ? base : base + '/';
    
    const filenames = {
      'tcja-expiration': 'household_tax_income_changes_senate_current_law_baseline.csv',
      'tcja-extension': 'household_tax_income_changes_senate_tcja_baseline.csv'
    };
    
    const url = `${normalizedBase}${filenames[datasetKey]}`;
    
    console.log(`🔄 Loading full ${datasetKey} dataset in background...`);
    const startTime = performance.now();
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to load full dataset: ${response.status}`);
    }
    
    const text = await response.text();
    
    // Parse with web worker if available
    const result = await new Promise((resolve, reject) => {
      Papa.parse(text, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        worker: typeof Worker !== 'undefined',
        complete: resolve,
        error: reject
      });
    });
    
    // Full data processing
    const data = result.data.map((d, i) => ({
      ...d,
      id: String(d['Household ID'] || i),
      householdId: d['Household ID'],
      'Market Income': Number(d['Market Income']) || 0,
      'Total change in net income': Number(d['Total change in net income'] || d['Change in Household Net Income']) || 0,
      'Percentage change in net income': Number(d['Percentage change in net income']) || 0,
      'Household weight': Number(d['Household weight']) || 1,
      'Number of Dependents': Number(d['Number of Dependents'] || d['Dependents']) || 0,
      'Age of Head': Number(d['Age of Head'] || d['Age']) || 40,
      'Is Married': !!(d['Is Married'] === true || d['Is Married'] === 'True' || d['Is Married'] === 1 || d['Is Married'] === '1')
    }));
    
    const loadTime = performance.now() - startTime;
    console.log(`✅ Full ${datasetKey} dataset ready (${data.length} rows) in ${(loadTime / 1000).toFixed(1)}s`);
    
    onUpdate({
      [datasetKey]: data,
      phase: 'full',
      isComplete: datasetKey === 'tcja-extension' // Complete when both datasets loaded
    });
    
  } catch (error) {
    console.error(`Error loading full ${datasetKey} dataset:`, error);
    throw error;
  }
}