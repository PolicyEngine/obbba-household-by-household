<script>
  export let message = 'Loading data...';
  export let dataset = null; // For backwards compatibility
  
  // Use message if provided, otherwise fallback to dataset format
  $: displayMessage = message || (dataset ? `Loading ${dataset.label} data...` : 'Loading data...');
</script>

<div class="loading-overlay">
  <div class="loading-content">
    <div class="spinner"></div>
    <p>{displayMessage}</p>
  </div>
</div>

<style>
  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.95);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .loading-content {
    text-align: center;
  }

  .loading-content p {
    font-size: 14px;
    color: var(--text-secondary);
    margin: 15px 0 0 0;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--light-gray);
    border-top: 3px solid var(--text-secondary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>