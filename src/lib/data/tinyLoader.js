import Papa from 'papaparse';

// Load just 1000 points for instant visualization
export async function loadTinyVisualization(onUpdate) {
  const startTime = performance.now();
  
  try {
    // Load the small sample instead of full minimal
    const base = import.meta.env.BASE_URL || '/';
    const normalizedBase = base.endsWith('/') ? base : base + '/';
    const url = `${normalizedBase}samples/household_tax_income_changes_senate_current_law_baseline_sample_small.csv`;
    
    console.log('⚡ Loading 1000-point sample for instant visualization...');
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to load sample: ${response.status}`);
    }
    
    const text = await response.text();
    
    // Parse CSV
    const result = Papa.parse(text, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      fastMode: true
    });
    
    // Process data minimally
    const data = result.data.map((d, i) => ({
      id: String(d['Household ID'] || i),
      householdId: d['Household ID'],
      'Market Income': d['Market Income'] || 0,
      'Total change in net income': d['Total change in net income'] || d['Change in Household Net Income'] || 0,
      'Change in Household Net Income': d['Total change in net income'] || d['Change in Household Net Income'] || 0,
      'Household weight': d['Household weight'] || 1,
      'Percentage change in net income': d['Percentage change in net income'] || 0,
      // Basic demographics
      'Number of Dependents': d['Number of Dependents'] || d['Dependents'] || 0,
      'Dependents': d['Dependents'] || d['Number of Dependents'] || 0,
      'Age of Head': d['Age of Head'] || d['Age'] || 40,
      'Age': d['Age'] || d['Age of Head'] || 40,
      'Is Married': !!(d['Is Married'] === true || d['Is Married'] === 'True' || d['Is Married'] === 1 || d['Is Married'] === '1')
    }));
    
    const totalTime = performance.now() - startTime;
    console.log(`✅ Sample ready in ${totalTime.toFixed(0)}ms - ${data.length} dots for instant display!`);
    
    // Return data immediately for starfield animation
    onUpdate({
      visualData: data,
      phase: 'sample',
      isComplete: false
    });
    
  } catch (error) {
    console.error('Error loading sample visualization:', error);
    throw error;
  }
}