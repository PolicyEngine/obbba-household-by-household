<script>
  import { onMount, onDestroy, tick } from 'svelte';
  import { page } from '$app/stores';
  import { base } from '$app/paths';
  import { DATASETS } from '$lib/config/datasets.js';
  import { introMethodology, scrollStates } from '$lib/config/views.js';
  import { loadFullDataBackground } from '$lib/data/instantLoader.js';
  import { loadTinyVisualization } from '$lib/data/tinyLoader.js';
  import { calculateSectionStats } from '$lib/data/householdStats.js';
  import {
    parseUrlParams,
    updateUrlWithHousehold,
    findSectionForHousehold,
    notifyParentOfUrlChange,
    EXPLORER_URL_QUERY
  } from '$lib/navigation/urlSync.js';
  import {
    createIntersectionObserver,
    getRandomWeightedHousehold,
    cleanupScrollObserver,
    navigateToSection,
    currentStateIndex,
    previousStateIndex,
    isTransitioning,
    currentInterpolationT
  } from '$lib/navigation/scrollHandler.js';
  import {
    animateHouseholdEmphasis,
    createAnimatedNumber,
    cleanupAnimations
  } from '$lib/utils/animations.js';
  import LoadingOverlay from '$lib/components/LoadingOverlay.svelte';
  import HouseholdProfile from '$lib/components/HouseholdProfile.svelte';
  import ScatterPlot from '$lib/components/ScatterPlot.svelte';

  // Data state
  let allDatasets = {};
  let data = [];
  let selectedHousehold = null;
  let isLoading = false;
  let loadError = null;
  let selectedDataset = 'tcja-expiration';
  let methodologyExpanded = false;

  async function toggleMethodology() {
    const savedScrollTop = scrollContainer?.scrollTop || 0;
    methodologyExpanded = !methodologyExpanded;
    await tick();

    if (scrollContainer) {
      const restoreScroll = () => {
        if (scrollContainer) scrollContainer.scrollTop = savedScrollTop;
      };

      restoreScroll();
      requestAnimationFrame(() => {
        requestAnimationFrame(restoreScroll);
      });
      setTimeout(restoreScroll, 100);
    }
  }

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

  // Initialize or update random households for visible sections
  function initializeRandomHouseholds() {
    scrollStates.forEach((state) => {
      if (state.viewType === 'group' && !randomHouseholds[state.id]) {
        const filteredData = data.filter((d) => state.filter(d));
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

  // Force re-render when state changes
  $: if (chartComponent && $currentStateIndex >= 0) {
    chartComponent.renderVisualization();
  }

  // Set up scroll observer when sections are populated
  // This must be reactive because textSections is populated via bind:this after initial render
  // Pass scrollContainer as root since sections scroll inside .content-overlay, not the viewport
  $: if (textSections.length > 0 && textSections[0] && scrollContainer && !scrollObserver) {
    scrollObserver = createIntersectionObserver(textSections, handleSectionChange, scrollContainer);
  }

  function getSectionIdForHousehold(household) {
    const targetIndex = findSectionForHousehold(household, scrollStates);
    return scrollStates[targetIndex]?.id;
  }

  function scrollToSectionIndex(targetIndex, behavior = 'smooth') {
    const targetSection = textSections[targetIndex];
    if (!scrollContainer || !targetSection) return false;

    const targetTop =
      targetSection.offsetTop - (scrollContainer.clientHeight - targetSection.offsetHeight) / 2;
    const maxScrollTop = scrollContainer.scrollHeight - scrollContainer.clientHeight;
    const top = Math.max(0, Math.min(targetTop, maxScrollTop));

    scrollContainer.scrollTo({ top, behavior });
    return true;
  }

  async function updateHouseholdUrl(householdId) {
    isInternalUpdate = true;
    try {
      await updateUrlWithHousehold(householdId, selectedDataset);
    } catch (error) {
      isInternalUpdate = false;
      throw error;
    }
  }

  // Handle pending scroll to household when sections are ready
  $: if (
    pendingScrollToHousehold &&
    textSections.length > 0 &&
    textSections[pendingScrollToHousehold.targetIndex]
  ) {
    const { household, targetIndex } = pendingScrollToHousehold;

    // Ensure the household is selected
    selectedHousehold = household;

    // Scroll to the section
    setTimeout(() => {
      scrollToSectionIndex(targetIndex);
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
  async function selectHousehold(household, shouldScroll = true, sectionId = null) {
    // If not scrolling, lock the scroll position
    const savedScrollTop = scrollContainer?.scrollTop || 0;
    if (!shouldScroll && scrollContainer) {
      // Save current scroll position
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

    const currentState = scrollStates[$currentStateIndex];
    const targetSectionId =
      sectionId ||
      (shouldScroll
        ? getSectionIdForHousehold(household)
        : currentState?.id?.replace('-individual', ''));
    let scrollTargetIndex = -1;

    if (targetSectionId && targetSectionId !== 'intro' && targetSectionId !== 'all-households') {
      randomHouseholds = {
        ...randomHouseholds,
        [targetSectionId]: { ...household }
      };

      if (shouldScroll) {
        scrollTargetIndex = scrollStates.findIndex((state) => state.id === targetSectionId);
      }
    }

    if (currentState && currentState.viewType === 'individual') {
      const sectionIndex = Math.floor($currentStateIndex / 2);

      // Animate other household numbers
      createAnimatedNumber(
        `num-dependents-${sectionIndex}`,
        0,
        Math.round(household['Number of Dependents'] || household['Dependents'] || 0),
        (d) => Math.round(d),
        700
      );
      createAnimatedNumber(
        `age-of-head-${sectionIndex}`,
        18,
        household['Age of Head'] || household['Age'] || 40,
        (d) => Math.round(d),
        800
      );
    }

    // Animate the household point
    animateHouseholdEmphasis(household.id);

    // Update URL
    await updateHouseholdUrl(household.id);

    if (shouldScroll && scrollTargetIndex >= 0) {
      await tick();
      requestAnimationFrame(() => {
        if (!scrollToSectionIndex(scrollTargetIndex)) {
          pendingScrollToHousehold = { household, targetIndex: scrollTargetIndex };
        }
      });
    } else if (!shouldScroll && scrollContainer) {
      requestAnimationFrame(() => {
        scrollContainer.scrollTop = savedScrollTop;
      });
    }

    // Force chart re-render
    if (chartComponent?.forceRender) {
      chartComponent.forceRender();
    }
  }

  // Randomize household for current section
  function randomizeHousehold(sectionId = null) {
    const baseViewId =
      sectionId || currentState?.id?.replace('-individual', '') || currentState?.id;
    const state = scrollStates.find((s) => s.id === baseViewId);

    if (state && data.length > 0) {
      const filteredData = data.filter((d) => state.filter(d));
      const newHousehold = getRandomWeightedHousehold(filteredData);

      if (newHousehold) {
        // Don't scroll when randomizing
        selectHousehold({ ...newHousehold }, false, baseViewId);

        // Re-trigger animations
        const sectionIndex = Math.floor($currentStateIndex / 2);
        createAnimatedNumber(
          `household-id-${sectionIndex}`,
          selectedHousehold?.id || 0,
          newHousehold.id,
          (d) => Math.round(d),
          600
        );
      }
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
      const { householdId, baseline, section } = parseUrlParams();
      console.log('handleUrlParams called with:', { householdId, baseline, section });

      // Ignore links to scenarios this paper-consistent release does not ship.
      if (baseline && DATASETS[baseline] && baseline !== selectedDataset) {
        selectedDataset = baseline;
      }

      // Navigate to section if provided (and data is ready)
      if (section && scrollStates.length > 0) {
        navigateToSection(section, scrollStates);
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
        }).catch((error) => {
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
              console.log(
                `Full ${selectedDataset} data ready: ${update[selectedDataset].length} rows`
              );

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

              isLoadingData = false;
            }
          }).catch((error) => {
            console.error('Error loading data:', error);
            loadError = error.message;
            isLoading = false;
            isLoadingData = false; // Clear on error too
          });
        }, 300); // Delay to ensure dots are rendering before loading full data
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
      const household = data.find((d) => String(d.id) === householdId);
      if (household) {
        console.log('Found household:', household);
        selectedHousehold = household;

        // Find appropriate section
        const targetIndex = findSectionForHousehold(household, scrollStates);
        console.log('Target index:', targetIndex, 'textSections length:', textSections.length);

        // Update the random household for the appropriate section
        const baseViewId =
          scrollStates[targetIndex]?.id?.replace('-individual', '') ||
          scrollStates[targetIndex]?.id;
        if (baseViewId) {
          // Use proper reactivity assignment
          randomHouseholds = {
            ...randomHouseholds,
            [baseViewId]: household
          };
        }

        if (textSections[targetIndex] && scrollContainer) {
          // Delay to ensure DOM is ready
          setTimeout(() => {
            scrollToSectionIndex(targetIndex);
          }, 100);
        } else {
          // If sections aren't ready yet, store for later
          pendingScrollToHousehold = { household, targetIndex };
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
    console.log(
      `Component mounted at ${performance.now().toFixed(0)}ms (${(performance.now() - pageLoadStart).toFixed(0)}ms since page load)`
    );

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

    // Add class to body if in iframe
    if (isInIframe) {
      document.body.classList.add('in-iframe');
      console.log('Running in iframe, checking for parent URL parameters...');

      // Request parent to send current URL parameters
      window.parent.postMessage(
        {
          type: 'requestUrlParams'
        },
        '*'
      );

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
          const parentUrlMatch = parentUrl.match(EXPLORER_URL_QUERY);
          if (parentUrlMatch) {
            console.log('Found parameters in parent path, applying to iframe');
            const parentParams = new URLSearchParams(parentUrlMatch[1]);
            const currentUrl = new URL(window.location);

            // Copy relevant parameters
            ['household', 'baseline', 'section'].forEach((param) => {
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

    // Note: Scroll observer is set up via reactive statement below
    // because textSections may not be populated yet when onMount runs

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
            response.message = 'This release includes the TCJA-expiration baseline only';
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
  <meta
    name="description"
    content="Explore how 21 provisions of OBBBA change household resources across 57,240 modeled Microcosm records."
  />
  <!-- PolicyEngine Design System Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap"
    rel="stylesheet"
  />
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
      onPointClick={(household) => selectHousehold(household, true)}
    />
  </div>

  <!-- Title overlay (always visible) -->
  <div class="title-overlay">
    <h1 class="overlay-title">
      <span class="title-full"
        >{scrollStates[0]?.title || 'The One Big Beautiful Bill Act, household by household'}</span
      >
      <span class="title-mobile">OBBBA, household by household</span>
    </h1>
  </div>

  <!-- Top right links -->
  <div class="top-right-links">
    <a href="{base}/explore" class="explore-link" title="Explore by Congressional District">
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path
          d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l5.447 2.724A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
        />
      </svg>
      <span class="link-text">Explore by District</span>
    </a>
    <a
      href="https://github.com/PolicyEngine/obbba-household-by-household"
      target="_blank"
      rel="noopener noreferrer"
      class="github-link"
      title="View source on GitHub"
      aria-label="View source on GitHub"
    >
      <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path
          d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.43 9.8 8.21 11.39.6.11.82-.26.82-.58 0-.29-.01-1.05-.02-2.06-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.21.08 1.85 1.24 1.85 1.24 1.07 1.84 2.81 1.31 3.5 1 .11-.78.42-1.31.76-1.61-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.14-.3-.54-1.52.1-3.18 0 0 1-.32 3.3 1.23a11.5 11.5 0 013.01-.4c1.02.01 2.05.14 3.01.4 2.28-1.55 3.29-1.23 3.29-1.23.64 1.66.24 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.63-5.48 5.92.42.36.81 1.1.81 2.22 0 1.61-.01 2.9-.01 3.29 0 .32.21.7.82.58C20.57 21.8 24 17.31 24 12c0-6.63-5.37-12-12-12z"
        />
      </svg>
    </a>
  </div>

  <!-- The paper's certified household stack has one counterfactual. -->
  <div class="baseline-selector-overlay">
    <span class="baseline-label">Baseline:</span>
    <span class="selected-baseline">{DATASETS[selectedDataset].label}</span>
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
            class:align-left={startOnLeft
              ? ['lower-income', 'upper-income'].includes(state.id)
              : ['middle-income', 'highest-income'].includes(state.id)}
            class:align-right={startOnLeft
              ? ['middle-income', 'highest-income'].includes(state.id)
              : ['lower-income', 'upper-income'].includes(state.id)}
            data-index={i}
            bind:this={textSections[i]}
            style="transform: translate({sectionPositions[i]?.x || 0}px, {sectionPositions[i]?.y ||
              0}px)"
          >
            <div class="section-content">
              <button
                type="button"
                class="drag-handle"
                title="Drag to move"
                aria-label="Move {state.title} section"
                on:mousedown={(e) => startDrag(e, i)}>⋮⋮</button
              >
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
                <button
                  type="button"
                  class="methodology-toggle"
                  aria-expanded={methodologyExpanded}
                  on:click={toggleMethodology}
                >
                  <span aria-hidden="true">{methodologyExpanded ? '▾' : '▸'}</span>
                  Methodology and provenance
                </button>
                {#if methodologyExpanded}
                  <div class="methodology-panel">
                    {@html introMethodology}
                  </div>
                {/if}
                <!-- Dynamic content for income sections -->
              {:else if data.length > 0}
                {@const sectionData = data.filter((d) => state.filter(d))}
                {@const stats = calculateSectionStats(sectionData, false, state.id)}
                {#if stats}
                  {#if state.id === 'lower-income'}
                    <p>
                      Of the {stats.total} million households with market income below $50,000, OBBBA
                      increases resources by more than $1 for {stats.positivePercent}% and reduces
                      them by more than $1 for {stats.negativePercent}%.
                    </p>
                    <p>
                      Each dot is a modeled record; opacity and random selection reflect its
                      household weight. Click a dot or inspect the weighted random example below.
                    </p>
                  {:else if state.id === 'middle-income'}
                    {@const lowerStats = calculateSectionStats(
                      data.filter((d) => d['Market Income'] >= 0 && d['Market Income'] < 50000)
                    )}
                    <p>
                      Among the {stats.total} million households with $50,000–$200,000 of market income,
                      {stats.positivePercent}% gain more than $1 in resources and {stats.negativePercent}%
                      lose more than $1.
                    </p>
                    <p>
                      This group has {stats.positivePercent > lowerStats.positivePercent
                        ? 'a higher gain rate'
                        : 'a lower gain rate'} than households below $50,000 ({stats.positivePercent}%
                      versus {lowerStats.positivePercent}%). The record-level profiles show why
                      households at similar incomes can land far apart.
                    </p>
                  {:else if state.id === 'upper-income'}
                    {@const middleStats = calculateSectionStats(
                      data.filter((d) => d['Market Income'] >= 50000 && d['Market Income'] < 200000)
                    )}
                    <p>
                      Of the {stats.total} million households with $200,000–$1 million of market income,
                      {stats.positivePercent}% gain more than $1 in resources and {stats.negativePercent}%
                      lose more than $1.
                    </p>
                    <p>
                      The gain rate is {stats.positivePercent > middleStats.positivePercent
                        ? 'higher'
                        : 'lower'} than in the $50,000–$200,000 group. SALT, the AMT, business income,
                      and itemized-deduction interactions create substantial dispersion.
                    </p>
                  {:else if state.id === 'highest-income'}
                    {@const upperStats = calculateSectionStats(
                      data.filter(
                        (d) => d['Market Income'] >= 200000 && d['Market Income'] < 1000000
                      )
                    )}
                    <p>
                      Among the {stats.total} million households with market income over $1 million,
                      {stats.positivePercent}% gain more than $1 in resources and {stats.negativePercent}%
                      lose more than $1.
                    </p>
                    <p>
                      The gain rate {stats.positivePercent > upperStats.positivePercent
                        ? 'rises'
                        : 'falls'} relative to the $200,000–$1 million group. The provision breakdown
                      separates rate, AMT, SALT, and deduction effects for each record.
                    </p>
                  {:else if state.id === 'all-households'}
                    {@const allStats = calculateSectionStats(sectionData, true, state.id)}
                    <p>
                      {@html state.description
                        .replace('{totalPercentage}', allStats.affectedPercent)
                        .replace('{medianImpact}', allStats.medianChange)}
                    </p>
                  {/if}
                {/if}

                <!-- Integrated household profile for all income sections except all-households -->
                {#if randomHouseholds[state.id] && state.id !== 'all-households'}
                  <div class="integrated-household-profile">
                    <HouseholdProfile
                      household={randomHouseholds[state.id]}
                      {selectedDataset}
                      currentState={state}
                      sectionIndex={0}
                      onRandomize={() => randomizeHousehold(state.id)}
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
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="M12 5v14M19 12l-7 7-7-7" />
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
    /* PolicyEngine Design System - Colors */
    --app-background: #ffffff;
    --text-primary: #000000;
    --text-secondary: #5a5a5a;
    --text-tertiary: #9ca3af;
    --border: #e2e8f0;
    --border-medium: #cbd5e1;
    --border-dark: #94a3b8;
    --hover: #f9fafb;

    /* Primary (Teal) */
    --primary-50: #e6fffa;
    --primary-100: #b2f5ea;
    --primary-200: #81e6d9;
    --primary-300: #4fd1c5;
    --primary-400: #38b2ac;
    --primary-500: #319795;
    --primary-600: #2c7a7b;
    --primary-700: #285e61;

    /* Scatter plot colors */
    --scatter-positive: #319795; /* Teal for gains */
    --scatter-negative: #6b7280; /* Gray for losses */

    /* Semantic colors */
    --success: #22c55e;
    --warning: #fec601;
    --error: #ef4444;
    --info: #1890ff;

    /* Gray scale */
    --gray-50: #f9fafb;
    --gray-100: #f2f4f7;
    --gray-200: #e2e8f0;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #344054;

    /* Button colors */
    --button-bg: #319795;
    --button-hover: #2c7a7b;

    /* Legacy aliases */
    --darkest-blue: #000000;
    --primary-blue: #319795;
    --dark-gray: #5a5a5a;
    --medium-dark-gray: #d1d5db;
    --grid-lines: #e2e8f0;

    /* PolicyEngine Typography */
    --font-sans: var(--pe-font-family-primary);
    --font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
    --font-body: var(--pe-font-family-primary);
    --font-chart: var(--pe-font-family-primary);
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
    height: calc(100vh - var(--pe-shell-height, 0px));
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
    top: var(--pe-shell-height, 0px); /* Below the PolicyEngine site header */
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
    top: calc(2rem + var(--pe-shell-height, 0px));
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

  /* Top right links */
  .top-right-links {
    position: fixed;
    top: calc(2rem + var(--pe-shell-height, 0px));
    right: 2rem;
    z-index: 20;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .explore-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.875rem;
    background: rgba(255, 255, 255, 0.95);
    color: #319795;
    text-decoration: none;
    font-family: 'Inter', sans-serif;
    font-size: 0.8125rem;
    font-weight: 500;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
  }

  .explore-link:hover {
    background: #319795;
    color: #fff;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(49, 151, 149, 0.3);
  }

  .explore-link svg {
    flex-shrink: 0;
  }

  .github-link {
    color: var(--text-secondary);
    opacity: 0.7;
    transition:
      opacity 0.2s ease,
      transform 0.2s ease;
    background: rgba(255, 255, 255, 0.9);
    padding: 0.75rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .github-link:hover {
    opacity: 1;
    transform: scale(1.1);
  }

  /* Baseline selector overlay (aligned with chart edge) */
  .baseline-selector-overlay {
    position: fixed;
    bottom: 2rem;
    right: calc(100px + 3rem); /* Align with chart's right margin */
    z-index: 20; /* Same as title overlay, above content */
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border: 1px solid rgba(226, 232, 240, 0.7);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.92);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  .baseline-label {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    font-family: var(--font-sans);
    text-shadow:
      0 1px 2px rgba(255, 255, 255, 0.8),
      0 0 4px rgba(255, 255, 255, 0.8);
  }

  .selected-baseline {
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 700;
    font-family: var(--font-sans);
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
    0%,
    20%,
    50%,
    80%,
    100% {
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
    0%,
    100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(3px);
    }
  }

  .text-section {
    margin-bottom: 100vh;
    transition:
      transform 0.1s ease,
      box-shadow 0.5s ease,
      background 0.5s ease;
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
    overflow-anchor: none;
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
    padding: 0;
    border: 0;
    background: transparent;
    line-height: 1;
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

  .methodology-toggle {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--primary-blue);
    font: inherit;
    font-size: 0.875rem;
    text-decoration: underline;
    cursor: pointer;
  }

  .methodology-panel {
    margin-top: 0.5rem;
    padding: 0.75rem;
    border-radius: 6px;
    background: rgba(91, 155, 213, 0.05);
    color: var(--text-secondary);
    font-size: 0.875rem;
    line-height: 1.5;
  }

  .methodology-panel :global(a) {
    color: var(--primary-blue);
    text-decoration: underline;
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
    color: #ef4444;
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
  @media (max-width: 1400px) {
    .explore-link .link-text {
      display: none;
    }
  }

  @media (max-width: 1100px) {
    .title-full {
      display: none;
    }

    .title-mobile {
      display: inline;
    }

    .overlay-title {
      font-size: 1.75rem;
    }
  }

  @media (max-width: 768px) {
    .top-right-links {
      top: 1rem;
      right: 1rem;
      gap: 0.5rem;
    }

    .explore-link {
      padding: 0.5rem;
    }

    .explore-link .link-text {
      display: none;
    }

    .github-link {
      padding: 0.5rem;
    }

    .github-link svg {
      width: 20px;
      height: 20px;
    }

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
      gap: 8px;
      padding: 0.5rem 0.75rem;
      background: rgba(255, 255, 255, 0.95);
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
      border: 1px solid rgba(226, 232, 240, 0.5);
    }

    .baseline-label {
      font-size: 12px;
    }

    .selected-baseline {
      font-size: 12px;
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

    .baseline-label {
      font-size: 11px;
    }

    .selected-baseline {
      font-size: 11px;
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
