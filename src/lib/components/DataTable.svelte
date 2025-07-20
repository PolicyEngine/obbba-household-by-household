<script>
  export let selectedData = null;
  export let onClose = () => {};
  
  // Fields to exclude from display
  const excludeFields = ['id', 'isAnnotated', 'sectionIndex', 'isHighlighted', 'highlightGroup', 'stateIndex', 'householdId'];
  
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
</script>

{#if selectedData}
  <div class="data-table-overlay" on:click={onClose}>
    <div class="data-table-container" on:click|stopPropagation>
      <h3>Selected Household Data</h3>
      <table class="data-table">
        <tbody>
          {#each Object.entries(selectedData) as [key, value], index}
            {#if !excludeFields.includes(key)}
              <tr>
                <td class="key-column">{key}</td>
                <td class="value-column">
                  <span id="table-value-{index}">{formatValue(key, value)}</span>
                </td>
              </tr>
            {/if}
          {/each}
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