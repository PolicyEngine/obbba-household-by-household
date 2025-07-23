import Papa from 'papaparse';
import { DATASETS } from '../config/datasets.js';

// Load dataset from CSV file
export async function loadDataset(datasetKey) {
  const dataset = DATASETS[datasetKey];
  if (!dataset) {
    throw new Error(`Unknown dataset: ${datasetKey}`);
  }

  // Handle base path for both dev and production
  const base = import.meta.env.BASE_URL || '/';
  // Ensure base ends with / and filename doesn't start with /
  const normalizedBase = base.endsWith('/') ? base : base + '/';
  const normalizedFilename = dataset.filename.startsWith('/') ? dataset.filename.slice(1) : dataset.filename;
  const url = `${normalizedBase}${normalizedFilename}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to load CSV: ${response.status} ${response.statusText}`);
    }
    
    const raw = await response.text();
    
    // Use Papa Parse in worker mode to avoid blocking the main thread
    const result = await new Promise((resolve, reject) => {
      Papa.parse(raw, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        worker: true, // Use web worker to avoid blocking
        complete: resolve,
        error: reject
      });
    });
    
    if (result.errors.length > 0) {
      console.warn('CSV parsing warnings:', result.errors);
    }
    
    return result.data;
  } catch (error) {
    console.error('Error loading data:', error);
    console.error('Dataset key:', datasetKey);
    console.error('Filename:', dataset?.filename);
    console.error('Full URL:', url);
    throw error;
  }
}

// Process raw data into usable format
export function processData(rawData) {
  return rawData.map((d, i) => ({
    ...d,
    // Ensure 'Is Married' is a boolean
    ...(d['Is Married'] !== undefined ? { 'Is Married': d['Is Married'] === true || d['Is Married'] === 'True' || d['Is Married'] === 1 || d['Is Married'] === '1' } : {}),
    id: String(d['Household ID'] || i), // Convert to string for consistent comparison
    householdId: d['Household ID'], // Keep original for reference
    isAnnotated: false,
    sectionIndex: null
  }));
}

// Process raw data into usable format with chunking to avoid blocking
export async function processDataAsync(rawData, chunkSize = 1000, onProgress = null) {
  const result = [];
  const totalRows = rawData.length;
  
  for (let i = 0; i < rawData.length; i += chunkSize) {
    const chunk = rawData.slice(i, i + chunkSize);
    const processedChunk = chunk.map((d, index) => ({
      ...d,
      // Ensure 'Is Married' is a boolean
      ...(d['Is Married'] !== undefined ? { 'Is Married': d['Is Married'] === true || d['Is Married'] === 'True' || d['Is Married'] === 1 || d['Is Married'] === '1' } : {}),
      id: String(d['Household ID'] || (i + index)), // Convert to string for consistent comparison
      householdId: d['Household ID'], // Keep original for reference
      isAnnotated: false,
      sectionIndex: null
    }));
    
    result.push(...processedChunk);
    
    // Report progress if callback provided
    if (onProgress) {
      const progress = Math.min(100, Math.round(((i + chunkSize) / totalRows) * 100));
      onProgress(progress);
    }
    
    // Yield control to browser between chunks
    if (i + chunkSize < rawData.length) {
      await new Promise(resolve => setTimeout(resolve, 0));
    }
  }
  
  return result;
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

// Load datasets progressively - primary dataset first, then secondary in background
export async function loadDatasetsProgressive(onFirstDatasetLoaded, onSecondDatasetLoaded) {
  const allDatasets = {};
  
  try {
    // Load TCJA expiration first (primary dataset)
    console.log('Loading primary dataset (TCJA expiration)...');
    const tcjaExpiration = await loadDataset('tcja-expiration');
    allDatasets['tcja-expiration'] = processData(tcjaExpiration);
    
    // Notify that first dataset is ready
    if (onFirstDatasetLoaded) {
      onFirstDatasetLoaded(allDatasets);
    }
    
    // Load TCJA extension in the background with async processing
    console.log('Loading secondary dataset (TCJA extension) in background...');
    loadDataset('tcja-extension')
      .then(async (tcjaExtension) => {
        console.log('Secondary dataset downloaded, processing asynchronously...');
        // Use async processing to avoid blocking the main thread
        allDatasets['tcja-extension'] = await processDataAsync(tcjaExtension);
        console.log('Secondary dataset loaded successfully');
        
        // Notify that second dataset is ready
        if (onSecondDatasetLoaded) {
          onSecondDatasetLoaded(allDatasets);
        }
      })
      .catch(error => {
        console.error('Failed to load secondary dataset:', error);
        // Don't throw - we can still work with just the primary dataset
      });
    
    return allDatasets;
  } catch (error) {
    console.error('Failed to load primary dataset:', error);
    throw new Error('Failed to load primary dataset');
  }
}