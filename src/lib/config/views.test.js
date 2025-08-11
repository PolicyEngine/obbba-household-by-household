import { describe, it, expect } from 'vitest';
import { HOUSEHOLD_COUNTS } from './views.js';

describe('Precomputed Household Counts', () => {
  it('should have reasonable household counts for all income groups', () => {
    // Check lower-income
    expect(HOUSEHOLD_COUNTS['lower-income']).toBe(43);
    expect(HOUSEHOLD_COUNTS['lower-income']).toBeGreaterThan(0);
    expect(HOUSEHOLD_COUNTS['lower-income']).toBeLessThan(100);
    
    // Check middle-income
    expect(HOUSEHOLD_COUNTS['middle-income']).toBe(51);
    expect(HOUSEHOLD_COUNTS['middle-income']).toBeGreaterThan(0);
    expect(HOUSEHOLD_COUNTS['middle-income']).toBeLessThan(100);
    
    // Check upper-income
    expect(HOUSEHOLD_COUNTS['upper-income']).toBe(12);
    expect(HOUSEHOLD_COUNTS['upper-income']).toBeGreaterThan(0);
    expect(HOUSEHOLD_COUNTS['upper-income']).toBeLessThan(50);
    
    // Check highest-income
    expect(HOUSEHOLD_COUNTS['highest-income']).toBe(0.8);
    expect(HOUSEHOLD_COUNTS['highest-income']).toBeGreaterThan(0);
    expect(HOUSEHOLD_COUNTS['highest-income']).toBeLessThan(5);
  });
  
  it('should sum to approximately total US households', () => {
    const total = Object.values(HOUSEHOLD_COUNTS).reduce((sum, count) => sum + count, 0);
    // US has roughly 130 million households
    expect(total).toBeGreaterThan(90);
    expect(total).toBeLessThan(150);
  });
  
  it('should have appropriate distribution across income groups', () => {
    // Middle income is actually the largest group in the US
    expect(HOUSEHOLD_COUNTS['middle-income']).toBeGreaterThan(HOUSEHOLD_COUNTS['lower-income']);
    expect(HOUSEHOLD_COUNTS['lower-income']).toBeGreaterThan(HOUSEHOLD_COUNTS['upper-income']);
    expect(HOUSEHOLD_COUNTS['upper-income']).toBeGreaterThan(HOUSEHOLD_COUNTS['highest-income']);
  });
});