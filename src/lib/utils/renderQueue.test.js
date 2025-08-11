import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createRenderQueue } from './renderQueue.js';

describe('renderQueue for preventing render loss', () => {
  let mockRenderFn;
  let renderQueue;
  
  beforeEach(() => {
    mockRenderFn = vi.fn();
    vi.useFakeTimers();
  });
  
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });
  
  it('should ensure render is called even with rapid updates', () => {
    renderQueue = createRenderQueue(mockRenderFn);
    
    // Simulate rapid calls
    for (let i = 0; i < 10; i++) {
      renderQueue.enqueue();
    }
    
    // Fast-forward time
    vi.runAllTimers();
    
    // Should have called render at least once
    expect(mockRenderFn).toHaveBeenCalled();
  });
  
  it('should debounce rapid calls but guarantee final render', () => {
    renderQueue = createRenderQueue(mockRenderFn, { debounceMs: 50 });
    
    // Call multiple times rapidly
    renderQueue.enqueue();
    renderQueue.enqueue();
    renderQueue.enqueue();
    
    // Should not have called yet
    expect(mockRenderFn).not.toHaveBeenCalled();
    
    // Advance time past debounce
    vi.advanceTimersByTime(60);
    
    // Should have called exactly once
    expect(mockRenderFn).toHaveBeenCalledTimes(1);
  });
  
  it('should handle scroll events without losing renders', () => {
    renderQueue = createRenderQueue(mockRenderFn, { debounceMs: 16 }); // ~60fps
    
    // Simulate scroll events
    const scrollEvents = 20;
    for (let i = 0; i < scrollEvents; i++) {
      renderQueue.enqueue();
      vi.advanceTimersByTime(5); // Rapid scrolling
    }
    
    // Complete all pending renders
    vi.runAllTimers();
    
    // Should have rendered
    expect(mockRenderFn).toHaveBeenCalled();
    expect(mockRenderFn.mock.calls.length).toBeGreaterThan(0);
  });
  
  it('should prioritize latest state when multiple updates queued', () => {
    const states = [];
    const statefulRender = (state) => states.push(state);
    renderQueue = createRenderQueue(statefulRender, { debounceMs: 30 });
    
    // Queue multiple states
    renderQueue.enqueue(1);
    vi.advanceTimersByTime(10);
    renderQueue.enqueue(2);
    vi.advanceTimersByTime(10);
    renderQueue.enqueue(3);
    
    // Let all renders complete
    vi.runAllTimers();
    
    // Should have rendered with latest state
    expect(states).toContain(3);
  });
  
  it('should not drop renders when cancelled mid-animation', () => {
    let renderCount = 0;
    const animatingRender = () => {
      renderCount++;
      // Simulate animation frame
      return new Promise(resolve => setTimeout(resolve, 16));
    };
    
    renderQueue = createRenderQueue(animatingRender);
    
    // Start render
    renderQueue.enqueue();
    
    // Interrupt with new render request
    renderQueue.enqueue();
    
    vi.runAllTimers();
    
    // Should complete at least one render
    expect(renderCount).toBeGreaterThan(0);
  });
});