<script>
  import { formatCurrency, formatDollarChange, formatPercentage } from '../utils/formatting.js';
  import { copyHouseholdUrl } from '../utils/clipboard.js';
  import { onMount, onDestroy } from 'svelte';
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';
  
  // Custom interpolation function for train station board effect
  function trainStationInterpolate(from, to) {
    return (t) => {
      // Add random digits during transition for shuffling effect
      if (t < 0.7) {
        const progress = from + (to - from) * t;
        const randomOffset = (Math.random() - 0.5) * Math.abs(to - from) * 0.5;
        return progress + randomOffset;
      }
      // Settle on the actual value
      return from + (to - from) * t;
    };
  }
  
  export let household = null;
  export let selectedDataset = 'tcja-expiration';
  export let currentState = null;
  export let sectionIndex = 0;
  export let onRandomize = () => {};
  
  let showHouseholdDetails = false;
  let showProvisionDetails = false;
  
  // Animated values with train station board effect
  const householdId = tweened(0, { 
    duration: 600, 
    easing: cubicOut,
    interpolate: trainStationInterpolate
  });
  const marketIncome = tweened(0, { 
    duration: 700, 
    easing: cubicOut,
    interpolate: trainStationInterpolate
  });
  const baselineNetIncome = tweened(0, { 
    duration: 750, 
    easing: cubicOut,
    interpolate: trainStationInterpolate
  });
  const obbbaNetIncome = tweened(0, { 
    duration: 800, 
    easing: cubicOut,
    interpolate: trainStationInterpolate
  });
  const absoluteImpact = tweened(0, { 
    duration: 850, 
    easing: cubicOut,
    interpolate: trainStationInterpolate
  });
  const relativeImpact = tweened(0, { 
    duration: 900, 
    easing: cubicOut,
    interpolate: trainStationInterpolate
  });
  
  let previousHouseholdId = null;
  let previousDataset = null;
  
  // Update animated values when household changes or dataset changes
  $: if (household && (household.id !== previousHouseholdId || selectedDataset !== previousDataset)) {
    console.log('HouseholdProfile updating:', {
      householdId: household.id,
      dataset: selectedDataset,
      netChange: household['Total change in net income'] || household['Change in Household Net Income'],
      percentChange: household['Percentage change in net income'],
      baselineNetIncome: household['Baseline Net Income'],
      marketIncome: household['Market Income'] || household['Gross Income'],
      allKeys: Object.keys(household).filter(k => k.includes('Income') || k.includes('Net'))
    });
    
    // Don't reset expanded states when just shuffling households
    // Only reset when switching datasets
    if (selectedDataset !== previousDataset) {
      showHouseholdDetails = false;
      showProvisionDetails = false;
    }
    
    previousHouseholdId = household.id;
    previousDataset = selectedDataset;
    
    // If this is the first household, start from random values for dramatic effect
    if ($householdId === 0) {
      householdId.set(Math.random() * 40000, { duration: 0 });
      marketIncome.set(Math.random() * 200000, { duration: 0 });
      baselineNetIncome.set(Math.random() * 150000, { duration: 0 });
      obbbaNetIncome.set(Math.random() * 150000, { duration: 0 });
      absoluteImpact.set((Math.random() - 0.5) * 20000, { duration: 0 });
      relativeImpact.set((Math.random() - 0.5) * 20, { duration: 0 });
    }
    
    // Animate to actual values
    householdId.set(parseInt(household.id) || 0);
    marketIncome.set(household['Market Income'] || household['Gross Income'] || 0);
    baselineNetIncome.set(household['Baseline Net Income'] || 0);
    obbbaNetIncome.set((household['Baseline Net Income'] || 0) + (household['Total change in net income'] || household['Change in Household Net Income'] || 0));
    absoluteImpact.set(household['Total change in net income'] || household['Change in Household Net Income'] || 0);
    relativeImpact.set(household['Percentage change in net income'] || 0);
  }
  
  // State abbreviation to full name mapping
  const stateNames = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
  };
  
  // Get ages of all household members
  function getHouseholdAges(household) {
    if (!household) return '';
    const ages = [];
    
    // Add head age
    const headAge = household['Age of Head'] || household['Age'];
    if (headAge) ages.push(Math.round(headAge));
    
    // Add spouse age if married
    if (household['Is Married'] && household['Age of spouse']) {
      ages.push(Math.round(household['Age of spouse']));
    }
    
    // Add individual dependent ages
    const numDependents = Math.round(household['Number of Dependents'] || household['Dependents'] || 0);
    if (numDependents > 0) {
      // Check for individual dependent ages
      for (let i = 1; i <= numDependents; i++) {
        const depAge = household[`Age of dependent ${i}`];
        if (depAge && depAge > 0) {
          ages.push(Math.round(depAge));
        }
      }
    }
    
    // Sort ages in descending order
    ages.sort((a, b) => b - a);
    
    return ages.join(', ');
  }
  
  // Get all non-zero fields from household data
  function getNonZeroFields(household) {
    if (!household) return [];
    
    const excludeFields = ['id', 'isAnnotated', 'sectionIndex', 'isHighlighted', 'highlightGroup', 'stateIndex', 'householdId'];
    const fields = [];
    
    Object.entries(household).forEach(([key, value]) => {
      if (!excludeFields.includes(key) && value !== 0 && value !== '0' && value) {
        // Group provisions by reform name
        if (key.includes(' after ')) {
          const match = key.match(/after (.+)$/);
          const reformName = match ? match[1] : key;
          fields.push({ key, value, type: 'provision', reformName });
        } else {
          fields.push({ key, value, type: 'basic' });
        }
      }
    });
    
    // Sort provisions by absolute value of net income impact
    const provisions = fields.filter(f => f.type === 'provision' && f.key.includes('Net income'));
    const sortedProvisions = provisions.sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
    
    // Return organized data
    return {
      basic: fields.filter(f => f.type === 'basic'),
      provisions: sortedProvisions
    };
  }
  
  // Get provision breakdown for a household
  function getProvisionBreakdown(household) {
    if (!household) return [];
    
    const provisions = [
      { name: 'Rate adjustment', key: 'Change in Net income after Rate adjustments' },
      { name: 'Standard deduction increase', key: 'Change in Net income after Standard deduction increase' },
      { name: 'Exemption repeal', key: 'Change in Net income after Exemption repeal' },
      { name: 'Child tax credit social security number requirement', key: 'Change in Net income after Child tax credit social security number requirement' },
      { name: 'Child tax credit expansion', key: 'Change in Net income after Child tax credit expansion' },
      { name: 'Qualified Business Income Deduction Reform', key: 'Change in Net income after Qualified business interest deduction reform' },
      { name: 'Alternative minimum tax reform', key: 'Change in Net income after Alternative minimum tax reform' },
      { name: 'Miscellaneous deduction reform', key: 'Change in Net income after Miscellaneous deduction reform' },
      { name: 'Charitable deductions reform', key: 'Change in Net income after Charitable deductions reform' },
      { name: 'Casualty loss deduction repeal', key: 'Change in Net income after Casualty loss deduction repeal' },
      { name: 'Pease repeal', key: 'Change in Net income after Pease repeal' },
      { name: 'Limitation on itemized deductions reform', key: 'Change in Net income after Limitation on itemized deductions reform' },
      { name: 'Estate tax reform', key: 'Change in Net income after Estate tax reform' },
      { name: 'New senior deduction', key: 'Change in Net income after New senior deduction' },
      { name: 'Tip exemption', key: 'Change in Net income after Tip exemption' },
      { name: 'Overtime exemption', key: 'Change in Net income after Overtime exemption' },
      { name: 'Auto loan interest deduction', key: 'Change in Net income after Auto loan interest deduction' },
      { name: 'Cap on State and Local Tax Deduction', key: 'Change in Net income after Cap on state and local tax deduction' },
      { name: 'Child and Dependent Care Credit Reform', key: 'Change in Net income after Child and dependent care credit reform' },
      { name: 'Extension of ACA enhanced subsidies', key: 'Change in Net income after Extension of ACA enhanced subsidies' },
      { name: 'SNAP reform', key: 'Change in Net income after SNAP reform' },
      { name: 'Medicaid reform', key: 'Change in Net income after Medicaid reform' }
    ];
    
    return provisions
      .map((provision, index) => ({
        name: provision.name,
        value: household[provision.key] || 0,
        index: index
      }))
      .filter(p => Math.abs(p.value) > 0.01);
  }
  
  $: provisionBreakdown = household ? getProvisionBreakdown(household) : [];
</script>

{#if household}
  <div class="household-profile">
    <h3>
      Household #{Math.round($householdId)}
      <div class="header-buttons">
        <span class="random-indicator">Representative sample</span>
        <button 
          class="action-button random-button" 
          on:click|preventDefault|stopPropagation={(e) => {
            // Prevent any default scroll behavior
            e.preventDefault();
            e.stopPropagation();
            
            // Blur the button to prevent focus-related scrolling
            e.currentTarget.blur({ preventScroll: true });
            
            // Call the randomize function
            onRandomize();
          }}
          title="Show another representative household"
        >
          🔀
        </button>
        <button 
          class="action-button link-button" 
          on:click={(e) => copyHouseholdUrl(household, selectedDataset, currentState, e)}
          title="Copy link to this household"
        >
          🔗
        </button>
      </div>
    </h3>
    
    <!-- Household Attributes Section -->
    <div class="household-section">
      <div class="household-basics">
        <div class="detail-item">
          <span class="label">State:</span>
          <span class="value">{stateNames[household['State']] || household['State'] || 'N/A'}</span>
        </div>
        <div class="detail-item">
          <span class="label">Ages:</span>
          <span class="value">{getHouseholdAges(household)}</span>
        </div>
        <div class="detail-item">
          <span class="label">Market income:</span>
          <span class="value">{formatCurrency($marketIncome)}</span>
        </div>
        <button 
          class="expand-button" 
          on:click={() => showHouseholdDetails = !showHouseholdDetails}
          title="{showHouseholdDetails ? 'Hide' : 'Show'} more household details"
        >
          <span class="expand-icon">{showHouseholdDetails ? '−' : '+'}</span>
          {showHouseholdDetails ? 'Show less' : 'Show more'}
        </button>
      </div>
      
      {#if showHouseholdDetails}
        <div class="expandable-details">
          <div class="detail-item">
            <span class="label">Marital status:</span>
            <span class="value">{household['Is Married'] ? 'Married' : 'Single'}</span>
          </div>
          {#if household['Baseline Net Income']}
            <div class="detail-item">
              <span class="label">Baseline net income:</span>
              <span class="value">{formatCurrency(household['Baseline Net Income'])}</span>
            </div>
          {/if}
          {#each getNonZeroFields(household).basic as field}
            {#if !['State', 'Age of Head', 'Age', 'Market Income', 'Gross Income', 'Is Married', 'Number of Dependents', 'Dependents', 'Baseline Net Income'].includes(field.key)}
              <div class="detail-item">
                <span class="label">{field.key}:</span>
                <span class="value">
                  {#if typeof field.value === 'number'}
                    {#if field.key.includes('Income') || field.key.includes('Taxes') || field.key.includes('Benefits')}
                      {formatCurrency(field.value)}
                    {:else}
                      {Math.round(field.value).toLocaleString()}
                    {/if}
                  {:else}
                    {field.value}
                  {/if}
                </span>
              </div>
            {/if}
          {/each}
        </div>
      {/if}
    </div>
    
    <!-- OBBBA Impact Section -->
    <div class="impact-section">
      <h4>OBBBA impact</h4>
      <div class="impact-details">
        <div class="detail-item">
          <span class="label">Net income under TCJA {selectedDataset === 'tcja-expiration' ? 'expiration' : 'extension'}:</span>
          <span class="value">{formatCurrency($baselineNetIncome)}</span>
        </div>
        <div class="detail-item">
          <span class="label">Net income under OBBBA:</span>
          <span class="value">{formatCurrency($obbbaNetIncome)}</span>
        </div>
        <div class="detail-item">
          <span class="label">OBBBA absolute impact:</span>
          <span class="value impact" class:pos={$absoluteImpact > 0} class:neg={$absoluteImpact < 0}>
            {formatDollarChange($absoluteImpact)}
          </span>
        </div>
        <div class="detail-item">
          <span class="label">OBBBA relative impact:</span>
          <span class="value impact" class:pos={$relativeImpact > 0} class:neg={$relativeImpact < 0}>
            {formatPercentage($relativeImpact)}
          </span>
        </div>
        <button 
          class="expand-button" 
          on:click={() => showProvisionDetails = !showProvisionDetails}
          title="{showProvisionDetails ? 'Hide' : 'Show'} provision breakdown"
        >
          <span class="expand-icon">{showProvisionDetails ? '−' : '+'}</span>
          {showProvisionDetails ? 'Hide provisions' : 'Show provisions'}
        </button>
      </div>
    </div>
    
      <!-- Provision Details (Expandable) -->
      {#if showProvisionDetails}
        <div class="expandable-details provision-details">
          {#if provisionBreakdown.length > 0}
            {#each provisionBreakdown as provision}
              <div class="detail-item">
                <span class="label">{provision.name}:</span>
                <span class="value impact" class:pos={provision.value > 0} class:neg={provision.value < 0}>
                  {formatDollarChange(provision.value)}
                </span>
              </div>
            {/each}
          {:else}
            <p class="no-provisions">No significant provision changes for this household.</p>
          {/if}
        </div>
      {/if}
  </div>
{/if}

<style>
  .household-profile {
    margin-top: 2rem;
    padding: 1.5rem;
    background: rgba(247, 250, 252, 0.85);
    border-radius: 8px;
    border: 1px solid rgba(226, 232, 240, 0.7);
    /* Maintain stable layout */
    min-height: 350px;
    /* Prevent being used as scroll anchor */
    overflow-anchor: none;
    /* Prevent layout shifts during animations */
    contain: layout style paint;
    will-change: transform;
    /* Force GPU acceleration for smoother updates */
    transform: translateZ(0);
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

  .random-indicator {
    font-size: 0.7em;
    font-weight: 400;
    color: var(--text-secondary);
    opacity: 0.6;
    margin-right: 0.25rem;
    white-space: nowrap;
    display: flex;
    align-items: center;
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
    font-size: 13px;
    color: var(--text-secondary);
    font-weight: 500;
  }

  .detail-item .value {
    font-size: 14px;
    font-weight: 600;
  }

  .provision-details {
    border-top: none;
    padding-top: 0;
    margin-top: 0.5rem;
  }

  .no-provisions {
    font-size: 14px;
    color: var(--text-secondary);
    font-style: italic;
    margin: 0;
  }

  /* Color logic for positive/negative/zero values */
  .value.pos { color: var(--scatter-positive); }
  .value.neg { color: var(--scatter-negative); }

  /* Use Roboto Mono for all text in the household box */
  .household-profile,
  .household-profile * {
    font-family: 'Roboto Mono', monospace !important;
  }
  
  /* New section styles */
  .household-section {
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
  }
  
  .impact-section {
    margin-bottom: 1rem;
  }
  
  .impact-section h4 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 1rem 0;
  }
  
  /* Expand buttons */
  .expand-button {
    background: none;
    border: none;
    color: var(--primary-blue);
    cursor: pointer;
    font-size: 0.85rem;
    padding: 0.5rem 0;
    margin-top: 0.5rem;
    text-decoration: none;
    transition: color 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .expand-button:hover {
    color: var(--darkest-blue);
  }
  
  .expand-icon {
    display: inline-flex;
    width: 16px;
    height: 16px;
    align-items: center;
    justify-content: center;
    border: 1px solid currentColor;
    border-radius: 2px;
    font-size: 14px;
    line-height: 1;
    font-weight: 400;
  }
  
  /* Expandable details */
  .expandable-details {
    margin-top: 1rem;
    padding-top: 1rem;
  }
  
  .impact-details .detail-item {
    margin-bottom: 0.5rem;
  }
  
  .value.impact {
    font-weight: 700;
  }
  
  /* Mobile responsive styles */
  @media (max-width: 768px) {
    .household-profile {
      margin-top: 1rem;
      padding: 1rem;
      border-radius: 6px;
    }
    
    .household-profile h3 {
      font-size: 1rem;
      margin-bottom: 0.75rem;
    }
    
    .header-buttons {
      gap: 0.25rem;
    }
    
    .random-indicator {
      font-size: 0.65em;
    }
    
    .action-button {
      font-size: 14px;
      padding: 2px;
    }
    
    .detail-item {
      padding: 0.375rem 0;
      flex-wrap: wrap;
      gap: 0.25rem;
    }
    
    .detail-item .label {
      font-size: 12px;
      flex: 1 1 auto;
      min-width: 120px;
    }
    
    .detail-item .value {
      font-size: 13px;
      text-align: right;
      flex: 0 0 auto;
    }
    
    .impact-section h4 {
      font-size: 0.95rem;
      margin-bottom: 0.75rem;
    }
    
    .expand-button {
      font-size: 0.75rem;
      padding: 0.375rem 0;
      margin-top: 0.375rem;
    }
    
    .expand-icon {
      width: 14px;
      height: 14px;
      font-size: 12px;
    }
    
    .household-section,
    .impact-section {
      margin-bottom: 1rem;
      padding-bottom: 1rem;
    }
    
    .expandable-details {
      margin-top: 0.75rem;
      padding-top: 0.75rem;
    }
    
    .no-provisions {
      font-size: 12px;
    }
  }
  
  @media (max-width: 480px) {
    .household-profile {
      padding: 0.875rem;
    }
    
    .household-profile h3 {
      font-size: 0.875rem;
    }
    
    .random-indicator {
      display: none;
    }
    
    .detail-item .label {
      font-size: 11px;
    }
    
    .detail-item .value {
      font-size: 12px;
    }
    
    .impact-section h4 {
      font-size: 0.875rem;
    }
    
    .expand-button {
      font-size: 0.7rem;
    }
  }
</style>