#!/usr/bin/env node

import fs from 'fs';
import Papa from 'papaparse';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Sample sizes for different loading phases
const SAMPLE_SIZES = {
  micro: 200,      // Ultra-fast initial load
  small: 1000,     // Quick sample
  medium: 5000,    // Good representation
  large: 20000     // High quality sample
};

// Function to create stratified sample ensuring representation across income ranges
function createStratifiedSample(data, sampleSize) {
  // Define income brackets for stratification
  const brackets = [
    { min: 0, max: 25000, target: 0.2 },
    { min: 25000, max: 50000, target: 0.2 },
    { min: 50000, max: 100000, target: 0.2 },
    { min: 100000, max: 200000, target: 0.2 },
    { min: 200000, max: Infinity, target: 0.2 }
  ];
  
  // Group data by income bracket
  const bracketedData = brackets.map(bracket => ({
    ...bracket,
    items: data.filter(d => {
      const income = parseFloat(d['Market Income']) || 0;
      return income >= bracket.min && income < bracket.max;
    })
  }));
  
  // Calculate samples per bracket
  const sample = [];
  bracketedData.forEach(bracket => {
    const targetCount = Math.floor(sampleSize * bracket.target);
    const available = bracket.items.length;
    const sampleCount = Math.min(targetCount, available);
    
    // Random sampling within bracket
    const shuffled = [...bracket.items].sort(() => Math.random() - 0.5);
    sample.push(...shuffled.slice(0, sampleCount));
  });
  
  // Shuffle final sample
  return sample.sort(() => Math.random() - 0.5);
}

// Process a single CSV file
async function processCsvFile(inputPath, outputDir) {
  console.log(`Processing: ${path.basename(inputPath)}`);
  
  // Read the CSV file
  const csvContent = fs.readFileSync(inputPath, 'utf8');
  
  // Parse the CSV
  const parseResult = Papa.parse(csvContent, {
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true
  });
  
  if (parseResult.errors.length > 0) {
    console.warn('CSV parsing warnings:', parseResult.errors);
  }
  
  const fullData = parseResult.data;
  console.log(`  Total rows: ${fullData.length.toLocaleString()}`);
  
  // Generate samples for each size
  const baseFileName = path.basename(inputPath, '.csv');
  
  for (const [sizeName, sampleSize] of Object.entries(SAMPLE_SIZES)) {
    const sample = createStratifiedSample(fullData, sampleSize);
    const outputFileName = `${baseFileName}_sample_${sizeName}.csv`;
    const outputPath = path.join(outputDir, outputFileName);
    
    // Convert back to CSV
    const csv = Papa.unparse(sample, {
      header: true,
      quotes: true
    });
    
    // Write sample file
    fs.writeFileSync(outputPath, csv);
    const fileSize = fs.statSync(outputPath).size;
    console.log(`  Created ${sizeName} sample: ${sample.length} rows (${(fileSize / 1024).toFixed(1)} KB)`);
  }
}

// Main function
async function main() {
  const staticDir = path.join(__dirname, '..', 'static');
  
  // Find all CSV files to process
  const csvFiles = [
    'household_tax_income_changes_senate_current_law_baseline.csv',
    'household_tax_income_changes_senate_tcja_baseline.csv'
  ];
  
  // Create samples directory
  const samplesDir = path.join(staticDir, 'samples');
  if (!fs.existsSync(samplesDir)) {
    fs.mkdirSync(samplesDir, { recursive: true });
  }
  
  console.log('Generating sample CSV files...\n');
  
  for (const csvFile of csvFiles) {
    const inputPath = path.join(staticDir, csvFile);
    
    if (fs.existsSync(inputPath)) {
      await processCsvFile(inputPath, samplesDir);
      console.log('');
    } else {
      console.warn(`File not found: ${csvFile}`);
    }
  }
  
  console.log('✅ Sample generation complete!');
  console.log(`\nSamples saved to: ${samplesDir}`);
}

// Run the script
main().catch(console.error);