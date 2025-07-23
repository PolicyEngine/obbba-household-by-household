#!/usr/bin/env node

import fs from 'fs';
import Papa from 'papaparse';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Process CSV to extract only visualization columns
async function createMinimalCsv(inputPath, outputPath) {
  console.log(`Processing: ${path.basename(inputPath)}`);
  
  // Read the full CSV
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
  
  // Extract only the columns needed for visualization
  const minimalData = fullData.map((row, index) => ({
    // Essential ID for matching with full data later
    'Household ID': row['Household ID'] || index,
    // X-axis
    'Market Income': row['Market Income'] || 0,
    // Y-axis (handle both possible column names)
    'Total change in net income': row['Total change in net income'] || row['Change in Household Net Income'] || 0,
    // Opacity
    'Household weight': row['Household weight'] || 1
  }));
  
  // Convert back to CSV
  const csv = Papa.unparse(minimalData, {
    header: true,
    quotes: false // Don't quote numbers to save space
  });
  
  // Write minimal file
  fs.writeFileSync(outputPath, csv);
  const fileSize = fs.statSync(outputPath).size;
  console.log(`  Created minimal CSV: ${(fileSize / 1024 / 1024).toFixed(1)} MB (from ${(fs.statSync(inputPath).size / 1024 / 1024).toFixed(1)} MB)`);
  
  // Calculate reduction
  const reduction = ((1 - fileSize / fs.statSync(inputPath).size) * 100).toFixed(1);
  console.log(`  Size reduction: ${reduction}%`);
}

// Main function
async function main() {
  const staticDir = path.join(__dirname, '..', 'static');
  
  // Only process TCJA expiration (default baseline)
  const inputFile = 'household_tax_income_changes_senate_current_law_baseline.csv';
  const outputFile = 'household_tax_income_changes_senate_current_law_baseline_minimal.csv';
  
  const inputPath = path.join(staticDir, inputFile);
  const outputPath = path.join(staticDir, outputFile);
  
  console.log('Generating minimal CSV for instant visualization...\n');
  
  if (fs.existsSync(inputPath)) {
    await createMinimalCsv(inputPath, outputPath);
  } else {
    console.error(`File not found: ${inputFile}`);
    process.exit(1);
  }
  
  console.log('\n✅ Minimal CSV generation complete!');
  console.log(`\nFile saved to: ${outputFile}`);
}

// Run the script
main().catch(console.error);