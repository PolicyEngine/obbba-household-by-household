<script>
  import { onMount } from 'svelte';
  import { DATASETS } from '../config/datasets.js';
  
  export let selectedDataset = 'tcja-expiration';
  export let loading = false;
  export let onDatasetChange = () => {};
  
  let headerEl;
  let isInIframe = false;
  
  onMount(() => {
    // Check if we're in an iframe
    isInIframe = window.self !== window.top;
    
    // If in iframe, ensure header stays visible on scroll
    if (isInIframe && headerEl) {
      // Force the header to stay at the top of the viewport
      const ensureHeaderVisible = () => {
        if (headerEl) {
          headerEl.style.position = 'fixed';
          headerEl.style.top = '0';
          headerEl.style.transform = 'translateY(0)';
        }
      };
      
      // Monitor for any changes that might hide the header
      window.addEventListener('scroll', ensureHeaderVisible, true);
      window.addEventListener('resize', ensureHeaderVisible);
      
      // Initial call
      ensureHeaderVisible();
      
      return () => {
        window.removeEventListener('scroll', ensureHeaderVisible, true);
        window.removeEventListener('resize', ensureHeaderVisible);
      };
    }
  });
</script>

<header class="floating-header" bind:this={headerEl}>
  <div class="header-content">
    <h1 class="app-title">OBBBA Household Explorer</h1>
    <div class="baseline-selector-container">
      <span class="baseline-label">Baseline:</span>
      <div class="baseline-selector">
        {#each Object.entries(DATASETS) as [key, dataset]}
          <button 
            class="tab-button" 
            class:active={selectedDataset === key}
            on:click={() => onDatasetChange(key)}
            disabled={loading}
          >
            {dataset.label}
          </button>
        {/each}
      </div>
    </div>
  </div>
</header>

<style>
  /* Floating header styles */
  .floating-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(226, 232, 240, 0.5);
    z-index: 9999; /* Very high z-index to ensure it stays on top */
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transform: translateZ(0); /* Force GPU acceleration for better performance */
    will-change: transform; /* Optimize for animations */
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 48px 16px calc(120px + 48px); /* Match text content margin-left (120px) + padding (48px) */
    max-width: none;
    margin: 0;
  }
  

  .app-title {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
  }

  /* Baseline selector container */
  .baseline-selector-container {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .baseline-label {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
  }

  /* Use sans-serif for UI elements */
  .baseline-label,
  .tab-button {
    font-family: var(--font-sans);
  }

  /* Tabbed radio button styles */
  .baseline-selector {
    display: flex;
    background: var(--grid-lines);
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
  }

  .tab-button {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
  }

  .tab-button:hover:not(:disabled):not(.active) {
    background: rgba(44, 100, 150, 0.08);
    color: var(--text-primary);
  }

  .tab-button.active {
    background: var(--app-background);
    color: var(--text-primary);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
    font-weight: 700;
  }

  .tab-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Mobile responsive header */
  @media (max-width: 768px) {
    header {
      height: auto; /* Allow height to grow for stacked layout */
    }
    
    .header-content {
      padding: 12px;
      flex-direction: column; /* Stack vertically */
      align-items: stretch;
      gap: 10px;
    }

    .app-title {
      font-size: 18px;
      text-align: center;
      margin: 0;
    }

    .baseline-selector-container {
      width: 100%;
      flex-direction: column;
      align-items: stretch;
      gap: 4px;
    }

    .baseline-label {
      font-size: 11px;
      text-align: center;
      color: var(--text-secondary);
      margin: 0;
    }

    .baseline-selector {
      flex: 1;
      justify-content: center;
      border-radius: 20px;
      padding: 2px;
    }

    .tab-button {
      font-size: 12px;
      padding: 6px 12px;
    }
  }
  
  @media (max-width: 480px) {
    .app-title {
      font-size: 14px;
    }

    .tab-button {
      flex: 1;
      font-size: 13px;
      padding: 6px 12px;
    }
  }
</style>