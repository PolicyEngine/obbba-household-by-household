/**
 * Creates a render queue that ensures renders are not lost during rapid updates.
 * This prevents the issue where scrolling too fast can cause dots not to render.
 * 
 * @param {Function} renderFn - The render function to call
 * @param {Object} options - Configuration options
 * @param {number} options.debounceMs - Milliseconds to debounce (default: 16 for ~60fps)
 * @returns {Object} Queue interface with enqueue method
 */
export function createRenderQueue(renderFn, options = {}) {
  const { debounceMs = 16 } = options;
  
  let pendingRender = null;
  let isRendering = false;
  let lastState = null;
  let renderPromise = null;
  
  const performRender = async () => {
    if (isRendering) {
      // If already rendering, wait for it to complete then render again
      if (renderPromise) {
        await renderPromise;
      }
    }
    
    isRendering = true;
    
    try {
      // Call render with the latest state if provided
      renderPromise = Promise.resolve(renderFn(lastState));
      await renderPromise;
    } finally {
      isRendering = false;
      renderPromise = null;
      
      // If there's a pending render, execute it
      if (pendingRender !== null) {
        const pending = pendingRender;
        pendingRender = null;
        pending();
      }
    }
  };
  
  const enqueue = (state) => {
    // Update the state to render
    if (state !== undefined) {
      lastState = state;
    }
    
    // Clear any existing timeout
    if (pendingRender) {
      clearTimeout(pendingRender);
    }
    
    // Schedule render with debouncing
    pendingRender = setTimeout(() => {
      pendingRender = null;
      performRender();
    }, debounceMs);
  };
  
  const forceRender = () => {
    // Cancel pending render
    if (pendingRender) {
      clearTimeout(pendingRender);
      pendingRender = null;
    }
    
    // Render immediately
    return performRender();
  };
  
  const cancel = () => {
    if (pendingRender) {
      clearTimeout(pendingRender);
      pendingRender = null;
    }
  };
  
  return {
    enqueue,
    forceRender,
    cancel,
    get isRendering() {
      return isRendering;
    },
    get hasPending() {
      return pendingRender !== null;
    }
  };
}