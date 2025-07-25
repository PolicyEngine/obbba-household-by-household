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
      { 
        name: 'Rate adjustment', 
        key: 'Change in Net income after Rate adjustments',
        description: 'Permanently extends TCJA individual tax rates, including the 37% top rate. Rates are 10%, 12%, 22%, 24%, 32%, 35%, and 37%.'
      },
      { 
        name: 'Standard deduction increase', 
        key: 'Change in Net income after Standard deduction increase',
        description: 'Increases standard deduction to $15,750 for single filers and $31,500 for married filing jointly in 2025, indexed to inflation.'
      },
      { 
        name: 'Exemption repeal', 
        key: 'Change in Net income after Exemption repeal',
        description: 'Continues TCJA\'s repeal of personal exemptions, which were $4,050 per person before 2018.'
      },
      { 
        name: 'Child tax credit social security number requirement', 
        key: 'Change in Net income after Child tax credit social security number requirement',
        description: 'Requires work-eligible SSNs for both the child and at least one parent claiming the credit. Affects mixed-status families.'
      },
      { 
        name: 'Child tax credit expansion', 
        key: 'Change in Net income after Child tax credit expansion',
        description: 'Increases child tax credit from $2,000 to $2,200 per child, with inflation indexing starting in 2026. Refundable portion remains at $1,700.'
      },
      { 
        name: 'Qualified Business Income Deduction Reform', 
        key: 'Change in Net income after Qualified business interest deduction reform',
        description: 'Makes permanent the 20% deduction for pass-through entities. Expands phase-in limits to $75,000 ($150,000 joint) with $400 minimum deduction.'
      },
      { 
        name: 'Alternative minimum tax reform', 
        key: 'Change in Net income after Alternative minimum tax reform',
        description: 'AMT exemption: $88,100 (single)/$137,000 (joint) for 2025. Starting 2026: phaseout at $500K/$1M with 50% phaseout rate.'
      },
      { 
        name: 'Miscellaneous deduction reform', 
        key: 'Change in Net income after Miscellaneous deduction reform',
        description: 'Continues suspension of miscellaneous itemized deductions subject to 2% AGI floor, including unreimbursed employee expenses.'
      },
      { 
        name: 'Charitable deductions reform', 
        key: 'Change in Net income after Charitable deductions reform',
        description: 'Introduces 0.5% of AGI floor on charitable contributions, reducing deductible amounts. 37% bracket taxpayers limited to 35% benefit.'
      },
      { 
        name: 'Casualty loss deduction repeal', 
        key: 'Change in Net income after Casualty loss deduction repeal',
        description: 'Continues limitation of casualty loss deductions to federally declared disaster areas only.'
      },
      { 
        name: 'Pease repeal', 
        key: 'Change in Net income after Pease repeal',
        description: 'Maintains repeal of Pease limitation that previously reduced itemized deductions for high-income taxpayers by 3% of excess AGI.'
      },
      { 
        name: 'Limitation on itemized deductions reform', 
        key: 'Change in Net income after Limitation on itemized deductions reform',
        description: 'New limitation caps itemized deduction benefit at 35% of taxable income for taxpayers in 37% bracket.'
      },
      { 
        name: 'Estate tax reform', 
        key: 'Change in Net income after Estate tax reform',
        description: 'Increases estate and gift tax exemption to $15 million per person ($30 million per couple), indexed for inflation.'
      },
      { 
        name: 'New senior deduction', 
        key: 'Change in Net income after New senior deduction',
        description: 'New $6,000 deduction for taxpayers age 65+, available 2025-2028. Reduces taxable income regardless of itemization.'
      },
      { 
        name: 'Tip exemption', 
        key: 'Change in Net income after Tip exemption',
        description: 'Deduction up to $25,000 for tip income, 2025-2028. Tips remain reportable income but receive federal tax deduction.'
      },
      { 
        name: 'Overtime exemption', 
        key: 'Change in Net income after Overtime exemption',
        description: 'Deduction up to $25,000 for overtime wages, 2025-2028. Applies to wages earned above regular hours.'
      },
      { 
        name: 'Auto loan interest deduction', 
        key: 'Change in Net income after Auto loan interest deduction',
        description: 'Deduction up to $10,000 for auto loan interest, 2025-2028. Applies to qualifying vehicle loans.'
      },
      { 
        name: 'Cap on State and Local Tax Deduction', 
        key: 'Change in Net income after Cap on state and local tax deduction',
        description: 'SALT deduction cap increases to $40,000 for taxpayers earning under $500,000, indexed annually. Reverts to $10,000 in 2030.'
      },
      { 
        name: 'Child and Dependent Care Credit Reform', 
        key: 'Change in Net income after Child and dependent care credit reform',
        description: 'Modifies child and dependent care credit structure and income phaseouts. Credit remains nonrefundable.'
      },
      { 
        name: 'Extension of ACA enhanced subsidies', 
        key: 'Change in Net income after Extension of ACA enhanced subsidies',
        description: 'Extends enhanced premium tax credits from American Rescue Plan, maintaining lower health insurance costs for eligible households.'
      },
      { 
        name: 'SNAP reform', 
        key: 'Change in Net income after SNAP reform',
        description: 'Modifies SNAP (food stamp) eligibility and benefit calculations, potentially affecting household food assistance.'
      },
      { 
        name: 'Medicaid reform', 
        key: 'Change in Net income after Medicaid reform',
        description: 'Changes to Medicaid eligibility and coverage, including potential work requirements and funding modifications.'
      }
    ];
    
    return provisions
      .map((provision, index) => {
        // Extract the provision suffix from the key
        const suffix = provision.key.replace('Change in Net income after ', '');
        
        return {
          name: provision.name,
          value: household[provision.key] || 0,
          index: index,
          description: provision.description,
          // Automatically generate the federal, state, and benefits keys
          federalChange: household[`Change in Federal tax liability after ${suffix}`] || 0,
          stateChange: household[`Change in State tax liability after ${suffix}`] || 0,
          benefitsChange: household[`Change in Benefits after ${suffix}`] || 0
        };
      })
      .filter(p => Math.abs(p.value) > 0.01);
  }
  
  $: provisionBreakdown = household ? getProvisionBreakdown(household) : [];
  
  // Calculate total federal, state, and benefits changes
  $: totalFederalChange = household ? (household['Total change in federal tax liability'] || 0) : 0;
  $: totalStateChange = household ? (household['Total change in state tax liability'] || 0) : 0;
  $: totalBenefitsChange = household ? (household['Total Change in Benefits'] || 0) : 0;
  
  // Get income sources breakdown
  function getIncomeSources(household) {
    if (!household) return [];
    
    const sources = [
      { name: 'Employment income', value: household['Employment income'] || 0 },
      { name: 'Self-employment income', value: household['Self-employment income'] || 0 },
      { name: 'Dividend income', value: household['Dividend income'] || 0 },
      { name: 'Farm income', value: household['Farm income'] || 0 },
      { name: 'Interest income', value: household['Taxable interest income'] || 0 },
      { name: 'Rental income', value: household['rental income'] || 0 },
      { name: 'Pension income', value: household['Taxable pension income'] || 0 },
      { name: 'Social Security', value: household['Taxable Social Security'] || 0 },
      { name: 'Tip income', value: household['Tip income'] || 0 },
      { name: 'Overtime income', value: household['Overtime income'] || 0 },
      { name: 'Other income', value: household['Miscellaneous income'] || 0 }
    ];
    
    // Filter out zero values and sort by amount descending
    return sources
      .filter(s => Math.abs(s.value) > 0.01)
      .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
  }
  
  $: incomeSources = household ? getIncomeSources(household) : [];
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
          <span class="value value-with-breakdown">
            {formatCurrency($marketIncome)}
            {#if incomeSources.length > 0}
              <div class="breakdown-tooltip income-sources-tooltip">
                {#each incomeSources as source}
                  <div class="breakdown-item">
                    <span class="breakdown-label">{source.name}:</span>
                    <span class="breakdown-value">
                      {formatCurrency(source.value)}
                    </span>
                  </div>
                {/each}
              </div>
            {/if}
          </span>
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
          <span class="value impact value-with-breakdown" class:pos={$absoluteImpact > 0} class:neg={$absoluteImpact < 0}>
            {formatDollarChange($absoluteImpact)}
            <div class="breakdown-tooltip">
              <div class="breakdown-item">
                <span class="breakdown-label">Federal tax:</span>
                <span class="breakdown-value" class:pos={totalFederalChange < 0} class:neg={totalFederalChange > 0}>
                  {formatDollarChange(-totalFederalChange)}
                </span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-label">State tax:</span>
                <span class="breakdown-value" class:pos={totalStateChange < 0} class:neg={totalStateChange > 0}>
                  {formatDollarChange(-totalStateChange)}
                </span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-label">Benefits:</span>
                <span class="breakdown-value" class:pos={totalBenefitsChange > 0} class:neg={totalBenefitsChange < 0}>
                  {formatDollarChange(totalBenefitsChange)}
                </span>
              </div>
            </div>
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
              <div class="detail-item provision-item">
                <span class="label provision-label">
                  {provision.name}
                </span>
                <span class="value impact value-with-breakdown" class:pos={provision.value > 0} class:neg={provision.value < 0}>
                  {formatDollarChange(provision.value)}
                  <div class="breakdown-tooltip">
                    <div class="breakdown-item">
                      <span class="breakdown-label">Federal tax:</span>
                      <span class="breakdown-value" class:pos={provision.federalChange < 0} class:neg={provision.federalChange > 0}>
                        {formatDollarChange(-provision.federalChange)}
                      </span>
                    </div>
                    <div class="breakdown-item">
                      <span class="breakdown-label">State tax:</span>
                      <span class="breakdown-value" class:pos={provision.stateChange < 0} class:neg={provision.stateChange > 0}>
                        {formatDollarChange(-provision.stateChange)}
                      </span>
                    </div>
                    <div class="breakdown-item">
                      <span class="breakdown-label">Benefits:</span>
                      <span class="breakdown-value" class:pos={provision.benefitsChange > 0} class:neg={provision.benefitsChange < 0}>
                        {formatDollarChange(provision.benefitsChange)}
                      </span>
                    </div>
                  </div>
                </span>
                <div class="provision-tooltip">{provision.description}</div>
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
    /* Allow tooltips to overflow */
    overflow: visible;
    /* Prevent layout shifts during animations */
    contain: layout style;
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
    font-size: 0.6em;
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
    overflow: visible;
    position: relative;
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
    font-size: 0.95rem;
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
    overflow: visible;
  }
  
  .impact-details .detail-item {
    margin-bottom: 0.5rem;
  }
  
  .value.impact {
    font-weight: 700;
  }
  
  /* Provision tooltips */
  .provision-item {
    position: relative;
  }
  
  .provision-label {
    display: inline-flex;
    align-items: center;
    cursor: help;
    position: relative;
    text-decoration: underline;
    text-decoration-style: dotted;
    text-underline-offset: 2px;
    text-decoration-thickness: 1px;
    text-decoration-color: var(--text-secondary);
  }
  
  .provision-label:hover {
    text-decoration-color: var(--text-primary);
  }
  
  .provision-tooltip {
    position: absolute;
    left: 0;
    top: 100%;
    margin-top: 4px;
    padding: 8px 12px;
    background: rgba(24, 35, 51, 0.95);
    color: white;
    font-size: 12px;
    line-height: 1.4;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    max-width: 300px;
    width: max-content;
    z-index: 1000;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-4px);
    transition: all 0.2s ease;
    pointer-events: none;
  }
  
  /* Position tooltip above for last few items to prevent cutoff */
  .provision-item:nth-last-child(-n+3) .provision-tooltip {
    top: auto;
    bottom: 100%;
    margin-top: 0;
    margin-bottom: 4px;
    transform: translateY(4px);
  }
  
  .provision-label:hover ~ .provision-tooltip {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
  }
  
  /* Tooltip arrow */
  .provision-tooltip::before {
    content: '';
    position: absolute;
    top: -4px;
    left: 20px;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 4px solid rgba(24, 35, 51, 0.95);
  }
  
  /* Arrow pointing down for tooltips above */
  .provision-item:nth-last-child(-n+3) .provision-tooltip::before {
    top: auto;
    bottom: -4px;
    border-bottom: none;
    border-top: 4px solid rgba(24, 35, 51, 0.95);
  }
  
  /* Value breakdown tooltip */
  .value-with-breakdown {
    position: relative;
    cursor: help;
    text-decoration: underline;
    text-decoration-style: dotted;
    text-underline-offset: 2px;
    text-decoration-thickness: 1px;
  }
  
  .breakdown-tooltip {
    position: absolute;
    right: 100%;
    top: 50%;
    transform: translateY(-50%);
    margin-right: 8px;
    padding: 10px 12px;
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid var(--border);
    color: var(--text-primary);
    font-size: 12px;
    line-height: 1.5;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    width: max-content;
    min-width: 180px;
    z-index: 1001;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
    pointer-events: none;
  }
  
  .value-with-breakdown:hover .breakdown-tooltip {
    opacity: 1;
    visibility: visible;
  }
  
  .breakdown-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2px 0;
    gap: 12px;
  }
  
  .breakdown-label {
    font-size: 11px;
    color: var(--text-secondary);
    white-space: nowrap;
  }
  
  .breakdown-value {
    font-weight: 600;
    font-size: 12px;
    white-space: nowrap;
  }
  
  /* Breakdown tooltip arrow pointing right */
  .breakdown-tooltip::after {
    content: '';
    position: absolute;
    left: 100%;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-top: 4px solid transparent;
    border-bottom: 4px solid transparent;
    border-left: 4px solid var(--border);
  }
  
  /* Income sources tooltip - positioned below */
  .income-sources-tooltip {
    right: auto;
    left: 0;
    top: 100%;
    bottom: auto;
    transform: none;
    margin-top: 8px;
    margin-right: 0;
  }
  
  /* Income sources tooltip arrow pointing up */
  .income-sources-tooltip::after {
    left: 20px;
    top: -4px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 4px solid var(--border);
    border-top: none;
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
      font-size: 0.55em;
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
      font-size: 0.85rem;
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
    
    /* Mobile tooltip adjustments */
    .provision-tooltip {
      font-size: 11px;
      padding: 6px 10px;
      max-width: 250px;
    }
    
    /* Mobile breakdown tooltip */
    .breakdown-tooltip {
      right: auto;
      left: 50%;
      top: auto;
      bottom: 100%;
      transform: translateX(-50%);
      margin-bottom: 8px;
      margin-right: 0;
      font-size: 11px;
      min-width: 160px;
    }
    
    .breakdown-tooltip::after {
      left: 50%;
      top: 100%;
      transform: translateX(-50%);
      border-left: 4px solid transparent;
      border-right: 4px solid transparent;
      border-top: 4px solid var(--border);
      border-bottom: none;
    }
    
    .breakdown-label {
      font-size: 10px;
    }
    
    .breakdown-value {
      font-size: 11px;
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
      font-size: 0.8rem;
    }
    
    .expand-button {
      font-size: 0.7rem;
    }
    
    /* Small mobile tooltip adjustments */
    .provision-tooltip {
      font-size: 10px;
      padding: 5px 8px;
      max-width: 200px;
    }
    
    /* Small mobile breakdown tooltip */
    .breakdown-tooltip {
      font-size: 10px;
      min-width: 140px;
      padding: 8px 10px;
    }
    
    .breakdown-label {
      font-size: 9px;
    }
    
    .breakdown-value {
      font-size: 10px;
    }
  }
</style>