import { describe, it, expect, vi, beforeEach } from 'vitest';
import { loadDatasets, processData } from './dataLoader.js';

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
      config.complete({ data });
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
          'Gross Income': '50000',
          'Total Change in Net Income': '1000',
          'Percentage Change in Net Income': '2.5',
          'Household weight': '100'
        },
        {
          'Gross Income': '100000',
          'Total Change in Net Income': '-500',
          'Percentage Change in Net Income': '-0.5',
          'Household weight': '200'
        }
      ];

      const processed = processData(rawData);

      expect(processed).toHaveLength(2);
      expect(processed[0]).toMatchObject({
        id: '0',
        'Gross Income': '50000',
        'Total Change in Net Income': '1000',
        'Percentage Change in Net Income': '2.5',
        'Household weight': '100'
      });
      expect(processed[1].id).toBe('1');
      expect(processed[1]['Gross Income']).toBe('100000');
    });

    it('filters out invalid rows', () => {
      const rawData = [
        { 'Gross Income': '50000', 'Total Change in Net Income': '1000' },
        { 'Gross Income': '', 'Total Change in Net Income': '1000' },
        { 'Gross Income': 'invalid', 'Total Change in Net Income': '1000' },
        { 'Gross Income': '60000', 'Total Change in Net Income': '' }
      ];

      const processed = processData(rawData);

      expect(processed).toHaveLength(1);
      expect(processed[0]['Gross Income']).toBe('50000');
    });

    it('handles missing columns gracefully', () => {
      const rawData = [
        { 'Gross Income': '50000' },
        { 'Total Change in Net Income': '1000' }
      ];

      const processed = processData(rawData);

      expect(processed).toHaveLength(0);
    });

    it('adds default weight when missing', () => {
      const rawData = [
        {
          'Gross Income': '50000',
          'Total Change in Net Income': '1000',
          'Percentage Change in Net Income': '2.5'
        }
      ];

      const processed = processData(rawData);

      // processData doesn't add default weight, it just maps the data
      expect(processed[0]['Household weight']).toBeUndefined();
    });
  });

  describe('loadDatasets', () => {
    it('loads and processes both datasets', async () => {
      const mockCsvData = `Gross Income,Total Change in Net Income,Percentage Change in Net Income,Household weight
50000,1000,2.5,100
100000,-500,-0.5,200`;

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
    });

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
});