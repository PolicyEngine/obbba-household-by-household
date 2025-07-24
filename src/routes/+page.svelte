<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { DATASETS } from '$lib/config/datasets.js';
  import { scrollStates } from '$lib/config/views.js';
  import { loadDatasets, loadDatasetsProgressive } from '$lib/data/dataLoader.js';
  import { loadDatasetsUltraFast } from '$lib/data/optimizedDataLoader.js';
  import { loadDatasetUltraFast } from '$lib/data/ultraFastLoader.js';
  import { loadInstantVisualization, loadFullDataBackground } from '$lib/data/instantLoader.js';
  import { loadTinyVisualization } from '$lib/data/tinyLoader.js';
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
  import HouseholdProfile from '$lib/components/HouseholdProfile.svelte';
  import ScatterPlot from '$lib/components/ScatterPlot.svelte';
  
  // Data state
  let allDatasets = {}; // Store both datasets
  let data = [];
  let selectedHousehold = null;
  let isLoading = false;
  let loadError = null;
  let selectedDataset = 'tcja-expiration';
  let secondDatasetLoading = false; // Track background loading
  let baselineDropdownOpen = false; // Track dropdown state on mobile
  
  // Random households for each section
  let randomHouseholds = {};
  
  // References
  let scrollObserver = null;
  let textSections = [];
  let scrollContainer = null;
  let chartComponent = null;
  
  // Track if we need to scroll to a household on load
  let pendingScrollToHousehold = null;
  
  // Random starting side for alternating layout (consistent per session)
  const startOnLeft = Math.random() < 0.5;
  
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
      const weight = d['Household weight'] || d['Household weight'] || 1;
      const percentChange = d['Percentage change in net income'] || 0;
      
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
    
    const isInIframe = window.self !== window.top;
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
  async function selectHousehold(household, shouldScroll = true) {
    // If not scrolling, lock the scroll position
    if (!shouldScroll && scrollContainer) {
      // Save current scroll position
      const savedScrollTop = scrollContainer.scrollTop;
      
      // Use a debounced scroll handler to avoid vibration
      let scrollTimeout;
      const maintainScroll = (e) => {
        // Clear any pending position restore
        clearTimeout(scrollTimeout);
        
        // Restore position after a tiny delay to avoid fighting with browser
        scrollTimeout = setTimeout(() => {
          if (scrollContainer && Math.abs(scrollContainer.scrollTop - savedScrollTop) > 1) {
            scrollContainer.scrollTop = savedScrollTop;
          }
        }, 10);
      };
      
      // Add scroll listener to maintain position
      scrollContainer.addEventListener('scroll', maintainScroll, { passive: false });
      
      // Remove listener after animations complete
      setTimeout(() => {
        clearTimeout(scrollTimeout);
        scrollContainer.removeEventListener('scroll', maintainScroll);
      }, 1000); // Match the longest animation duration
    }
    
    selectedHousehold = household;
    
    // If we're in a group view, update the random household for that section
    const currentState = scrollStates[$currentStateIndex];
    if (currentState && currentState.viewType === 'group') {
      // Update the random household for this section - use object spread
      randomHouseholds = {
        ...randomHouseholds,
        [currentState.id]: { ...household }
      };
      
      // Only scroll if explicitly requested (not when randomizing) AND not in iframe
      const isInIframe = window.self !== window.top;
      if (shouldScroll && !isInIframe) {
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
        [baseViewId]: { ...household }
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
    await updateUrlWithHousehold(household.id, selectedDataset);
    
    // Force chart re-render
    if (chartComponent?.forceRender) {
      chartComponent.forceRender();
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
        selectHousehold({ ...newHousehold }, false);
        
        // Re-trigger animations
        const sectionIndex = Math.floor($currentStateIndex / 2);
        createAnimatedNumber(`household-id-${sectionIndex}`, 
          selectedHousehold?.id || 0, newHousehold.id, d => Math.round(d), 600);
      }
    }
  }
  
  // Handle dataset change
  async function handleDatasetChange(dataset) {
    // Always allow switching, even if dataset isn't fully loaded yet
    if (!allDatasets[dataset]) {
      console.log(`Switching to ${dataset} - will use when available`);
      selectedDataset = dataset;
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
            oldNetIncome: oldHousehold['Total change in net income'] || oldHousehold['Change in Household Net Income'],
            newNetIncome: newHousehold['Total change in net income'] || newHousehold['Change in Household Net Income'],
            oldPercentChange: oldHousehold['Percentage change in net income'],
            newPercentChange: newHousehold['Percentage change in net income']
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
          oldNetChange: oldHousehold['Total change in net income'] || oldHousehold['Change in Household Net Income'],
          newNetChange: newHousehold['Total change in net income'] || newHousehold['Change in Household Net Income'],
          oldPercentChange: oldHousehold['Percentage change in net income'],
          newPercentChange: newHousehold['Percentage change in net income'],
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
    await updateUrlWithHousehold(selectedHousehold?.id, dataset);
    
    // Force chart re-render
    if (chartComponent?.forceRender) {
      chartComponent.forceRender();
    }
    
    // Restore scroll position after a brief delay to allow for any layout changes
    if (scrollContainer && currentScrollTop > 0) {
      requestAnimationFrame(() => {
        scrollContainer.scrollTop = currentScrollTop;
      });
    }
  }
  
  // Track if data is currently loading to prevent duplicate loads
  let isLoadingData = false;
  
  // Handle URL parameters
  async function handleUrlParams() {
    // Prevent duplicate loads
    if (isLoadingData) {
      console.log('Already loading data, skipping duplicate call');
      return;
    }
    
    try {
      const { householdId, baseline } = parseUrlParams();
      console.log('handleUrlParams called with:', { householdId, baseline });
      
      // Update baseline if provided
      if (baseline && baseline !== selectedDataset) {
        selectedDataset = baseline;
      }
      
      // Load all datasets if needed
      if (Object.keys(allDatasets).length === 0) {
        // Don't show loading spinner - minimal data loads instantly
        isLoadingData = true; // Set the flag to prevent duplicate loads
        
        // Use TINY sample for instant visualization - 1000 dots
        console.log('Starting tiny sample loading for instant display...');
        
        // STEP 1: Load 1000-point sample for instant starfield
        loadTinyVisualization((update) => {
          try {
            if (update.phase === 'sample') {
              console.log(`✨ Sample visualization data ready: ${update.visualData.length} dots`);
              
              // Set data immediately for full starfield animation
              data = update.visualData;
              isLoading = false;
              
              // Delay household initialization to let dots render first
              setTimeout(() => {
                initializeRandomHouseholds();
              }, 50);
              
              // Force immediate render without waiting for next frame
              if (chartComponent?.forceRender) {
                // Use microtask to ensure data is set first
                Promise.resolve().then(() => {
                  chartComponent.forceRender();
                });
              }
            }
          } catch (error) {
            console.error('Error processing instant visualization:', error);
            loadError = `Failed to process visualization: ${error.message}`;
            isLoading = false;
            isLoadingData = false;
          }
        }).catch(error => {
          console.error('Error loading instant visualization:', error);
          loadError = `Failed to load minimal data: ${error.message}`;
          isLoading = false;
          isLoadingData = false;
        });
        
        // STEP 2: Load full datasets in background after dots are rendering
        setTimeout(() => {
          console.log('Starting background full data loading...');
          
          // Load selected dataset first
          loadFullDataBackground(selectedDataset, (update) => {
            if (update[selectedDataset]) {
              console.log(`Full ${selectedDataset} data ready: ${update[selectedDataset].length} rows`);
              
              // Update with full data (keeps same visual positions)
              allDatasets[selectedDataset] = update[selectedDataset];
              data = update[selectedDataset];
              
              // Clear and re-initialize random households with full data
              randomHouseholds = {};
              // Delay household initialization to prevent UI blocking
              setTimeout(() => {
                initializeRandomHouseholds();
              }, 100);
              
              // Clear selected household to force re-selection with full data
              selectedHousehold = null;
              
              // Handle household selection if pending
              if (householdId) {
                handleHouseholdSelection(householdId);
              }
              
              // Now load the other dataset
              const otherDataset = selectedDataset === 'tcja-expiration' ? 'tcja-extension' : 'tcja-expiration';
              loadFullDataBackground(otherDataset, (otherUpdate) => {
                if (otherUpdate[otherDataset]) {
                  console.log(`Full ${otherDataset} data ready: ${otherUpdate[otherDataset].length} rows`);
                  allDatasets[otherDataset] = otherUpdate[otherDataset];
                  
                  // All done!
                  secondDatasetLoading = false;
                  isLoadingData = false;
                }
              }).catch(error => {
                console.error(`Error loading ${otherDataset}:`, error);
                secondDatasetLoading = false;
                isLoadingData = false;
              });
            }
          }).catch(error => {
          console.error('Error loading data:', error);
          loadError = error.message;
          isLoading = false;
          secondDatasetLoading = false;
          isLoadingData = false; // Clear on error too
        });
        }, 300); // Delay to ensure dots are rendering before loading full data
        
        // FALLBACK: Keep old progressive loader as backup
        /*loadDatasetsProgressive(
            // First dataset sample loaded callback
            (sampleDatasets) => {
              // Callback when first dataset sample is loaded
              console.log('First dataset sample loaded:', Object.keys(sampleDatasets));
              allDatasets = { ...sampleDatasets };
              
              // Always stop loading overlay once first dataset sample is available
              isLoading = false;
              
              // SMOOTH TRANSITION: Only set data if we don't already have data to prevent jumps
              if (data.length === 0) {
                                  // If current selection is TCJA expiration, show it immediately
                  if (selectedDataset === 'tcja-expiration' && sampleDatasets['tcja-expiration']) {
                    data = sampleDatasets['tcja-expiration'];
                    initializeRandomHouseholds();
                    secondDatasetLoading = true; // But indicate background loading
                    
                    // Force immediate chart render
                    if (chartComponent?.forceRender) {
                      setTimeout(() => chartComponent.forceRender(), 0);
                    }
                    
                    // Handle household selection now that data is loaded
                    handleHouseholdSelection(householdId);
                  } else if (selectedDataset === 'tcja-extension') {
                    // If user wants extension dataset but it's not loaded yet, 
                    // show expiration dataset temporarily and indicate loading
                    if (sampleDatasets['tcja-expiration']) {
                      data = sampleDatasets['tcja-expiration'];
                      initializeRandomHouseholds();
                      secondDatasetLoading = true;
                      
                      // Force immediate chart render
                      if (chartComponent?.renderVisualization) {
                        setTimeout(() => chartComponent.renderVisualization(), 0);
                      }
                    }
                  }
                  
                  // CHECK FOR ULTRA-FAST COMPLETION: If both datasets loaded in first phase
                  if (sampleDatasets['tcja-expiration'] && sampleDatasets['tcja-extension']) {
                    secondDatasetLoading = false;
                  }
              }
            },
            // Second dataset sample loaded callback
            (completeDatasets) => {
              console.log('Second dataset sample loaded in background');
              allDatasets = { ...completeDatasets };
              
              // SMOOTH TRANSITION: Only update if significant improvement or user switched datasets
              const currentDataSize = data.length;
              const newDataSize = completeDatasets[selectedDataset]?.length || 0;
              const isSignificantImprovement = newDataSize > currentDataSize * 1.5; // 50% more data
              
              // If user switched to extension dataset while it was loading, update now
              if (selectedDataset === 'tcja-extension' && completeDatasets['tcja-extension'] && 
                  (currentDataSize === 0 || isSignificantImprovement)) {
                data = completeDatasets['tcja-extension'];
                initializeRandomHouseholds();
                // Handle household selection for extension dataset
                handleHouseholdSelection(householdId);
              }
              
              // CHECK FOR COMPLETION: If both datasets are now available, remove loading indicator
              if (completeDatasets['tcja-expiration'] && completeDatasets['tcja-extension']) {
                secondDatasetLoading = false;
              }
            },
            // Full dataset loaded callback
            (fullDatasets, datasetKey) => {
              console.log(`Full dataset loaded: ${datasetKey}`);
              allDatasets = { ...fullDatasets };
              
              // If this is the currently selected dataset, update the view
              if (selectedDataset === datasetKey) {
                console.log(`Updating view with full ${datasetKey} dataset (${fullDatasets[datasetKey].length} households)`);
                data = fullDatasets[datasetKey];
                initializeRandomHouseholds();
                
                // Re-handle household selection with full dataset
                handleHouseholdSelection(householdId);
                
                // Force chart re-render with full data
                if (chartComponent?.renderVisualization) {
                  chartComponent.renderVisualization();
                }
              }
              
              // SIMPLIFIED COMPLETION LOGIC: Just check if both datasets exist
              if (fullDatasets['tcja-expiration'] && fullDatasets['tcja-extension']) {
                const expirationSize = fullDatasets['tcja-expiration'].length;
                const extensionSize = fullDatasets['tcja-extension'].length;
                
                // Both datasets have data, so remove loading indicator
                secondDatasetLoading = false;
              }
            }
          ).catch(error => {
            console.error('Error loading data:', error);
            loadError = error.message;
            isLoading = false;
            secondDatasetLoading = false;
          });*/
      } else {
        // Datasets already loaded, just switch
        if (allDatasets[selectedDataset]) {
          data = allDatasets[selectedDataset];
          // Handle household selection immediately
          handleHouseholdSelection(householdId);
        }
      }
    } catch (error) {
      console.error('Error in handleUrlParams:', error);
      loadError = `Failed to load data: ${error.message}`;
    }
  }
  
  // Separate function to handle household selection after data is loaded
  function handleHouseholdSelection(householdId) {
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
          // Use proper reactivity assignment
          randomHouseholds = {
            ...randomHouseholds,
            [baseViewId]: household
          };
        }
        
        // Scroll to section only if not in iframe
        const isInIframe = window.self !== window.top;
        if (!isInIframe) {
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
        
        // Ensure chart updates
        if (chartComponent?.renderVisualization) {
          chartComponent.renderVisualization();
        }
      } else {
        console.log('Household not found:', householdId);
      }
    }
  }
  
  // Track performance timing
  let pageLoadStart = typeof window !== 'undefined' ? performance.now() : 0;
  
  // Lifecycle
  onMount(async () => {
    console.log(`Component mounted at ${performance.now().toFixed(0)}ms (${(performance.now() - pageLoadStart).toFixed(0)}ms since page load)`);
    
    // Add global error handler
    const handleError = (event) => {
      console.error('Global error caught:', event.error);
      loadError = `An error occurred: ${event.error?.message || 'Unknown error'}`;
      event.preventDefault();
    };
    
    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleError);
    
    // Handle clicks outside dropdown to close it
    const handleClickOutside = (event) => {
      const selector = event.target.closest('.baseline-selector-overlay');
      if (!selector && baselineDropdownOpen) {
        baselineDropdownOpen = false;
      }
    };
    
    window.addEventListener('click', handleClickOutside);
    
    // Check if we're in an iframe and get URL params from parent if needed
    const isInIframe = window.self !== window.top;
    
    // Add class to body if in iframe
    if (isInIframe) {
      document.body.classList.add('in-iframe');
      console.log('Running in iframe, checking for parent URL parameters...');
      
      // Request parent to send current URL parameters
      window.parent.postMessage({
        type: 'requestUrlParams'
      }, '*');
      
      // Also check if parent URL has parameters that should be used
      // This handles the case where the iframe src doesn't include the params
      const parentUrl = document.referrer;
      if (parentUrl) {
        try {
          const parentUrlObj = new URL(parentUrl);
          const parentParams = new URLSearchParams(parentUrlObj.search);
          const household = parentParams.get('household');
          const baseline = parentParams.get('baseline');
          
          if (household || baseline) {
            console.log('Found parameters in parent URL:', { household, baseline });
            // Update our URL to match parent
            const currentUrl = new URL(window.location);
            if (household) currentUrl.searchParams.set('household', household);
            if (baseline) currentUrl.searchParams.set('baseline', baseline);
            window.history.replaceState({}, '', currentUrl);
          }
        } catch (e) {
          console.log('Could not parse parent URL:', e);
        }
      }
      
      // For PolicyEngine integration, check if URL params are missing from iframe src
      // but present in the parent page URL structure
      if (!window.location.search && parentUrl) {
        try {
          // Check if parent URL contains household explorer path with params
          const parentUrlMatch = parentUrl.match(/obbba-household-by-household[^?]*\?(.+)/);
          if (parentUrlMatch) {
            console.log('Found parameters in parent path, applying to iframe');
            const parentParams = new URLSearchParams(parentUrlMatch[1]);
            const currentUrl = new URL(window.location);
            
            // Copy relevant parameters
            ['household', 'baseline', 'section'].forEach(param => {
              const value = parentParams.get(param);
              if (value) {
                currentUrl.searchParams.set(param, value);
              }
            });
            
            window.history.replaceState({}, '', currentUrl);
          }
        } catch (e) {
          console.log('Could not extract parameters from parent path:', e);
        }
      }
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
      // For security, we could check event.origin here in production
      // if (event.origin !== expectedOrigin) return;
      
      if (event.data?.type === 'urlParams') {
        console.log('Received URL params from parent:', event.data.params);
        const url = new URL(window.location);
        const params = new URLSearchParams(event.data.params);
        
        let hasChanges = false;
        
        // Update our URL to match parent
        for (const [key, value] of params) {
          if (url.searchParams.get(key) !== value) {
            url.searchParams.set(key, value);
            hasChanges = true;
          }
        }
        
        // Only update if there are actual changes
        if (hasChanges) {
          window.history.replaceState({}, '', url);
          console.log('Updated iframe URL based on parent params');
          handleUrlParams();
        }
      }
      
      // Handle test messages
      if (event.data?.type === 'test') {
        const action = event.data.action;
        let response = { type: 'testResponse', action };
        
        switch (action) {
          case 'randomHousehold':
            try {
              randomizeHousehold();
              response.message = 'Random household selected successfully';
            } catch (error) {
              response.message = `Error: ${error.message}`;
            }
            break;
            
          case 'scroll':
            try {
              if (scrollContainer) {
                scrollContainer.scrollTop += 200;
                response.message = 'Scroll test completed';
              } else {
                response.message = 'Error: No scroll container found';
              }
            } catch (error) {
              response.message = `Error: ${error.message}`;
            }
            break;
            
          case 'switchBaseline':
            try {
              const newDataset = selectedDataset === 'tcja-expiration' ? 'tcja-extension' : 'tcja-expiration';
              handleDatasetChange(newDataset);
              response.message = `Switched to ${newDataset}`;
            } catch (error) {
              response.message = `Error: ${error.message}`;
            }
            break;
            
          case 'checkIframe':
            const isInIframe = window.self !== window.top;
            const hasClass = document.body.classList.contains('in-iframe');
            response.message = `Iframe detected: ${isInIframe}, CSS class applied: ${hasClass}`;
            break;
            
          default:
            response.message = `Unknown test action: ${action}`;
        }
        
        // Send response back to parent
        event.source.postMessage(response, event.origin);
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
      window.removeEventListener('click', handleClickOutside);
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
  
  <!-- Title overlay (always visible) -->
  <div class="title-overlay">
    <h1 class="overlay-title">
      <span class="title-full">{scrollStates[0]?.title || "The One Big Beautiful Bill Act, household by household"}</span>
      <span class="title-mobile">OBBBA, household by household</span>
    </h1>
  </div>
  
  <!-- Baseline selector overlay (always visible on right) -->
  <div class="baseline-selector-overlay" class:dropdown-open={baselineDropdownOpen}>
    <span class="baseline-label desktop-only">Baseline:</span>
    <div class="baseline-selector-header">
      <span class="baseline-label">Baseline:</span>
      <button 
        class="baseline-dropdown-toggle"
        on:click={() => baselineDropdownOpen = !baselineDropdownOpen}
      >
        <span class="selected-baseline">{DATASETS[selectedDataset].label}</span>
        <svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 4.5L6 7.5L9 4.5"/>
        </svg>
      </button>
    </div>
    <div class="baseline-selector">
      {#each Object.entries(DATASETS) as [key, dataset]}
        <button 
          class="tab-button" 
          class:active={selectedDataset === key}
          on:click={() => {
            handleDatasetChange(key);
            baselineDropdownOpen = false;
          }}
          disabled={isLoading || (key === 'tcja-extension' && secondDatasetLoading && !allDatasets['tcja-extension'])}
        >
          {dataset.label}
          {#if key === 'tcja-extension' && secondDatasetLoading}
            <span class="loading-dot"></span>
          {/if}
        </button>
      {/each}
    </div>
  </div>
  
  <!-- Scrollable content overlay -->
  <div class="content-overlay" bind:this={scrollContainer}>
    <div class="text-content">
      {#each scrollStates as state, i}
        {#if state.viewType === 'group'}
          <section 
            class="text-section {state.id}"
            class:active={$currentStateIndex === i}
            class:dragging={draggingSectionIndex === i}
            class:centered={state.id === 'intro' || state.id === 'all-households'}
            class:align-left={startOnLeft ? ['lower-income', 'upper-income'].includes(state.id) : ['middle-income', 'highest-income'].includes(state.id)}
            class:align-right={startOnLeft ? ['middle-income', 'highest-income'].includes(state.id) : ['lower-income', 'upper-income'].includes(state.id)}
            data-index={i}
            bind:this={textSections[i]}
            style="transform: translate({sectionPositions[i]?.x || 0}px, {sectionPositions[i]?.y || 0}px)"
            on:mousedown={(e) => startDrag(e, i)}
          >
            <div class="section-content">
              <div class="drag-handle" title="Drag to move">⋮⋮</div>
              {#if state.id !== 'intro'}
                <h2>
                  <span class="title-desktop">{state.title}</span>
                  <span class="title-mobile">
                    {#if state.id === 'lower-income'}
                      Households with income below $50k
                    {:else if state.id === 'middle-income'}
                      Households with income $50k to $200k
                    {:else if state.id === 'upper-income'}
                      Households with income $200k to $1M
                    {:else if state.id === 'highest-income'}
                      Households with income over $1M
                    {:else}
                      {state.title}
                    {/if}
                  </span>
                </h2>
              {/if}
              
              <!-- Intro section content -->
              {#if state.id === 'intro'}
                {#if state.description}
                  <p>{@html state.description}</p>
                {/if}
              <!-- Dynamic content for income sections -->
              {:else if data.length > 0}
                {@const sectionData = data.filter(d => state.filter(d))}
                {@const stats = calculateSectionStats(sectionData, false, state.id)}
                {#if stats}
                  {#if state.id === 'lower-income'}
                    <p>Of the {stats.total} million households with market income below $50,000, OBBBA will increase the net income of {stats.positivePercent}% and reduce the net income of {stats.negativePercent}%.</p>
                    <p>Each dot represents a household. Click any dot to explore that household's details, or scroll to see the randomly selected household below.</p>
                  {:else if state.id === 'middle-income'}
                    {@const lowerStats = calculateSectionStats(data.filter(d => d['Market Income'] >= 0 && d['Market Income'] < 50000))}
                    <p>Among the {stats.total} million households earning $50,000–$200,000, {stats.positivePercent}% will see gains and {stats.negativePercent}% will see losses.</p>
                    <p>Notice how this middle-income group has {stats.positivePercent > lowerStats.positivePercent ? 'more winners' : 'fewer winners'} than the lower-income group ({stats.positivePercent}% vs {lowerStats.positivePercent}%). The impact patterns shift as income rises.</p>
                  {:else if state.id === 'upper-income'}
                    {@const middleStats = calculateSectionStats(data.filter(d => d['Market Income'] >= 50000 && d['Market Income'] < 200000))}
                    <p>For the {stats.total} million households earning $200,000–$1 million, the reform creates {stats.positivePercent}% winners and {stats.negativePercent}% losers.</p>
                    <p>This upper-income bracket shows {stats.positivePercent > middleStats.positivePercent ? 'higher' : 'lower'} gain rates than middle-income households. The concentration of impacts increases at higher incomes.</p>
                  {:else if state.id === 'highest-income'}
                    {@const upperStats = calculateSectionStats(data.filter(d => d['Market Income'] >= 200000 && d['Market Income'] < 1000000))}
                    <p>Among the {stats.total} million households with income over $1 million, {stats.positivePercent}% benefit while {stats.negativePercent}% pay more.</p>
                    <p>At the highest incomes, the pattern {stats.positivePercent > upperStats.positivePercent ? 'continues with more households gaining' : 'shifts with fewer households benefiting'} compared to the $200k–$1M group. These households see the largest absolute changes in both directions.</p>
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
    <LoadingOverlay message="Loading data..." />
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
  
  /* Adjust positioning when in iframe */
  :global(body.in-iframe) .app-container {
    height: calc(100vh - 60px); /* Account for PolicyEngine header */
  }
  
  /* Full-screen chart background */
  .chart-background {
    position: fixed; /* Fixed to viewport */
    top: 0; /* Start from top now that header is removed */
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1;
  }
  
  /* In iframe, don't use fixed positioning to avoid conflicts */
  :global(body.in-iframe) .chart-background {
    position: absolute;
    top: 0;
  }
  
  /* Title overlay - always visible, centered */
  .title-overlay {
    position: fixed;
    top: 2rem;
    left: 50%;
    transform: translateX(-50%);
    z-index: 20; /* Higher than content overlay (15) to be above boxes */
    background: rgba(255, 255, 255, 0.95);
    padding: 1rem 2rem;
    border-radius: 12px;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(226, 232, 240, 0.5);
    text-align: center;
  }
  
  .overlay-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    white-space: nowrap;
  }
  
  /* Show full title on desktop, hide mobile title */
  .title-mobile {
    display: none;
  }
  
  .title-desktop {
    display: inline;
  }
  
  
  .scroll-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    color: var(--text-secondary);
    font-size: 0.875rem;
    opacity: 0.7;
  }
  
  .scroll-indicator .arrow {
    font-size: 1.25rem;
    animation: arrow-bounce 2s infinite;
  }
  
  /* Baseline selector overlay (aligned with chart edge) */
  .baseline-selector-overlay {
    position: fixed;
    bottom: 2rem;
    right: calc(100px + 3rem); /* Align with chart's right margin */
    z-index: 20; /* Same as title overlay, above content */
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .baseline-label {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    font-family: var(--font-sans);
    text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8), 0 0 4px rgba(255, 255, 255, 0.8);
  }
  
  /* Hide dropdown elements on desktop */
  .baseline-selector-header,
  .baseline-dropdown-toggle {
    display: none;
  }

  .baseline-selector {
    display: flex;
    gap: 8px;
  }

  .tab-button {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(226, 232, 240, 0.5);
    color: var(--text-secondary);
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
    font-family: var(--font-sans);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
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
  
  /* Scrollable content overlay - full width to allow dragging anywhere */
  .content-overlay {
    position: absolute;
    top: 0; /* Start from top now that header is removed */
    left: 0;
    width: 100%; /* Full width for dragging */
    bottom: 0;
    overflow-y: auto;
    overflow-x: hidden; /* Prevent horizontal scroll */
    z-index: 15; /* Higher than title overlay (10) */
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
  
  /* In iframe, adjust content overlay positioning */
  :global(body.in-iframe) .content-overlay {
    top: 0;
  }
  
  .text-content {
    padding: 2rem 3rem 50vh 3rem;
    padding-left: calc(120px + 3rem); /* Space for y-axis - matches chart margin */
    padding-right: calc(120px + 3rem); /* Match left side for symmetry */
    margin-top: 25vh; /* Push content down so second box appears centered */
    width: 100%;
    position: relative;
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
    max-width: 480px;
    width: 100%;
  }
  
  
  /* Centered sections (intro and all-households) */
  .text-section.centered {
    margin-left: auto;
    margin-right: auto;
  }
  
  /* Right-aligned sections */
  .text-section.align-right {
    margin-left: auto;
    margin-right: 0;
  }
  
  /* Left-aligned sections */
  .text-section.align-left {
    margin-left: 0;
    margin-right: auto;
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
    font-size: 24px;
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
  
  /* Intro section special layout */
  .intro-title-bar {
    margin: -1.5rem -1.5rem 1rem -1.5rem; /* Negative margins to extend to box edges */
    padding: 1rem 1.5rem;
    background: rgba(255, 255, 255, 0.5);
    border-bottom: 1px solid var(--border);
  }
  
  .intro-title-bar h2 {
    margin: 0;
  }
  
  .intro-content {
    transition: opacity 0.3s ease;
  }
  
  
  .integrated-household-profile {
    margin-top: 0.75rem;
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
      top: 0; /* Start from top */
      /* Extra prevention of scroll snap on mobile */
      -webkit-overflow-scrolling: auto !important;
      scroll-snap-type: none !important;
    }
    
    /* Mobile title overlay styles */
    .title-overlay {
      top: 1rem;
      padding: 0.75rem 1.5rem;
    }
    
    .overlay-title {
      font-size: 1.5rem;
    }
    
    /* Hide full title, show mobile title */
    .title-full {
      display: none;
    }
    
    .title-mobile {
      display: inline;
    }
    
    /* Switch section titles on mobile */
    .title-desktop {
      display: none;
    }
    
    .baseline-selector-overlay {
      top: auto;
      bottom: 3rem;
      right: 30px; /* Align with mobile chart margin */
      padding: 0;
      gap: 0;
      flex-direction: column;
      align-items: stretch;
      background: transparent;
      box-shadow: none;
      border: none;
      backdrop-filter: none;
      -webkit-backdrop-filter: none;
    }
    
    /* Show dropdown elements on mobile */
    .baseline-selector-header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0.5rem 0.75rem;
      background: rgba(255, 255, 255, 0.95);
      border-radius: 12px;
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
      border: 1px solid rgba(226, 232, 240, 0.5);
    }
    
    .baseline-dropdown-toggle {
      display: flex;
      align-items: center;
      gap: 6px;
      background: none;
      border: none;
      padding: 0;
      font-size: 12px;
      font-weight: 500;
      color: var(--text-primary);
      cursor: pointer;
      font-family: var(--font-sans);
    }
    
    .dropdown-arrow {
      transition: transform 0.2s ease;
    }
    
    .baseline-selector-overlay.dropdown-open .dropdown-arrow {
      transform: rotate(180deg);
    }
    
    .baseline-label {
      font-size: 12px;
    }
    
    /* Hide desktop-only label on mobile */
    .baseline-label.desktop-only {
      display: none;
    }
    
    /* Dropdown menu on mobile */
    .baseline-selector {
      display: none;
      position: absolute;
      bottom: 100%;
      right: 0;
      margin-bottom: 8px;
      padding: 8px;
      flex-direction: column;
      gap: 4px;
      background: rgba(255, 255, 255, 0.95);
      border-radius: 12px;
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
      border: 1px solid rgba(226, 232, 240, 0.5);
      min-width: 200px;
    }
    
    .baseline-selector-overlay.dropdown-open .baseline-selector {
      display: flex;
    }
    
    .tab-button {
      font-size: 12px;
      padding: 8px 12px;
      text-align: left;
      border-radius: 6px;
    }
    
    .text-content {
      padding: 1rem 1rem 30vh 1rem;
      max-width: 100%;
      margin-top: 10vh; /* Base spacing for mobile */
    }
    
    /* Specific centering for intro section on mobile */
    .text-section.intro {
      position: relative;
      top: calc(40vh - 150px); /* Push intro down to center */
      margin-bottom: calc(60vh + 40vh - 150px); /* Ensure next box is full screen away */
    }
    
    .text-section {
      margin-bottom: 60vh;
      padding: 1rem;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.85);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      /* Center all sections on mobile */
      margin-left: auto !important;
      margin-right: auto !important;
    }
    
    
    .text-section h2 {
      font-size: 18px;
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
      margin-top: 0.5rem;
    }
    
    .scroll-indicator {
      font-size: 12px;
      margin-top: 1rem;
      padding-top: 0.75rem;
    }
    
    .chart-background {
      top: 50px; /* Reduce top spacing on mobile */
    }
  }
  
  /* Small mobile devices */
  @media (max-width: 480px) {
    .title-overlay {
      top: 0.5rem;
      padding: 0.5rem 1rem;
    }
    
    .overlay-title {
      font-size: 1.125rem;
    }
    
    /* Ensure mobile title is shown on small screens too */
    .title-full {
      display: none;
    }
    
    .title-mobile {
      display: inline;
    }
    
    .baseline-selector-overlay {
      bottom: 0.5rem;
      right: 15px; /* Align with small mobile chart margin */
    }
    
    .baseline-selector-header {
      padding: 0.375rem 0.5rem;
    }
    
    .baseline-dropdown-toggle {
      font-size: 11px;
    }
    
    .baseline-label {
      font-size: 11px;
    }
    
    .baseline-selector {
      padding: 6px;
    }
    
    .tab-button {
      font-size: 11px;
      padding: 6px 10px;
    }
    
    .text-content {
      padding: 0.75rem 0.75rem 20vh 0.75rem;
      margin-top: 2.5rem;
    }
    
    .text-section {
      padding: 0.875rem;
      margin-bottom: 50vh;
    }
    
    
    .text-section h2 {
      font-size: 16px;
    }
    
    .text-section p {
      font-size: 0.8125rem;
    }
  }
</style>