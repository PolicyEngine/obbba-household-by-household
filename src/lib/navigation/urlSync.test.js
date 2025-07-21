import { describe, it, expect, vi, beforeEach } from 'vitest';
import { 
  parseUrlParams, 
  updateUrlWithHousehold, 
  notifyParentOfUrlChange,
  findSectionForHousehold 
} from './urlSync.js';
import { scrollStates } from '../config/views.js';

// Mock $app/navigation
vi.mock('$app/navigation', () => ({
  goto: vi.fn()
}));

describe('urlSync utilities', () => {
  beforeEach(() => {
    // Reset window.location mock
    delete window.location;
    window.location = {
      origin: 'https://example.com',
      pathname: '/obbba-scatter',
      search: '',
      href: 'https://example.com/obbba-scatter'
    };
    
    // Reset window.parent mock
    Object.defineProperty(window, 'parent', {
      value: window,
      writable: true,
      configurable: true
    });
    
    vi.clearAllMocks();
  });

  describe('parseUrlParams', () => {
    it('parses household ID from URL', () => {
      window.location.search = '?household=12345';
      const params = parseUrlParams();
      
      expect(params.householdId).toBe('12345');
      expect(params.section).toBeNull();
      expect(params.baseline).toBeNull();
    });

    it('parses all parameters', () => {
      window.location.search = '?household=12345&baseline=tcja-extension&section=middle-income';
      const params = parseUrlParams();
      
      expect(params.householdId).toBe('12345');
      expect(params.baseline).toBe('tcja-extension');
      expect(params.section).toBe('middle-income');
    });

    it('returns defaults when no parameters', () => {
      window.location.search = '';
      const params = parseUrlParams();
      
      expect(params.householdId).toBe('');
      expect(params.section).toBeNull();
      expect(params.baseline).toBeNull();
    });
  });

  describe('notifyParentOfUrlChange', () => {
    it('sends message to parent when in iframe', () => {
      const parentWindow = { 
        postMessage: vi.fn() 
      };
      Object.defineProperty(window, 'parent', {
        value: parentWindow,
        writable: true,
        configurable: true
      });
      
      window.location.search = '?household=12345&baseline=tcja-expiration';
      
      notifyParentOfUrlChange();
      
      expect(parentWindow.postMessage).toHaveBeenCalledWith({
        type: 'urlUpdate',
        params: 'household=12345&baseline=tcja-expiration'
      }, '*');
    });

    it('does not send message when not in iframe', () => {
      const postMessageSpy = vi.spyOn(window, 'postMessage');
      
      notifyParentOfUrlChange();
      
      expect(postMessageSpy).not.toHaveBeenCalled();
    });
  });

  describe('findSectionForHousehold', () => {
    it('finds lower-income section for households under $50k', () => {
      const household = { 'Gross Income': 30000 };
      const index = findSectionForHousehold(household, scrollStates);
      
      const state = scrollStates[index];
      expect(state.id).toContain('lower-income');
    });

    it('finds middle-income section for households $50k-$200k', () => {
      const household = { 'Gross Income': 100000 };
      const index = findSectionForHousehold(household, scrollStates);
      
      const state = scrollStates[index];
      expect(state.id).toContain('middle-income');
    });

    it('finds upper-income section for households $200k-$1M', () => {
      const household = { 'Gross Income': 500000 };
      const index = findSectionForHousehold(household, scrollStates);
      
      const state = scrollStates[index];
      expect(state.id).toContain('upper-income');
    });

    it('finds highest-income section for households over $1M', () => {
      const household = { 'Gross Income': 2000000 };
      const index = findSectionForHousehold(household, scrollStates);
      
      const state = scrollStates[index];
      expect(state.id).toContain('highest-income');
    });

    it('advances to individual view when available', () => {
      const household = { 'Gross Income': 75000 };
      const index = findSectionForHousehold(household, scrollStates);
      
      // Should return individual view index, not group view
      expect(scrollStates[index].viewType).toBe('individual');
    });
  });
});