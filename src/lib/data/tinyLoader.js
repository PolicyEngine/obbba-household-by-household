import Papa from 'papaparse';

// Load just 1000 points for instant visualization
export async function loadTinyVisualization(onUpdate) {
  const startTime = performance.now();
  
  try {
    // Load the truly minimal 3-column CSV
    const base = import.meta.env.BASE_URL || '/';
    const normalizedBase = base.endsWith('/') ? base : base + '/';
    const url = `${normalizedBase}household_visualization_minimal_1000.csv`;
    
    console.log('⚡ Loading minimal 3-column visualization data (27KB)...');
    
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
    
    // Process data - we only have 3 columns!
    const data = result.data.map((d, i) => ({
      id: String(i),
      householdId: i,
      'Market Income': d['Market Income'] || 0,
      'Total change in net income': d['Total change in net income'] || 0,
      'Change in Household Net Income': d['Total change in net income'] || 0, // Alias
      'Household weight': d['Household weight'] || 1,
      // Estimate percentage for color
      'Percentage change in net income': 0,
      // Placeholder demographics for compatibility
      'Number of Dependents': 0,
      'Dependents': 0,
      'Age of Head': 40,
      'Age': 40,
      'Is Married': false,
      'State': null // Will be filled when full data loads
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