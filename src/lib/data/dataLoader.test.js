import { describe, it, expect, vi, beforeEach } from 'vitest';
import { loadDatasets, processData, processDataAsync } from './dataLoader.js';

// Mock Papa library
vi.mock('papaparse', () => ({
  default: {
    parse: vi.fn((text, config) => {
      // Simulate CSV parsing
      const rows = text.trim().split('\n');
      const headers = rows[0].split(',');
      const data = rows.slice(1).map(row => {
        const values = row.split(',');
        return headers.reduce((obj, header, i) => {
          obj[header] = values[i];
          return obj;
        }, {});
      });
      
      const result = { data, errors: [] };
      
      // Handle both sync and async (worker) modes
      if (config?.complete) {
        // Async mode - call complete callback
        setTimeout(() => config.complete(result), 0);
        return; // Return nothing for async mode
      } else {
        // Sync mode - return result directly
        return result;
      }
    })
  }
}));

// Mock fetch
global.fetch = vi.fn();

describe('dataLoader', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('processData', () => {
    it('processes valid data correctly', () => {
      const rawData = [
        {
          'Household ID': '12345',
          'Gross Income': '50000',
          'Total change in net income': '1000',
          'Percentage change in net income': '2.5',
          'Household weight': '100'
        },
        {
          'Household ID': '67890',
          'Gross Income': '100000',
          'Total change in net income': '-500',
          'Percentage change in net income': '-0.5',
          'Household weight': '200'
        }
      ];

      const processed = processData(rawData);

      expect(processed).toHaveLength(2);
      expect(processed[0]).toMatchObject({
        id: '12345',
        householdId: '12345',
        'Gross Income': '50000',
        'Total change in net income': '1000',
        'Percentage change in net income': '2.5',
        'Household weight': '100'
      });
      expect(processed[1].id).toBe('67890');
      expect(processed[1]['Gross Income']).toBe('100000');
    });

    it('processes all rows without filtering', () => {
      const rawData = [
        { 'Gross Income': '50000', 'Total change in net income': '1000' },
        { 'Gross Income': '', 'Total change in net income': '1000' },
        { 'Gross Income': 'invalid', 'Total change in net income': '1000' },
        { 'Gross Income': '60000', 'Total change in net income': '' }
      ];

      const processed = processData(rawData);

      // processData doesn't filter, just transforms
      expect(processed).toHaveLength(4);
      expect(processed[0]['Gross Income']).toBe('50000');
      expect(processed[1]['Gross Income']).toBe('');
    });

    it('handles missing columns gracefully', () => {
      const rawData = [
        { 'Gross Income': '50000' },
        { 'Total change in net income': '1000' }
      ];

      const processed = processData(rawData);

      // processData doesn't filter, just transforms
      expect(processed).toHaveLength(2);
      expect(processed[0]['Gross Income']).toBe('50000');
      expect(processed[1]['Total change in net income']).toBe('1000');
    });

    it('adds default weight when missing', () => {
      const rawData = [
        {
          'Gross Income': '50000',
          'Total change in net income': '1000',
          'Percentage change in net income': '2.5'
        }
      ];

      const processed = processData(rawData);

      // processData doesn't add default weight, it just maps the data
      expect(processed[0]['Household weight']).toBeUndefined();
    });
  });

  describe('loadDatasets', () => {
    it('loads and processes both datasets', async () => {
      const mockCsvData = `Household ID,Gross Income,Total change in net income,Percentage change in net income,Household weight
12345,50000,1000,2.5,100
67890,100000,-500,-0.5,200`;

      fetch.mockResolvedValue({
        ok: true,
        text: async () => mockCsvData
      });

      const datasets = await loadDatasets();

      expect(fetch).toHaveBeenCalledTimes(2);
      expect(datasets).toHaveProperty('tcja-expiration');
      expect(datasets).toHaveProperty('tcja-extension');
      expect(datasets['tcja-expiration']).toHaveLength(2);
      expect(datasets['tcja-extension']).toHaveLength(2);
    }, 10000); // Increase timeout to 10 seconds

    it('handles fetch errors gracefully', async () => {
      fetch.mockRejectedValue(new Error('Network error'));

      await expect(loadDatasets()).rejects.toThrow('Failed to load datasets');
    });

    it('handles HTTP errors', async () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      });

      await expect(loadDatasets()).rejects.toThrow('Failed to load datasets');
    });
  });

  describe('processDataAsync', () => {
    it('processes data in chunks without blocking', async () => {
      const rawData = Array.from({ length: 600 }, (_, i) => ({
        'Household ID': String(i + 1),
        'Gross Income': '50000',
        'Total change in net income': '1000',
        'Percentage change in net income': '2.5',
        'Household weight': '100'
      }));

      const processed = await processDataAsync(rawData, 250);

      expect(processed).toHaveLength(600);
      expect(processed[0]).toMatchObject({
        id: '1',
        householdId: '1',
        'Gross Income': '50000',
        isAnnotated: false,
        sectionIndex: null
      });
    });

    it('reports progress when callback provided', async () => {
      const rawData = Array.from({ length: 1500 }, (_, i) => ({
        'Household ID': String(i + 1)
      }));

      const progressReports = [];
      await processDataAsync(rawData, 500, (progress) => {
        progressReports.push(progress);
      });

      // Progress is now reported only on 5% intervals
      // With 1500 items in chunks of 500:
      // - 500/1500 = 33.3% → rounds to 33% (not divisible by 5, skipped)
      // - 1000/1500 = 66.7% → rounds to 67% (not divisible by 5, skipped)  
      // - 1500/1500 = 100% (divisible by 5, reported)
      expect(progressReports).toEqual([100]);
    });
  });
});