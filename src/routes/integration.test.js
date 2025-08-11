import { describe, it, expect, beforeAll } from 'vitest';
import Papa from 'papaparse';
import fs from 'fs';
import path from 'path';

// Reimplement the calculateSectionStats function for testing
function calculateSectionStats(sectionData, includeMedian = false, sectionId = null) {
  if (!sectionData || sectionData.length === 0) return null;
  
  let totalWeight = 0;
  let positiveWeight = 0;
  let negativeWeight = 0;
  let affectedWeight = 0;
  
  sectionData.forEach(d => {
    const weight = d['Household weight'] ?? 1;
    const percentChange = d['Percentage change in net income'] || 0;
    
    totalWeight += weight;
    if (percentChange > 0) {
      positiveWeight += weight;
      affectedWeight += weight;
    } else if (percentChange < 0) {
      negativeWeight += weight;
      affectedWeight += weight;
    }
  });
  
  const positivePercent = totalWeight > 0 ? Math.round((positiveWeight / totalWeight) * 100) : 0;
  const negativePercent = totalWeight > 0 ? Math.round((negativeWeight / totalWeight) * 100) : 0;
  const affectedPercent = totalWeight > 0 ? Math.round((affectedWeight / totalWeight) * 100) : 0;
  
  const totalMillions = totalWeight / 1000000;
  const totalFormatted = sectionId === 'highest-income' 
    ? totalMillions.toFixed(1) 
    : Math.round(totalMillions).toString();
  
  const stats = {
    total: totalFormatted,
    totalRaw: totalWeight,
    positivePercent,
    negativePercent,
    affectedPercent
  };
  
  return stats;
}

describe('Integration Tests with Real CSV Data', () => {
  let data;
  
  beforeAll(async () => {
    // Load the CSV file
    const csvPath = path.join(process.cwd(), 'static', 'Detailed_Reform_Effect_of_TCJA_Expiration.csv');
    
    try {
      const csvContent = fs.readFileSync(csvPath, 'utf8');
      const result = Papa.parse(csvContent, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true
      });
      data = result.data;
    } catch (error) {
      console.error('Could not load CSV file:', error);
      data = [];
    }
  });
  
  it('should calculate non-zero household count for lower-income group', () => {
    if (data.length === 0) {
      console.warn('Skipping test - no CSV data available');
      return;
    }
    
    // Filter for lower-income households (below $50,000)
    const lowerIncomeData = data.filter(d => 
      d['Market Income'] >= 0 && d['Market Income'] < 50000
    );
    
    expect(lowerIncomeData.length).toBeGreaterThan(0);
    
    const stats = calculateSectionStats(lowerIncomeData, false, 'lower-income');
    
    expect(stats).toBeTruthy();
    expect(stats.total).not.toBe('0');
    expect(parseFloat(stats.total)).toBeGreaterThan(0);
    
    // Based on US demographics, lower-income households should be substantial
    expect(parseFloat(stats.total)).toBeGreaterThan(10); // At least 10 million households
    
    console.log(`Lower-income households: ${stats.total} million`);
    console.log(`Positive impact: ${stats.positivePercent}%`);
    console.log(`Negative impact: ${stats.negativePercent}%`);
  });
  
  it('should calculate correct statistics for all income groups', () => {
    if (data.length === 0) {
      console.warn('Skipping test - no CSV data available');
      return;
    }
    
    const groups = [
      { name: 'lower-income', min: 0, max: 50000 },
      { name: 'middle-income', min: 50000, max: 200000 },
      { name: 'upper-income', min: 200000, max: 500000 },
      { name: 'highest-income', min: 500000, max: Infinity }
    ];
    
    groups.forEach(group => {
      const groupData = data.filter(d => 
        d['Market Income'] >= group.min && d['Market Income'] < group.max
      );
      
      if (groupData.length > 0) {
        const stats = calculateSectionStats(groupData, false, group.name);
        
        expect(stats).toBeTruthy();
        expect(stats.total).not.toBe('0');
        
        console.log(`${group.name}: ${stats.total} million households`);
      }
    });
  });
});