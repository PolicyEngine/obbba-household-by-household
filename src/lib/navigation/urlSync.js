import { goto } from '$app/navigation';

// Helper function to notify parent window of URL changes (for iframe integration)
export function notifyParentOfUrlChange(explicitParams = null) {
  if (typeof window !== 'undefined' && window.parent !== window) {
    // We're in an iframe, notify parent of URL change
    // Use explicit params if provided, otherwise read from URL
    const params = explicitParams || new URLSearchParams(window.location.search);
    window.parent.postMessage({
      type: 'urlUpdate',
      params: params.toString()
    }, '*');
  }
}

// Update URL with household selection
export async function updateUrlWithHousehold(householdId, selectedDataset) {
  if (typeof window !== 'undefined') {
    const url = new URL(window.location);
    
    if (householdId) {
      url.searchParams.set('household', String(householdId));
      url.searchParams.set('baseline', selectedDataset);
    } else {
      url.searchParams.delete('household');
      url.searchParams.delete('baseline');
    }
    
    // Update URL without triggering navigation
    // Use the full path including search params for SvelteKit goto
    const newUrl = url.pathname + url.search;
    
    // Pass the new params to notifyParentOfUrlChange BEFORE goto
    // This ensures the parent gets the correct (new) state
    notifyParentOfUrlChange(url.searchParams);
    
    // Then update the local URL
    await goto(newUrl, { replaceState: true, noScroll: true });
  }
}

// Parse URL parameters
export function parseUrlParams() {
  if (typeof window !== 'undefined') {
    const urlParams = new URLSearchParams(window.location.search);
    return {
      householdId: urlParams.get('household') || '',
      baseline: urlParams.get('baseline') || null,
      section: urlParams.get('section') || null
    };
  }
  return { householdId: '', baseline: null, section: null };
}

// Find appropriate section index for a household
export function findSectionForHousehold(household, scrollStates) {
  let targetSectionIndex = 0;
  
  const income = household['Market Income'] || household['Gross Income'] || 0;
  console.log('Finding section for household with income:', income);
  
  // Determine which income bracket
  if (income < 50000) {
    targetSectionIndex = scrollStates.findIndex(s => s.id === 'lower-income');
  } else if (income < 200000) {
    targetSectionIndex = scrollStates.findIndex(s => s.id === 'middle-income');
  } else if (income < 1000000) {
    targetSectionIndex = scrollStates.findIndex(s => s.id === 'upper-income');
  } else {
    targetSectionIndex = scrollStates.findIndex(s => s.id === 'highest-income');
  }
  
  console.log('Target section index:', targetSectionIndex, 'for section:', scrollStates[targetSectionIndex]?.id);
  
  // Since we removed individual views, we don't need to advance
  // Just return the group view index
  
  return Math.max(0, targetSectionIndex);
}