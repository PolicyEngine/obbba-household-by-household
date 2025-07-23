import Papa from 'papaparse';
import { DATASETS } from '../config/datasets.js';

// Minimal sample for instant loading (just enough for visual feedback)
function createMicroSample(fullDataset, sampleSize = 300) {
  // Ultra-fast systematic sampling - every nth element
  const step = Math.floor(fullDataset.length / sampleSize);
  const sample = [];
  
  for (let i = 0; i < fullDataset.length && sample.length < sampleSize; i += Math.max(1, step)) {
    sample.push(fullDataset[i]);
  }
  
  return sample;
}

// Streaming CSV parser that can terminate early for samples
async function parseCSVStream(raw, maxRows = null) {
  return new Promise((resolve, reject) => {
    const results = [];
    let rowCount = 0;
    let headers = null;
    
    Papa.parse(raw, {
      header: false, // Parse headers manually for speed
      dynamicTyping: false, // Skip type conversion for speed
      skipEmptyLines: true,
      worker: false, // Use main thread for small samples (faster setup)
      chunkSize: 1024 * 1024, // 1MB chunks for faster streaming
      step: (result) => {
        if (!headers) {
          headers = result.data;
          return;
        }
        
        // Convert row to object manually (faster than Papa's header mode)
        const row = {};
        for (let i = 0; i < headers.length; i++) {
          row[headers[i]] = result.data[i];
        }
        results.push(row);
        rowCount++;
        
        // Early termination for samples
        if (maxRows && rowCount >= maxRows) {
          return false; // Stop parsing
        }
      },
      complete: () => resolve(results),
      error: reject
    });
  });
}

// Load dataset from CSV file with optional early termination
export async function loadDataset(datasetKey, maxRows = null) {
  const dataset = DATASETS[datasetKey];
  if (!dataset) {
    throw new Error(`Unknown dataset: ${datasetKey}`);
  }

  // Handle base path for both dev and production
  const base = import.meta.env.BASE_URL || '/';
  const normalizedBase = base.endsWith('/') ? base : base + '/';
  const normalizedFilename = dataset.filename.startsWith('/') ? dataset.filename.slice(1) : dataset.filename;
  const url = `${normalizedBase}${normalizedFilename}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to load CSV: ${response.status} ${response.statusText}`);
    }
    
    const raw = await response.text();
    
    // Use streaming parser for samples, regular parser for full datasets
    if (maxRows) {
      console.log(`Parsing ${maxRows} rows from CSV stream...`);
      return await parseCSVStream(raw, maxRows);
    }
    
    // For full datasets, use optimized Papa Parse
    const isTestEnvironment = typeof window === 'undefined' || typeof Worker === 'undefined';
    
    let result;
    if (isTestEnvironment) {
      result = Papa.parse(raw, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true
      });
    } else {
      result = await new Promise((resolve, reject) => {
        Papa.parse(raw, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true,
          worker: true,
          chunkSize: 4 * 1024 * 1024, // 4MB chunks for balance of speed and memory
          fastMode: true,
          complete: resolve,
          error: reject
        });
      });
    }
    
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

// Ultra-minimal data processing for micro samples
export function processMicroSample(rawData) {
  // Skip all expensive operations for micro samples
  return rawData.map((d, i) => ({
    // Only essential fields for visualization
    'Market Income': parseFloat(d['Market Income']) || 0,
    'Total change in net income': parseFloat(d['Total change in net income'] || d['Change in Household Net Income']) || 0,
    'Percentage change in net income': parseFloat(d['Percentage change in net income']) || 0,
    'Household weight': parseFloat(d['Household weight']) || 1,
    id: String(d['Household ID'] || i),
    householdId: d['Household ID'],
    // Minimal additional fields
    'Number of Dependents': parseInt(d['Number of Dependents'] || d['Dependents']) || 0,
    'Age of Head': parseInt(d['Age of Head'] || d['Age']) || 40,
    'Is Married': !!(d['Is Married'] === true || d['Is Married'] === 'True' || d['Is Married'] === 1 || d['Is Married'] === '1'),
    isAnnotated: false,
    sectionIndex: null
  }));
}

// Optimized data processing for better performance
export function processData(rawData) {
  const result = new Array(rawData.length);
  
  for (let i = 0; i < rawData.length; i++) {
    const d = rawData[i];
    result[i] = {
      ...d,
      // Optimize 'Is Married' conversion
      ...(d['Is Married'] !== undefined ? { 'Is Married': !!(d['Is Married'] === true || d['Is Married'] === 'True' || d['Is Married'] === 1 || d['Is Married'] === '1') } : {}),
      id: String(d['Household ID'] || i),
      householdId: d['Household ID'],
      isAnnotated: false,
      sectionIndex: null
    };
  }
  
  return result;
}

// Helper function to convert 'Is Married' to boolean (optimized)
function normalizeMarriedStatus(value) {
  if (value === undefined) return undefined;
  return value === true || value === 'True' || value === 1 || value === '1';
}

// Better yielding mechanism
function yieldToMain() {
  return new Promise(resolve => {
    if (typeof requestIdleCallback !== 'undefined') {
      requestIdleCallback(resolve, { timeout: 5 });
    } else if (typeof requestAnimationFrame !== 'undefined') {
      requestAnimationFrame(() => setTimeout(resolve, 0));
    } else {
      setTimeout(resolve, 0);
    }
  });
}

// Process raw data into usable format with optimized chunking
export async function processDataAsync(rawData, chunkSize = 250, onProgress = null) {
  const result = [];
  const totalRows = rawData.length;
  
  result.length = totalRows;
  let resultIndex = 0;
  let lastProgressReport = -1;
  
  for (let i = 0; i < rawData.length; i += chunkSize) {
    const endIndex = Math.min(i + chunkSize, rawData.length);
    
    for (let j = i; j < endIndex; j++) {
      const d = rawData[j];
      
      const processed = { ...d };
      processed.id = String(d['Household ID'] || j);
      processed.householdId = d['Household ID'];
      processed.isAnnotated = false;
      processed.sectionIndex = null;
      
      const marriedValue = d['Is Married'];
      if (marriedValue !== undefined) {
        processed['Is Married'] = normalizeMarriedStatus(marriedValue);
      }
      
      result[resultIndex++] = processed;
    }
    
    if (onProgress) {
      const progress = Math.min(100, Math.round((endIndex / totalRows) * 100));
      if (progress !== lastProgressReport && (progress % 5 === 0 || progress === 100)) {
        onProgress(progress);
        lastProgressReport = progress;
      }
    }
    
    if (endIndex < rawData.length) {
      await yieldToMain();
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

// Ultra-fast sample creation using reservoir sampling
function createFastSample(fullDataset, sampleSize = 1000) {
  if (fullDataset.length <= sampleSize) {
    return fullDataset;
  }
  
  const reservoir = new Array(sampleSize);
  
  for (let i = 0; i < sampleSize; i++) {
    reservoir[i] = fullDataset[i];
  }
  
  for (let i = sampleSize; i < fullDataset.length; i++) {
    const j = Math.floor(Math.random() * (i + 1));
    if (j < sampleSize) {
      reservoir[j] = fullDataset[i];
    }
  }
  
  return reservoir;
}

// Create a stratified sample of the dataset
function createSampleDataset(fullDataset, sampleSize = 1500) {
  if (fullDataset.length <= sampleSize) {
    return fullDataset;
  }
  
  const incomeGroups = {
    low: [],
    middle: [],
    upper: [],
    highest: []
  };
  
  const totalHouseholds = fullDataset.length;
  fullDataset.forEach(household => {
    const income = household['Market Income'] || 0;
    if (income < 50000) {
      incomeGroups.low.push(household);
    } else if (income < 200000) {
      incomeGroups.middle.push(household);
    } else if (income < 1000000) {
      incomeGroups.upper.push(household);
    } else {
      incomeGroups.highest.push(household);
    }
  });
  
  const sample = [];
  const groupNames = ['low', 'middle', 'upper', 'highest'];
  
  groupNames.forEach(groupName => {
    const households = incomeGroups[groupName];
    if (households.length === 0) return;
    
    const proportion = households.length / totalHouseholds;
    const groupSampleSize = Math.max(1, Math.round(sampleSize * proportion));
    
    const shuffled = [...households];
    const sampleCount = Math.min(groupSampleSize, households.length);
    
    for (let i = 0; i < sampleCount; i++) {
      const j = i + Math.floor(Math.random() * (shuffled.length - i));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    
    sample.push(...shuffled.slice(0, sampleCount));
  });
  
  if (sample.length < sampleSize) {
    const remaining = sampleSize - sample.length;
    const usedIds = new Set(sample.map(h => h['Household ID']));
    
    let added = 0;
    for (let i = 0; i < fullDataset.length && added < remaining; i++) {
      const household = fullDataset[i];
      if (!usedIds.has(household['Household ID'])) {
        if (Math.random() < (remaining - added) / (fullDataset.length - i)) {
          sample.push(household);
          added++;
        }
      }
    }
  }
  
  return sample.slice(0, sampleSize);
}

// ULTRA-AGGRESSIVE LOADING: Multiple phases for sub-10-second experience
export async function loadDatasetsProgressive(onFirstDatasetLoaded, onSecondDatasetLoaded, onFullDatasetLoaded) {
  const allDatasets = {};
  
  try {
    // PHASE 1: Instant micro-sample (target: <500ms)
    console.log('🚀 PHASE 1: Loading micro-sample for instant feedback...');
    const startTime = performance.now();
    
    // Load just first 200 rows for ultra-fast visualization
    const tcjaExpirationMicro = await loadDataset('tcja-expiration', 200);
    console.log(`📊 Micro dataset loaded: ${tcjaExpirationMicro.length} rows`);
    
    // Create minimal sample for instant display (even smaller)
    const microSample = createMicroSample(tcjaExpirationMicro, 150);
    allDatasets['tcja-expiration'] = processMicroSample(microSample);
    
    const phase1Time = performance.now() - startTime;
    console.log(`⚡ PHASE 1 complete in ${phase1Time.toFixed(0)}ms - App ready for interaction!`);
    
    // Notify immediately for instant user interaction
    if (onFirstDatasetLoaded) {
      onFirstDatasetLoaded(allDatasets);
    }
    
    // PHASE 2: Better sample (target: 2-3 seconds total)
    setTimeout(async () => {
      console.log('📈 PHASE 2: Loading better sample...');
      const phase2Start = performance.now();
      
      // Load more rows for better sample
      const tcjaExpirationSample = await loadDataset('tcja-expiration', 2000);
      const betterSample = createFastSample(tcjaExpirationSample, 800);
      allDatasets['tcja-expiration'] = processData(betterSample);
      
      const phase2Time = performance.now() - phase2Start;
      console.log(`✨ PHASE 2 complete in ${phase2Time.toFixed(0)}ms - Better quality sample ready`);
      
      // Notify upgrade
      if (onFirstDatasetLoaded) {
        onFirstDatasetLoaded(allDatasets);
      }
      
      // PHASE 3: High-quality sample (target: 4-5 seconds total)
      setTimeout(async () => {
        console.log('🎯 PHASE 3: Loading high-quality sample...');
        const phase3Start = performance.now();
        
        // Load full dataset and create high-quality stratified sample
        const tcjaExpirationFull = await loadDataset('tcja-expiration');
        const highQualitySample = createSampleDataset(tcjaExpirationFull, 1500);
        allDatasets['tcja-expiration'] = processData(highQualitySample);
        
        const phase3Time = performance.now() - phase3Start;
        console.log(`🎨 PHASE 3 complete in ${phase3Time.toFixed(0)}ms - High-quality stratified sample ready`);
        
        // Notify high-quality upgrade
        if (onFirstDatasetLoaded) {
          onFirstDatasetLoaded(allDatasets);
        }
        
        // PHASE 4: Full dataset (background, target: 6-8 seconds total)
        setTimeout(async () => {
          console.log('🔄 PHASE 4: Processing full dataset in background...');
          const phase4Start = performance.now();
          
          const fullTcjaExpiration = await processDataAsync(tcjaExpirationFull, 500); // Larger chunks
          allDatasets['tcja-expiration'] = fullTcjaExpiration;
          
          const phase4Time = performance.now() - phase4Start;
          const totalTime = performance.now() - startTime;
          console.log(`🏁 PHASE 4 complete in ${phase4Time.toFixed(0)}ms - Full dataset ready (${totalTime.toFixed(0)}ms total)`);
          
          // Notify full dataset ready
          if (onFullDatasetLoaded) {
            onFullDatasetLoaded(allDatasets, 'tcja-expiration');
          }
        }, 100);
      }, 200);
    }, 50);
    
    // SECONDARY DATASET: Load in parallel phases
    console.log('🔄 Loading secondary dataset in parallel...');
    setTimeout(async () => {
      try {
        // Micro sample for secondary dataset
        const tcjaExtensionMicro = await loadDataset('tcja-extension', 200);
        const secondaryMicroSample = createMicroSample(tcjaExtensionMicro, 150);
        allDatasets['tcja-extension'] = processMicroSample(secondaryMicroSample);
        console.log('📊 Secondary micro-sample ready');
        
        if (onSecondDatasetLoaded) {
          onSecondDatasetLoaded(allDatasets);
        }
        
        // Better secondary sample
        setTimeout(async () => {
          const tcjaExtensionSample = await loadDataset('tcja-extension', 2000);
          const secondaryBetterSample = createFastSample(tcjaExtensionSample, 800);
          allDatasets['tcja-extension'] = processData(secondaryBetterSample);
          console.log('✨ Secondary better sample ready');
          
          if (onSecondDatasetLoaded) {
            onSecondDatasetLoaded(allDatasets);
          }
          
          // Full secondary dataset
          setTimeout(async () => {
            const tcjaExtensionFull = await loadDataset('tcja-extension');
            const secondaryHighQuality = createSampleDataset(tcjaExtensionFull, 1500);
            allDatasets['tcja-extension'] = processData(secondaryHighQuality);
            console.log('🎨 Secondary high-quality sample ready');
            
            if (onSecondDatasetLoaded) {
              onSecondDatasetLoaded(allDatasets);
            }
            
            // Full secondary processing
            const fullTcjaExtension = await processDataAsync(tcjaExtensionFull, 500);
            allDatasets['tcja-extension'] = fullTcjaExtension;
            console.log('🏁 Secondary full dataset ready');
            
            if (onFullDatasetLoaded) {
              onFullDatasetLoaded(allDatasets, 'tcja-extension');
            }
          }, 300);
        }, 500);
      } catch (error) {
        console.error('Failed to load secondary dataset:', error);
      }
    }, 1000); // Start secondary dataset after 1 second
    
    return allDatasets;
  } catch (error) {
    console.error('Failed to load primary dataset:', error);
    throw new Error('Failed to load primary dataset');
  }
}