/**
 * Debug utility to track scroll behavior in the app
 * This helps identify what's causing unwanted scrolling
 */

export class ScrollDebugger {
  constructor() {
    this.events = [];
    this.enabled = false;
    this.targetElement = null;
  }

  start(container) {
    if (this.enabled) return;
    
    this.enabled = true;
    this.targetElement = container;
    this.events = [];

    // Track all scroll-related events
    const eventTypes = [
      'scroll',
      'scrollend',
      'wheel',
      'touchmove',
      'focus',
      'blur',
      'resize'
    ];

    eventTypes.forEach(type => {
      window.addEventListener(type, this.logEvent.bind(this, 'window', type), { capture: true });
      if (container) {
        container.addEventListener(type, this.logEvent.bind(this, 'container', type), { capture: true });
      }
    });

    // Monitor DOM mutations that might trigger scroll
    this.observer = new MutationObserver((mutations) => {
      mutations.forEach(mutation => {
        if (mutation.type === 'childList' || mutation.type === 'characterData') {
          this.logEvent('dom', 'mutation', {
            type: mutation.type,
            target: mutation.target.className || mutation.target.nodeName,
            addedNodes: mutation.addedNodes.length,
            removedNodes: mutation.removedNodes.length
          });
        }
      });
    });

    if (container) {
      this.observer.observe(container, {
        childList: true,
        subtree: true,
        characterData: true,
        attributes: true,
        attributeFilter: ['style', 'class']
      });
    }

    // Track scroll position changes
    this.scrollPositions = new Map();
    this.trackScrollPosition();

    console.log('🔍 Scroll debugger started');
  }

  logEvent(source, type, detail = {}) {
    const timestamp = performance.now();
    const scrollTop = this.targetElement?.scrollTop || window.scrollY;
    const event = {
      timestamp,
      source,
      type,
      scrollTop,
      detail: typeof detail === 'object' ? detail : { value: detail }
    };

    // Check if this caused a scroll
    const lastEvent = this.events[this.events.length - 1];
    if (lastEvent && Math.abs(scrollTop - lastEvent.scrollTop) > 1) {
      event.causedScroll = true;
      event.scrollDelta = scrollTop - lastEvent.scrollTop;
    }

    this.events.push(event);

    // Log significant events
    if (event.causedScroll || type === 'focus' || type === 'blur') {
      console.log(`📍 ${source}.${type}`, {
        scrollDelta: event.scrollDelta,
        scrollTop: event.scrollTop,
        detail: event.detail
      });
    }
  }

  trackScrollPosition() {
    if (!this.enabled) return;

    const elements = document.querySelectorAll('.household-profile, .integrated-household-profile');
    elements.forEach(el => {
      const rect = el.getBoundingClientRect();
      const id = el.querySelector('h3')?.textContent || 'unknown';
      this.scrollPositions.set(id, {
        top: rect.top,
        scrollTop: this.targetElement?.scrollTop || window.scrollY
      });
    });

    requestAnimationFrame(() => this.trackScrollPosition());
  }

  stop() {
    this.enabled = false;
    if (this.observer) {
      this.observer.disconnect();
    }
    console.log('🔍 Scroll debugger stopped');
    this.analyze();
  }

  analyze() {
    console.log('📊 Scroll Debug Analysis:');
    
    // Find events that caused scrolling
    const scrollCausingEvents = this.events.filter(e => e.causedScroll);
    console.log(`Found ${scrollCausingEvents.length} events that caused scrolling:`);
    
    scrollCausingEvents.forEach(event => {
      console.log(`  - ${event.source}.${event.type} caused ${event.scrollDelta}px scroll`, event.detail);
    });

    // Identify patterns
    const eventTypes = {};
    this.events.forEach(e => {
      const key = `${e.source}.${e.type}`;
      eventTypes[key] = (eventTypes[key] || 0) + 1;
    });

    console.log('Event frequency:', eventTypes);

    // Check for focus-related scrolling
    const focusEvents = this.events.filter(e => e.type === 'focus' || e.type === 'blur');
    if (focusEvents.some(e => e.causedScroll)) {
      console.warn('⚠️ Focus events are causing scrolling - consider using preventScroll option');
    }

    return {
      totalEvents: this.events.length,
      scrollCausingEvents: scrollCausingEvents.length,
      eventTypes
    };
  }

  // Helper to inject into the page for debugging
  static injectDebugger() {
    window.scrollDebugger = new ScrollDebugger();
    
    // Start debugging when content loads
    setTimeout(() => {
      const container = document.querySelector('.content-overlay');
      if (container) {
        window.scrollDebugger.start(container);
        console.log('Scroll debugger injected. Use window.scrollDebugger.stop() to see analysis.');
      }
    }, 1000);
  }
}

// Export for use in tests or development
export default ScrollDebugger;