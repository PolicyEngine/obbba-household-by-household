<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto, afterNavigate } from '$app/navigation';
  import { browser } from '$app/environment';
  import { base } from '$app/paths';
  import { districtDatasets } from '$lib/config/datasets.js';
  import ExplorerLayout from '$lib/components/ExplorerLayout.svelte';
  import ScatterPlot from '$lib/components/ScatterPlot.svelte';
  import HouseholdProfile from '$lib/components/HouseholdProfile.svelte';
  import { COLORS } from '$lib/config/colors.js';
  import { getRandomWeightedHousehold } from '$lib/navigation/scrollHandler.js';

  // Data state
  let data = [];
  let isLoading = false;
  let loadError = null;
  let selectedDataset = 'obbba-vs-current-policy';
  let selectedDistrict = null;
  let selectedHousehold = null;

  // Provision impacts data
  let provisionImpacts = {};
  let provisionImpactsLoaded = false;

  // Chart reference
  let chartComponent = null;

  // Y-axis scale control (logarithmic slider)
  let yAxisMax = 500000; // Default 500k
  const yAxisMin = 50000; // $50K minimum
  const yAxisMaxLimit = 10000000; // $10M maximum

  // Format value for display
  function formatYAxisValue(value) {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`.replace('.0M', 'M');
    }
    return `$${Math.round(value / 1000)}K`;
  }

  // Convert slider position (0-100) to actual value (logarithmic)
  function sliderToValue(sliderPos) {
    const minLog = Math.log(yAxisMin);
    const maxLog = Math.log(yAxisMaxLimit);
    const scale = (maxLog - minLog) / 100;
    return Math.round(Math.exp(minLog + scale * sliderPos));
  }

  // Convert actual value to slider position (0-100)
  function valueToSlider(value) {
    const minLog = Math.log(yAxisMin);
    const maxLog = Math.log(yAxisMaxLimit);
    return ((Math.log(value) - minLog) / (maxLog - minLog)) * 100;
  }

  // Reactive slider position
  $: sliderPosition = valueToSlider(yAxisMax);

  function handleSliderChange(event) {
    yAxisMax = sliderToValue(parseFloat(event.target.value));
  }

  // Simple scroll states for the explorer view (reactive to yAxisMax)
  $: explorerScrollStates = [
    {
      id: 'all',
      title: 'All Households',
      filter: () => true,
      xDomain: [-20, 20],
      yDomain: [0, yAxisMax],
      viewType: 'all'
    }
  ];

  // Generate mock data for testing
  function generateMockData(count = 5000) {
    const states = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI'];
    const mockData = [];

    // Congressional districts by state (simplified)
    const districtsByState = {
      CA: 52,
      TX: 38,
      FL: 28,
      NY: 26,
      PA: 17,
      IL: 17,
      OH: 15,
      GA: 14,
      NC: 14,
      MI: 13
    };

    const stateFips = {
      CA: 6,
      TX: 48,
      FL: 12,
      NY: 36,
      PA: 42,
      IL: 17,
      OH: 39,
      GA: 13,
      NC: 37,
      MI: 26
    };

    for (let i = 0; i < count; i++) {
      const state = states[Math.floor(Math.random() * states.length)];
      const numDistricts = districtsByState[state];
      const districtNum = Math.floor(Math.random() * numDistricts) + 1;
      const fips = stateFips[state];
      const congressionalDistrict = fips * 100 + districtNum;

      // Generate realistic income and tax change values
      const income = Math.exp(Math.random() * 4 + 9); // Log-normal distribution, roughly $8k - $500k
      const baseChange = (Math.random() - 0.4) * 10; // Slightly positive bias
      const incomeEffect = income > 200000 ? -2 : income < 50000 ? 1.5 : 0;
      const percentChange = baseChange + incomeEffect + (Math.random() - 0.5) * 3;

      mockData.push({
        id: i + 1,
        'Household ID': i + 1,
        State: state,
        'Congressional District': congressionalDistrict,
        'Market Income': Math.round(income),
        'Gross Income': Math.round(income * 1.1),
        'Household Weight': Math.round(Math.random() * 5000 + 500),
        'Percentage change in net income': Math.round(percentChange * 100) / 100,
        'Total change in net income': Math.round((percentChange * income) / 100),
        'Household Size': Math.floor(Math.random() * 4) + 1,
        'Number of Dependents': Math.floor(Math.random() * 3),
        'Age of Head': Math.floor(Math.random() * 50) + 25
      });
    }

    return mockData;
  }

  // Dataset folder mapping
  const datasetFolders = {
    'obbba-vs-current-policy': 'districts/tcja-expiration',
    'obbba-vs-current-law': 'districts/tcja-extension'
  };

  // Provision impacts file mapping
  const provisionFiles = {
    'obbba-vs-current-policy': 'provision_impacts.json',
    'obbba-vs-current-law': 'provision_impacts_current_law.json'
  };

  // Provision descriptions for tooltips
  const provisionDescriptions = {
    'Tax Rate Reform':
      'Permanently extends TCJA individual tax rates, including the 37% top rate. Rates are 10%, 12%, 22%, 24%, 32%, 35%, and 37%.',
    'Standard Deduction Reform':
      'Increases the standard deduction by $750 for single filers and $1,500 for married filing jointly, building on the TCJA amounts.',
    'Exemption Reform':
      "Continues TCJA's repeal of personal exemptions, which were $4,050 per person before 2018.",
    'CTC SSN Requirement':
      'Requires work-eligible SSNs for both the child and at least one parent claiming the credit. Affects mixed-status families.',
    'CTC Expansion':
      'Increases child tax credit from $2,000 to $2,200 per child, with inflation indexing starting in 2026. Refundable portion remains at $1,700.',
    'CDCC Reform':
      'Modifies child and dependent care credit structure and income phaseouts. Credit remains nonrefundable.',
    'QBI Deduction Reform':
      'Makes permanent the 20% deduction for pass-through entities. Expands phase-in limits to $75,000 ($150,000 joint) with $400 minimum deduction.',
    'AMT Reform':
      'AMT exemption: $88,100 (single)/$137,000 (joint) for 2025. Starting 2026: phaseout at $500K/$1M with 50% phaseout rate.',
    'Miscellaneous Reform':
      'Continues suspension of miscellaneous itemized deductions subject to 2% AGI floor, including unreimbursed employee expenses.',
    'Casualty Loss Repeal':
      'Continues limitation of casualty loss deductions to federally declared disaster areas only.',
    'Other Itemized Deductions Reform':
      'Charitable deduction for non-itemizers ($2,000/$1,000) and mortgage interest cap ($750K).',
    'Limitation on Itemized Deductions Reform':
      'New limitation caps itemized deduction benefit at 35% of taxable income for taxpayers in 37% bracket.',
    'Estate Tax Reform':
      'Increases estate and gift tax exemption to $15 million per person ($30 million per couple), indexed for inflation.',
    'SALT Cap Reform':
      'SALT deduction cap increases to $40,000 for taxpayers earning under $500,000, indexed annually. Reverts to $10,000 in 2030.',
    'Tip Income Exemption':
      'Deduction up to $25,000 for tip income, 2025-2028. Tips remain reportable income but receive federal tax deduction.',
    'Overtime Exemption':
      'Deduction for overtime premium pay (the extra 50% only, not base wage) up to $12,500 for individuals or $25,000 for joint filers, 2025-2028.',
    'Senior Deduction':
      'New $6,000 deduction for taxpayers age 65+, available 2025-2028. Reduces taxable income regardless of itemization.',
    'Auto Loan Interest':
      'Deduction up to $10,000 for auto loan interest, 2025-2028. Applies to qualifying vehicle loans.',
    'SNAP Takeup Reform': 'Reduced-form scenario for projected changes in SNAP participation.',
    'ACA Takeup Reform':
      'Reduced-form scenario for projected changes in marketplace participation and premium tax credits.',
    'Medicaid Takeup Reform':
      'Reduced-form scenario for projected changes in Medicaid participation.'
  };

  // Cache for loaded district data
  let districtDataCache = {};

  // Load provision impacts data
  async function loadProvisionImpacts() {
    const filename = provisionFiles[selectedDataset];
    if (!filename) return;

    try {
      const basePath = import.meta.env.BASE_URL || '/';
      const normalizedBase = basePath.endsWith('/') ? basePath : basePath + '/';
      const url = `${normalizedBase}${filename}`;

      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to load provision impacts');

      provisionImpacts = await response.json();
      provisionImpactsLoaded = true;
      console.log(
        'Loaded provision impacts for',
        Object.keys(provisionImpacts).length,
        'districts'
      );
    } catch (error) {
      console.error('Error loading provision impacts:', error);
      provisionImpacts = {};
    }
  }

  // Provision panel state
  let provisionExpanded = false;
  let showRelativeImpact = false; // false = absolute ($), true = relative (%)

  // Get provisions for selected district, separated by positive/negative
  $: allProvisions =
    selectedDistrict && provisionImpacts[selectedDistrict]
      ? provisionImpacts[selectedDistrict]
      : [];

  $: positiveProvisions = allProvisions.filter((p) => p.avgImpact > 0);
  $: negativeProvisions = allProvisions.filter((p) => p.avgImpact < 0);

  // Show top 3 of each when collapsed, all when expanded
  $: displayPositive = provisionExpanded ? positiveProvisions : positiveProvisions.slice(0, 3);
  $: displayNegative = provisionExpanded ? negativeProvisions : negativeProvisions.slice(0, 3);

  // Check if there are more to show
  $: hasMoreProvisions = positiveProvisions.length > 3 || negativeProvisions.length > 3;

  // Load data for a specific district (on-demand)
  async function loadDistrictData(district) {
    if (!district) {
      data = [];
      return;
    }

    const cacheKey = `${selectedDataset}_${district}`;
    if (districtDataCache[cacheKey]) {
      data = districtDataCache[cacheKey];
      console.log(`Using cached data for district ${district}: ${data.length} households`);
      return;
    }

    isLoading = true;
    loadError = null;

    try {
      const folder = datasetFolders[selectedDataset];
      if (!folder) {
        throw new Error(`Unknown dataset: ${selectedDataset}`);
      }

      const basePath = import.meta.env.BASE_URL || '/';
      const normalizedBase = basePath.endsWith('/') ? basePath : basePath + '/';
      const url = `${normalizedBase}${folder}/district_${district}.csv`;

      console.log('Loading district data from:', url);
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`District ${district} data not available`);
      }

      const text = await response.text();
      console.log('CSV loaded, size:', (text.length / 1024 / 1024).toFixed(1), 'MB');
      const parsed = parseCSV(text);

      data = parsed;
      districtDataCache[cacheKey] = data;

      console.log(`Loaded ${data.length} households for district ${district}`);
    } catch (error) {
      console.error('Error loading district data:', error);
      loadError = error.message;
      data = [];
    } finally {
      isLoading = false;
    }
  }

  // Simple CSV parser
  function parseCSV(text) {
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',');
    const data = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      const row = {};

      headers.forEach((header, idx) => {
        const val = values[idx];
        // Try to parse as number
        const num = parseFloat(val);
        row[header.trim()] = isNaN(num) ? val : num;
      });

      // Add unique ID if not present
      if (!row.id) {
        row.id = row['Household ID'] || i;
      }

      data.push(row);
    }

    return data;
  }

  // Handle district selection - load data on-demand
  async function handleDistrictChange(event) {
    const newDistrict = event.detail.district;

    // Clear selected household and reset provision panel when changing districts
    selectedHousehold = null;
    provisionExpanded = false;

    // Update URL
    const url = new URL(window.location.href);
    if (newDistrict) {
      url.searchParams.set('district', newDistrict);
    } else {
      url.searchParams.delete('district');
    }
    goto(url.pathname + url.search, { replaceState: true, noScroll: true });

    // Update selected district and load data
    selectedDistrict = newDistrict;
    await loadDistrictData(newDistrict);
  }

  // Handle point click
  function handlePointClick(household) {
    selectedHousehold = household;
  }

  // Close household profile
  function closeProfile() {
    selectedHousehold = null;
  }

  // Randomize to a different household
  function randomizeHousehold() {
    const currentData = selectedDistrict
      ? data.filter((d) => d['Congressional District'] === selectedDistrict)
      : data;

    selectedHousehold = getRandomWeightedHousehold(currentData);
  }

  // Parse URL params on load
  function parseUrlParams() {
    const params = $page.url.searchParams;

    const district = params.get('district');
    if (district) {
      selectedDistrict = parseInt(district, 10);
    } else {
      selectedDistrict = null; // Reset if no district in URL
    }

    const dataset = params.get('dataset');
    if (dataset && districtDatasets[dataset]) {
      selectedDataset = dataset;
    }
  }

  // Load data on mount (only if district is in URL)
  onMount(async () => {
    parseUrlParams();
    await loadProvisionImpacts();
    if (selectedDistrict) {
      await loadDistrictData(selectedDistrict);
    }
  });

  // Reload provision impacts when dataset changes
  $: if (browser && selectedDataset) {
    loadProvisionImpacts();
  }

  // Re-render chart when data changes
  $: if (chartComponent && data.length > 0) {
    setTimeout(() => chartComponent.renderVisualization(), 50);
  }

  // Re-render chart when y-axis scale changes
  $: if (chartComponent && data.length > 0 && yAxisMax) {
    setTimeout(() => chartComponent.forceRender(), 50);
  }
</script>

<svelte:head>
  <title>Explore by District | Tax Reform Impact</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    rel="stylesheet"
  />
</svelte:head>

<div class="explore-page">
  <!-- Header -->
  <header class="header">
    <div class="header-left">
      <a href="{base}/" class="back-link">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path
            d="M12.5 15L7.5 10L12.5 5"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
        Back to Story
      </a>
      <h1 class="page-title">Explore by Congressional District</h1>
    </div>
  </header>

  <!-- Y-axis slider (bottom left) -->
  <div class="controls-overlay left">
    <div class="control-group slider-group">
      <span class="control-label">Y-Axis Max:</span>
      <div class="slider-container">
        <input
          type="range"
          class="scale-slider"
          min="0"
          max="100"
          step="1"
          value={sliderPosition}
          on:input={handleSliderChange}
        />
        <span class="slider-value">{formatYAxisValue(yAxisMax)}</span>
      </div>
    </div>
  </div>

  <!-- Baseline selector (bottom right) -->
  <div class="controls-overlay right">
    <div class="control-group">
      <span class="control-label">Baseline:</span>
      <div class="baseline-selector">
        {#each Object.entries(districtDatasets) as [key, config]}
          <button
            class="tab-button"
            class:active={selectedDataset === key}
            on:click={async () => {
              selectedDataset = key;
              // Reload data for current district with new baseline
              if (selectedDistrict) {
                await loadDistrictData(selectedDistrict);
              }
            }}
          >
            {config.label}
          </button>
        {/each}
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <main class="main-content">
    {#if loadError && !selectedDistrict}
      <div class="error-state">
        <p>Error: {loadError}</p>
      </div>
    {:else}
      <ExplorerLayout
        dataset={selectedDataset}
        bind:selectedDistrict
        on:districtChange={handleDistrictChange}
      >
        <div slot="scatter" class="scatter-wrapper">
          {#if isLoading}
            <div class="loading-state">
              <div class="spinner"></div>
              <p>Loading district data...</p>
            </div>
          {:else if selectedDistrict && data.length > 0}
            <ScatterPlot
              bind:this={chartComponent}
              {data}
              scrollStates={explorerScrollStates}
              currentStateIndex={0}
              previousStateIndex={0}
              isTransitioning={false}
              interpolationT={1}
              randomHouseholds={{}}
              {selectedHousehold}
              onPointClick={handlePointClick}
            />
            <!-- Provision impacts panel -->
            {#if allProvisions.length > 0}
              <div class="provision-panel">
                <div class="provision-header">
                  <h3>Provision Impacts</h3>
                  <div class="impact-toggle">
                    <button
                      class="toggle-btn"
                      class:active={!showRelativeImpact}
                      on:click={() => (showRelativeImpact = false)}>$</button
                    >
                    <button
                      class="toggle-btn"
                      class:active={showRelativeImpact}
                      on:click={() => (showRelativeImpact = true)}>%</button
                    >
                  </div>
                </div>

                <!-- Positive impacts (gains) -->
                {#if displayPositive.length > 0}
                  <div class="provision-section">
                    <div class="section-header positive">
                      <span class="section-icon">▲</span>
                      <span class="section-title">Gains</span>
                    </div>
                    <div class="provision-list">
                      {#each displayPositive as provision}
                        <div class="provision-item">
                          <span class="provision-name">{provision.shortName}</span>
                          <span class="provision-value positive">
                            {#if showRelativeImpact}
                              +{provision.avgRelativeImpact.toFixed(2)}%
                            {:else}
                              +${Math.round(provision.avgImpact).toLocaleString()}
                            {/if}
                          </span>
                          {#if provisionDescriptions[provision.name]}
                            <div class="provision-tooltip">
                              {provisionDescriptions[provision.name]}
                            </div>
                          {/if}
                        </div>
                      {/each}
                    </div>
                  </div>
                {/if}

                <!-- Negative impacts (losses) -->
                {#if displayNegative.length > 0}
                  <div class="provision-section">
                    <div class="section-header negative">
                      <span class="section-icon">▼</span>
                      <span class="section-title">Losses</span>
                    </div>
                    <div class="provision-list">
                      {#each displayNegative as provision}
                        <div class="provision-item">
                          <span class="provision-name">{provision.shortName}</span>
                          <span class="provision-value negative">
                            {#if showRelativeImpact}
                              {provision.avgRelativeImpact.toFixed(2)}%
                            {:else}
                              −${Math.round(Math.abs(provision.avgImpact)).toLocaleString()}
                            {/if}
                          </span>
                          {#if provisionDescriptions[provision.name]}
                            <div class="provision-tooltip">
                              {provisionDescriptions[provision.name]}
                            </div>
                          {/if}
                        </div>
                      {/each}
                    </div>
                  </div>
                {/if}

                <!-- Expand/collapse button -->
                {#if hasMoreProvisions}
                  <button
                    class="expand-btn"
                    on:click={() => (provisionExpanded = !provisionExpanded)}
                  >
                    {provisionExpanded ? 'Show less' : `Show all (${allProvisions.length})`}
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 12 12"
                      class:rotated={provisionExpanded}
                    >
                      <path
                        d="M3 4.5L6 7.5L9 4.5"
                        stroke="currentColor"
                        stroke-width="1.5"
                        fill="none"
                        stroke-linecap="round"
                      />
                    </svg>
                  </button>
                {/if}

                <p class="provision-note">
                  {showRelativeImpact
                    ? 'Avg. % change in net income'
                    : 'Avg. $ impact per household'}
                </p>
              </div>
            {/if}
          {:else}
            <div class="select-district-prompt">
              <div class="prompt-icon">
                <svg
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                >
                  <path d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                  <path
                    d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z"
                  />
                </svg>
              </div>
              <h2>Select a Congressional District</h2>
              <p>Click on a district in the map to explore household-level impacts</p>
            </div>
          {/if}
        </div>
      </ExplorerLayout>
    {/if}
  </main>

  <!-- Household Profile Modal -->
  {#if selectedHousehold}
    <div class="profile-overlay" on:click={closeProfile}>
      <div class="profile-modal" on:click|stopPropagation>
        <button class="close-btn" on:click={closeProfile}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M18 6L6 18M6 6L18 18"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
        </button>
        <HouseholdProfile
          household={selectedHousehold}
          {selectedDataset}
          onRandomize={randomizeHousehold}
        />
      </div>
    </div>
  {/if}
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family:
      'Inter',
      -apple-system,
      BlinkMacSystemFont,
      sans-serif;
    background: #f8fafc;

    /* Scatter plot colors - match nationwide styling */
    --scatter-positive: #319795; /* Teal for gains */
    --scatter-negative: #6b7280; /* Gray for losses */
  }

  .explore-page {
    display: flex;
    flex-direction: column;
    height: calc(100vh - var(--pe-shell-height, 0px));
    overflow: hidden;
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 24px;
    background: #fff;
    border-bottom: 1px solid #e2e8f0;
    flex-shrink: 0;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .back-link {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #64748b;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: color 0.15s ease;
  }

  .back-link:hover {
    color: #319795;
  }

  .page-title {
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }

  /* Controls overlay */
  .controls-overlay {
    position: fixed;
    bottom: 2rem;
    z-index: 20;
    display: flex;
    align-items: center;
    gap: 24px;
  }

  .controls-overlay.left {
    left: 2rem;
  }

  .controls-overlay.right {
    right: 2rem;
  }

  .control-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .control-label {
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
    font-family: 'Inter', sans-serif;
  }

  .slider-group {
    background: rgba(255, 255, 255, 0.9);
    padding: 8px 12px;
    border-radius: 6px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(226, 232, 240, 0.5);
  }

  .slider-container {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .scale-slider {
    width: 120px;
    height: 6px;
    -webkit-appearance: none;
    appearance: none;
    background: #e2e8f0;
    border-radius: 3px;
    cursor: pointer;
  }

  .scale-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    background: #319795;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transition: transform 0.1s ease;
  }

  .scale-slider::-webkit-slider-thumb:hover {
    transform: scale(1.1);
  }

  .scale-slider::-moz-range-thumb {
    width: 18px;
    height: 18px;
    background: #319795;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .scale-slider:focus {
    outline: none;
  }

  .slider-value {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: #319795;
    min-width: 55px;
    text-align: right;
  }

  .baseline-selector {
    display: flex;
    gap: 8px;
  }

  .tab-button {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(226, 232, 240, 0.5);
    color: #64748b;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
    font-family: 'Inter', sans-serif;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .tab-button:hover:not(.active) {
    background: rgba(255, 255, 255, 1);
    border-color: #cbd5e1;
  }

  .tab-button.active {
    background: #319795;
    color: white;
    border-color: #319795;
    box-shadow: 0 2px 8px rgba(49, 151, 149, 0.3);
  }

  .main-content {
    flex: 1;
    overflow: hidden;
    min-height: 0; /* Important for nested flex containers */
  }

  .main-content > :global(*) {
    height: 100%;
  }

  .scatter-wrapper {
    width: 100%;
    height: 100%;
    position: relative;
  }

  /* Provision impacts panel */
  .provision-panel {
    position: absolute;
    top: 60px;
    right: 16px;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 10;
    min-width: 200px;
    max-height: calc(100vh - 200px);
    overflow-y: auto;
  }

  .provision-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .provision-panel h3 {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0;
  }

  .impact-toggle {
    display: flex;
    gap: 2px;
    background: #e2e8f0;
    border-radius: 4px;
    padding: 2px;
  }

  .toggle-btn {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 10px;
    border: none;
    border-radius: 3px;
    background: transparent;
    color: #64748b;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .toggle-btn:hover:not(.active) {
    background: rgba(255, 255, 255, 0.5);
  }

  .toggle-btn.active {
    background: white;
    color: #319795;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }

  .provision-section {
    margin-bottom: 12px;
  }

  .provision-section:last-of-type {
    margin-bottom: 8px;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 1px solid #e2e8f0;
  }

  .section-icon {
    font-size: 10px;
  }

  .section-header.positive .section-icon {
    color: #319795;
  }

  .section-header.negative .section-icon {
    color: #6b7280;
  }

  .section-title {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }

  .section-header.positive .section-title {
    color: #319795;
  }

  .section-header.negative .section-title {
    color: #6b7280;
  }

  .provision-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .provision-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    position: relative;
  }

  .provision-name {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: #334155;
    cursor: help;
    text-decoration: underline;
    text-decoration-style: dotted;
    text-underline-offset: 2px;
    text-decoration-thickness: 1px;
    text-decoration-color: #94a3b8;
  }

  .provision-name:hover {
    text-decoration-color: #334155;
  }

  .provision-tooltip {
    position: absolute;
    left: 0;
    right: 0;
    top: 100%;
    margin-top: 6px;
    padding: 10px 12px;
    background: rgba(24, 35, 51, 0.98);
    color: white;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    line-height: 1.5;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    z-index: 100;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-4px);
    transition: all 0.15s ease;
    pointer-events: none;
  }

  .provision-tooltip::before {
    content: '';
    position: absolute;
    top: -5px;
    left: 12px;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 5px solid rgba(24, 35, 51, 0.98);
  }

  .provision-item:hover .provision-tooltip {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
  }

  .provision-value {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
  }

  .provision-value.positive {
    color: #319795;
  }

  .provision-value.negative {
    color: #6b7280;
  }

  .expand-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    width: 100%;
    padding: 6px 8px;
    margin-top: 8px;
    background: #f1f5f9;
    border: none;
    border-radius: 4px;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 500;
    color: #64748b;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .expand-btn:hover {
    background: #e2e8f0;
    color: #475569;
  }

  .expand-btn svg {
    transition: transform 0.2s ease;
  }

  .expand-btn svg.rotated {
    transform: rotate(180deg);
  }

  .provision-note {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    color: #94a3b8;
    margin: 8px 0 0 0;
    text-align: center;
  }

  .select-district-prompt {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 16px;
    color: #64748b;
    text-align: center;
    padding: 40px;
  }

  .select-district-prompt .prompt-icon {
    color: #cbd5e1;
  }

  .select-district-prompt h2 {
    font-size: 20px;
    font-weight: 600;
    color: #334155;
    margin: 0;
  }

  .select-district-prompt p {
    font-size: 14px;
    color: #64748b;
    margin: 0;
    max-width: 300px;
  }

  .loading-state,
  .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 16px;
    color: #64748b;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e2e8f0;
    border-top-color: #319795;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .error-state button {
    padding: 8px 16px;
    background: #319795;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
  }

  /* Profile Modal */
  .profile-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .profile-modal {
    position: relative;
    background: #fff;
    border-radius: 12px;
    width: 90vw;
    max-width: 650px;
    max-height: 85vh;
    overflow: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    padding: 8px;
  }

  .close-btn {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f1f5f9;
    border: none;
    border-radius: 6px;
    color: #64748b;
    cursor: pointer;
    z-index: 1;
  }

  .close-btn:hover {
    background: #e2e8f0;
    color: #334155;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .header {
      padding: 12px 16px;
    }

    .header-left {
      width: 100%;
      justify-content: space-between;
    }

    .page-title {
      font-size: 16px;
    }

    .controls-overlay {
      bottom: 1rem;
      flex-direction: column;
      gap: 12px;
    }

    .controls-overlay.left {
      left: 1rem;
      align-items: flex-start;
    }

    .controls-overlay.right {
      right: 1rem;
      align-items: flex-end;
    }

    .control-group {
      flex-direction: column;
      gap: 4px;
    }

    .controls-overlay.left .control-group {
      align-items: flex-start;
    }

    .controls-overlay.right .control-group {
      align-items: flex-end;
    }

    .control-label {
      font-size: 12px;
    }

    .provision-panel {
      top: auto;
      bottom: 80px;
      right: 8px;
      left: 8px;
      min-width: auto;
      max-height: 50vh;
      padding: 10px 12px;
    }

    .provision-panel h3 {
      font-size: 11px;
    }

    .section-header {
      margin-bottom: 4px;
      padding-bottom: 3px;
    }

    .section-icon {
      font-size: 9px;
    }

    .section-title {
      font-size: 10px;
    }

    .provision-name,
    .provision-value {
      font-size: 12px;
    }

    .expand-btn {
      font-size: 11px;
      padding: 5px 6px;
    }

    .provision-tooltip {
      font-size: 12px;
      padding: 10px 14px;
      max-width: 280px;
    }

    .slider-group {
      padding: 6px 10px;
    }

    .scale-slider {
      width: 80px;
    }

    .slider-value {
      font-size: 12px;
      min-width: 45px;
    }

    .baseline-selector {
      flex-direction: column;
      gap: 6px;
    }

    .tab-button {
      font-size: 12px;
      padding: 6px 12px;
    }
  }
</style>
