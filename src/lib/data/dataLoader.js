import Papa from 'papaparse';
import { datasets } from '../config/datasets.js';

// Load dataset from CSV file
export async function loadDataset(datasetKey) {
  const dataset = datasets[datasetKey];
  if (!dataset) {
    throw new Error(`Unknown dataset: ${datasetKey}`);
  }

  try {
    const response = await fetch(`/obbba-scatter/${dataset.filename}`);
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
  } catch (error) {
    console.error('Error loading data:', error);
    console.error('Dataset key:', datasetKey);
    console.error('Filename:', dataset?.filename);
    console.error('Full URL:', `/obbba-scatter/${dataset?.filename}`);
    throw error;
  }
}

// Process raw data into usable format
export function processData(rawData) {
  return rawData.map((d, i) => ({
    ...d,
    id: String(d['Household ID'] || i), // Convert to string for consistent comparison
    householdId: d['Household ID'], // Keep original for reference
    isAnnotated: false,
    sectionIndex: null
  }));
}

// Build household ID map for quick lookups
export function buildHouseholdMap(data) {
  const householdIdMap = new Map();
  data.forEach(household => {
    householdIdMap.set(household.id, household);
  });
  return householdIdMap;
}

// Load all datasets
export async function loadDatasets() {
  try {
    const [tcjaExpiration, tcjaExtension] = await Promise.all([
      loadDataset('tcja-expiration'),
      loadDataset('tcja-extension')
    ]);
    
    return {
      'tcja-expiration': processData(tcjaExpiration),
      'tcja-extension': processData(tcjaExtension)
    };
  } catch (error) {
    console.error('Failed to load datasets:', error);
    throw new Error('Failed to load datasets');
  }
}