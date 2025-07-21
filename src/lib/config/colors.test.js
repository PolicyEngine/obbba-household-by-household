import { describe, it, expect } from 'vitest';
import { COLORS, getPointColor } from './colors.js';

describe('color configuration', () => {
  describe('COLORS', () => {
    it('has all required color definitions', () => {
      expect(COLORS.WHITE).toBe('#FFFFFF');
      expect(COLORS.BLACK).toBe('#000000');
      expect(COLORS.DARKEST_BLUE).toBe('#0C1A27');
      expect(COLORS.DARK_GRAY).toBe('#616161');
      expect(COLORS.MEDIUM_DARK_GRAY).toBe('#D2D2D2');
      expect(COLORS.TEAL_MEDIUM).toBe('#2D9E99');
    });
  });

  describe('getPointColor', () => {
    it('returns positive color for positive values', () => {
      expect(getPointColor(5)).toBe(COLORS.TEAL_MEDIUM);
      expect(getPointColor(0.2)).toBe(COLORS.TEAL_MEDIUM);
      expect(getPointColor(100)).toBe(COLORS.TEAL_MEDIUM);
    });

    it('returns negative color for negative values', () => {
      expect(getPointColor(-5)).toBe(COLORS.DARK_GRAY);
      expect(getPointColor(-0.2)).toBe(COLORS.DARK_GRAY);
      expect(getPointColor(-100)).toBe(COLORS.DARK_GRAY);
    });

    it('returns neutral color for near-zero values', () => {
      expect(getPointColor(0)).toBe(COLORS.MEDIUM_DARK_GRAY);
      expect(getPointColor(0.05)).toBe(COLORS.MEDIUM_DARK_GRAY);
      expect(getPointColor(-0.05)).toBe(COLORS.MEDIUM_DARK_GRAY);
    });

    it('handles edge cases', () => {
      expect(getPointColor(null)).toBe(COLORS.MEDIUM_DARK_GRAY);
      expect(getPointColor(undefined)).toBe(COLORS.MEDIUM_DARK_GRAY);
      expect(getPointColor(NaN)).toBe(COLORS.MEDIUM_DARK_GRAY);
      expect(getPointColor('not a number')).toBe(COLORS.MEDIUM_DARK_GRAY);
    });
  });
});