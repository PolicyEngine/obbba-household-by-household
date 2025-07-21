import { writable, get } from 'svelte/store';

// Scroll state management stores
export const currentStateIndex = writable(0);
export const previousStateIndex = writable(0);
export const isTransitioning = writable(false);
export const transitionT = writable(0);
export const currentInterpolationT = writable(0);

// Track transition state
let transitionStartTime = null;
let transitionDuration = 1200; // ms - longer for smoother zoom effect

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
        if (!isNaN(index) && index !== get(currentStateIndex)) {
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
  if (get(isTransitioning) || targetIndex === get(currentStateIndex)) return;
  
  previousStateIndex.set(get(currentStateIndex));
  currentStateIndex.set(targetIndex);
  isTransitioning.set(true);
  transitionT.set(0);
  transitionStartTime = performance.now();
  
  // Cancel any existing animation
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  
  // Animate transition
  function animate(currentTime) {
    const elapsed = currentTime - transitionStartTime;
    const t = Math.min(elapsed / transitionDuration, 1);
    
    // Update both raw and eased values
    transitionT.set(t);
    currentInterpolationT.set(easeInOutCubic(t));
    
    if (t < 1) {
      animationFrameId = requestAnimationFrame(animate);
    } else {
      // Ensure final values are set
      isTransitioning.set(false);
      transitionT.set(1);
      currentInterpolationT.set(1);
      if (onComplete) onComplete(get(currentStateIndex));
    }
  }
  
  animationFrameId = requestAnimationFrame(animate);
}

// Easing function - smoother for zoom transitions
function easeInOutCubic(t) {
  // Use a smoother easing for better zoom effect
  return t < 0.5 
    ? 2 * t * t 
    : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

// Check active section based on scroll position
export function checkActiveSection(container, textSections) {
  if (get(isTransitioning) || !textSections.length) return;
  
  const scrollTop = container.scrollTop;
  const containerHeight = container.clientHeight;
  const scrollCenter = scrollTop + containerHeight / 2;
  
  // Find which section is at the center of the viewport
  let newIndex = get(currentStateIndex);
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