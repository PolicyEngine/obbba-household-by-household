// Copy household URL to clipboard with fallback methods
export async function copyHouseholdUrl(household, selectedDataset, currentState, event) {
  // Prevent default if event provided
  if (event && event.preventDefault) {
    event.preventDefault();
  }
  
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
    // Try to use the Clipboard API
    await navigator.clipboard.writeText(fullUrl);
    console.log('Successfully copied URL to clipboard');
    
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
    
    return true;
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
        
        return true;
      } else {
        console.error('execCommand copy failed');
        alert('Failed to copy URL. URL is: ' + fullUrl);
        return false;
      }
    } catch (fallbackErr) {
      console.error('All copy methods failed:', fallbackErr);
      alert('Failed to copy URL. URL is: ' + fullUrl);
      return false;
    }
  }
}