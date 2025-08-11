import { describe, it, expect } from 'vitest';

// Extract and test the calculateSectionStats logic
function calculateSectionStats(sectionData, includeMedian = false, sectionId = null) {
  if (!sectionData || sectionData.length === 0) return null;
  
  let totalWeight = 0;
  let positiveWeight = 0;
  let negativeWeight = 0;
  let affectedWeight = 0;
  
  sectionData.forEach(d => {
    const weight = d['Household weight'] ?? 1;  // Use nullish coalescing to only fallback for null/undefined
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
  
  // Format total households in millions
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

describe('Household Statistics Calculation', () => {
  it('should calculate correct statistics for lower-income households', () => {
    // Mock data representing lower-income households
    const mockData = [
      { 'Market Income': 30000, 'Household weight': 15000000, 'Percentage change in net income': 5 },
      { 'Market Income': 40000, 'Household weight': 20000000, 'Percentage change in net income': -2 },
      { 'Market Income': 25000, 'Household weight': 8000000, 'Percentage change in net income': 0 },
    ];
    
    const stats = calculateSectionStats(mockData, false, 'lower-income');
    
    // Total should be 43 million (15+20+8)
    expect(stats).toBeTruthy();
    expect(stats.total).toBe('43');
    expect(stats.totalRaw).toBe(43000000);
    
    // 15M positive out of 43M = ~35%
    expect(stats.positivePercent).toBe(35);
    
    // 20M negative out of 43M = ~47%
    expect(stats.negativePercent).toBe(47);
    
    // 35M affected (15M + 20M) out of 43M = ~81%
    expect(stats.affectedPercent).toBe(81);
  });
  
  it('should handle empty data gracefully', () => {
    const stats = calculateSectionStats([]);
    expect(stats).toBeNull();
  });
  
  it('should handle data with zero weights', () => {
    const mockData = [
      { 'Market Income': 30000, 'Household weight': 0, 'Percentage change in net income': 5 },
      { 'Market Income': 40000, 'Household weight': 0, 'Percentage change in net income': -2 },
    ];
    
    const stats = calculateSectionStats(mockData);
    expect(stats.total).toBe('0');
    expect(stats.positivePercent).toBe(0);
    expect(stats.negativePercent).toBe(0);
  });
  
  it('should format high-income totals with decimal', () => {
    const mockData = [
      { 'Market Income': 500000, 'Household weight': 1500000, 'Percentage change in net income': -10 },
    ];
    
    const stats = calculateSectionStats(mockData, false, 'highest-income');
    expect(stats.total).toBe('1.5');
  });
});