#!/usr/bin/env node

import fs from 'fs';
import Papa from 'papaparse';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Generate minimal 3-column CSV with just 1000 rows
async function createMinimal1000() {
  const staticDir = path.join(__dirname, '..', 'static');
  
  // Use the existing small sample as source
  const inputFile = 'samples/household_tax_income_changes_senate_current_law_baseline_sample_small.csv';
  const outputFile = 'household_visualization_minimal_1000.csv';
  
  const inputPath = path.join(staticDir, inputFile);
  const outputPath = path.join(staticDir, outputFile);
  
  console.log('Generating minimal 3-column CSV with 1000 rows...\n');
  
  // Read the sample CSV
  const csvContent = fs.readFileSync(inputPath, 'utf8');
  
  // Parse the CSV
  const parseResult = Papa.parse(csvContent, {
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true
  });
  
  console.log(`Source has ${parseResult.data.length} rows`);
  
  // Extract ONLY the 3 columns needed for visualization
  const minimalData = parseResult.data.slice(0, 1000).map(row => ({
    'Market Income': row['Market Income'] || 0,
    'Total change in net income': row['Total change in net income'] || row['Change in Household Net Income'] || 0,
    'Household weight': row['Household weight'] || 1
  }));
  
  // Convert back to CSV - no quotes needed for numbers
  const csv = Papa.unparse(minimalData, {
    header: true,
    quotes: false
  });
  
  // Write minimal file
  fs.writeFileSync(outputPath, csv);
  const fileSize = fs.statSync(outputPath).size;
  console.log(`Created minimal CSV: ${(fileSize / 1024).toFixed(1)} KB`);
  console.log(`Columns: Market Income, Total change in net income, Household weight`);
  console.log(`Rows: ${minimalData.length}`);
  
  console.log('\n✅ Done! File saved to:', outputFile);
}

// Run the script
createMinimal1000().catch(console.error);