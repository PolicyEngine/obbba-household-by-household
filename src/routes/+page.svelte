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
  let allDatasets = {}; // Store both datasets
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
  
  // Track if we need to scroll to a household on load
  let pendingScrollToHousehold = null;
  
  // Flag to prevent URL subscription from triggering during internal updates
  let isInternalUpdate = false;
  
  // Draggable state
  let draggingSectionIndex = null;
  let dragOffset = { x: 0, y: 0 };
  let sectionPositions = {};
  
  // Calculate statistics for a section
  function calculateSectionStats(sectionData, includeMedian = false, sectionId = null) {
    if (!sectionData || sectionData.length === 0) return null;
    
    let totalWeight = 0;
    let positiveWeight = 0;
    let negativeWeight = 0;
    let affectedWeight = 0;
    const percentChanges = [];
    
    sectionData.forEach(d => {
      const weight = d['Household weight'] || d['Household Weight'] || 1;
      const percentChange = d['Percentage Change in Net Income'] || 0;
      
      totalWeight += weight;
      if (percentChange > 0) {
        positiveWeight += weight;
        affectedWeight += weight;
      } else if (percentChange < 0) {
        negativeWeight += weight;
        affectedWeight += weight;
      }
      
      // For median calculation
      if (includeMedian) {
        percentChanges.push({ change: percentChange, weight: weight });
      }
    });
    
    const positivePercent = totalWeight > 0 ? Math.round((positiveWeight / totalWeight) * 100) : 0;
    const negativePercent = totalWeight > 0 ? Math.round((negativeWeight / totalWeight) * 100) : 0;
    const affectedPercent = totalWeight > 0 ? Math.round((affectedWeight / totalWeight) * 100) : 0;
    
    // Format total households in millions
    const totalMillions = totalWeight / 1000000;
    // Show one decimal place only for highest income group, round others to nearest million
    const totalFormatted = sectionId === 'highest-income' 
      ? totalMillions.toFixed(1) 
      : Math.round(totalMillions).toString();
    
    const stats = {
      total: totalFormatted,
      totalRaw: totalWeight,
      positivePercent,
      negativePercent,
      affectedPercent
    };
    
    // Calculate weighted median if requested
    if (includeMedian && percentChanges.length > 0) {
      // Sort by percent change
      percentChanges.sort((a, b) => a.change - b.change);
      
      // Find weighted median
      let cumulativeWeight = 0;
      const halfWeight = totalWeight / 2;
      let medianChange = 0;
      
      for (const item of percentChanges) {
        cumulativeWeight += item.weight;
        if (cumulativeWeight >= halfWeight) {
          medianChange = item.change;
          break;
        }
      }
      
      stats.medianChange = medianChange.toFixed(1);
    }
    
    return stats;
  }
  
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
  
  // Get current state
  $: currentState = scrollStates[$currentStateIndex] || scrollStates[0];
  
  // Re-render chart whenever transition values change
  $: if (chartComponent && ($isTransitioning || $currentInterpolationT)) {
    chartComponent.renderVisualization();
  }
  
  // Handle pending scroll to household when sections are ready
  $: if (pendingScrollToHousehold && textSections.length > 0 && textSections[pendingScrollToHousehold.targetIndex]) {
    const { household, targetIndex } = pendingScrollToHousehold;
    
    // Ensure the household is selected
    selectedHousehold = household;
    
    // Scroll to the section
    setTimeout(() => {
      if (textSections[targetIndex]) {
        textSections[targetIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 200);
    
    // Clear the pending scroll
    pendingScrollToHousehold = null;
  }
  
  // Handle section changes
  function handleSectionChange() {
    // This is called when a new section becomes active
    // The continuous animation is handled by the reactive statement above
  }
  
  // Drag handling
  function startDrag(event, index) {
    draggingSectionIndex = index;
    const currentPos = sectionPositions[index] || { x: 0, y: 0 };
    dragOffset = {
      x: event.clientX - currentPos.x,
      y: event.clientY - currentPos.y
    };
    event.preventDefault();
  }
  
  function handleDrag(event) {
    if (draggingSectionIndex === null) return;
    
    const newPos = {
      x: event.clientX - dragOffset.x,
      y: event.clientY - dragOffset.y
    };
    
    sectionPositions[draggingSectionIndex] = newPos;
    sectionPositions = sectionPositions; // Trigger reactivity
  }
  
  function endDrag() {
    draggingSectionIndex = null;
  }
  
  // Handle household selection
  function selectHousehold(household, shouldScroll = true) {
    // If not scrolling, prevent all scroll behavior
    if (!shouldScroll) {
      // Disable scroll events temporarily
      const preventScroll = (e) => {
        e.preventDefault();
        e.stopPropagation();
        return false;
      };
      
      // Add listeners to block scroll
      window.addEventListener('scroll', preventScroll, { capture: true });
      scrollContainer?.addEventListener('scroll', preventScroll, { capture: true });
      
      // Remove listeners after update
      setTimeout(() => {
        window.removeEventListener('scroll', preventScroll, { capture: true });
        scrollContainer?.removeEventListener('scroll', preventScroll, { capture: true });
      }, 300);
    }
    
    selectedHousehold = household;
    
    // If we're in a group view, update the random household for that section
    const currentState = scrollStates[$currentStateIndex];
    if (currentState && currentState.viewType === 'group') {
      // Update the random household for this section - use object spread
      randomHouseholds = {
        ...randomHouseholds,
        [currentState.id]: household
      };
      
      // Only scroll if explicitly requested (not when randomizing)
      if (shouldScroll) {
        // Find the next individual view and scroll to it
        const nextIndex = $currentStateIndex + 1;
        if (scrollStates[nextIndex] && scrollStates[nextIndex].viewType === 'individual') {
          // Scroll to the individual view
          if (textSections[nextIndex]) {
            textSections[nextIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }
      }
    } else if (currentState && currentState.viewType === 'individual') {
      // Update the random household for the base section
      const baseViewId = currentState.id.replace('-individual', '');
      randomHouseholds = {
        ...randomHouseholds,
        [baseViewId]: household
      };
      
      // Update household display
      const sectionIndex = Math.floor($currentStateIndex / 2);
      
      // Animate other household numbers
      createAnimatedNumber(`num-dependents-${sectionIndex}`, 0, 
        Math.round(household['Number of Dependents'] || household['Dependents'] || 0), 
        d => Math.round(d), 700);
      createAnimatedNumber(`age-of-head-${sectionIndex}`, 18, 
        household['Age of Head'] || household['Age'] || 40, 
        d => Math.round(d), 800);
    }
    
    // Animate the household point
    animateHouseholdEmphasis(household.id);
    
    // Update URL
    updateUrlWithHousehold(household.id, selectedDataset);
    
    // Force chart re-render
    if (chartComponent?.renderVisualization) {
      chartComponent.renderVisualization();
    }
  }
  
  // Randomize household for current section
  function randomizeHousehold() {
    const baseViewId = currentState?.id?.replace('-individual', '') || currentState?.id;
    const state = scrollStates.find(s => s.id === baseViewId);
    
    if (state && data.length > 0) {
      const filteredData = data.filter(d => state.filter(d));
      const newHousehold = getRandomWeightedHousehold(filteredData);
      
      if (newHousehold) {
        // Don't scroll when randomizing
        selectHousehold(newHousehold, false);
        
        // Re-trigger animations
        const sectionIndex = Math.floor($currentStateIndex / 2);
        createAnimatedNumber(`household-id-${sectionIndex}`, 
          selectedHousehold?.id || 0, newHousehold.id, d => Math.round(d), 600);
      }
    }
  }
  
  // Handle dataset change
  function handleDatasetChange(dataset) {
    if (!allDatasets[dataset]) {
      console.error('Dataset not loaded:', dataset);
      return;
    }
    
    // Preserve current scroll position
    const currentScrollTop = scrollContainer?.scrollTop || 0;
    
    // Debug: Check if datasets are actually different
    console.log('Switching from', selectedDataset, 'to', dataset);
    console.log('Old dataset length:', data.length);
    console.log('New dataset length:', allDatasets[dataset]?.length);
    
    // Remember current household ID if one is selected
    const currentHouseholdId = selectedHousehold?.id;
    
    // Sample a few households to verify data differences
    if (data.length > 0 && allDatasets[dataset]?.length > 0) {
      const sampleIds = ['1', '100', '1000', '10000'];
      sampleIds.forEach(id => {
        const oldHousehold = data.find(d => String(d.id) === id);
        const newHousehold = allDatasets[dataset].find(d => String(d.id) === id);
        if (oldHousehold && newHousehold) {
          console.log(`Sample household ${id} comparison:`, {
            oldNetIncome: oldHousehold['Total Change in Net Income'] || oldHousehold['Change in Household Net Income'],
            newNetIncome: newHousehold['Total Change in Net Income'] || newHousehold['Change in Household Net Income'],
            oldPercentChange: oldHousehold['Percentage Change in Net Income'],
            newPercentChange: newHousehold['Percentage Change in Net Income']
          });
        }
      });
    }
    
    // NOW update selectedDataset after logging
    selectedDataset = dataset;
    
    // Switch to the new dataset instantly
    data = allDatasets[dataset];
    
    // Preserve random households by finding the same household IDs in the new dataset
    const oldRandomHouseholds = { ...randomHouseholds };
    const newRandomHouseholds = {};
    
    Object.entries(oldRandomHouseholds).forEach(([sectionId, oldHousehold]) => {
      // Find the household with the same ID in the new dataset
      const newHousehold = data.find(d => String(d.id) === String(oldHousehold.id));
      if (newHousehold) {
        newRandomHouseholds[sectionId] = newHousehold;
        // Debug: Check if values are actually different
        console.log(`Household ${oldHousehold.id} in section ${sectionId}:`, {
          previousDataset: dataset === 'tcja-expiration' ? 'tcja-extension' : 'tcja-expiration',
          newDataset: dataset,
          oldNetChange: oldHousehold['Total Change in Net Income'] || oldHousehold['Change in Household Net Income'],
          newNetChange: newHousehold['Total Change in Net Income'] || newHousehold['Change in Household Net Income'],
          oldPercentChange: oldHousehold['Percentage Change in Net Income'],
          newPercentChange: newHousehold['Percentage Change in Net Income'],
          // Check all possible income fields
          oldFields: Object.keys(oldHousehold).filter(k => k.includes('Income')).map(k => ({ [k]: oldHousehold[k] })),
          newFields: Object.keys(newHousehold).filter(k => k.includes('Income')).map(k => ({ [k]: newHousehold[k] }))
        });
      }
    });
    
    // If any sections don't have households, initialize them
    scrollStates.forEach(state => {
      if (state.viewType === 'group' && !newRandomHouseholds[state.id]) {
        const filteredData = data.filter(d => state.filter(d));
        const randomHousehold = getRandomWeightedHousehold(filteredData);
        if (randomHousehold) {
          newRandomHouseholds[state.id] = randomHousehold;
        }
      }
    });
    
    // Assign the new random households object to trigger reactivity
    randomHouseholds = newRandomHouseholds;
    
    // Force Svelte to detect the change
    randomHouseholds = randomHouseholds;
    
    // Try to find the same household in the new dataset
    if (currentHouseholdId) {
      const household = data.find(d => String(d.id) === String(currentHouseholdId));
      if (household) {
        selectedHousehold = household;
        animateHouseholdEmphasis(household.id);
      } else {
        selectedHousehold = null;
      }
    }
    
    // Update URL with internal flag to prevent re-triggering
    isInternalUpdate = true;
    updateUrlWithHousehold(selectedHousehold?.id, dataset);
    
    // Force chart re-render
    if (chartComponent?.renderVisualization) {
      chartComponent.renderVisualization();
    }
    
    // Restore scroll position after a brief delay to allow for any layout changes
    if (scrollContainer && currentScrollTop > 0) {
      requestAnimationFrame(() => {
        scrollContainer.scrollTop = currentScrollTop;
      });
    }
  }
  
  // Handle URL parameters
  async function handleUrlParams() {
    try {
      const { householdId, baseline } = parseUrlParams();
      console.log('handleUrlParams called with:', { householdId, baseline });
      
      // Update baseline if provided
      if (baseline && baseline !== selectedDataset) {
        selectedDataset = baseline;
      }
      
      // Load all datasets if needed
      if (Object.keys(allDatasets).length === 0) {
      isLoading = true;
      try {
        console.log('Loading all datasets...');
        allDatasets = await loadDatasets();
        console.log('Loaded datasets:', Object.keys(allDatasets), 'lengths:', {
          'tcja-expiration': allDatasets['tcja-expiration']?.length,
          'tcja-extension': allDatasets['tcja-extension']?.length
        });
        data = allDatasets[selectedDataset];
        console.log('Selected dataset:', selectedDataset, 'length:', data.length);
        initializeRandomHouseholds();
      } catch (error) {
        console.error('Error loading data:', error);
        loadError = error.message;
        isLoading = false;
        return;
      }
      isLoading = false;
    } else {
      // Datasets already loaded, just switch
      data = allDatasets[selectedDataset];
    }
    
    // Handle household selection
    if (householdId && data.length > 0) {
      console.log('Looking for household:', householdId, 'in', data.length, 'households');
      const household = data.find(d => String(d.id) === householdId);
      if (household) {
        console.log('Found household:', household);
        selectedHousehold = household;
        
        // Find appropriate section
        const targetIndex = findSectionForHousehold(household, scrollStates);
        console.log('Target index:', targetIndex, 'textSections length:', textSections.length);
        
        // Update the random household for the appropriate section
        const baseViewId = scrollStates[targetIndex]?.id?.replace('-individual', '') || scrollStates[targetIndex]?.id;
        if (baseViewId) {
          randomHouseholds[baseViewId] = household;
        }
        
        // Scroll to section
        if (textSections[targetIndex] && scrollContainer) {
          // Delay to ensure DOM is ready
          setTimeout(() => {
            textSections[targetIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 100);
        } else {
          // If sections aren't ready yet, store for later
          pendingScrollToHousehold = { household, targetIndex };
        }
      }
    }
    } catch (error) {
      console.error('Error in handleUrlParams:', error);
      loadError = `Failed to load data: ${error.message}`;
    }
  }
  
  // Lifecycle
  onMount(async () => {
    console.log('Component mounted, starting initialization...');
    
    // Add global error handler
    const handleError = (event) => {
      console.error('Global error caught:', event.error);
      loadError = `An error occurred: ${event.error?.message || 'Unknown error'}`;
      event.preventDefault();
    };
    
    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleError);
    
    // Check if we're in an iframe and get URL params from parent if needed
    const isInIframe = window.self !== window.top;
    if (isInIframe) {
      // Check if parent passed parameters
      const urlParams = new URLSearchParams(window.location.search);
      console.log('In iframe, URL params:', urlParams.toString());
    }
    
    // Handle initial URL parameters
    await handleUrlParams();
    
    // Set up scroll observer
    if (textSections.length > 0) {
      scrollObserver = createIntersectionObserver(textSections, handleSectionChange);
    }
    
    // Listen for URL changes
    const unsubscribe = page.subscribe(() => {
      // Skip if this is an internal update
      if (isInternalUpdate) {
        isInternalUpdate = false;
        return;
      }
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
    
    // Add wheel event listener to enable scrolling from anywhere
    function handleWheel(event) {
      // Always scroll the container when wheel event happens
      if (scrollContainer) {
        scrollContainer.scrollTop += event.deltaY;
        event.preventDefault();
      }
    }
    
    window.addEventListener('wheel', handleWheel, { passive: false });
    
    // Add drag event listeners
    window.addEventListener('mousemove', handleDrag);
    window.addEventListener('mouseup', endDrag);
    
    // Notify parent we're ready
    notifyParentOfUrlChange();
    
    return () => {
      unsubscribe();
      window.removeEventListener('message', handleMessage);
      window.removeEventListener('wheel', handleWheel);
      window.removeEventListener('mousemove', handleDrag);
      window.removeEventListener('mouseup', endDrag);
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleError);
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
      onPointClick={(household) => selectHousehold(household, false)}
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
            class:dragging={draggingSectionIndex === i}
            data-index={i}
            bind:this={textSections[i]}
            style="transform: translate({sectionPositions[i]?.x || 0}px, {sectionPositions[i]?.y || 0}px)"
            on:mousedown={(e) => startDrag(e, i)}
          >
            <div class="section-content">
              <div class="drag-handle" title="Drag to move">⋮⋮</div>
              <h2>{state.title}</h2>
              
              <!-- Dynamic content for income sections -->
              {#if state.id !== 'intro' && data.length > 0}
                {@const sectionData = data.filter(d => state.filter(d))}
                {@const stats = calculateSectionStats(sectionData, false, state.id)}
                {#if stats}
                  {#if state.id === 'lower-income'}
                    <p>Of the {stats.total} million households with market income below $50,000, OBBBA will increase the net income of {stats.positivePercent}% and reduce the net income of {stats.negativePercent}%. Let's take a look at one of them at random. You can also click on a dot to view information about a household.</p>
                  {:else if state.id === 'middle-income'}
                    <p>Of the {stats.total} million households with market income between $50,000 and $200,000, OBBBA will increase the net income of {stats.positivePercent}% and reduce the net income of {stats.negativePercent}%. Let's take a look at one of them at random. You can also click on a dot to view information about a household.</p>
                  {:else if state.id === 'upper-income'}
                    <p>Of the {stats.total} million households with market income between $200,000 and $1 million, OBBBA will increase the net income of {stats.positivePercent}% and reduce the net income of {stats.negativePercent}%. Let's take a look at one of them at random. You can also click on a dot to view information about a household.</p>
                  {:else if state.id === 'highest-income'}
                    <p>Of the {stats.total} million households with market income over $1 million, OBBBA will increase the net income of {stats.positivePercent}% and reduce the net income of {stats.negativePercent}%. Let's take a look at one of them at random. You can also click on a dot to view information about a household.</p>
                  {:else if state.id === 'all-households'}
                    {@const allStats = calculateSectionStats(sectionData, true, state.id)}
                    <p>{@html state.description.replace('{totalPercentage}', allStats.affectedPercent).replace('{medianImpact}', allStats.medianChange)}</p>
                  {/if}
                {/if}
                
                <!-- Integrated household profile for all income sections except all-households -->
                {#if randomHouseholds[state.id] && state.id !== 'all-households'}
                  <div class="integrated-household-profile">
                    <HouseholdProfile
                      household={randomHouseholds[state.id]}
                      selectedDataset={selectedDataset}
                      currentState={state}
                      sectionIndex={0}
                      onRandomize={randomizeHousehold}
                    />
                  </div>
                {/if}
              {:else if state.id === 'intro'}
                {#if state.description}
                  <p>{@html state.description}</p>
                {/if}
                {#if state.content}
                  <p>{@html state.content}</p>
                {/if}
              {/if}
              
              <!-- Scroll indicator inside first section -->
              {#if i === 0 && $currentStateIndex === 0}
                <div class="scroll-indicator">
                  <span>Scroll to explore</span>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 5v14M19 12l-7 7-7-7"/>
                  </svg>
                </div>
              {/if}
            </div>
          </section>
        {/if}
      {/each}
    </div>
  </div>
  
  {#if isLoading}
    <LoadingOverlay message="Loading tax impact data..." />
  {/if}
  
  {#if loadError}
    <div class="error-overlay">
      <div class="error-content">
        <h2>Error loading data</h2>
        <p>{loadError}</p>
        <button on:click={() => location.reload()}>Reload page</button>
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
  
  /* Scrollable content overlay - full width to allow dragging anywhere */
  .content-overlay {
    position: absolute;
    top: 60px; /* Account for header */
    left: 0;
    width: 100%; /* Full width for dragging */
    bottom: 0;
    overflow-y: auto;
    overflow-x: hidden; /* Prevent horizontal scroll */
    z-index: 10; /* Higher than chart but much lower than header (9999) */
    pointer-events: none; /* Allow clicks through except on text sections */
    -webkit-overflow-scrolling: touch; /* Smooth scrolling on iOS */
    /* Prevent automatic scroll adjustments */
    overflow-anchor: none;
    scroll-behavior: auto;
    
    /* Prevent scroll snap behavior */
    scroll-snap-type: none !important;
    scroll-behavior: auto !important;
    
    /* Hide scrollbar while keeping functionality */
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE and Edge */
  }
  
  /* Hide scrollbar for Chrome, Safari and Opera */
  .content-overlay::-webkit-scrollbar {
    display: none;
  }
  
  .text-content {
    padding: 2rem 3rem 50vh 3rem;
    margin-left: 120px; /* Space for y-axis - matches chart margin */
    max-width: 680px; /* Keep text content constrained to left side */
  }
  
  
  /* Make text sections interactive */
  .text-section {
    pointer-events: auto;
  }
  
  /* Scroll indicator */
  .scroll-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-secondary);
    font-size: 13px;
    font-weight: 500;
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    animation: bounce 2s infinite;
    opacity: 0.7;
  }
  
  .scroll-indicator:hover {
    opacity: 1;
  }
  
  .scroll-indicator svg {
    animation: arrow-bounce 1.5s ease-in-out infinite;
  }
  
  @keyframes bounce {
    0%, 20%, 50%, 80%, 100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-3px);
    }
    60% {
      transform: translateY(-1px);
    }
  }
  
  @keyframes arrow-bounce {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(3px);
    }
  }
  
  .text-section {
    margin-bottom: 100vh;
    transition: transform 0.1s ease, box-shadow 0.5s ease, background 0.5s ease;
    min-height: 200px;
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(226, 232, 240, 0.5);
    pointer-events: auto;
    position: relative;
    cursor: move;
    user-select: none;
    z-index: 15;
    /* Prevent any scroll snap behavior */
    scroll-snap-align: none !important;
    scroll-margin: 0 !important;
  }
  
  .text-section:not(.active) {
    background: rgba(255, 255, 255, 0.5);
  }
  
  .text-section.dragging {
    background: rgba(255, 255, 255, 0.65);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
    z-index: 100;
  }
  
  .text-section.active {
    background: rgba(255, 255, 255, 0.7);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
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
    position: relative;
  }
  
  .drag-handle {
    position: absolute;
    top: -0.5rem;
    right: 0.5rem;
    color: var(--text-secondary);
    opacity: 0.3;
    font-size: 20px;
    cursor: grab;
    transition: opacity 0.2s;
    user-select: none;
  }
  
  .text-section:hover .drag-handle {
    opacity: 0.6;
  }
  
  .text-section.dragging .drag-handle {
    cursor: grabbing;
    opacity: 0.8;
  }
  
  
  .integrated-household-profile {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
    /* Prevent layout shifts by maintaining minimum height */
    min-height: 400px;
    position: relative;
    /* Prevent being used as scroll anchor */
    overflow-anchor: none;
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
      top: 90px; /* Account for multi-row header */
      /* Extra prevention of scroll snap on mobile */
      -webkit-overflow-scrolling: auto !important;
      scroll-snap-type: none !important;
    }
    
    .text-content {
      padding: 1rem 1rem 30vh 1rem;
      margin-left: 0; /* Full width on mobile */
      max-width: 100%;
    }
    
    .text-section {
      margin-bottom: 60vh;
      padding: 1rem;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.85);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
    }
    
    .text-section h2 {
      font-size: 1.25rem;
      line-height: 1.3;
      margin-bottom: 0.75rem;
    }
    
    .text-section p {
      font-size: 0.875rem;
      line-height: 1.5;
    }
    
    .drag-handle {
      display: none; /* Hide drag handle on mobile */
    }
    
    .integrated-household-profile {
      margin-top: 1rem;
      padding-top: 1rem;
    }
    
    .scroll-indicator {
      font-size: 12px;
      margin-top: 1rem;
      padding-top: 0.75rem;
    }
    
    .chart-background {
      top: 90px; /* Match multi-row header height */
    }
  }
  
  /* Small mobile devices */
  @media (max-width: 480px) {
    .text-content {
      padding: 0.75rem 0.75rem 20vh 0.75rem;
    }
    
    .text-section {
      padding: 0.875rem;
      margin-bottom: 50vh;
    }
    
    .text-section h2 {
      font-size: 1.125rem;
    }
    
    .text-section p {
      font-size: 0.8125rem;
    }
  }
</style>