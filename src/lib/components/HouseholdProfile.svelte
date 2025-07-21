<script>
  import { formatCurrency, formatDollarChange, formatPercentage } from '../utils/formatting.js';
  import { copyHouseholdUrl } from '../utils/clipboard.js';
  
  export let household = null;
  export let selectedDataset = 'tcja-expiration';
  export let currentState = null;
  export let sectionIndex = 0;
  export let onRandomize = () => {};
  export let onShowDetails = () => {};
  
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
        index: index
      }))
      .filter(p => Math.abs(p.value) > 0.01);
  }
  
  $: provisionBreakdown = household ? getProvisionBreakdown(household) : [];
</script>

{#if household}
  <div class="household-profile">
    <h3>
      Household #<span id="household-id-{sectionIndex}">{household.id}</span>
      <div class="header-buttons">
        <button 
          class="action-button random-button" 
          on:click={onRandomize}
          title="Pick a new random household"
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
        <button 
          class="action-button info-button" 
          on:click={() => onShowDetails(household)}
          title="Show detailed data for this household"
        >
          ⓘ
        </button>
      </div>
    </h3>
    <div class="household-details">
      <div class="detail-item">
        <span class="label">Marital Status:</span>
        <span class="value">{household['Is Married'] ? 'Married' : 'Single'}</span>
      </div>
      <div class="detail-item">
        <span class="label">State:</span>
        <span class="value">{household['State'] || 'N/A'}</span>
      </div>
      <div class="detail-item">
        <span class="label"># Dependents:</span>
        <span class="value" id="num-dependents-{sectionIndex}">
          {Math.round(household['Number of Dependents'] || household['Dependents'] || 0)}
        </span>
      </div>
      <div class="detail-item">
        <span class="label">Age of Head:</span>
        <span class="value" id="age-of-head-{sectionIndex}">
          {household['Age of Head'] || household['Age'] || 'N/A'}
        </span>
      </div>
      <div class="detail-item">
        <span class="label">Market Income:</span>
        <span class="value" id="market-income-{sectionIndex}">
          {formatCurrency(household['Market Income'] || household['Gross Income'] || 0)}
        </span>
      </div>
      <div class="detail-item">
        <span class="label">Baseline Net Income:</span>
        <span class="value" id="baseline-net-{sectionIndex}">
          {formatCurrency(household['Baseline Net Income'] || 0)}
        </span>
      </div>
      <div class="detail-item">
        <span class="label">Net Income Change:</span>
        <span class="value {household['Total Change in Net Income'] > 0 ? 'pos' : household['Total Change in Net Income'] < 0 ? 'neg' : 'zero'}" 
              id="net-change-{sectionIndex}">
          {formatDollarChange(household['Total Change in Net Income'])}
        </span>
      </div>
      <div class="detail-item">
        <span class="label">% Change:</span>
        <span class="value {household['Percentage Change in Net Income'] > 0 ? 'pos' : household['Percentage Change in Net Income'] < 0 ? 'neg' : 'zero'}" 
              id="percent-change-{sectionIndex}">
          {formatPercentage(household['Percentage Change in Net Income'])}
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
              <span class="value {provision.value > 0 ? 'pos' : provision.value < 0 ? 'neg' : 'zero'}" 
                    id="provision-{sectionIndex}-{provision.index}">
                {formatDollarChange(provision.value)}
              </span>
            </div>
          {/each}
        </div>
      </div>
    {:else}
      <div class="provision-breakdown">
        <p class="no-provisions">No significant provision changes for this household.</p>
      </div>
    {/if}
  </div>
{/if}

<style>
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

  /* Color logic for positive/negative/zero values */
  .value.pos { color: var(--scatter-positive); }
  .value.neg { color: var(--scatter-negative); }

  /* Use monospace for data/numbers */
  .household-details,
  .household-details .label,
  .household-details .value,
  .household-profile h3,
  .household-profile h3 span,
  .provision-breakdown h4,
  .provision-breakdown,
  .provision-breakdown .provision-name,
  .provision-breakdown .value {
    font-family: var(--font-mono) !important;
  }
</style>