<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { DATASETS } from '$lib/config/datasets.js';
  import { scrollStates } from '$lib/config/views.js';
  import { loadDatasets } from '$lib/data/dataLoader.js';
  import { 
    parseUrlParams, 
    updateUrlWithHousehold, 
    findSectionForHousehold,
    notifyParentOfUrlChange 
  } from '$lib/navigation/urlSync.js';
  import {
    createIntersectionObserver,
    getRandomWeightedHousehold,
    cleanupScrollObserver,
    currentStateIndex,
    previousStateIndex,
    isTransitioning,
    currentInterpolationT
  } from '$lib/navigation/scrollHandler.js';
  import { animateHouseholdEmphasis, createAnimatedNumber, cleanupAnimations } from '$lib/utils/animations.js';
  import LoadingOverlay from '$lib/components/LoadingOverlay.svelte';
  import Header from '$lib/components/Header.svelte';
  import HouseholdProfile from '$lib/components/HouseholdProfile.svelte';
  import ScatterPlot from '$lib/components/ScatterPlot.svelte';
  
  // Data state
  let data = [];
  let selectedHousehold = null;
  let isLoading = false;
  let loadError = null;
  let selectedDataset = 'tcja-expiration';
  
  // Random households for each section
  let randomHouseholds = {};
  
  // References
  let scrollObserver = null;
  let textSections = [];
  let scrollContainer = null;
  let chartComponent = null;
  
  // Initialize or update random households for visible sections
  function initializeRandomHouseholds() {
    scrollStates.forEach(state => {
      if (state.viewType === 'group' && !randomHouseholds[state.id]) {
        const filteredData = data.filter(d => state.filter(d));
        const randomHousehold = getRandomWeightedHousehold(filteredData);
        if (randomHousehold) {
          randomHouseholds[state.id] = randomHousehold;
        }
      }
    });
  }
  
  // Get current state and its households
  $: currentState = scrollStates[$currentStateIndex] || scrollStates[0];
  $: currentRandomHousehold = (() => {
    if (currentState?.viewType === 'individual') {
      const baseViewId = currentState.id.replace('-individual', '');
      return randomHouseholds[baseViewId];
    } else if (currentState?.viewType === 'group') {
      return randomHouseholds[currentState.id];
    }
    return null;
  })();
  
  // Handle section changes
  function handleSectionChange(newIndex) {
    const newState = scrollStates[newIndex];
    if (newState?.viewType === 'individual') {
      const baseViewId = newState.id.replace('-individual', '');
      const household = randomHouseholds[baseViewId];
      if (household) {
        selectHousehold(household);
        
        // Animate the household numbers
        const sectionIndex = Math.floor(newIndex / 2);
        createAnimatedNumber(`household-id-${sectionIndex}`, 0, household.id, d => Math.round(d), 600);
        createAnimatedNumber(`num-dependents-${sectionIndex}`, 0, 
          Math.round(household['Number of Dependents'] || household['Dependents'] || 0), 
          d => Math.round(d), 700);
        createAnimatedNumber(`age-of-head-${sectionIndex}`, 18, 
          household['Age of Head'] || household['Age'] || 40, 
          d => Math.round(d), 800);
      }
    } else if (selectedHousehold) {
      updateUrlWithHousehold(null, selectedDataset);
      selectedHousehold = null;
    }
    
    // Force chart re-render
    if (chartComponent?.renderVisualization) {
      chartComponent.renderVisualization();
    }
  }
  
  // Handle household selection
  function selectHousehold(household) {
    selectedHousehold = household;
    
    // Animate the household point
    animateHouseholdEmphasis(household.id);
    
    // Update URL
    updateUrlWithHousehold(household.id, selectedDataset);
  }
  
  // Randomize household for current section
  function randomizeHousehold() {
    const baseViewId = currentState?.id?.replace('-individual', '') || currentState?.id;
    const state = scrollStates.find(s => s.id === baseViewId);
    
    if (state && data.length > 0) {
      const filteredData = data.filter(d => state.filter(d));
      const newHousehold = getRandomWeightedHousehold(filteredData);
      
      if (newHousehold) {
        randomHouseholds[baseViewId] = newHousehold;
        selectHousehold(newHousehold);
        
        // Re-trigger animations
        const sectionIndex = Math.floor($currentStateIndex / 2);
        createAnimatedNumber(`household-id-${sectionIndex}`, 
          selectedHousehold?.id || 0, newHousehold.id, d => Math.round(d), 600);
      }
    }
  }
  
  // Handle dataset change
  async function handleDatasetChange(dataset) {
    selectedDataset = dataset;
    isLoading = true;
    
    // Remember current household ID if one is selected
    const currentHouseholdId = selectedHousehold?.id;
    
    try {
      const datasets = await loadDatasets();
      data = datasets[dataset];
      
      // Reset random households
      randomHouseholds = {};
      initializeRandomHouseholds();
      
      // Try to find the same household in the new dataset
      if (currentHouseholdId) {
        const household = data.find(d => String(d.id) === String(currentHouseholdId));
        if (household) {
          selectedHousehold = household;
          updateUrlWithHousehold(household.id, dataset);
          
          // Animate emphasis on the household
          animateHouseholdEmphasis(household.id);
        } else {
          // Household not found in new dataset, clear selection
          selectedHousehold = null;
          updateUrlWithHousehold(null, dataset);
        }
      }
      
      // Force chart re-render
      if (chartComponent?.renderVisualization) {
        chartComponent.renderVisualization();
      }
    } catch (error) {
      console.error('Error loading dataset:', error);
      loadError = error.message;
    } finally {
      isLoading = false;
    }
  }
  
  // Handle URL parameters
  async function handleUrlParams() {
    const { householdId, baseline } = parseUrlParams();
    
    // Update baseline if provided
    if (baseline && baseline !== selectedDataset) {
      selectedDataset = baseline;
    }
    
    // Load data if needed
    if (data.length === 0) {
      isLoading = true;
      try {
        console.log('Loading datasets in handleUrlParams...');
        const datasets = await loadDatasets();
        console.log('Loaded datasets:', Object.keys(datasets), 'lengths:', {
          'tcja-expiration': datasets['tcja-expiration']?.length,
          'tcja-extension': datasets['tcja-extension']?.length
        });
        data = datasets[selectedDataset];
        console.log('Selected dataset:', selectedDataset, 'length:', data.length);
        initializeRandomHouseholds();
      } catch (error) {
        console.error('Error loading data:', error);
        loadError = error.message;
        isLoading = false;
        return;
      }
      isLoading = false;
    }
    
    // Handle household selection
    if (householdId && data.length > 0) {
      const household = data.find(d => String(d.id) === householdId);
      if (household) {
        selectedHousehold = household;
        
        // Find appropriate section
        const targetIndex = findSectionForHousehold(household, scrollStates);
        
        // Scroll to section
        if (textSections[targetIndex] && scrollContainer) {
          // Delay to ensure DOM is ready
          setTimeout(() => {
            textSections[targetIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 100);
        }
      }
    }
  }
  
  // Lifecycle
  onMount(async () => {
    console.log('Component mounted, starting initialization...');
    
    // Handle initial URL parameters
    await handleUrlParams();
    
    // Set up scroll observer
    if (textSections.length > 0) {
      scrollObserver = createIntersectionObserver(textSections, handleSectionChange);
    }
    
    // Listen for URL changes
    const unsubscribe = page.subscribe(() => {
      handleUrlParams();
    });
    
    // Listen for parent messages (iframe integration)
    function handleMessage(event) {
      if (event.data?.type === 'urlParams') {
        const url = new URL(window.location);
        const params = new URLSearchParams(event.data.params);
        
        // Update our URL to match parent
        for (const [key, value] of params) {
          url.searchParams.set(key, value);
        }
        
        window.history.replaceState({}, '', url);
        handleUrlParams();
      }
    }
    
    window.addEventListener('message', handleMessage);
    
    // Notify parent we're ready
    notifyParentOfUrlChange();
    
    return () => {
      unsubscribe();
      window.removeEventListener('message', handleMessage);
      cleanupScrollObserver(scrollObserver);
      cleanupAnimations();
    };
  });
  
  onDestroy(() => {
    cleanupScrollObserver(scrollObserver);
    cleanupAnimations();
  });
</script>

<svelte:head>
  <title>OBBBA Household Explorer</title>
  <meta name="description" content="Interactive visualization showing how different American households are affected by tax policy changes">
</svelte:head>

<div class="app-container">
  <Header 
    {selectedDataset} 
    onDatasetChange={handleDatasetChange}
  />
  
  <!-- Full-screen chart background -->
  <div class="chart-background">
    <ScatterPlot
      bind:this={chartComponent}
      {data}
      {scrollStates}
      currentStateIndex={$currentStateIndex}
      previousStateIndex={$previousStateIndex}
      isTransitioning={$isTransitioning}
      interpolationT={$currentInterpolationT}
      {randomHouseholds}
      {selectedHousehold}
      onPointClick={selectHousehold}
    />
  </div>
  
  <!-- Scrollable content overlay -->
  <div class="content-overlay" bind:this={scrollContainer}>
    <div class="text-content">
      {#each scrollStates as state, i}
        {#if state.viewType === 'group'}
          <section 
            class="text-section"
            class:active={$currentStateIndex === i}
            data-index={i}
            bind:this={textSections[i]}
          >
            <div class="section-content">
              <h2>{state.title}</h2>
              {#if state.description}
                <p>{@html state.description}</p>
              {/if}
              {#if state.content}
                <p>{@html state.content}</p>
              {/if}
            </div>
          </section>
        {:else if state.viewType === 'individual'}
          <section 
            class="text-section individual-section"
            class:active={$currentStateIndex === i}
            data-index={i}
            bind:this={textSections[i]}
          >
            <HouseholdProfile
              household={currentRandomHousehold}
              {selectedDataset}
              currentState={state}
              sectionIndex={Math.floor(i / 2)}
              onRandomize={randomizeHousehold}
            />
          </section>
        {/if}
      {/each}
    </div>
    <!-- Transparent area for chart interaction -->
    <div class="chart-interaction-area"></div>
  </div>
  
  {#if isLoading}
    <LoadingOverlay message="Loading {DATASETS[selectedDataset].label} baseline..." />
  {/if}
  
  {#if loadError}
    <div class="error-overlay">
      <div class="error-content">
        <h2>Error Loading Data</h2>
        <p>{loadError}</p>
        <button on:click={() => location.reload()}>Reload Page</button>
      </div>
    </div>
  {/if}
</div>

<style>
  :global(:root) {
    /* Colors */
    --app-background: #FFFFFF;
    --text-primary: #2C3E50;
    --text-secondary: #606F7B;
    --border: #E2E8F0;
    --hover: #F7FAFC;
    --scatter-positive: #2D9E99; /* Teal */
    --scatter-negative: #616161; /* Dark Gray */
    --button-bg: #3B82F6;
    --button-hover: #2563EB;
    
    /* PolicyEngine Colors */
    --darkest-blue: #182333;
    --primary-blue: #5B9BD5;
    --lightest-blue: #ECF5FC;
    --dark-gray: #6B7280;
    --medium-dark-gray: #D1D5DB;
    --policyengine-blue: #5B9BD5;
    --grid-lines: #D1D5DB;
    
    /* Fonts */
    --font-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'Roboto Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
  }
  
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: var(--font-sans);
    background: var(--app-background);
    color: var(--text-primary);
  }
  
  :global(*) {
    box-sizing: border-box;
  }
  
  .app-container {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
  }
  
  /* Full-screen chart background */
  .chart-background {
    position: fixed; /* Fixed to viewport */
    top: 60px; /* Account for header */
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1;
  }
  
  /* Scrollable overlay only on the left side */
  .content-overlay {
    position: absolute;
    top: 60px; /* Account for header */
    left: 0;
    width: 40%;
    max-width: 680px; /* 600px + 80px margin */
    bottom: 0;
    overflow-y: auto;
    z-index: 2;
  }
  
  .text-content {
    padding: 2rem 3rem 50vh 3rem;
    margin-left: 80px; /* Space for y-axis */
  }
  
  /* Make text sections interactive */
  .text-section {
    pointer-events: auto;
  }
  
  /* Transparent area for chart interaction - remove this as it's blocking */
  .chart-interaction-area {
    display: none;
  }
  
  .text-section {
    margin-bottom: 100vh;
    opacity: 0.4;
    transition: all 0.5s ease;
    min-height: 200px;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.5);
    pointer-events: auto;
  }
  
  .text-section:global(.active) {
    opacity: 1;
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  }
  
  .text-section h2 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 1rem 0;
    color: var(--text-primary);
  }
  
  .text-section p {
    font-size: 1.1rem;
    line-height: 1.6;
    color: var(--text-secondary);
    margin: 0 0 1rem 0;
  }
  
  .section-content {
    padding: 0;
  }
  
  
  .individual-section {
    margin-bottom: 80vh;
    background: rgba(255, 255, 255, 0.9);
  }
  
  .individual-section:global(.active) {
    background: rgba(255, 255, 255, 0.98);
  }
  
  
  .error-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .error-content {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    max-width: 500px;
    text-align: center;
  }
  
  .error-content h2 {
    color: #EF4444;
    margin: 0 0 1rem 0;
  }
  
  .error-content button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: var(--button-bg);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }
  
  .error-content button:hover {
    background: var(--button-hover);
  }
  
  /* Responsive design */
  @media (max-width: 768px) {
    .content-overlay {
      width: 100%;
      max-width: none;
    }
    
    .text-content {
      padding: 1rem 1.5rem 20vh 1.5rem;
      margin-left: 40px; /* Less space needed on mobile */
    }
    
    .text-section {
      margin-bottom: 50vh;
    }
    
    .text-section h2 {
      font-size: 1.5rem;
    }
    
    .text-section p {
      font-size: 1rem;
    }
  }
</style>