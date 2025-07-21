// Scroll state management
export let currentStateIndex = 0;
export let previousStateIndex = 0;
export let isTransitioning = false;
export let transitionT = 0;
export let currentInterpolationT = 0;

// Track transition state
let transitionStartTime = null;
let transitionDuration = 800; // ms

// Animation frame ID for smooth transitions
let animationFrameId = null;

// Create intersection observer for scroll sections
export function createIntersectionObserver(textSections, onSectionChange) {
  const observerOptions = {
    root: null,
    rootMargin: '-45% 0px -45% 0px',
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const index = parseInt(entry.target.dataset.index);
        if (!isNaN(index) && index !== currentStateIndex) {
          startTransition(index, onSectionChange);
        }
      }
    });
  }, observerOptions);

  // Observe all text sections
  textSections.forEach(section => {
    if (section) observer.observe(section);
  });

  return observer;
}

// Start transition to new state
export function startTransition(targetIndex, onComplete) {
  if (isTransitioning || targetIndex === currentStateIndex) return;
  
  previousStateIndex = currentStateIndex;
  currentStateIndex = targetIndex;
  isTransitioning = true;
  transitionT = 0;
  transitionStartTime = performance.now();
  
  // Cancel any existing animation
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  
  // Animate transition
  function animate(currentTime) {
    const elapsed = currentTime - transitionStartTime;
    transitionT = Math.min(elapsed / transitionDuration, 1);
    
    // Use easing function
    currentInterpolationT = easeInOutCubic(transitionT);
    
    if (transitionT < 1) {
      animationFrameId = requestAnimationFrame(animate);
    } else {
      isTransitioning = false;
      transitionT = 1;
      currentInterpolationT = 1;
      if (onComplete) onComplete(currentStateIndex);
    }
  }
  
  animationFrameId = requestAnimationFrame(animate);
}

// Easing function
function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// Check active section based on scroll position
export function checkActiveSection(container, textSections) {
  if (isTransitioning || !textSections.length) return;
  
  const scrollTop = container.scrollTop;
  const containerHeight = container.clientHeight;
  const scrollCenter = scrollTop + containerHeight / 2;
  
  // Find which section is at the center of the viewport
  let newIndex = currentStateIndex;
  let minDistance = Infinity;
  
  textSections.forEach((section, index) => {
    if (!section) return;
    
    const rect = section.getBoundingClientRect();
    const sectionTop = section.offsetTop;
    const sectionHeight = section.offsetHeight;
    const sectionCenter = sectionTop + sectionHeight / 2;
    
    const distance = Math.abs(scrollCenter - sectionCenter);
    
    if (distance < minDistance) {
      minDistance = distance;
      newIndex = index;
    }
  });
  
  return newIndex;
}

// Get random weighted household from filtered data
export function getRandomWeightedHousehold(filteredData) {
  if (!filteredData.length) return null;
  
  // Calculate total weight
  const totalWeight = filteredData.reduce((sum, d) => {
    const weight = d['Household weight'] || d['Household Weight'] || 1;
    return sum + weight;
  }, 0);
  
  // Pick random point in weight space
  const randomWeight = Math.random() * totalWeight;
  
  // Find household at that weight point
  let cumulativeWeight = 0;
  for (const household of filteredData) {
    const weight = household['Household weight'] || household['Household Weight'] || 1;
    cumulativeWeight += weight;
    if (cumulativeWeight >= randomWeight) {
      return household;
    }
  }
  
  // Fallback to last household
  return filteredData[filteredData.length - 1];
}

// Clean up scroll observer
export function cleanupScrollObserver(observer) {
  if (observer) {
    observer.disconnect();
  }
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
}