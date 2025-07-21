<script>
  import { DATASETS } from '../config/datasets.js';
  
  export let selectedDataset = 'tcja-expiration';
  export let loading = false;
  export let onDatasetChange = () => {};
</script>

<header class="floating-header">
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
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.5);
    z-index: 1000;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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
    .header-content {
      padding: 12px 16px 12px calc(60px + 24px); /* Match mobile text content margin + padding */
      flex-direction: column;
      gap: 12px;
    }

    .app-title {
      font-size: 20px;
    }

    .baseline-selector-container {
      width: 100%;
    }

    .baseline-label {
      font-size: 13px;
    }

    .baseline-selector {
      flex: 1;
      justify-content: center;
    }

    .tab-button {
      flex: 1;
      font-size: 13px;
      padding: 6px 12px;
    }
  }
</style>