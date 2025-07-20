<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Papa from 'papaparse';
  import * as d3 from 'd3';

  let data = [];
  let loading = true;
  let scrollProgress = 0;
  let selectedPoint = null;
  let selectedData = null;
  let canvasRef;
  let svgRef;
  let scrollContainer;
  let currentSectionIndex = 0;
  let renderedPoints = []; // Store positions for hit detection
  let randomHouseholds = {}; // Store random household for each group
  let animatedNumbers = new Map(); // Store animated number references
  let animatedHouseholds = new Map(); // Store animated household emphasis
  let emphasisAnimationId = null; // Track current emphasis animation
  
  // Consistent number formatters
  const fmtUSD = new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD', 
    maximumFractionDigits: 0 
  });
  
  const fmtPct = new Intl.NumberFormat('en-US', { 
    style: 'percent', 
    minimumFractionDigits: 1, 
    maximumFractionDigits: 1 
  });

  // Get font family from CSS variables
  function getFontFamily(type = 'sans') {
    const fontMap = {
      'serif': "'Roboto Serif', serif",
      'sans': "'Roboto', sans-serif",
      'mono': "'Roboto Mono', monospace"
    };
    return fontMap[type] || fontMap['sans'];
  }
  
  // Deep linking variables
  let householdIdMap = new Map(); // Map household IDs to data objects
  let urlSelectedHouseholdId = null;
  let isUserInitiatedChange = false; // Flag to distinguish user clicks from URL navigation
  
  // Dataset selection state
  let selectedDataset = 'tcja-expiration'; // 'tcja-expiration' or 'tcja-extension'
  
  // PolicyEngine Color Constants
  const COLORS = {
    BLACK: "#000000",
    BLUE_98: "#F7FAFD",
    BLUE: "#2C6496",
    BLUE_LIGHT: "#D8E6F3",
    BLUE_PRESSED: "#17354F",
    DARK_BLUE_HOVER: "#1d3e5e",
    DARK_GRAY: "#616161",
    DARK_RED: "#b50d0d",
    DARKEST_BLUE: "#0C1A27",
    GRAY: "#808080",
    LIGHT_GRAY: "#F2F2F2",
    MEDIUM_DARK_GRAY: "#D2D2D2",
    MEDIUM_LIGHT_GRAY: "#BDBDBD",
    TEAL_ACCENT: "#39C6C0",
    TEAL_LIGHT: "#F7FDFC",
    TEAL_MEDIUM: "#2D9E99",
    TEAL_PRESSED: "#227773",
    WHITE: "#FFFFFF"
  };
  
  // Dataset configuration
  const datasets = {
    'tcja-expiration': {
      filename: 'household_tax_income_changes_senate_current_law_baseline.csv',
      label: 'TCJA Expiration',
      description: 'Analysis showing impact if TCJA provisions expire'
    },
    'tcja-extension': {
      filename: 'household_tax_income_changes_senate_tcja_baseline.csv', 
      label: 'TCJA Extension',
      description: 'Analysis showing impact if TCJA provisions are extended'
    }
  };

  const baseViews = [
    {
      id: 'intro',
      title: "How tax changes affect every American household",
      groupText: "Each dot represents a household, positioned by their income and how much they gain or lose under the proposed tax changes. Teal dots show households that benefit, gray shows those that face increases.",
      view: {
        xDomain: [-15, 15],
        yDomain: [0, 350000],
        filter: d => d['Gross Income'] < 350000,
        highlightGroup: null
      }
    },
    {
      id: 'lower-income', 
      title: "Lower-income households under $50,000",
      groupText: "Households earning under $50,000 see varied outcomes. While many benefit from Child Tax Credit expansions and TCJA extensions, some undocumented families lose access to credits due to new SSN requirements. Individuals in the bottom decile will gain an average of $213, while the top decile will gain an average of $13,075.",
      view: {
        xDomain: [-15, 15],
        yDomain: [0, 50000],
        filter: d => d['Gross Income'] >= 0 && d['Gross Income'] < 50000,
        highlightGroup: 'lower'
      }
    },
    {
      id: 'middle-income',
      title: "Middle-income households ($50,000 - $200,000)", 
      groupText: "This broad middle class benefits significantly from TCJA extensions, enhanced Child Tax Credits, and new deductions for tips and overtime pay. Seniors in this range gain substantially from the additional $6,000 senior deduction. These households typically see Net Income increases from the tax provisions.",
      view: {
        xDomain: [-25, 25],
        yDomain: [50000, 200000],
        filter: d => d['Gross Income'] >= 50000 && d['Gross Income'] < 200000,
        highlightGroup: 'middle'
      }
    },
    {
      id: 'upper-income',
      title: "Upper-income households ($200,000 - $1 million)",
      groupText: "Higher earners face more complex outcomes as they benefit from TCJA extensions but encounter new limitations. The $40,000 SALT cap provides relief compared to the current $10,000 limit, but itemized deduction limitations at the 35% bracket reduce benefits. Many still see net gains, but the effects vary widely based on deduction usage.",
      view: {
        xDomain: [-30, 30], 
        yDomain: [200000, 1000000],
        filter: d => d['Gross Income'] >= 200000 && d['Gross Income'] < 1000000,
        highlightGroup: 'upper'
      }
    },
    {
      id: 'highest-income',
      title: "Highest-income households ($1 million+)",
      groupText: "The wealthiest households experience the largest absolute gains but face the most limitations. While they benefit from rate reductions and QBID provisions, new restrictions on itemized deductions and charitable contribution floors reduce their benefits. The top 10% gains most in absolute terms, averaging $13,231, contributing to a 0.4% increase in income inequality.",
      view: {
        xDomain: [-50, 50],
        yDomain: [1000000, 10000000],
        filter: d => d['Gross Income'] >= 1000000,
        highlightGroup: 'highest'
      }
    }
  ];

  // Create dual scroll states: group view + individual household view for each
  const scrollStates = [];
  baseViews.forEach((baseView, index) => {
    // Group view
    scrollStates.push({
      ...baseView,
      text: baseView.groupText,
      viewType: 'group'
    });
    
    // Individual household view (only for groups that have households)
    if (index > 0) { // Skip intro section
      scrollStates.push({
        ...baseView,
        id: baseView.id + '-individual',
        title: baseView.title + ' — individual profile',
        text: 'Meet a specific household affected by these changes.',
        viewType: 'individual'
      });
    }
  });

  // Function to load dataset
  async function loadDataset(datasetKey, preservedHouseholdIds = null) {
    loading = true;
    try {
      const response = await fetch(`/obbba-scatter/${datasets[datasetKey].filename}`);
      if (!response.ok) {
        throw new Error(`Failed to load CSV: ${response.status} ${response.statusText}`);
      }
      const raw = await response.text();
      const result = Papa.parse(raw, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true
      });
      
      data = result.data.map((d, i) => ({
        ...d,
        id: String(d['Household ID'] || i), // Convert to string for consistent comparison
        householdId: d['Household ID'], // Keep original for reference
        isAnnotated: false,
        sectionIndex: null
      }));

      // Build household ID map for quick lookups
      data.forEach(household => {
        householdIdMap.set(household.id, household);
      });
      
      // Clear existing selections when switching datasets
      selectedData = null;
      randomHouseholds = {};

      // Find representative points for each scroll state and select random households
      baseViews.forEach((baseView, baseIndex) => {
        const filteredData = data.filter(baseView.view.filter);
        if (filteredData.length > 0) {
          // Find representative point for group view
          const centerY = (baseView.view.yDomain[0] + baseView.view.yDomain[1]) / 2;
          const centerX = (baseView.view.xDomain[0] + baseView.view.xDomain[1]) / 2;
          
          let closest = null;
          let minDistance = Infinity;
          filteredData.forEach(d => {
            const dx = (d['Percentage Change in Net Income'] - centerX) / (baseView.view.xDomain[1] - baseView.view.xDomain[0]);
            const dy = (d['Gross Income'] - centerY) / (baseView.view.yDomain[1] - baseView.view.yDomain[0]);
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < minDistance) {
              minDistance = distance;
              closest = d;
            }
          });
          if (closest) {
            closest.isHighlighted = true;
            closest.highlightGroup = baseView.view.highlightGroup;
            closest.stateIndex = baseIndex;
          }

          // Select random household for individual view (skip intro)
          if (baseIndex > 0) {
            let selectedHousehold = null;
            
            // Try to preserve the household from previous dataset
            if (preservedHouseholdIds && preservedHouseholdIds[baseView.id]) {
              const preservedId = preservedHouseholdIds[baseView.id];
              selectedHousehold = filteredData.find(h => h.id === preservedId);
            }
            
            // If no preserved household or not found, select random
            if (!selectedHousehold) {
              selectedHousehold = getRandomWeightedHousehold(filteredData);
            }
            
            if (selectedHousehold) {
              randomHouseholds[baseView.id] = selectedHousehold;
            }
          }
        }
      });

      loading = false;
      
      // Check for household ID in URL and restore state after everything is ready
      setTimeout(() => {
        // Wait for text sections to be bound
        const waitForSections = () => {
          const boundSections = textSections.filter(s => s).length;
          const totalSections = scrollStates.length;
          
          console.log('⏳ Waiting for sections:', { boundSections, totalSections });
          
          if (boundSections >= totalSections || boundSections > 5) {
            // Sections are ready or mostly ready
            checkUrlParams();
          } else {
            // Wait a bit more
            setTimeout(waitForSections, 100);
          }
        };
        
        waitForSections();
      }, 500);
    } catch (error) {
      console.error('Error loading data:', error);
      console.error('Dataset key:', datasetKey);
      console.error('Filename:', datasets[datasetKey]?.filename);
      console.error('Full URL:', `/obbba-scatter/${datasets[datasetKey]?.filename}`);
      loading = false;
    }
  }

  // Function to handle dataset switching
  function switchDataset(newDataset) {
    // Store current household IDs before switching
    const preservedHouseholdIds = {};
    Object.keys(randomHouseholds).forEach(viewId => {
      if (randomHouseholds[viewId]) {
        preservedHouseholdIds[viewId] = randomHouseholds[viewId].id;
      }
    });
    
    selectedDataset = newDataset;
    loadDataset(newDataset, preservedHouseholdIds); // Pass preserved IDs
    
    // Update URL to reflect dataset change if there are existing URL params
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.has('household') || urlParams.has('section')) {
        // Keep existing household/section params but update baseline
        urlParams.set('baseline', newDataset);
        const url = new URL(window.location);
        url.search = urlParams.toString();
        goto(url.pathname + url.search, { replaceState: true, noScroll: true });
        notifyParentOfUrlChange();
      }
    }
  }

  // Helper function to notify parent window of URL changes
  function notifyParentOfUrlChange() {
    if (typeof window !== 'undefined' && window.parent !== window) {
      // We're in an iframe, notify parent of URL change
      const params = new URLSearchParams(window.location.search);
      window.parent.postMessage({
        type: 'urlUpdate',
        params: params.toString()
      }, '*');
    }
  }

  // Load data on mount
  onMount(() => {
    loadDataset(selectedDataset);
  });

  // Deep linking functions
  function updateUrlWithHousehold(householdId, viewSection = null) {
    if (typeof window !== 'undefined') {
      const url = new URL(window.location);
      
      if (householdId) {
        url.searchParams.set('household', String(householdId));
        
        // Always include the current baseline
        url.searchParams.set('baseline', selectedDataset);
        
        // Optionally include the section/view
        if (viewSection) {
          url.searchParams.set('section', viewSection);
        }
      } else {
        url.searchParams.delete('household');
        url.searchParams.delete('section');
        url.searchParams.delete('baseline');
      }
      
      // Update URL without triggering navigation
      goto(url.pathname + url.search, { replaceState: true, noScroll: true });
      
      // Notify parent window of URL change
      notifyParentOfUrlChange();
    }
  }

  function checkUrlParams() {
    if (typeof window !== 'undefined' && data.length > 0) {
      const urlParams = new URLSearchParams(window.location.search);
      const householdId = String(urlParams.get('household') || ''); // Convert to string for consistent comparison
      const sectionParam = urlParams.get('section');
      const datasetParam = urlParams.get('baseline');
      
      console.log('🔗 Deep Link Check:', { 
        householdId, 
        sectionParam, 
        datasetParam,
        currentDataset: selectedDataset,
        foundInMap: householdIdMap.has(householdId) 
      });
      
      // Switch dataset if specified and different from current
      if (datasetParam && datasets[datasetParam] && datasetParam !== selectedDataset) {
        console.log('🔄 Switching dataset from URL:', datasetParam);
        selectedDataset = datasetParam;
        // Reload data with new dataset - this will trigger checkUrlParams again once loaded
        loadDataset(datasetParam);
      } else if (householdId && householdIdMap.has(householdId)) {
        const household = householdIdMap.get(householdId);
        
        // Find appropriate section for this household
        let targetSectionIndex = 0;
        
        if (sectionParam) {
          // Try to find section by name first
          const sectionIndex = scrollStates.findIndex(state => 
            state.id === sectionParam || state.id.includes(sectionParam)
          );
          if (sectionIndex >= 0) {
            targetSectionIndex = sectionIndex;
          }
        } else {
          // Auto-determine best section based on household income
          const income = household['Gross Income'] || 0;
          if (income < 50000) {
            targetSectionIndex = scrollStates.findIndex(state => state.id.includes('lower-income'));
          } else if (income < 200000) {
            targetSectionIndex = scrollStates.findIndex(state => state.id.includes('middle-income'));
          } else if (income < 1000000) {
            targetSectionIndex = scrollStates.findIndex(state => state.id.includes('upper-income'));
          } else {
            targetSectionIndex = scrollStates.findIndex(state => state.id.includes('highest-income'));
          }
          
          // Prefer individual view if available
          const individualIndex = targetSectionIndex + 1;
          if (individualIndex < scrollStates.length && scrollStates[individualIndex]?.viewType === 'individual') {
            targetSectionIndex = individualIndex;
          }
        }
        
        console.log('🎯 Navigating to section:', targetSectionIndex);
        
        if (targetSectionIndex >= 0) {
          // Set the household for the appropriate section
          const baseViewId = baseViews[Math.floor(targetSectionIndex / 2)]?.id;
          if (baseViewId) {
            randomHouseholds[baseViewId] = household;
            // Trigger reactivity
            randomHouseholds = { ...randomHouseholds };
          }
          
          // Disable intersection observer temporarily to prevent conflicts
          if (intersectionObserver) {
            intersectionObserver.disconnect();
          }
          
          // Navigate to the section immediately
          currentStateIndex = targetSectionIndex;
          isTransitioning = true;
          
          // Wait for DOM to be ready, then scroll and re-enable observer
          setTimeout(() => {
            renderVisualization();
            
            // Force scroll to the correct section with multiple attempts
            const scrollToSection = () => {
              const section = textSections[targetSectionIndex];
              const textColumn = document.querySelector('.text-column');
              
              console.log('📜 Attempting scroll to section:', {
                targetSectionIndex,
                sectionExists: !!section,
                textSectionsLength: textSections.length,
                boundSections: textSections.filter(s => s).length,
                textColumnExists: !!textColumn
              });
              
              // If sections aren't bound yet, try alternative approach
              if (!section && textColumn) {
                const fallbackSection = textColumn.querySelector(`[data-section-id="${scrollStates[targetSectionIndex]?.id}"]`);
                if (fallbackSection) {
                  console.log('📜 Using fallback section selection');
                  fallbackSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  return true;
                }
              }
              
              if (section && textColumn) {
                // Get section position relative to the text column
                const sectionRect = section.getBoundingClientRect();
                const columnRect = textColumn.getBoundingClientRect();
                const currentScrollTop = textColumn.scrollTop;
                
                // Calculate target scroll position
                const sectionTopInColumn = sectionRect.top - columnRect.top + currentScrollTop;
                const containerHeight = textColumn.clientHeight;
                const targetScrollTop = sectionTopInColumn - containerHeight / 2 + section.offsetHeight / 2;
                
                console.log('📍 Scroll calculation:', {
                  sectionTopInColumn,
                  containerHeight,
                  targetScrollTop,
                  currentScrollTop
                });
                
                // Smooth scroll to target
                textColumn.scrollTo({
                  top: Math.max(0, targetScrollTop),
                  behavior: 'smooth'
                });
                
                return true; // Success
              }
              return false; // Failed, try again
            };
            
            // Try scrolling immediately, then retry if needed
            if (!scrollToSection()) {
              setTimeout(() => {
                if (!scrollToSection()) {
                  // Final attempt after more time with DOM query fallback
                  setTimeout(() => {
                    if (!scrollToSection()) {
                      // Last resort: scroll by section index
                      const textColumn = document.querySelector('.text-column');
                      const allSections = textColumn?.querySelectorAll('.text-section');
                      if (allSections && allSections[targetSectionIndex]) {
                        console.log('📜 Using DOM query fallback');
                        allSections[targetSectionIndex].scrollIntoView({ 
                          behavior: 'smooth', 
                          block: 'center' 
                        });
                      }
                    }
                  }, 500);
                }
              }, 100);
            }
            
            // Re-enable intersection observer
            setTimeout(() => {
              isTransitioning = false;
              setupIntersectionObserver();
              console.log('✅ Deep link navigation complete');
            }, 800);
          }, 300);
        } else {
          console.log('❌ No valid section found for household');
        }
        
        urlSelectedHouseholdId = householdId;
      }
    }
  }

  // Reactive statement to watch for URL parameter changes
  $: if ($page?.url?.searchParams && data.length > 0 && !loading) {
    const currentHouseholdId = String($page.url.searchParams.get('household') || '');
    const currentDatasetParam = $page.url.searchParams.get('baseline');
    
    // Check if dataset changed
    if (currentDatasetParam && datasets[currentDatasetParam] && currentDatasetParam !== selectedDataset) {
      // Dataset changed via URL - switch dataset
      selectedDataset = currentDatasetParam;
      loadDataset(currentDatasetParam);
    } else if (currentHouseholdId !== urlSelectedHouseholdId && !isTransitioning) {
      // Only process household changes if dataset hasn't changed
      urlSelectedHouseholdId = currentHouseholdId;
      
      // Only trigger deep link navigation if this is NOT a user-initiated change
      if (currentHouseholdId && householdIdMap.has(currentHouseholdId) && !isUserInitiatedChange) {
        setTimeout(() => checkUrlParams(), 100);
      }
      
      // Reset the flag after processing
      isUserInitiatedChange = false;
    }
  }

  // Animated number utility functions
  function createAnimatedNumber(elementId, startValue, endValue, formatter, duration = 800) {
    // Cancel any existing animation for this element
    if (animatedNumbers.has(elementId)) {
      clearInterval(animatedNumbers.get(elementId));
    }
    
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const startTime = performance.now();
    
    function animate(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Cubic ease-out for smooth animation
      const eased = 1 - Math.pow(1 - progress, 3);
      
      const currentValue = startValue + (endValue - startValue) * eased;
      element.textContent = formatter(currentValue);
      
      if (progress < 1) {
        const animationId = requestAnimationFrame(animate);
        animatedNumbers.set(elementId, animationId);
      } else {
        animatedNumbers.delete(elementId);
      }
    }
    
    const animationId = requestAnimationFrame(animate);
    animatedNumbers.set(elementId, animationId);
  }


  // Animate household emphasis (simple grow and fade back)
  function animateHouseholdEmphasis(householdId, duration = 600) {
    // Cancel existing animation if any
    if (emphasisAnimationId) {
      cancelAnimationFrame(emphasisAnimationId);
    }
    
    const startTime = performance.now();
    
    function animate(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Simple ease-out: grow to max, then shrink back
      const eased = 1 - Math.pow(1 - progress, 3);
      const emphasisScale = 1 + (Math.sin(eased * Math.PI) * 0.8); // Grows then shrinks
      const emphasisOpacity = 1;
      
      // Store the animation state
      animatedHouseholds.set(householdId, {
        scale: emphasisScale,
        opacity: emphasisOpacity,
        isAnimating: progress < 1
      });
      
      // Trigger re-render
      if (!isTransitioning) {
        renderVisualization();
      }
      
      if (progress < 1) {
        emphasisAnimationId = requestAnimationFrame(animate);
      } else {
        // Animation complete, remove from animated households
        animatedHouseholds.delete(householdId);
        emphasisAnimationId = null;
        // Final render without animation
        if (!isTransitioning) {
          renderVisualization();
        }
      }
    }
    
    emphasisAnimationId = requestAnimationFrame(animate);
  }

  // Formatting functions
  function formatCurrency(value) {
    return fmtUSD.format(Math.round(value));
  }

  function formatPercentage(value) {
    const formatted = fmtPct.format(value / 100); // Convert to decimal for Intl formatter
    return value >= 0 ? '+' + formatted : formatted;
  }

  function formatDollarChange(value) {
    const formatted = fmtUSD.format(Math.abs(Math.round(value)));
    return value >= 0 ? '+' + formatted : '-' + formatted;
  }

  // Generate prose summary for a household
  function generateHouseholdSummary(household) {
    if (!household) return '';
    
    const income = household['Gross Income'];
          const baselineNetIncome = household['Baseline Net Income'];
      const changeInNetIncome = household['Total Change in Net Income'];
    const percentChange = household['Percentage Change in Net Income'];
          const householdSize = household['Household Size'];
      const isMarried = household['Is Married'];
          const numDependents = household['Number of Dependents'];
      const age = household['Age of Head'];
    const state = household['State'];
    
    const familyStructure = isMarried ? 
      (numDependents > 0 ? `married couple with ${numDependents} dependent${numDependents > 1 ? 's' : ''}` : 'married couple') :
      (numDependents > 0 ? `single parent with ${numDependents} dependent${numDependents > 1 ? 's' : ''}` : 'single person');
    
    const gainOrLoss = changeInNetIncome > 0 ? 'gains' : 'loses';
    
    return `This household is a ${familyStructure} living in ${state}. The head of household is ${age} years old. Under the baseline tax system, this household has a Gross Income of $${Math.round(income).toLocaleString()} and a Net Income of $${Math.round(baselineNetIncome).toLocaleString()}. After the proposed tax reforms, this household ${gainOrLoss} $${Math.round(Math.abs(changeInNetIncome)).toLocaleString()} annually, representing a ${Math.abs(percentChange).toFixed(1)}% ${changeInNetIncome > 0 ? 'increase' : 'decrease'} in their net income.`;
  }

  // Get provision breakdown for a household
  function getProvisionBreakdown(household) {
    if (!household) return [];
    
    const provisions = [
      { name: 'Rate Adjustment', key: 'Change in Net income after Rate Adjustments' },
      { name: 'Standard Deduction Increase', key: 'Change in Net income after Standard deduction increase' },
      { name: 'Exemption Repeal', key: 'Change in Net income after Exemption Reform' },
      { name: 'Child Tax Credit Social Security Number Requirement', key: 'Change in Net income after Child Tax Credit Social Security Number Requirement' },
      { name: 'Child Tax Credit Expansion', key: 'Change in Net income after Child Tax Credit Expansion' },
      { name: 'Qualified Business Income Deduction Reform', key: 'Change in Net income after Qualified Business Interest Deduction Reform' },
      { name: 'Alternative Minimum Tax Reform', key: 'Change in Net income after Alternative Minimum Tax Reform' },
      { name: 'Miscellaneous Deductions Reform', key: 'Change in Net income after Miscellaneous Deduction Reform' },
      { name: 'Charitable Deductions Reform', key: 'Change in Net income after Charitable Deductions Reform' },
      { name: 'Casualty Loss Deductions Repeal', key: 'Change in Net income after Casualty Loss Deductions Repeal' },
      { name: 'Pease Repeal', key: 'Change in Net income after Pease Repeal' },
      { name: 'Limitation on Itemized Deductions Reform', key: 'Change in Net income after Limitation on Itemized Deductions Reform' },
      { name: 'Estate Tax Reform', key: 'Change in Net income after Estate Tax Reform' },
      { name: 'New Senior Deduction', key: 'Change in Net income after New Senior Deduction' },
      { name: 'Tip Exemption', key: 'Change in Net income after Tip Exemption' },
      { name: 'Overtime Exemption', key: 'Change in Net income after Overtime Exemption' },
      { name: 'Auto Loan Interest Deduction', key: 'Change in Net income after Auto Loan Interest Deduction' },
      { name: 'Cap on State and Local Tax Deduction', key: 'Change in Net income after Cap on state and local tax deduction' },
      { name: 'Child and Dependent Care Credit Reform', key: 'Change in Net income after Child and dependent care credit reform' },
      { name: 'Extension of ACA Enhanced Subsidies', key: 'Change in Net income after Extension of ACA Enhanced Subsidies' },
      { name: 'SNAP Reform', key: 'Change in Net income after SNAP Reform' },
      { name: 'Medicaid Reform', key: 'Change in Net income after Medicaid Reform' }
    ];
    
    return provisions
      .map((provision, index) => ({
        name: provision.name,
        value: household[provision.key] || 0,
        index: index // Add index for unique IDs
      }))
      .filter(provision => Math.abs(provision.value) > 0.01) // Only show non-zero provisions
      .sort((a, b) => Math.abs(b.value) - Math.abs(a.value)); // Sort by absolute impact
  }

  // Scroll handling with intersection observer pattern
  let textSections = [];
  let currentStateIndex = 0;
  let previousStateIndex = 0;
  let isTransitioning = false;
  let intersectionObserver;

  function setupIntersectionObserver() {
    if (intersectionObserver) {
      intersectionObserver.disconnect();
    }


    // Clean intersection observer setup (backup method)
    const textColumn = document.querySelector('.text-column');
    if (!textColumn) return;

    intersectionObserver = new IntersectionObserver(
      (entries) => {
        let mostVisibleEntry = null;
        let maxRatio = 0;

        entries.forEach((entry) => {
          const index = parseInt(entry.target.dataset.index);
          if (entry.isIntersecting && entry.intersectionRatio > maxRatio) {
            maxRatio = entry.intersectionRatio;
            mostVisibleEntry = { entry, index };
          }
        });

        if (mostVisibleEntry && mostVisibleEntry.index !== currentStateIndex && !isTransitioning && !urlSelectedHouseholdId) {
          transitionToState(mostVisibleEntry.index);
        }
      },
      {
        root: textColumn,
        threshold: [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1],
        rootMargin: '-30% 0px -30% 0px'
      }
    );

    textSections.forEach((section, index) => {
      if (section) {
        section.dataset.index = index.toString();
        intersectionObserver.observe(section);
      }
    });
  }

  function transitionToState(newIndex, skipRandomHousehold = false) {
    if (newIndex === currentStateIndex || isTransitioning) return;
    
    isTransitioning = true;
    previousStateIndex = currentStateIndex;
    const fromState = scrollStates[currentStateIndex];
    const toState = scrollStates[newIndex];
    
    // Pick new random household when transitioning to individual view (unless skipped for deep linking)
    if (toState.viewType === 'individual' && !skipRandomHousehold) {
      const baseViewId = baseViews[Math.floor(newIndex / 2)]?.id;
      const filteredData = data.filter(baseViews[Math.floor(newIndex / 2)]?.view?.filter || (() => true));
      if (filteredData.length > 0) {
        const randomHousehold = getRandomWeightedHousehold(filteredData);
        if (randomHousehold) {
          randomHouseholds[baseViewId] = randomHousehold;
          // Trigger reactivity
          randomHouseholds = { ...randomHouseholds };
        }
      }
    }
    
    // Update text section immediately for instant feedback
    currentStateIndex = newIndex;
    
    animateScales({
      from: fromState.view,
      to: toState.view,
      duration: 1200,
      onComplete: () => {
        isTransitioning = false;
      }
    });
  }

  function animateScales({ from, to, duration, onComplete }) {
    const startTime = performance.now();
    
    function animate(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Cubic easing for smooth transitions
      const eased = progress < 0.5
        ? 4 * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 3) / 2;
      
      renderVisualization(from, to, eased);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        onComplete();
      }
    }
    
    requestAnimationFrame(animate);
  }

  function renderVisualization(fromView = null, toView = null, t = 0) {
    if (!data.length || !canvasRef) return;

    const canvas = canvasRef;
    const ctx = canvas.getContext('2d', { alpha: false });
    
    // Set up high-DPI canvas
    const devicePixelRatio = window.devicePixelRatio || 1;
    const displayWidth = 800;
    const displayHeight = 600;
    
    canvas.width = displayWidth * devicePixelRatio;
    canvas.height = displayHeight * devicePixelRatio;
    canvas.style.width = displayWidth + 'px';
    canvas.style.height = displayHeight + 'px';
    
    ctx.scale(devicePixelRatio, devicePixelRatio);
    
    const width = displayWidth;
    const height = displayHeight;
    const margin = { top: 80, right: 120, bottom: 100, left: 100 };

    // Determine current view and interpolation
    let currentView, targetView, interpolationT;
    
    if (isTransitioning && fromView !== null && toView !== null) {
      currentView = fromView;
      targetView = toView;
      interpolationT = t;
    } else {
      currentView = scrollStates[currentStateIndex].view;
      targetView = currentView;
      interpolationT = 0;
    }

    // Interpolate between views with D3
    const yMin = d3.interpolate(currentView.yDomain[0], targetView.yDomain[0])(interpolationT);
    const yMax = d3.interpolate(currentView.yDomain[1], targetView.yDomain[1])(interpolationT);
    const xMin = d3.interpolate(currentView.xDomain[0], targetView.xDomain[0])(interpolationT);
    const xMax = d3.interpolate(currentView.xDomain[1], targetView.xDomain[1])(interpolationT);
    
    // Clear canvas with PolicyEngine background
    ctx.fillStyle = COLORS.WHITE;
    ctx.fillRect(0, 0, width, height);

    // Don't filter data here - let points fade in/out during rendering
    // Include all data that might be visible in either current or target view
    let allRelevantData = data;
    if (isTransitioning && fromView && toView) {
      // During transition, include data visible in either view
      allRelevantData = data.filter(d => {
        const inFrom = fromView.filter ? fromView.filter(d) : true;
        const inTo = toView.filter ? toView.filter(d) : true;
        return inFrom || inTo;
      });
    } else {
      // Static view - include current view data plus wider buffer for smooth transitions
      const currentState = currentView;
      allRelevantData = data.filter(d => {
        // Include a much wider range so we can fade points in/out smoothly
            return d['Gross Income'] >= 0 && d['Gross Income'] <= 15000000 &&
           d['Percentage Change in Net Income'] >= -100 &&
           d['Percentage Change in Net Income'] <= 100;
      });
    }

    // Create scales
    const xScale = d3.scaleLinear()
      .domain([xMin, xMax])
      .range([margin.left, width - margin.right]);

    const yScale = d3.scaleLinear()
      .domain([yMin, yMax])
      .range([height - margin.bottom, margin.top]);

    // Draw grid lines
    ctx.strokeStyle = COLORS.MEDIUM_DARK_GRAY;
    ctx.lineWidth = 0.5;
    ctx.setLineDash([]);
    
    // Vertical grid lines
    const xTickInterval = Math.max(5, Math.floor((xMax - xMin) / 10));
    for (let i = Math.ceil(xMin / xTickInterval) * xTickInterval; i <= xMax; i += xTickInterval) {
      const x = xScale(i);
      ctx.beginPath();
      ctx.moveTo(x, margin.top);
      ctx.lineTo(x, height - margin.bottom);
      ctx.stroke();
    }
    
    // Horizontal grid lines
    const yTicks = yScale.ticks(6);
    yTicks.forEach(tick => {
      const y = yScale(tick);
      ctx.beginPath();
      ctx.moveTo(margin.left, y);
      ctx.lineTo(width - margin.right, y);
      ctx.stroke();
    });

    // Clear rendered points for hit detection
    renderedPoints = [];

    // Calculate min/max weights for visible households to scale opacity dynamically
    let minWeight = Infinity;
    let maxWeight = -Infinity;
    
    // First pass: find weight range for visible households
    allRelevantData.forEach(d => {
      const x = xScale(d['Percentage Change in Net Income']);
      const y = yScale(d['Gross Income']);
      
      // Only consider points that will be visible on screen
      if (x >= margin.left && x <= width - margin.right && 
          y >= margin.top && y <= height - margin.bottom) {
        const weight = d['Household weight'] || d['Household Weight'] || 1;
        minWeight = Math.min(minWeight, weight);
        maxWeight = Math.max(maxWeight, weight);
      }
    });
    
    // Ensure we have valid range
    if (minWeight === Infinity || maxWeight === -Infinity || minWeight === maxWeight) {
      minWeight = 1;
      maxWeight = 100000;
    }

    // Enhanced point rendering with smooth fade animations
    allRelevantData.forEach(d => {
      const x = xScale(d['Percentage Change in Net Income']);
      const y = yScale(d['Gross Income']);
      
      // Skip if outside canvas bounds
      if (x < margin.left || x > width - margin.right || y < margin.top || y > height - margin.bottom) return;

      // Calculate fade opacity based on filter transitions
      let fadeOpacity = 1;
      
      // Make sure interpolationT is available in this scope
      const currentInterpolationT = interpolationT;
      
      if (isTransitioning && fromView && toView && interpolationT !== undefined) {
        const visibleInFrom = fromView.filter ? fromView.filter(d) : true;
        const visibleInTo = toView.filter ? toView.filter(d) : true;
        
        if (visibleInFrom && visibleInTo) {
          fadeOpacity = 1; // Always visible
        } else if (visibleInFrom && !visibleInTo) {
          // Fade out with smooth easing: start at 1, end at 0
          const easedProgress = interpolationT * interpolationT; // Quadratic ease-in
          fadeOpacity = 1 - easedProgress;
        } else if (!visibleInFrom && visibleInTo) {
          // Fade in with smooth easing: start at 0, end at 1
          const easedProgress = interpolationT * (2 - interpolationT); // Quadratic ease-out
          fadeOpacity = easedProgress;
        } else {
          fadeOpacity = 0; // Never visible
        }
      } else {
        // Static view - check if point should be visible
        const currentState = currentView;
        const shouldBeVisible = currentState.filter ? currentState.filter(d) : true;
        fadeOpacity = shouldBeVisible ? 1 : 0;
      }

      // PolicyEngine color scheme
      let color;
              const change = d['Percentage Change in Net Income'];
      if (Math.abs(change) < 0.1) {
        color = COLORS.MEDIUM_DARK_GRAY; // light gray for no change
      } else if (change > 0) {
        color = COLORS.TEAL_MEDIUM; // medium teal for gains
      } else {
        color = COLORS.DARK_GRAY; // dark gray for losses
      }

      // Point sizing and final opacity with smooth transitions
      const currentState = scrollStates[currentStateIndex];
      const fromState = isTransitioning ? scrollStates[previousStateIndex] : currentState;
      const toState = currentState;
      
      const isGroupHighlighted = d.isHighlighted && d.stateIndex === Math.floor(currentStateIndex / 2);
      
      // Individual household highlighting
      let isIndividualHighlighted = false;
      let wasIndividualHighlighted = false;
      
      if (currentState?.viewType === 'individual') {
        const baseViewId = baseViews[Math.floor(currentStateIndex / 2)]?.id;
        const randomHousehold = randomHouseholds[baseViewId];
        isIndividualHighlighted = randomHousehold && d.id === randomHousehold.id;
      }
      
      // Check previous state for smooth transitions
      if (isTransitioning && fromState?.viewType === 'individual') {
        const baseViewId = baseViews[Math.floor(previousStateIndex / 2)]?.id;
        const prevRandomHousehold = randomHouseholds[baseViewId];
        wasIndividualHighlighted = prevRandomHousehold && d.id === prevRandomHousehold.id;
      }
      
      const isHighlighted = isGroupHighlighted || isIndividualHighlighted;
      
      // Use uniform radius for all points
      const weight = d['Household weight'] || d['Household Weight'] || 1;
      let radius = isHighlighted ? (isIndividualHighlighted ? 6 : 4) : 2;
      
      // Calculate opacity based on household weight using dynamic logarithmic scale
      // Map weights from [minWeight, maxWeight] to opacity [0.3, 0.85] for non-highlighted points
      const logWeight = Math.log10(weight + 1); // Add 1 to handle weight=0
      const logMinWeight = Math.log10(minWeight + 1);
      const logMaxWeight = Math.log10(maxWeight + 1);
      const minOpacity = 0.3; // Increased minimum for better visibility
      const maxOpacity = 0.85; // Slightly higher max for contrast
      
      // Normalize to 0-1 range based on visible data
      const normalizedWeight = (logWeight - logMinWeight) / (logMaxWeight - logMinWeight);
      const weightBasedOpacity = minOpacity + (maxOpacity - minOpacity) * normalizedWeight;
      
      let baseOpacity = isHighlighted ? 1 : Math.min(Math.max(weightBasedOpacity, minOpacity), maxOpacity);
      
      // Apply animation effects if this household is being animated
      const animationState = animatedHouseholds.get(d.id);
      if (animationState && animationState.isAnimating) {
        radius = radius * animationState.scale;
        baseOpacity = Math.min(baseOpacity * animationState.opacity, 1);
      }
      
      // Fade other points during individual view
      if (currentState?.viewType === 'individual' && !isIndividualHighlighted) {
        baseOpacity *= 0.15; // Make non-selected households very faint
      }
      
      const finalOpacity = baseOpacity * fadeOpacity;

      if (finalOpacity > 0.02) { // Only render if sufficiently visible
        // Store point for hit detection
        renderedPoints.push({
          x: x,
          y: y,
          radius: radius,
          data: d,
          opacity: finalOpacity
        });

        ctx.globalAlpha = finalOpacity;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);
        ctx.fill();

        // Highlight stroke for featured points
        if (isHighlighted && finalOpacity > 0.5) {
          ctx.globalAlpha = finalOpacity;
          ctx.strokeStyle = COLORS.BLACK;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    });

    ctx.globalAlpha = 1;

    // Draw zero line
    if (xMin <= 0 && xMax >= 0) {
      ctx.strokeStyle = COLORS.BLACK;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(xScale(0), margin.top);
      ctx.lineTo(xScale(0), height - margin.bottom);
      ctx.stroke();
    }

    // Draw axes using SVG overlay
    if (svgRef) {
      const svg = d3.select(svgRef);
      svg.selectAll('*').remove();

      const g = svg.append('g');

      // X-axis with animated labels
      const xAxis = g.append('g')
        .attr('transform', `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(xScale).tickFormat(d => `${d > 0 ? '+' : ''}${d}%`))
        .style('font-family', getFontFamily('sans'))
        .style('font-size', '10px')
        .style('color', COLORS.DARKEST_BLUE);

      // Y-axis with labels (no animation)
      const yAxis = g.append('g')
        .attr('transform', `translate(${margin.left},0)`)
        .call(d3.axisLeft(yScale).ticks(6).tickFormat(d => d3.format('$,')(d)))
        .style('font-family', getFontFamily('sans'))
        .style('font-size', '10px')
        .style('color', COLORS.DARKEST_BLUE);

      // Style axes lines
      xAxis.select('.domain').style('stroke', COLORS.BLACK).style('stroke-width', 1);
      yAxis.select('.domain').style('stroke', COLORS.BLACK).style('stroke-width', 1);
      
      // Style tick lines
      xAxis.selectAll('.tick line').style('stroke', COLORS.BLACK).style('stroke-width', 0.5);
      yAxis.selectAll('.tick line').style('stroke', COLORS.BLACK).style('stroke-width', 0.5);

      // Axis labels
      g.append('text')
        .attr('x', width / 2)
        .attr('y', height - 15)
        .attr('text-anchor', 'middle')
        .style('font-family', getFontFamily('sans'))
        .style('font-size', '16px')
        .style('font-weight', '400')
        .style('fill', COLORS.DARK_GRAY)
        .text('Change in income →');

      g.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -height / 2)
        .attr('y', 25)
        .attr('text-anchor', 'middle')
        .style('font-family', getFontFamily('sans'))
        .style('font-size', '16px')
        .style('font-weight', '400')
        .style('fill', COLORS.DARK_GRAY)
        .text('Annual household income →');
    }
  }

  // Reactive statements for rendering
  $: if (data.length && canvasRef && !isTransitioning) {
    renderVisualization();
  }

  // Reactive statement to animate numbers when household changes
  let previousHouseholds = {};
  $: {
    if (typeof window !== 'undefined') {
      Object.keys(randomHouseholds).forEach(viewId => {
        const currentHousehold = randomHouseholds[viewId];
        const previousHousehold = previousHouseholds[viewId];
        
        if (currentHousehold && previousHousehold && currentHousehold.id !== previousHousehold.id) {
          // Find the section index for this household
          const sectionIndex = scrollStates.findIndex(state => 
            state.viewType === 'individual' && 
            baseViews[Math.floor(scrollStates.indexOf(state) / 2)]?.id === viewId
          );
          
          if (sectionIndex >= 0) {
            // Check if this is the currently visible section
            const isCurrentSection = sectionIndex === currentStateIndex;
            const animationDelay = isCurrentSection ? 50 : 100; // Faster animation for current section
            const animationDuration = isCurrentSection ? 400 : 600; // Shorter duration for clicks
            
            // Animate the numbers with delay for smooth effect
            setTimeout(() => {
              createAnimatedNumber(
                `household-id-${sectionIndex}`,
                parseInt(previousHousehold.id),
                parseInt(currentHousehold.id),
                (val) => Math.round(val),
                animationDuration
              );
            }, animationDelay - 100); // Start household ID first
            
            // Animate demographic values
            setTimeout(() => {
              createAnimatedNumber(
                `num-dependents-${sectionIndex}`,
                previousHousehold['Number of Dependents'] || previousHousehold['Dependents'] || 0,
                currentHousehold['Number of Dependents'] || currentHousehold['Dependents'] || 0,
                (val) => Math.round(val),
                animationDuration
              );
            }, animationDelay);
            
            setTimeout(() => {
              const prevAge = previousHousehold['Age of Head'] || previousHousehold['Age'];
              const currAge = currentHousehold['Age of Head'] || currentHousehold['Age'];
              if (typeof prevAge === 'number' && typeof currAge === 'number') {
                createAnimatedNumber(
                  `age-of-head-${sectionIndex}`,
                  prevAge,
                  currAge,
                  (val) => Math.round(val),
                  animationDuration
                );
              }
            }, animationDelay);
            
            setTimeout(() => {
              createAnimatedNumber(
                `market-income-${sectionIndex}`,
                previousHousehold['Market Income'] || previousHousehold['Gross Income'] || 0,
                currentHousehold['Market Income'] || currentHousehold['Gross Income'] || 0,
                formatCurrency,
                animationDuration
              );
            }, animationDelay);
            
            setTimeout(() => {
              createAnimatedNumber(
                `baseline-net-${sectionIndex}`,
                previousHousehold['Baseline Net Income'] || 0,
                currentHousehold['Baseline Net Income'] || 0,
                formatCurrency,
                animationDuration
              );
            }, animationDelay);
            
            setTimeout(() => {
              createAnimatedNumber(
                `gross-income-${sectionIndex}`,
                previousHousehold['Gross Income'],
                currentHousehold['Gross Income'],
                formatCurrency,
                animationDuration
              );
            }, animationDelay);
            
            setTimeout(() => {
              createAnimatedNumber(
                `net-change-${sectionIndex}`,
                previousHousehold['Total Change in Net Income'],
                currentHousehold['Total Change in Net Income'],
                formatDollarChange,
                animationDuration
              );
            }, animationDelay + 100);
            
            setTimeout(() => {
              createAnimatedNumber(
                `percent-change-${sectionIndex}`,
                previousHousehold['Percentage Change in Net Income'],
                currentHousehold['Percentage Change in Net Income'],
                formatPercentage,
                animationDuration
              );
            }, animationDelay + 200);
            
            // Animate provision values
            const currentProvisions = getProvisionBreakdown(currentHousehold);
            const previousProvisions = getProvisionBreakdown(previousHousehold);
            
            currentProvisions.forEach((currentProv, provIndex) => {
              const prevProv = previousProvisions.find(p => p.index === currentProv.index);
              const prevValue = prevProv ? prevProv.value : 0;
              
              setTimeout(() => {
                createAnimatedNumber(
                  `provision-${sectionIndex}-${currentProv.index}`,
                  prevValue,
                  currentProv.value,
                  formatDollarChange,
                  animationDuration
                );
              }, animationDelay + 300 + (provIndex * 20)); // Stagger provision animations
            });
          }
        }
      });
      
      // Update previous households for next comparison
      previousHouseholds = { ...randomHouseholds };
    }
  }

  // Reactive statement to animate data table numbers when selectedData changes
  let previousSelectedData = null;
  $: {
    if (typeof window !== 'undefined' && selectedData && previousSelectedData) {
      // Use sophisticated timing like provision breakdown for "train station" effect
      const animationDelay = 50;
      const animationDuration = 400;
      
      let index = 0;
      Object.entries(selectedData).forEach(([key, value]) => {
        if (key !== 'id' && key !== 'isAnnotated' && key !== 'sectionIndex' && key !== 'isHighlighted' && key !== 'highlightGroup' && key !== 'stateIndex') {
          if (typeof value === 'number') {
            const prevValue = previousSelectedData[key];
            if (typeof prevValue === 'number' && prevValue !== value) {
              
              // All values animate together simultaneously
              const delay = animationDelay;
              
              setTimeout(() => {
                if (key.includes('Income') || key.includes('Taxes') || key.includes('Tax Liability') || key.includes('Benefits') || key.includes('Gains') || key.includes('Interest') || key.includes('Medicaid') || key.includes('ACA') || key.includes('CHIP') || key.includes('SNAP') || key.toLowerCase().includes('change in') && !key.includes('Percentage')) {
                  createAnimatedNumber(
                    `table-value-${index}`,
                    prevValue,
                    value,
                    (val) => (val < 0 ? '-' : '') + '$' + Math.abs(Math.round(val)).toLocaleString(),
                    animationDuration
                  );
                } else if (key.includes('Percentage')) {
                  createAnimatedNumber(
                    `table-value-${index}`,
                    prevValue,
                    value,
                    (val) => (val > 0 ? '+' : '') + val.toFixed(2) + '%',
                    animationDuration
                  );
                } else if (key.includes('ID') || key.includes('Household')) {
                  createAnimatedNumber(
                    `table-value-${index}`,
                    typeof prevValue === 'string' ? parseInt(prevValue) : prevValue,
                    typeof value === 'string' ? parseInt(value) : value,
                    (val) => Math.round(val),
                    animationDuration
                  );
                } else {
                  createAnimatedNumber(
                    `table-value-${index}`,
                    prevValue,
                    value,
                    (val) => Math.round(val).toLocaleString(),
                    animationDuration
                  );
                }
              }, delay);
            }
          }
          index++;
        }
      });
    }
    previousSelectedData = selectedData ? { ...selectedData } : null;
  }

  // Initialize text sections and intersection observer
  onMount(() => {
    textSections = new Array(scrollStates.length);
    
    // Set up intersection observer after DOM is ready, but only if no URL params
    setTimeout(() => {
      const urlParams = new URLSearchParams(window.location.search);
      const hasHouseholdParam = urlParams.has('household');
      
      console.log('🔧 OnMount setup:', {
        hasHouseholdParam,
        scrollStatesLength: scrollStates.length,
        textSectionsLength: textSections.length
      });
      
      if (!hasHouseholdParam) {
        setupIntersectionObserver();
      }
      
      // Initial render
      if (data.length && canvasRef) {
        renderVisualization();
      }
    }, 200);
    
    return () => {
      if (intersectionObserver) {
        intersectionObserver.disconnect();
      }
    };
  });

  // Throttled scroll handler
  let scrollTimeout;
  function handleScroll(event) {
    if (!textSections.length) return;
    
    // Throttle scroll events
    if (scrollTimeout) clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      checkActiveSection(event.target);
    }, 50);
  }

  function checkActiveSection(container) {
    if (isTransitioning) return;
    
    const scrollTop = container.scrollTop;
    const containerHeight = container.clientHeight;
    
    // Query sections directly from DOM
    const domSections = container.querySelectorAll('.text-section');
    const sectionsToCheck = Array.from(domSections);
    
    // Find which section's center is closest to viewport center
    let activeSection = 0;
    let minDistance = Infinity;
    
    sectionsToCheck.forEach((section, index) => {
      if (section) {
        const rect = section.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        
        const sectionTop = rect.top - containerRect.top + scrollTop;
        const sectionCenter = sectionTop + rect.height / 2;
        const viewportCenter = scrollTop + containerHeight / 2;
        const distance = Math.abs(sectionCenter - viewportCenter);
        
        if (distance < minDistance) {
          minDistance = distance;
          activeSection = index;
        }
      }
    });
    
    if (activeSection !== currentStateIndex && minDistance !== Infinity) {
      transitionToState(activeSection);
    }
  }

  // Canvas click handler for dot selection
  function handleCanvasClick(event) {
    if (!canvasRef || !renderedPoints.length) return;
    
    const rect = canvasRef.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const clickY = event.clientY - rect.top;
    
    // Find the closest point within click radius
    let closestPoint = null;
    let minDistance = Infinity;
    const maxClickDistance = 20; // Much larger click area
    
    for (const point of renderedPoints) {
      if (point.opacity < 0.05) continue; // Skip nearly invisible points
      
      const dx = clickX - point.x;
      const dy = clickY - point.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance <= maxClickDistance && distance < minDistance) {
        minDistance = distance;
        closestPoint = point;
      }
    }
    
    if (closestPoint) {
      // Animate the clicked household
      animateHouseholdEmphasis(closestPoint.data.id);
      
      // If we're in an individual household view, update that section's household
      const currentState = scrollStates[currentStateIndex];
      if (currentState?.viewType === 'individual') {
        const baseViewId = baseViews[Math.floor(currentStateIndex / 2)]?.id;
        if (baseViewId) {
          // Update the random household for this section with the clicked household
          randomHouseholds[baseViewId] = closestPoint.data;
          // Trigger reactivity
          randomHouseholds = { ...randomHouseholds };
          
          // Update URL with selected household (mark as user-initiated)
          isUserInitiatedChange = true;
          updateUrlWithHousehold(closestPoint.data.id, currentState.id);
        }
      }
    }
  }

  // Function to show household details for info icon
  function showHouseholdDetails(household) {
    if (household) {
      selectedData = household;
    }
  }



  // Weighted random sampling function
  function getRandomWeightedHousehold(filteredData) {
    if (!filteredData || filteredData.length === 0) return null;
    
    // Calculate total weight
    const totalWeight = filteredData.reduce((sum, household) => sum + (household['Household Weight'] || 1), 0);
    
    // Generate random number between 0 and totalWeight
    let randomWeight = Math.random() * totalWeight;
    
    // Find the household that corresponds to this weight
    for (const household of filteredData) {
      randomWeight -= (household['Household Weight'] || 1);
      if (randomWeight <= 0) {
        return household;
      }
    }
    
    // Fallback to last household if rounding errors occur
    return filteredData[filteredData.length - 1];
  }

  // Function to pick a new random household for current section
  function pickRandomHousehold() {
    const currentState = scrollStates[currentStateIndex];
    if (currentState?.viewType === 'individual') {
      const baseViewIndex = Math.floor(currentStateIndex / 2);
      const baseView = baseViews[baseViewIndex];
      if (baseView) {
        const filteredData = data.filter(baseView.view.filter);
        const newHousehold = getRandomWeightedHousehold(filteredData);
        if (newHousehold) {
          // Animate the new random household
          animateHouseholdEmphasis(newHousehold.id);
          
          randomHouseholds[baseView.id] = newHousehold;
          // Trigger reactivity
          randomHouseholds = { ...randomHouseholds };
          
          // Update URL with new household (mark as user-initiated)
          isUserInitiatedChange = true;
          updateUrlWithHousehold(newHousehold.id, currentState.id);
        }
      }
    }
  }

  // Function to copy household URL to clipboard
  async function copyHouseholdUrl(household, event) {
    const currentState = scrollStates[currentStateIndex];
    let url;
    
    // Debug logging to understand the issue
    const isInIframe = typeof window !== 'undefined' && window.parent !== window;
    console.log('Copy URL debug:', {
      isInIframe,
      currentLocation: window.location.href,
      household: household.id,
      baseline: selectedDataset,
      section: currentState?.id
    });
    
    // Check if we're in an iframe
    if (isInIframe) {
      // We're in an iframe - always use PolicyEngine URL
      url = new URL('https://policyengine.org/us/obbba-household-explorer');
    } else {
      // Not in iframe, use current location
      url = new URL(window.location.href);
    }
    
    // Set household parameters
    url.searchParams.set('household', household.id);
    url.searchParams.set('baseline', selectedDataset);
    if (currentState) {
      url.searchParams.set('section', currentState.id);
    }
    
    const fullUrl = url.toString();
    console.log('Full URL to copy:', fullUrl);
    
    try {
      await navigator.clipboard.writeText(fullUrl);
      
      // Show temporary success feedback
      if (event && event.target) {
        const button = event.target.closest('button');
        if (button) {
          const originalTitle = button.title;
          button.title = 'Copied!';
          button.classList.add('copied');
          
          setTimeout(() => {
            button.title = originalTitle;
            button.classList.remove('copied');
          }, 2000);
        }
      }
      
      console.log('Successfully copied URL to clipboard');
    } catch (err) {
      console.error('Clipboard API failed:', err);
      
      // Fallback method: Create a temporary textarea
      try {
        const textarea = document.createElement('textarea');
        textarea.value = fullUrl;
        textarea.style.position = 'fixed';
        textarea.style.left = '-999999px';
        textarea.style.top = '-999999px';
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        
        const successful = document.execCommand('copy');
        document.body.removeChild(textarea);
        
        if (successful) {
          console.log('Successfully copied using execCommand fallback');
          
          // Show success feedback
          if (event && event.target) {
            const button = event.target.closest('button');
            if (button) {
              const originalTitle = button.title;
              button.title = 'Copied!';
              button.classList.add('copied');
              
              setTimeout(() => {
                button.title = originalTitle;
                button.classList.remove('copied');
              }, 2000);
            }
          }
        } else {
          console.error('execCommand copy failed');
          alert('Failed to copy URL. URL is: ' + fullUrl);
        }
      } catch (fallbackErr) {
        console.error('All copy methods failed:', fallbackErr);
        alert('Failed to copy URL. URL is: ' + fullUrl);
      }
    }
  }

  // Watch for text sections being bound
  $: if (textSections.length > 0 && textSections.every(el => el)) {
    setTimeout(() => {
      const urlParams = new URLSearchParams(window.location.search);
      const hasHouseholdParam = urlParams.has('household');
      
      if (!hasHouseholdParam) {
        setupIntersectionObserver();
      }
    }, 50);
  }



</script>

<svelte:head>
  <title>PolicyEngine Tax Impact Visualization</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: 'Roboto', helvetica, arial, sans-serif;
    }
  </style>
</svelte:head>

<div class="app">
  {#if loading}
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <p>Loading {datasets[selectedDataset].label} data...</p>
      </div>
    </div>
  {/if}

  <!-- Floating header -->
  <header class="floating-header">
    <div class="header-content">
      <h1 class="app-title">OBBBA Household Explorer</h1>
      <div class="baseline-selector-container">
        <span class="baseline-label">Baseline:</span>
        <div class="baseline-selector">
          <button 
            class="tab-button" 
            class:active={selectedDataset === 'tcja-expiration'}
            on:click={() => switchDataset('tcja-expiration')}
            disabled={loading}
          >
            TCJA Expiration
          </button>
          <button 
            class="tab-button" 
            class:active={selectedDataset === 'tcja-extension'}
            on:click={() => switchDataset('tcja-extension')}
            disabled={loading}
          >
            TCJA Extension
          </button>
        </div>
      </div>
    </div>
  </header>

  <div class="main-container">
    <!-- Layout: text on left, viz on right -->
    <div class="text-column" on:scroll={handleScroll}>
      {#each scrollStates as state, i}
        <section 
          class="text-section" 
          class:active={i === currentStateIndex}
          bind:this={textSections[i]}
          data-index={i}
          data-section-id={state.id}
        >
          <div class="section-content">
            <h2>{state.title}</h2>
            <p>{@html state.text}</p>
            
            
            {#if state.viewType === 'individual'}
              {@const baseViewId = baseViews[Math.floor(i / 2)]?.id}
              {@const randomHousehold = randomHouseholds[baseViewId]}
              {#if randomHousehold}
                {@const provisionBreakdown = getProvisionBreakdown(randomHousehold)}
                <div class="household-profile">
                  <h3>
                    Household #<span id="household-id-{i}">{randomHousehold.id}</span>
                    <div class="header-buttons">
                      <button 
                        class="action-button random-button" 
                        on:click={pickRandomHousehold}
                        title="Pick a new random household"
                      >
                        🔀
                      </button>
                      <button 
                        class="action-button link-button" 
                        on:click={(e) => copyHouseholdUrl(randomHousehold, e)}
                        title="Copy link to this household"
                      >
                        🔗
                      </button>
                      <button 
                        class="action-button info-button" 
                        on:click={() => showHouseholdDetails(randomHousehold)}
                        title="Show detailed data for this household"
                      >
                        ⓘ
                      </button>
                    </div>
                  </h3>
                  <div class="household-details">
                    <div class="detail-item">
                      <span class="label">Marital Status:</span>
                      <span class="value">{randomHousehold['Is Married'] ? 'Married' : 'Single'}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">State:</span>
                      <span class="value">{randomHousehold['State'] || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label"># Dependents:</span>
                      <span class="value" id="num-dependents-{i}">{Math.round(randomHousehold['Number of Dependents'] || randomHousehold['Dependents'] || 0)}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">Age of Head:</span>
                      <span class="value" id="age-of-head-{i}">{randomHousehold['Age of Head'] || randomHousehold['Age'] || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">Market Income:</span>
                      <span class="value" id="market-income-{i}">
                        {formatCurrency(randomHousehold['Market Income'] || randomHousehold['Gross Income'] || 0)}
                      </span>
                    </div>
                    <div class="detail-item">
                      <span class="label">Baseline Net Income:</span>
                      <span class="value" id="baseline-net-{i}">
                        {formatCurrency(randomHousehold['Baseline Net Income'] || 0)}
                      </span>
                    </div>
                    <div class="detail-item">
                      <span class="label">Net Income Change:</span>
                      <span class="value {randomHousehold['Total Change in Net Income'] > 0 ? 'pos' : randomHousehold['Total Change in Net Income'] < 0 ? 'neg' : 'zero'}" id="net-change-{i}">
                        {formatDollarChange(randomHousehold['Total Change in Net Income'])}
                      </span>
                    </div>
                    <div class="detail-item">
                      <span class="label">% Change:</span>
                      <span class="value {randomHousehold['Percentage Change in Net Income'] > 0 ? 'pos' : randomHousehold['Percentage Change in Net Income'] < 0 ? 'neg' : 'zero'}" id="percent-change-{i}">
                        {formatPercentage(randomHousehold['Percentage Change in Net Income'])}
                      </span>
                    </div>
                  </div>
                  
                  {#if provisionBreakdown.length > 0}
                    <div class="provision-breakdown">
                      <h4>Breakdown by provision</h4>
                      <div class="provision-list">
                        {#each provisionBreakdown as provision}
                          <div class="provision-item">
                            <span class="provision-name">{provision.name}:</span>
                            <span class="value {provision.value > 0 ? 'pos' : provision.value < 0 ? 'neg' : 'zero'}" id="provision-{i}-{provision.index}">
                              {formatDollarChange(provision.value)}
                            </span>
                          </div>
                        {/each}
                      </div>
                    </div>
                  {:else}
                    <div class="provision-breakdown">
                      <h4>Breakdown by provision</h4>
                      <p class="no-provisions">No policy provisions affect this household.</p>
                    </div>
                  {/if}
                </div>
              {/if}
            {/if}
          </div>
        </section>
      {/each}
    </div>
    
    <div class="viz-column">
      <div class="viz-sticky">
        <canvas 
          bind:this={canvasRef} 
          width="800" 
          height="600"
          class="main-canvas"
          on:click={handleCanvasClick}
        ></canvas>
        <svg 
          bind:this={svgRef} 
          width="800" 
          height="600"
          class="overlay-svg"
        ></svg>
        
      </div>
    </div>
  </div>

  <!-- Data table for selected point -->
  {#if selectedData}
    <div class="data-table-overlay" on:click={() => selectedData = null}>
      <div class="data-table-container" on:click|stopPropagation>
      <h3>Selected Household Data</h3>
      <table class="data-table">
        <tbody>
          {#each Object.entries(selectedData) as [key, value], index}
            {#if key !== 'id' && key !== 'isAnnotated' && key !== 'sectionIndex' && key !== 'isHighlighted' && key !== 'highlightGroup' && key !== 'stateIndex'}
              <tr>
                <td class="key-column">{key}</td>
                <td class="value-column">
                  {#if typeof value === 'number'}
                    {#if key.includes('Income') || key.includes('Taxes') || key.includes('Tax Liability') || key.includes('Benefits') || key.includes('Gains') || key.includes('Interest') || key.includes('Medicaid') || key.includes('ACA') || key.includes('CHIP') || key.includes('SNAP') || key.toLowerCase().includes('change in') && !key.includes('Percentage')}
                      <span id="table-value-{index}">{value < 0 ? '-' : ''}${Math.abs(Math.round(value)).toLocaleString()}</span>
                    {:else if key.includes('Percentage')}
                      <span id="table-value-{index}">{value > 0 ? '+' : ''}{value.toFixed(2)}%</span>
                    {:else if key.includes('ID') || key.includes('Household')}
                      <span id="table-value-{index}">{Math.round(value)}</span>
                    {:else}
                      <span id="table-value-{index}">{Math.round(value).toLocaleString()}</span>
                    {/if}
                  {:else}
                    {value}
                  {/if}
                </td>
              </tr>
            {/if}
          {/each}
        </tbody>
      </table>
        <button class="close-table" on:click={() => selectedData = null}>×</button>
      </div>
    </div>
  {/if}
</div>

<style>
  :root {
    /* PolicyEngine Color Constants */
    --black: #000000;
    --blue-98: #F7FAFD;
    --blue: #2C6496;
    --blue-light: #D8E6F3;
    --blue-pressed: #17354F;
    --dark-blue-hover: #1d3e5e;
    --dark-gray: #616161;
    --dark-red: #b50d0d;
    --darkest-blue: #0C1A27;
    --gray: #808080;
    --light-gray: #F2F2F2;
    --medium-dark-gray: #D2D2D2;
    --medium-light-gray: #BDBDBD;
    --teal-accent: #39C6C0;
    --teal-light: #F7FDFC;
    --teal-medium: #2D9E99;
    --teal-pressed: #227773;
    --white: #FFFFFF;

    /* Application Color Mappings */
    --app-background: var(--white);
    --text-primary: var(--darkest-blue);
    --text-secondary: var(--dark-gray);
    --axis-grid: var(--black);
    --grid-lines: var(--medium-dark-gray);
    --scatter-positive: var(--teal-medium);
    --scatter-negative: var(--dark-gray);
    --scatter-neutral: var(--medium-dark-gray);
    --border: var(--medium-dark-gray);
    --hover: var(--blue-98);
    --font-sans: 'Roboto', sans-serif;
    --font-serif: 'Roboto Serif', serif;
    --font-mono: 'Roboto Mono', monospace;
  }

  /* Typography utility classes */
  .font-serif {
  }

  .font-sans {
    font-family: var(--font-sans);
  }

  .font-mono {
  }

  /* Default typography for common elements */
  h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-sans);
  }

  p, span, div {
    font-family: var(--font-sans);
  }

  .app {
    width: 100%;
    min-height: 100vh;
    background: var(--app-background);
  }

  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.7);
    z-index: 1000;
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

  .main-container {
    display: flex;
    max-width: 1200px;
    margin: 0 auto;
  }

  .text-column {
    flex: 0 0 40%;
    background: var(--app-background);
    height: 100vh;
    overflow-y: auto;
  }

  .viz-column {
    flex: 0 0 60%;
    background: var(--app-background);
  }

  .viz-sticky {
    position: sticky;
    top: 60px;
    height: calc(100vh - 120px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }

  /* Dataset Selector Styles */
  .dataset-selector {
    background: var(--hover);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    margin: 32px 0 16px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    width: fit-content;
    max-width: 100%;
  }

  .selector-header {
    margin-bottom: 16px;
  }

  .selector-header h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 4px 0;
  }

  .selector-header p {
    font-size: 14px;
    color: var(--text-secondary);
    margin: 0;
  }

  .selector-buttons {
    display: flex;
    gap: 8px;
    justify-content: flex-start;
  }

  .dataset-button {
    background: var(--app-background);
    border: 2px solid var(--border);
    border-radius: 6px;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-height: 44px;
    white-space: nowrap;
  }

  .dataset-button:hover:not(:disabled) {
    background: var(--hover);
    border-color: var(--text-secondary);
    color: var(--text-primary);
  }

  .dataset-button.active {
    background: var(--text-primary);
    border-color: var(--text-primary);
    color: var(--app-background);
  }

  .dataset-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .main-canvas {
    background: var(--app-background);
    cursor: crosshair;
  }

  .overlay-svg {
    position: absolute;
    pointer-events: none;
  }

  .text-section {
    min-height: 60vh;
    padding: 60px 40px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid var(--border);
    transition: background-color 0.3s ease;
  }

  .text-section.active {
    background: var(--hover);
  }

  .section-content {
    max-width: 500px;
  }

  .text-section h2 {
    font-size: 1.8rem;
    font-weight: 700;
    line-height: 1.2;
    color: var(--text-primary);
    margin: 0 0 1rem 0;
  }

  .text-section p {
    font-size: 16px;
    line-height: 1.5;
    color: var(--text-secondary);
    margin: 24px 0 0 0;
  }

  .household-profile {
    margin-top: 2rem;
    padding: 1.5rem;
    background: var(--hover);
    border-radius: 8px;
    border: 1px solid var(--border);
  }

  .household-profile h3 {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 1rem 0;
    display: flex;
    align-items: center;
    justify-content: flex-start;
  }

  .household-profile h3 .header-buttons {
    margin-left: auto;
  }

  .header-buttons {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .action-button {
    background: none;
    border: none;
    padding: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    flex-shrink: 0;
    opacity: 0.7;
  }

  .action-button:hover {
    transform: scale(1.2);
    opacity: 1;
  }

  .random-button:hover {
    filter: hue-rotate(180deg) saturate(2);
  }

  .link-button:hover {
    filter: hue-rotate(90deg) saturate(1.5);
  }

  .info-button:hover {
    filter: hue-rotate(-90deg) saturate(1.5);
  }

  .action-button.copied {
    filter: hue-rotate(120deg) saturate(2);
    opacity: 1;
  }

  .action-button:active {
    transform: scale(1.1);
  }

  .household-details {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
  }

  .detail-item .label {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 500;
  }

  .detail-item .value {
    font-size: 13px;
    font-weight: 600;
  }

  .provision-breakdown {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
  }

  .provision-breakdown h4 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 1rem 0;
  }

  .provision-list {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .provision-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.3rem 0;
    font-size: 11px;
  }

  .provision-name {
    color: var(--text-secondary);
    font-weight: 400;
    flex: 1;
    margin-right: 0.5rem;
  }


  .no-provisions {
    font-size: 14px;
    color: var(--text-secondary);
    font-style: italic;
    margin: 0;
  }





  /* Mobile responsive */
  @media (max-width: 768px) {
    .main-container {
      flex-direction: column;
    }
    
    .text-column {
      flex: none;
      order: 2;
    }
    
    .viz-column {
      flex: none;
      order: 1;
    }
    
    .viz-sticky {
      position: relative;
      top: 0;
      height: 50vh;
    }
    
    .dataset-selector {
      padding: 16px;
      margin: 24px 0 12px 0;
    }
    
    .selector-header h3 {
      font-size: 1rem;
    }
    
    .selector-header p {
      font-size: 13px;
    }
    
    .dataset-button {
      padding: 10px 14px;
      font-size: 13px;
      min-height: 40px;
    }
    
    .main-canvas {
      max-width: 100%;
      max-height: 100%;
    }
    
    .text-section {
      min-height: 40vh;
      padding: 2rem 1rem;
    }
    
    .text-section h2 {
      font-size: 1.5rem;
    }
    
    .text-section p {
      font-size: 1rem;
    }
  }

  /* Data table styles */
  .data-table-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.3);
    z-index: 999;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 20px;
  }

  .data-table-container {
    position: relative;
    bottom: unset;
    left: unset;
    transform: unset;
    background: var(--app-background);
    border: 1px solid var(--border);
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    padding: 20px;
    max-width: 500px;
    max-height: 60vh;
    overflow-y: auto;
    z-index: 1000;
  }

  .data-table-container h3 {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 15px 0;
    padding-right: 30px;
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }

  .data-table tr {
    border-bottom: 1px solid var(--grid-lines);
  }

  .data-table tr:last-child {
    border-bottom: none;
  }

  .key-column {
    padding: 8px 12px 8px 0;
    color: var(--text-secondary);
    vertical-align: top;
    font-weight: 500;
    width: 60%;
  }

  .value-column {
    padding: 8px 0;
    color: var(--text-primary);
    font-weight: 600;
    text-align: right;
  }

  .close-table {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 20px;
    color: var(--text-secondary);
    cursor: pointer;
    width: 25px;
    height: 25px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.2s;
  }

  .close-table:hover {
    background-color: var(--hover);
    color: var(--text-primary);
  }

  /* Mobile responsive for data table */
  @media (max-width: 768px) {
    .data-table-overlay {
      align-items: flex-end;
      padding-bottom: 0;
    }

    .data-table-container {
      position: relative;
      bottom: 0;
      left: 0;
      right: 0;
      width: 100%;
      max-width: none;
      border-radius: 8px 8px 0 0;
      max-height: 50vh;
    }

    .data-table {
      font-size: 11px;
    }

    .key-column {
      width: 55%;
    }

    .loading-content p {
      font-size: 13px;
    }
  }

  /* Floating header styles */
  .floating-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: var(--app-background);
    border-bottom: 1px solid var(--border);
    z-index: 100;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    max-width: 1400px;
    margin: 0 auto;
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

  /* Use monospace for data/numbers */
  .data-table,
  .value-column,
  .key-column,
  .detail-item .value,
  .provision-breakdown,
  .provision-breakdown .provision-name,
  .provision-breakdown .value,
  .household-details,
  .household-details .label,
  .household-details .value,
  .household-profile h3,
  .household-profile h3 span,
  .provision-breakdown h4 {
    font-family: var(--font-mono) !important;
  }

  /* Shared value styles for consistent number alignment */
  .value {
    font-family: "Roboto", sans-serif;
    font-variant-numeric: tabular-nums lining-nums;
    text-align: right;
    white-space: nowrap;
    letter-spacing: 0;   /* overrides global headings */
    word-spacing: normal;
  }

  /* Color logic for positive/negative/zero values */
  .value.pos { color: var(--teal-medium); }
  .value.neg { color: var(--dark-gray); }

  /* Align sign + currency + digits as one block */
  .value > span { display: inline-block; }

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
    color: var(--policyengine-blue);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  }

  .tab-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Adjust main container for header */
  .main-container {
    padding-top: 70px; /* Account for fixed header */
  }

  /* Mobile responsive header */
  @media (max-width: 768px) {
    .header-content {
      padding: 12px 16px;
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

    .main-container {
      padding-top: 100px; /* More space for stacked header */
    }
  }


</style>