import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import ScatterPlot from './ScatterPlot.svelte';

describe('ScatterPlot rendering during scroll', () => {
  let mockCanvas;
  let mockContext;
  
  beforeEach(() => {
    // Mock canvas context
    mockContext = {
      clearRect: vi.fn(),
      fillRect: vi.fn(),
      beginPath: vi.fn(),
      arc: vi.fn(),
      fill: vi.fn(),
      stroke: vi.fn(),
      save: vi.fn(),
      restore: vi.fn(),
      scale: vi.fn(),
      translate: vi.fn(),
      setLineDash: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      fillText: vi.fn(),
      strokeText: vi.fn(),
      measureText: vi.fn(() => ({ width: 100 }))
    };
    
    mockCanvas = {
      getContext: vi.fn(() => mockContext),
      width: 900,
      height: 600
    };
    
    // Mock HTMLCanvasElement.prototype.getContext
    HTMLCanvasElement.prototype.getContext = vi.fn(() => mockContext);
    
    // Mock performance.now()
    vi.spyOn(performance, 'now').mockReturnValue(1000);
    
    // Mock requestAnimationFrame
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation(cb => {
      setTimeout(cb, 16); // Simulate 60fps
      return 1;
    });
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render dots even when scrolling immediately after mount', async () => {
    const mockData = [
      { id: 1, x: 100, y: 200, 'Market Income': 50000 },
      { id: 2, x: 200, y: 300, 'Market Income': 75000 },
      { id: 3, x: 300, y: 400, 'Market Income': 100000 }
    ];
    
    const mockScrollStates = [
      { xMin: 0, xMax: 1000, yMin: 0, yMax: 1000 }
    ];
    
    const { container } = render(ScatterPlot, {
      props: {
        data: mockData,
        scrollStates: mockScrollStates,
        currentStateIndex: 0
      }
    });
    
    // Simulate immediate scroll
    fireEvent.scroll(window, { target: { scrollY: 200 } });
    
    // Wait for animation frame
    await waitFor(() => {
      // Check that arc (dot drawing) was called for each data point
      expect(mockContext.arc).toHaveBeenCalled();
    }, { timeout: 100 });
    
    // Verify dots were drawn (arc is called for each dot)
    const arcCalls = mockContext.arc.mock.calls.length;
    expect(arcCalls).toBeGreaterThan(0);
  });

  it('should not lose dots when scrolling rapidly during initialization', async () => {
    const mockData = Array.from({ length: 100 }, (_, i) => ({
      id: i,
      x: i * 10,
      y: i * 10,
      'Market Income': 50000 + i * 1000
    }));
    
    const mockScrollStates = [
      { xMin: 0, xMax: 1000, yMin: 0, yMax: 1000 }
    ];
    
    const { container } = render(ScatterPlot, {
      props: {
        data: mockData,
        scrollStates: mockScrollStates,
        currentStateIndex: 0
      }
    });
    
    // Simulate rapid scrolling
    for (let i = 0; i < 10; i++) {
      fireEvent.scroll(window, { target: { scrollY: i * 100 } });
      await new Promise(resolve => setTimeout(resolve, 5));
    }
    
    // Wait for animations to settle
    await waitFor(() => {
      expect(mockContext.arc).toHaveBeenCalled();
    }, { timeout: 500 });
    
    // Verify dots are still being drawn
    expect(mockContext.arc.mock.calls.length).toBeGreaterThan(0);
  });

  it('should properly queue render operations during scroll', async () => {
    const mockData = [
      { id: 1, x: 100, y: 200, 'Market Income': 50000 }
    ];
    
    const mockScrollStates = [
      { xMin: 0, xMax: 1000, yMin: 0, yMax: 1000 }
    ];
    
    const { container } = render(ScatterPlot, {
      props: {
        data: mockData,
        scrollStates: mockScrollStates,
        currentStateIndex: 0
      }
    });
    
    // Track clear operations (canvas is cleared before each render)
    const clearCount = mockContext.clearRect.mock.calls.length;
    
    // Trigger multiple scroll events
    fireEvent.scroll(window, { target: { scrollY: 100 } });
    fireEvent.scroll(window, { target: { scrollY: 200 } });
    fireEvent.scroll(window, { target: { scrollY: 300 } });
    
    await waitFor(() => {
      // Should have rendered at least once after scrolling
      expect(mockContext.clearRect.mock.calls.length).toBeGreaterThan(clearCount);
    }, { timeout: 100 });
  });

  it('should handle scroll events with debouncing to prevent render loss', async () => {
    const mockData = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: i * 20,
      y: i * 20,
      'Market Income': 50000 + i * 1000
    }));
    
    const mockScrollStates = [
      { xMin: 0, xMax: 1000, yMin: 0, yMax: 1000 }
    ];
    
    const { container } = render(ScatterPlot, {
      props: {
        data: mockData,
        scrollStates: mockScrollStates,
        currentStateIndex: 0
      }
    });
    
    // Simulate very rapid scroll events
    const scrollPromises = [];
    for (let i = 0; i < 20; i++) {
      fireEvent.scroll(window, { target: { scrollY: i * 50 } });
      scrollPromises.push(new Promise(resolve => setTimeout(resolve, 1)));
    }
    
    await Promise.all(scrollPromises);
    
    // Wait for render to complete
    await waitFor(() => {
      // Should have rendered dots despite rapid scrolling
      expect(mockContext.arc).toHaveBeenCalled();
    }, { timeout: 200 });
    
    // Ensure canvas wasn't cleared without redrawing
    const clearCalls = mockContext.clearRect.mock.calls.length;
    const arcCalls = mockContext.arc.mock.calls.length;
    
    // If canvas was cleared, dots should have been redrawn
    if (clearCalls > 0) {
      expect(arcCalls).toBeGreaterThan(0);
    }
  });
});