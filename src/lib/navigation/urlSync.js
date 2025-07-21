import { goto } from '$app/navigation';

// Helper function to notify parent window of URL changes (for iframe integration)
export function notifyParentOfUrlChange() {
  if (typeof window !== 'undefined' && window.parent !== window) {
    // We're in an iframe, notify parent of URL change
    const params = new URLSearchParams(window.location.search);
    window.parent.postMessage({
      type: 'urlUpdate',
      params: params.toString()
    }, '*');
  }
}

// Update URL with household selection
export function updateUrlWithHousehold(householdId, selectedDataset, viewSection = null) {
  if (typeof window !== 'undefined') {
    const url = new URL(window.location);
    
    if (householdId) {
      url.searchParams.set('household', String(householdId));
      url.searchParams.set('baseline', selectedDataset);
      
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
    notifyParentOfUrlChange();
  }
}

// Parse URL parameters
export function parseUrlParams() {
  if (typeof window !== 'undefined') {
    const urlParams = new URLSearchParams(window.location.search);
    return {
      householdId: String(urlParams.get('household') || ''),
      section: urlParams.get('section'),
      baseline: urlParams.get('baseline')
    };
  }
  return { householdId: '', section: null, baseline: null };
}

// Find appropriate section index for a household
export function findSectionForHousehold(household, scrollStates) {
  let targetSectionIndex = 0;
  
  const income = household['Gross Income'];
  
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
  
  // If we found a group view, advance to individual view
  if (targetSectionIndex >= 0 && scrollStates[targetSectionIndex + 1]?.viewType === 'individual') {
    targetSectionIndex++;
  }
  
  return Math.max(0, targetSectionIndex);
}