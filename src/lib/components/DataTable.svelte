<script>
  export let selectedData = null;
  export let onClose = () => {};
  
  // Fields to exclude from display
  const excludeFields = ['id', 'isAnnotated', 'sectionIndex', 'isHighlighted', 'highlightGroup', 'stateIndex', 'householdId'];
  
  // Categorize fields
  function categorizeFields(data) {
    if (!data || typeof data !== 'object') {
      return { basicInfo: [], provisions: [], other: [] };
    }
    
    const basicInfo = [];
    let provisions = [];
    const other = [];
    
    Object.entries(data).forEach(([key, value]) => {
      if (!key || excludeFields.includes(key)) return;
      
      // Check if it's a provision-related field (contains "after" in the key)
      if (key.includes(' after ')) {
        provisions.push([key, value]);
      } else if (key.includes('Household') || key.includes('Age') || key.includes('Filing') || 
                 key.includes('Dependents') || key.includes('State') || key.includes('Gross Income')) {
        basicInfo.push([key, value]);
      } else {
        other.push([key, value]);
      }
    });
    
    // Group provisions by reform name
    const provisionsByReform = {};
    provisions.forEach(([key, value]) => {
      if (!key || typeof key !== 'string') return;
      
      // Extract the reform name (text after "after")
      const match = key.match(/after (.+)$/);
      if (match && match[1]) {
        const reformName = match[1];
        if (!provisionsByReform[reformName]) {
          provisionsByReform[reformName] = [];
        }
        provisionsByReform[reformName].push([key, value]);
      }
    });
    
    // Calculate net income impact for each reform and sort
    const reformsWithImpact = Object.entries(provisionsByReform).map(([reformName, items]) => {
      // Find the net income change for this reform
      const netIncomeItem = items.find(([k, v]) => k.includes('Net income'));
      const netIncomeValue = netIncomeItem ? netIncomeItem[1] : 0;
      return {
        reformName,
        items,
        impact: Math.abs(typeof netIncomeValue === 'number' ? netIncomeValue : 0)
      };
    });
    
    // Sort reforms by impact (largest first)
    reformsWithImpact.sort((a, b) => b.impact - a.impact);
    
    // Flatten back to provisions array, keeping Net income items first within each reform
    provisions = [];
    reformsWithImpact.forEach(({ items }) => {
      // Sort items within each reform to put Net income first
      items.sort((a, b) => {
        if (a[0].includes('Net income')) return -1;
        if (b[0].includes('Net income')) return 1;
        return 0;
      });
      provisions.push(...items);
    });
    
    return { basicInfo, provisions, other };
  }
  
  function formatValue(key, value) {
    if (typeof value === 'number') {
      if (key.includes('Income') || key.includes('Taxes') || key.includes('Tax Liability') || 
          key.includes('Benefits') || key.includes('Gains') || key.includes('Interest') || 
          key.includes('Medicaid') || key.includes('ACA') || key.includes('CHIP') || 
          key.includes('SNAP') || (key.toLowerCase().includes('change in') && !key.includes('Percentage'))) {
        return (value < 0 ? '-' : '') + '$' + Math.abs(Math.round(value)).toLocaleString();
      } else if (key.includes('Percentage')) {
        return (value > 0 ? '+' : '') + value.toFixed(2) + '%';
      } else if (key.includes('ID') || key.includes('Household')) {
        return Math.round(value);
      } else {
        return Math.round(value).toLocaleString();
      }
    }
    return value;
  }
  
  $: categorizedData = selectedData ? categorizeFields(selectedData) : null;
</script>

{#if selectedData && categorizedData}
  <div class="data-table-overlay" on:click={onClose}>
    <div class="data-table-container" on:click|stopPropagation>
      <h3>Selected Household Data</h3>
      <table class="data-table">
        <tbody>
          <!-- Basic Information -->
          {#if categorizedData.basicInfo.length > 0}
            <tr class="section-header">
              <td colspan="2">Basic Information</td>
            </tr>
            {#each categorizedData.basicInfo as [key, value], index}
              {#if key === 'Is Married'}
                <tr>
                  <td class="key-column">Marital status</td>
                  <td class="value-column">
                    <span id="table-basic-{index}">{value ? 'Married' : 'Single'}</span>
                  </td>
                </tr>
              {:else}
                <tr>
                  <td class="key-column">{key}</td>
                  <td class="value-column">
                    <span id="table-basic-{index}">{formatValue(key, value)}</span>
                  </td>
                </tr>
              {/if}
            {/each}
          {/if}
          
          <!-- Tax Provisions (sorted by impact) -->
          {#if categorizedData.provisions.length > 0}
            <tr class="section-header">
              <td colspan="2">Tax Provision Impacts (sorted by magnitude)</td>
            </tr>
            {#each categorizedData.provisions as [key, value], index}
              <tr>
                <td class="key-column">{key}</td>
                <td class="value-column">
                  <span id="table-provision-{index}" class:pos={value > 0} class:neg={value < 0}>
                    {formatValue(key, value)}
                  </span>
                </td>
              </tr>
            {/each}
          {/if}
          
          <!-- Other Data -->
          {#if categorizedData.other.length > 0}
            <tr class="section-header">
              <td colspan="2">Other Information</td>
            </tr>
            {#each categorizedData.other as [key, value], index}
              <tr>
                <td class="key-column">{key}</td>
                <td class="value-column">
                  <span id="table-other-{index}">{formatValue(key, value)}</span>
                </td>
              </tr>
            {/each}
          {/if}
        </tbody>
      </table>
      <button class="close-table" on:click={onClose}>×</button>
    </div>
  </div>
{/if}

<style>
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
  
  /* Section headers */
  .section-header td {
    padding: 12px 0 8px 0;
    font-weight: 700;
    color: var(--text-primary);
    border-bottom: 2px solid var(--border);
    font-size: 13px;
  }
  
  .section-header:not(:first-child) td {
    padding-top: 20px;
  }
  
  /* Color values based on positive/negative */
  .value-column .pos {
    color: var(--scatter-positive);
  }
  
  .value-column .neg {
    color: var(--scatter-negative);
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
      padding: 6px 8px 6px 0;
      width: 55%;
    }
  }
</style>