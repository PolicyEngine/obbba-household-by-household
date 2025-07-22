<script>
  import { onMount } from 'svelte';
  import { DATASETS } from '../config/datasets.js';
  
  export let selectedDataset = 'tcja-expiration';
  export let loading = false;
  export let secondDatasetLoading = false;
  export let onDatasetChange = () => {};
  export let allDatasets = {}; // Add this prop to check if datasets are loaded
  
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
            disabled={loading || (key === 'tcja-extension' && secondDatasetLoading && !allDatasets['tcja-extension'])}
          >
            {dataset.label}
            {#if key === 'tcja-extension' && secondDatasetLoading}
              <span class="loading-dot"></span>
            {/if}
          </button>
        {/each}
      </div>
    </div>
  </div>
</header>

<style>
  header {
    position: sticky;
    top: 0;
    left: 0;
    right: 0;
    z-index: 9999;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--border);
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    min-height: 60px;
    width: 100%;
    
    /* Ensure header stays visible even when scrolling */
    transform: translateZ(0);
    -webkit-transform: translateZ(0);
    will-change: transform;
  }
  
  /* Ensure header stays visible when embedded in iframe */
  :global(body.in-iframe) header {
    position: fixed !important;
    top: 0 !important;
    transform: translateY(0) !important;
    -webkit-transform: translateY(0) !important;
  }
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    max-width: none;
    margin: 0;
    padding: 0 1.5rem 0 calc(120px + 3rem); /* Left padding: y-axis space (120px) + text padding (3rem) */
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

  .loading-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: var(--text-secondary);
    margin-left: 6px;
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 0.3;
    }
    50% {
      opacity: 1;
    }
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
      flex: 0 1 auto;
      justify-content: center;
      border-radius: 20px;
      padding: 2px;
      margin: 0 auto; /* Center the selector */
      max-width: 280px; /* Limit width */
    }

    .tab-button {
      font-size: 11px;
      padding: 4px 8px;
      min-width: 0; /* Allow buttons to shrink */
    }
  }
  
  @media (max-width: 480px) {
    .app-title {
      font-size: 14px;
    }

    .baseline-selector {
      max-width: 240px; /* Even narrower on small screens */
    }

    .tab-button {
      flex: 1;
      font-size: 10px;
      padding: 4px 6px;
    }
  }
</style>