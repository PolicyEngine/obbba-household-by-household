// Store for managing animated numbers
export const animatedNumbers = new Map();
export const animatedHouseholds = new Map();

// Create animated number effect
export function createAnimatedNumber(elementId, startValue, endValue, formatter, duration = 800) {
  // Cancel any existing animation for this element
  if (animatedNumbers.has(elementId)) {
    clearInterval(animatedNumbers.get(elementId));
  }
  
  const element = document.getElementById(elementId);
  if (!element) return;
  
  const startTime = performance.now();
  
  function animate(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Cubic ease-out for smooth animation
    const eased = 1 - Math.pow(1 - progress, 3);
    
    const currentValue = startValue + (endValue - startValue) * eased;
    element.textContent = formatter(currentValue);
    
    if (progress < 1) {
      const animationId = requestAnimationFrame(animate);
      animatedNumbers.set(elementId, animationId);
    } else {
      animatedNumbers.delete(elementId);
    }
  }
  
  const animationId = requestAnimationFrame(animate);
  animatedNumbers.set(elementId, animationId);
}

// Animate household emphasis (grow and fade back)
export function animateHouseholdEmphasis(householdId, duration = 600) {
  // Clear existing animation if any
  const existingAnimation = animatedHouseholds.get(householdId);
  if (existingAnimation?.animationId) {
    cancelAnimationFrame(existingAnimation.animationId);
  }
  
  const startTime = performance.now();
  const animationState = {
    isAnimating: true,
    scale: 1,
    opacity: 1,
    animationId: null
  };
  
  animatedHouseholds.set(householdId, animationState);
  
  function animate(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Scale up then down
    if (progress < 0.5) {
      // Growing phase
      const growProgress = progress * 2;
      animationState.scale = 1 + (0.5 * growProgress);
      animationState.opacity = 1 + (0.3 * growProgress);
    } else {
      // Shrinking phase
      const shrinkProgress = (progress - 0.5) * 2;
      animationState.scale = 1.5 - (0.5 * shrinkProgress);
      animationState.opacity = 1.3 - (0.3 * shrinkProgress);
    }
    
    if (progress < 1) {
      animationState.animationId = requestAnimationFrame(animate);
    } else {
      animationState.isAnimating = false;
      animationState.scale = 1;
      animationState.opacity = 1;
      animatedHouseholds.delete(householdId);
    }
  }
  
  animationState.animationId = requestAnimationFrame(animate);
}

// Clean up all animations
export function cleanupAnimations() {
  animatedNumbers.forEach((id) => cancelAnimationFrame(id));
  animatedNumbers.clear();
  
  animatedHouseholds.forEach((state) => {
    if (state.animationId) cancelAnimationFrame(state.animationId);
  });
  animatedHouseholds.clear();
}