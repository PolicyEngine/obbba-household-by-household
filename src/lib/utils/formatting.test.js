import { describe, it, expect } from 'vitest';
import {
  formatCurrency,
  formatDollarChange,
  formatPercentage,
  formatNumber,
  getFontFamily
} from './formatting.js';

describe('formatting utilities', () => {
  describe('formatCurrency', () => {
    it('formats positive numbers correctly', () => {
      expect(formatCurrency(1000)).toBe('$1,000');
      expect(formatCurrency(1500.50)).toBe('$1,501');
      expect(formatCurrency(1000000)).toBe('$1,000,000');
    });

    it('formats negative numbers correctly', () => {
      expect(formatCurrency(-1000)).toBe('-$1,000');
      expect(formatCurrency(-1500.50)).toBe('-$1,501');
    });

    it('formats zero correctly', () => {
      expect(formatCurrency(0)).toBe('$0');
    });

    it('handles edge cases', () => {
      expect(formatCurrency(null)).toBe('$0');
      expect(formatCurrency(undefined)).toBe('$0');
      expect(formatCurrency(NaN)).toBe('$0');
    });
  });

  describe('formatDollarChange', () => {
    it('formats positive changes with plus sign', () => {
      expect(formatDollarChange(1000)).toBe('+$1,000');
      expect(formatDollarChange(500.75)).toBe('+$501');
    });

    it('formats negative changes with minus sign', () => {
      expect(formatDollarChange(-1000)).toBe('-$1,000');
      expect(formatDollarChange(-500.75)).toBe('-$501');
    });

    it('formats zero as $0', () => {
      expect(formatDollarChange(0)).toBe('$0');
    });

    it('handles edge cases', () => {
      expect(formatDollarChange(null)).toBe('$0');
      expect(formatDollarChange(undefined)).toBe('$0');
    });
  });

  describe('formatPercentage', () => {
    it('formats positive percentages correctly', () => {
      expect(formatPercentage(5.5)).toBe('+5.5%');
      expect(formatPercentage(10)).toBe('+10.0%');
      expect(formatPercentage(0.5)).toBe('+0.5%');
    });

    it('formats negative percentages correctly', () => {
      expect(formatPercentage(-5.5)).toBe('-5.5%');
      expect(formatPercentage(-10)).toBe('-10.0%');
    });

    it('formats zero without sign', () => {
      expect(formatPercentage(0)).toBe('0.0%');
    });

    it('rounds to one decimal place', () => {
      expect(formatPercentage(5.55)).toBe('+5.6%');
      expect(formatPercentage(5.54)).toBe('+5.5%');
    });
  });

  describe('formatNumber', () => {
    it('formats large numbers with commas', () => {
      expect(formatNumber(1000)).toBe('1,000');
      expect(formatNumber(1000000)).toBe('1,000,000');
      expect(formatNumber(1234567)).toBe('1,234,567');
    });

    it('handles decimals correctly', () => {
      expect(formatNumber(1234.56)).toBe('1,235');
      expect(formatNumber(999.99)).toBe('1,000');
    });

    it('handles edge cases', () => {
      expect(formatNumber(null)).toBe('0');
      expect(formatNumber(undefined)).toBe('0');
      expect(formatNumber(NaN)).toBe('0');
    });
  });

  describe('getFontFamily', () => {
    it('returns correct font families', () => {
      expect(getFontFamily('sans')).toContain('system-ui');
      expect(getFontFamily('mono')).toContain('Menlo');
    });

    it('defaults to sans font', () => {
      expect(getFontFamily()).toBe(getFontFamily('sans'));
      expect(getFontFamily('invalid')).toBe(getFontFamily('sans'));
    });
  });
});