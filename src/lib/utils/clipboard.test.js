import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { copyHouseholdUrl } from './clipboard.js';

describe('clipboard utilities', () => {
  let writeTextMock;
  let execCommandMock;
  let originalClipboard;
  let originalExecCommand;

  beforeEach(() => {
    // Save originals
    originalClipboard = navigator.clipboard;
    originalExecCommand = document.execCommand;

    // Mock clipboard API
    writeTextMock = vi.fn().mockResolvedValue();
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: writeTextMock },
      writable: true,
      configurable: true
    });

    // Mock execCommand
    execCommandMock = vi.fn().mockReturnValue(true);
    document.execCommand = execCommandMock;

    // Mock URL
    delete window.location;
    window.location = {
      href: 'https://example.com/obbba-scatter',
      origin: 'https://example.com',
      pathname: '/obbba-scatter',
      search: ''
    };
  });

  afterEach(() => {
    // Restore originals
    if (originalClipboard) {
      Object.defineProperty(navigator, 'clipboard', {
        value: originalClipboard,
        writable: true,
        configurable: true
      });
    }
    if (originalExecCommand) {
      document.execCommand = originalExecCommand;
    }
    vi.clearAllMocks();
  });

  describe('copyHouseholdUrl', () => {
    it('copies URL with household ID and dataset', async () => {
      const household = { id: 12345 };
      const dataset = 'tcja-expiration';
      const event = { preventDefault: vi.fn() };

      await copyHouseholdUrl(household, dataset, null, event);

      expect(event.preventDefault).toHaveBeenCalled();
      expect(writeTextMock).toHaveBeenCalledWith(
        'https://example.com/obbba-scatter?household=12345&baseline=tcja-expiration'
      );
    });

    it('does not include section parameter', async () => {
      const household = { id: 12345 };
      const dataset = 'tcja-extension';
      const currentState = { id: 'middle-income' };
      const event = { preventDefault: vi.fn() };

      await copyHouseholdUrl(household, dataset, currentState, event);

      expect(writeTextMock).toHaveBeenCalledWith(
        'https://example.com/obbba-scatter?household=12345&baseline=tcja-extension'
      );
    });

    it('handles missing household gracefully', async () => {
      const event = { preventDefault: vi.fn() };

      // Should throw or return early when household is null
      try {
        await copyHouseholdUrl(null, 'tcja-expiration', null, event);
      } catch (e) {
        // Expected to throw
      }

      expect(writeTextMock).not.toHaveBeenCalled();
    });

    it('falls back to execCommand when clipboard API fails', async () => {
      writeTextMock.mockRejectedValue(new Error('Clipboard blocked'));
      
      // Mock document methods
      const textarea = {
        value: '',
        style: {},
        focus: vi.fn(),
        select: vi.fn()
      };
      
      const createElementMock = vi.spyOn(document, 'createElement').mockReturnValue(textarea);
      const appendChildMock = vi.spyOn(document.body, 'appendChild').mockImplementation(() => textarea);
      const removeChildMock = vi.spyOn(document.body, 'removeChild').mockImplementation(() => textarea);

      const household = { id: 12345 };
      const event = { preventDefault: vi.fn() };

      await copyHouseholdUrl(household, 'tcja-expiration', null, event);

      expect(createElementMock).toHaveBeenCalledWith('textarea');
      expect(textarea.select).toHaveBeenCalled();
      expect(execCommandMock).toHaveBeenCalledWith('copy');
      expect(removeChildMock).toHaveBeenCalled();
      
      createElementMock.mockRestore();
    });

    it('works in iframe context', async () => {
      // Mock iframe environment
      const parentWindow = { location: { origin: 'https://parent.com' } };
      Object.defineProperty(window, 'parent', {
        value: parentWindow,
        writable: true,
        configurable: true
      });

      const household = { id: 12345 };
      const event = { preventDefault: vi.fn() };

      await copyHouseholdUrl(household, 'tcja-expiration', null, event);

      // When in iframe, it uses PolicyEngine URL
      expect(writeTextMock).toHaveBeenCalledWith(
        'https://policyengine.org/us/obbba-household-explorer?household=12345&baseline=tcja-expiration'
      );
    });
  });
});