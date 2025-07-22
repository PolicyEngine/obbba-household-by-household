/**
 * Wrapper that tries to load optimized format first, falls back to original format
 */

import * as originalLoader from './dataLoader.js';
import * as optimizedLoader from './dataLoaderOptimized.js';

let useOptimized = null;

// Check which format to use
async function checkFormat() {
  if (useOptimized !== null) {
    return useOptimized;
  }
  
  try {
    useOptimized = await optimizedLoader.hasOptimizedFiles();
    console.log(`Using ${useOptimized ? 'optimized' : 'original'} data format`);
    return useOptimized;
  } catch {
    useOptimized = false;
    return false;
  }
}

// Wrapped functions
export async function loadDataset(datasetKey) {
  const optimized = await checkFormat();
  return optimized 
    ? optimizedLoader.loadDataset(datasetKey)
    : originalLoader.loadDataset(datasetKey);
}

export async function loadDatasets() {
  const optimized = await checkFormat();
  return optimized
    ? optimizedLoader.loadDatasets()
    : originalLoader.loadDatasets();
}

export async function loadDatasetsProgressive(onFirstDatasetLoaded, onSecondDatasetLoaded) {
  const optimized = await checkFormat();
  return optimized
    ? optimizedLoader.loadDatasetsProgressive(onFirstDatasetLoaded, onSecondDatasetLoaded)
    : originalLoader.loadDatasetsProgressive(onFirstDatasetLoaded, onSecondDatasetLoaded);
}

// Re-export other functions
export { processData, buildHouseholdMap } from './dataLoader.js';