<script>
  import { onMount, onDestroy } from 'svelte';
  import * as d3 from 'd3';
  import { COLORS, getPointColor } from '../config/colors.js';
  import { getFontFamily } from '../utils/formatting.js';
  import { animatedHouseholds } from '../utils/animations.js';
  
  export let data = [];
  export let scrollStates = [];
  export let currentStateIndex = 0;
  export let previousStateIndex = 0;
  export let isTransitioning = false;
  export let interpolationT = 0;
  export let randomHouseholds = {};
  export let selectedHousehold = null;
  export let onPointClick = () => {};
  
  let canvasRef;
  let svgRef;
  let renderedPoints = [];
  
  // Progressive reveal state
  let hasScrolled = false;
  let reservedPoints = new Set(); // Points saved for scroll reveal
  let revealedReserved = false; // Track if we've revealed the reserved points
  let currentBatch = 0; // Track which batch we're revealing
  let batchTimeouts = []; // Store timeout IDs for cleanup
  
  // Staggered animation state
  let pointAnimations = new Map(); // Map of point ID to animation state
  let animationStartTime = 0;
  let lastDatasetLength = 0;
  let animationFrame = null;
  let isInitializingAnimations = false;
  
  // Chart dimensions
  let margin = { top: 60, right: 120, bottom: 100, left: 120 };
  let width = 900;
  let height = 600;
  
  // Responsive margins
  function updateMargins() {
    if (typeof window === 'undefined') return; // SSR safety
    
    const viewportWidth = window.innerWidth;
    if (viewportWidth <= 480) {
      margin = { top: 30, right: 50, bottom: 100, left: 50 };
    } else if (viewportWidth <= 768) {
      margin = { top: 40, right: 65, bottom: 60, left: 65 };
    } else {
      margin = { top: 60, right: 120, bottom: 100, left: 120 };
    }
  }
  
  // Initialize staggered animations for points
  function initializePointAnimations(dataPoints) {
    if (typeof window === 'undefined' || typeof performance === 'undefined') return;

    isInitializingAnimations = true;
    // Don't clear pointAnimations here - we want to keep the hidden state set in checkForDataChange
    animationStartTime = performance.now();

    // Create a magical starfield effect - randomize the order completely
    const shuffledPoints = [...dataPoints].sort(() => Math.random() - 0.5);

    // Slower, more graceful animation
    const maxAnimationDuration = Math.min(5000, dataPoints.length * 3); // Max 5 seconds
    
    // For small datasets, still take some time
    const minAnimationDuration = Math.min(2500, dataPoints.length * 2.5); // Min 2.5s
    const actualAnimationDuration = Math.max(minAnimationDuration, maxAnimationDuration);

    const baseDelay = actualAnimationDuration / Math.max(dataPoints.length, 1);

    shuffledPoints.forEach((point, index) => {
      // Restore linear scheduling for appearance time
      const scheduledDelay = index * baseDelay;

      // Add small random variation (±200ms) for organic feel while staying within bounds
      const randomVariation = (Math.random() - 0.5) * 400; // ±200ms
      const finalDelay = Math.max(0, Math.min(scheduledDelay + randomVariation, actualAnimationDuration - 400));

      // Add some clustering for more organic feel (some stars appear in small groups)
      const clusterChance = Math.random();
      let clusterDelay = 0;
      if (clusterChance < 0.3) {
        // 30% chance to be part of a cluster (appear close to previous star)
        clusterDelay = Math.random() * 100; // Smaller cluster delay
      }

      const totalDelay = Math.min(finalDelay + clusterDelay, actualAnimationDuration - 400);

      // Get existing animation state (which should be hidden) or create new
      const existingState = pointAnimations.get(point.id);
      pointAnimations.set(point.id, {
        startTime: animationStartTime + totalDelay,
        opacity: existingState?.opacity ?? 0, // Keep hidden state
        scale: existingState?.scale ?? 0.1,   // Keep small scale
        isAnimating: true,
        sparklePhase: existingState?.sparklePhase ?? Math.random() * Math.PI * 2,
        hasSparkled: false
      });
    });

    console.log(`🌟 Starfield animation initialized: ${dataPoints.length} stars over ${(actualAnimationDuration/1000).toFixed(1)}s`);

    // Start animation loop
    if (typeof window !== 'undefined') {
      if (animationFrame) cancelAnimationFrame(animationFrame);
      isInitializingAnimations = false;
      animatePoints();
    }
  }
  
  // Animation loop for smooth point reveals
  function animatePoints() {
    if (typeof window === 'undefined' || typeof performance === 'undefined') return;
    
    const currentTime = performance.now();
    const animationDuration = 600; // Slower individual star animation for more graceful appearance
    let needsRerender = false;
    
    pointAnimations.forEach((animation, pointId) => {
      if (!animation.isAnimating) return;
      
      const elapsed = currentTime - animation.startTime;
      
      if (elapsed >= 0) {
        const progress = Math.min(elapsed / animationDuration, 1);
        
        // Smooth easing function (ease-out cubic for even gentler feel)
        const eased = 1 - Math.pow(1 - progress, 3);
        
        // Create sparkle effect - stars get brighter then settle
        let sparkleMultiplier = 1;
        if (progress > 0.3 && progress < 0.8 && !animation.hasSparkled) {
          // Add sparkle during the middle phase
          const sparkleProgress = (progress - 0.3) / 0.5; // 0 to 1 over sparkle period
          const sparkleIntensity = Math.sin(sparkleProgress * Math.PI + animation.sparklePhase);
          sparkleMultiplier = 1 + (sparkleIntensity * 0.4); // Up to 40% brighter
          
          if (sparkleProgress > 0.8) {
            animation.hasSparkled = true; // Sparkle only once
          }
        }
        
        animation.opacity = Math.min(eased * sparkleMultiplier, 1.5); // Cap brightness for readability
        animation.scale = 0.2 + (0.8 * eased);
        
        // Add slight scale sparkle too
        if (sparkleMultiplier > 1) {
          animation.scale *= (1 + (sparkleMultiplier - 1) * 0.2);
        }
        
        if (progress >= 1) {
          animation.isAnimating = false;
          animation.opacity = 1;
          animation.scale = 1;
        }
        
        needsRerender = true;
      }
    });
    
    // Render the canvas if needed (without checking for data changes)
    if (needsRerender && canvasRef) {
      renderCanvas();
    }
    
    // Continue animation if any points are still animating
    const stillAnimating = Array.from(pointAnimations.values()).some(a => a.isAnimating);
    if (stillAnimating && typeof window !== 'undefined') {
      animationFrame = requestAnimationFrame(animatePoints);
    }
  }
  
  // Check if we need to restart animations
  function checkForDataChange() {
    // Prevent re-checking if we're already processing
    if (isInitializingAnimations) return;
    
    if (data.length !== lastDatasetLength && data.length > 0) {
      console.log(`Data changed: ${lastDatasetLength} → ${data.length} points, starting starfield animation ✨`);
      
      // For initial load (0 → some data), show dots immediately
      const isInitialLoad = lastDatasetLength === 0;
      
      if (isInitialLoad) {
        // Progressive batch reveal: 50 → 100 → 150 → etc.
        const totalPoints = data.length;
        const reserveCount = Math.floor(totalPoints * 0.2); // Still reserve 20% for scroll
        
        // Define batch sizes: 50, 100, 150, 200, ...
        const batchSizes = [];
        let accumulatedPoints = 0;
        let batchSize = 50;
        
        while (accumulatedPoints < totalPoints - reserveCount) {
          const pointsInBatch = Math.min(batchSize, totalPoints - reserveCount - accumulatedPoints);
          if (pointsInBatch > 0) {
            batchSizes.push(pointsInBatch);
            accumulatedPoints += pointsInBatch;
            batchSize += 50; // Increase by 50 each time
          }
        }
        
        console.log(`📊 Progressive batches: ${batchSizes.join(' → ')} (${reserveCount} reserved)`);
        
        // Randomly assign points to batches
        const shuffledIndices = Array.from({length: totalPoints}, (_, i) => i)
          .sort(() => Math.random() - 0.5);
        
        // Assign points to batches
        let currentIndex = 0;
        const pointBatches = new Map(); // point.id -> batch number
        
        // First batch (immediate)
        for (let i = 0; i < batchSizes[0] && currentIndex < shuffledIndices.length; i++) {
          const dataIndex = shuffledIndices[currentIndex++];
          pointBatches.set(data[dataIndex].id, 0);
        }
        
        // Subsequent batches
        for (let batch = 1; batch < batchSizes.length; batch++) {
          for (let i = 0; i < batchSizes[batch] && currentIndex < shuffledIndices.length; i++) {
            const dataIndex = shuffledIndices[currentIndex++];
            pointBatches.set(data[dataIndex].id, batch);
          }
        }
        
        // Reserve remaining points for scroll
        while (currentIndex < shuffledIndices.length) {
          const dataIndex = shuffledIndices[currentIndex++];
          reservedPoints.add(data[dataIndex].id);
        }
        
        // Set up initial animation states
        data.forEach((point) => {
          const batch = pointBatches.get(point.id);
          
          if (batch === 0) {
            // First batch appears instantly
            pointAnimations.set(point.id, {
              opacity: 1,
              scale: 1,
              isAnimating: false,
              sparklePhase: Math.random() * Math.PI * 2,
              hasSparkled: false
            });
          } else if (batch !== undefined) {
            // Later batches start hidden
            pointAnimations.set(point.id, {
              opacity: 0,
              scale: 0.1,
              isAnimating: false,
              startTime: 0,
              sparklePhase: Math.random() * Math.PI * 2,
              hasSparkled: false,
              batch: batch // Store batch number
            });
          } else if (reservedPoints.has(point.id)) {
            // Reserved for scroll - keep completely hidden
            pointAnimations.set(point.id, {
              opacity: 0,
              scale: 0,
              isAnimating: false,
              startTime: 0,
              sparklePhase: Math.random() * Math.PI * 2,
              hasSparkled: false,
              isReserved: true
            });
          } else {
            // Fallback - this shouldn't happen but just in case
            console.warn(`Point ${point.id} has no batch assignment or reservation`);
            pointAnimations.set(point.id, {
              opacity: 0,
              scale: 0,
              isAnimating: false,
              startTime: 0,
              sparklePhase: Math.random() * Math.PI * 2,
              hasSparkled: false
            });
          }
        });
        
        // Schedule batch reveals
        currentBatch = 0;
        batchTimeouts = [];
        
        for (let batch = 1; batch < batchSizes.length; batch++) {
          const delay = batch * 1500; // 1.5 seconds between batches
          const timeout = setTimeout(() => {
            console.log(`✨ Revealing batch ${batch + 1} (${batchSizes[batch]} points)`);
            currentBatch = batch;
            
            // Get points in this batch
            const batchPoints = data.filter(point => {
              const anim = pointAnimations.get(point.id);
              return anim && anim.batch === batch;
            });
            
            // Start their animation
            batchPoints.forEach(point => {
              const anim = pointAnimations.get(point.id);
              if (anim) {
                anim.isAnimating = true;
              }
            });
            
            initializePointAnimations(batchPoints);
          }, delay);
          
          batchTimeouts.push(timeout);
        }
      } else {
        // Subsequent loads: Only animate NEW points
        // Keep existing points visible
        const existingAnimations = new Map(pointAnimations);
        
        // Set up animations only for new points
        data.forEach(point => {
          if (!existingAnimations.has(point.id)) {
            // New point - start hidden for animation
            pointAnimations.set(point.id, {
              opacity: 0,
              scale: 0.1,
              isAnimating: true,
              startTime: 0, // Will be set properly in initializePointAnimations
              sparklePhase: Math.random() * Math.PI * 2,
              hasSparkled: false
            });
          }
          // Existing points keep their current state
        });
      }
      
      // Update BEFORE starting animations to prevent loops
      lastDatasetLength = data.length;
      
      // ALWAYS clear existing animations to prevent old slow animations
      if (animationFrame && typeof window !== 'undefined') {
        cancelAnimationFrame(animationFrame);
      }
      
      // Clear any pending batch timeouts when data changes
      batchTimeouts.forEach(timeout => clearTimeout(timeout));
      batchTimeouts = [];
      
      // Only animate if not already animating
      if (!isTransitioning && !isInitializingAnimations) {
        // Get only the new points for animation
        const newPoints = data.filter(point => {
          const anim = pointAnimations.get(point.id);
          return anim && anim.isAnimating;
        });
        
        if (newPoints.length > 0) {
          initializePointAnimations(newPoints);
        }
      }
      // Initial load animation is already started above
    }
  }
  
  // Mouse and touch interaction
  function handleCanvasClick(event) {
    const rect = canvasRef.getBoundingClientRect();
    // Handle both mouse and touch events
    const clientX = event.clientX || (event.touches && event.touches[0]?.clientX);
    const clientY = event.clientY || (event.touches && event.touches[0]?.clientY);
    
    if (!clientX || !clientY) return;
    
    const x = clientX - rect.left;
    const y = clientY - rect.top;
    
    // Find closest point
    let closestPoint = null;
    let minDistance = 20; // 20px threshold
    
    for (const point of renderedPoints) {
      const dx = x - point.x;
      const dy = y - point.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < minDistance && distance < point.radius + 5) {
        minDistance = distance;
        closestPoint = point;
      }
    }
    
    if (closestPoint) {
      onPointClick(closestPoint.data);
    }
  }
  
  // Track first render time
  let firstRenderTime = null;
  
  // Render just the canvas without checking for data changes
  function renderCanvas() {
    if (!canvasRef || !data.length) return;
    
    // Log time to first render
    if (!firstRenderTime && data.length > 0) {
      firstRenderTime = performance.now();
      console.log(`🎨 First dots rendered at ${firstRenderTime.toFixed(0)}ms`);
    }
    
    try {
      const ctx = canvasRef.getContext('2d', { 
        alpha: false, // Disable transparency for better performance
        desynchronized: true // Better performance on some browsers
      });
      const currentState = scrollStates[currentStateIndex];
      const fromState = isTransitioning ? scrollStates[previousStateIndex] : currentState;
      const toState = currentState;
    
    // Get current view bounds
    const currentView = currentState;
    const targetView = toState;
    
    if (!currentView || !targetView) return;
    
    // Interpolate between views
    const yMin = d3.interpolate(fromState.yDomain[0], targetView.yDomain[0])(interpolationT);
    const yMax = d3.interpolate(fromState.yDomain[1], targetView.yDomain[1])(interpolationT);
    // Calculate symmetric x domain around 0
    const xMinTarget = targetView.xDomain[0];
    const xMaxTarget = targetView.xDomain[1];
    const xAbsMax = Math.max(Math.abs(xMinTarget), Math.abs(xMaxTarget));
    const xMinSymmetric = -xAbsMax;
    const xMaxSymmetric = xAbsMax;
    
    const xMinFrom = fromState.xDomain[0];
    const xMaxFrom = fromState.xDomain[1];
    const xAbsMaxFrom = Math.max(Math.abs(xMinFrom), Math.abs(xMaxFrom));
    const xMinFromSymmetric = -xAbsMaxFrom;
    const xMaxFromSymmetric = xAbsMaxFrom;
    
    const xMin = d3.interpolate(xMinFromSymmetric, xMinSymmetric)(interpolationT);
    const xMax = d3.interpolate(xMaxFromSymmetric, xMaxSymmetric)(interpolationT);
    
    // Clear canvas
    ctx.fillStyle = COLORS.WHITE;
    ctx.fillRect(0, 0, width, height);
    
    // Filter relevant data
    let allRelevantData = data;
    if (isTransitioning && fromState && toState) {
      allRelevantData = data.filter(d => {
        const inFromView = fromState.filter ? fromState.filter(d) : true;
        const inToView = toState.filter ? toState.filter(d) : true;
        return inFromView || inToView;
      });
    } else {
      allRelevantData = data.filter(d => currentView.filter ? currentView.filter(d) : true);
    }
    
    // Create scales
    const xScale = d3.scaleLinear()
      .domain([xMin, xMax])
      .range([margin.left, width - margin.right]);
    
    const yScale = d3.scaleLinear()
      .domain([yMin, yMax])
      .range([height - margin.bottom, margin.top]);
    
    // Draw grid lines
    drawGridLines(ctx, xScale, yScale, xMin, xMax, yMin, yMax);
    
    // Clear rendered points for hit detection
    renderedPoints = [];
    
    // Calculate weight range for opacity scaling
    const weightRange = calculateWeightRange(allRelevantData, xScale, yScale);
    
    // Render points
    renderPoints(ctx, allRelevantData, xScale, yScale, weightRange, currentState, fromState);
    
    // Draw axes
    drawAxes(xScale, yScale);
    } catch (error) {
      console.error('Error rendering visualization:', error);
      // Clear the canvas to prevent partial renders
      if (canvasRef) {
        const ctx = canvasRef.getContext('2d');
        ctx.clearRect(0, 0, width, height);
      }
    }
  }
  
  // Main rendering function that checks for data changes
  export function renderVisualization() {
    if (!canvasRef || !data.length) return;
    
    // Check if we need to start new animations
    checkForDataChange();
    
    // Render the canvas
    renderCanvas();
  }
  
  function drawGridLines(ctx, xScale, yScale, xMin, xMax, yMin, yMax) {
    // Fade grid lines during transitions for smoother effect
    const gridOpacity = isTransitioning ? 0.3 + (interpolationT * 0.7) : 1;
    ctx.globalAlpha = gridOpacity;
    
    ctx.strokeStyle = COLORS.MEDIUM_DARK_GRAY;
    ctx.lineWidth = 0.5;
    ctx.setLineDash([]);
    
    // Vertical grid lines
    const xTickInterval = Math.max(5, Math.floor((xMax - xMin) / 10));
    for (let i = Math.ceil(xMin / xTickInterval) * xTickInterval; i <= xMax; i += xTickInterval) {
      const x = xScale(i);
      ctx.beginPath();
      ctx.moveTo(x, margin.top);
      ctx.lineTo(x, height - margin.bottom);
      ctx.stroke();
    }
    
    // Horizontal grid lines
    const yTicks = yScale.ticks(6);
    yTicks.forEach(tick => {
      const y = yScale(tick);
      ctx.beginPath();
      ctx.moveTo(margin.left, y);
      ctx.lineTo(width - margin.right, y);
      ctx.stroke();
    });
    
    ctx.globalAlpha = 1;
    
    // Draw zero line
    if (xMin <= 0 && xMax >= 0) {
      ctx.strokeStyle = COLORS.BLACK;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(xScale(0), margin.top);
      ctx.lineTo(xScale(0), height - margin.bottom);
      ctx.stroke();
    }
  }
  
  function calculateWeightRange(data, xScale, yScale) {
    let minWeight = Infinity;
    let maxWeight = -Infinity;
    
    data.forEach(d => {
      const x = xScale(d['Percentage change in net income']);
      const y = yScale(d['Market Income'] || d['Gross Income']);
      
      if (x >= margin.left && x <= width - margin.right && 
          y >= margin.top && y <= height - margin.bottom) {
        const weight = d['Household weight'] || d['Household weight'] || 1;
        minWeight = Math.min(minWeight, weight);
        maxWeight = Math.max(maxWeight, weight);
      }
    });
    
    if (minWeight === Infinity || maxWeight === -Infinity || minWeight === maxWeight) {
      minWeight = 1;
      maxWeight = 100000;
    }
    
    return { minWeight, maxWeight };
  }
  
  function renderPoints(ctx, data, xScale, yScale, weightRange, currentState, fromState) {
    const { minWeight, maxWeight } = weightRange;
    
    // Determine if we're in a zoomed state (not intro or all-households)
    const isZoomedView = currentState?.id !== 'intro' && currentState?.id !== 'all-households';
    
    // Limit rendering for performance on Safari
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    const maxPointsToRender = isSafari ? 10000 : data.length;
    const dataToRender = data.slice(0, maxPointsToRender);
    
    dataToRender.forEach(d => {
      let x = xScale(d['Percentage change in net income']);
      let y = yScale(d['Market Income'] || d['Gross Income']);
      
      // Check if point is outside bounds and clamp to edge
      const isOutOfBounds = x < margin.left || x > width - margin.right || y < margin.top || y > height - margin.bottom;
      
      // Clamp x coordinate to visible range
      if (x < margin.left) {
        x = margin.left + 5; // Small offset from edge
      } else if (x > width - margin.right) {
        x = width - margin.right - 5; // Small offset from edge
      }
      
      // Skip if y is out of bounds (we only clamp x-axis)
      if (y < margin.top || y > height - margin.bottom) return;
      
      // Determine fade opacity for transitions
      let fadeOpacity = 1;
      if (isTransitioning) {
        const inFromView = fromState?.filter ? fromState.filter(d) : true;
        const inToView = currentState?.filter ? currentState.filter(d) : true;
        
        if (!inFromView && inToView) {
          fadeOpacity = interpolationT;
        } else if (inFromView && !inToView) {
          fadeOpacity = 1 - interpolationT;
        }
      } else {
        const shouldBeVisible = currentState?.filter ? currentState.filter(d) : true;
        fadeOpacity = shouldBeVisible ? 1 : 0;
      }
      
      // Get point color
      const color = getPointColor(d['Percentage change in net income']);
      
      // Determine if highlighted
      const isGroupHighlighted = d.isHighlighted && d.stateIndex === Math.floor(currentStateIndex / 2);
      const baseViewId = currentState?.id;
      const currentRandomHousehold = randomHouseholds[baseViewId];
      // Highlight the random household for the current section (except intro and all-households)
      const isRandomHighlighted = currentRandomHousehold && 
                                d.id === currentRandomHousehold.id &&
                                baseViewId !== 'intro' && 
                                baseViewId !== 'all-households';
      const isSelectedHousehold = selectedHousehold && d.id === selectedHousehold.id;
      const isHighlighted = isGroupHighlighted || isRandomHighlighted || isSelectedHousehold;
      
      // Set radius - larger when zoomed for better visibility
      const weight = d['Household weight'] || d['Household weight'] || 1;
      const baseRadius = isZoomedView ? 2.2 : 1.8;  // Smaller dots
      let radius = isHighlighted ? (isRandomHighlighted || isSelectedHousehold ? 5 : 3.5) : baseRadius;  // Increased highlighted sizes
        
      // Calculate opacity based on weight
      const logWeight = Math.log10(weight + 1);
      const logMinWeight = Math.log10(minWeight + 1);
      const logMaxWeight = Math.log10(maxWeight + 1);
      const normalizedWeight = (logWeight - logMinWeight) / (logMaxWeight - logMinWeight);
      
      // Much higher opacity for sharper appearance
      const minOpacity = isZoomedView ? 0.7 : 0.5;   // Increased from 0.5/0.3
      const maxOpacity = isZoomedView ? 1.0 : 0.9;   // Increased from 0.95/0.85
      const opacityRange = maxOpacity - minOpacity;
      
      const weightBasedOpacity = minOpacity + (opacityRange * normalizedWeight);
      let baseOpacity = isHighlighted ? 1 : Math.min(Math.max(weightBasedOpacity, minOpacity), maxOpacity);
      
      // Apply animation effects (both existing and new staggered animations)
      const existingAnimationState = animatedHouseholds.get(d.id);
      const staggeredAnimationState = pointAnimations.get(d.id);
      
      // Apply existing animation system (for emphasis/click effects)
      if (existingAnimationState && existingAnimationState.isAnimating) {
        radius = radius * existingAnimationState.scale;
        baseOpacity = Math.min(baseOpacity * existingAnimationState.opacity, 1);
      }
      
      // Apply staggered reveal animation
      if (staggeredAnimationState) {
        radius = radius * staggeredAnimationState.scale;
        baseOpacity = baseOpacity * staggeredAnimationState.opacity;
      } else {
        // No animation state - this point shouldn't be visible yet
        baseOpacity = 0;
      }
      
      // Fade other points when showing a random household (but not for intro/all views)
      if (isRandomHighlighted && isZoomedView) {
        // This point IS the highlighted one, keep full opacity
      } else if (currentRandomHousehold && isZoomedView) {
        // There is a highlighted household but this isn't it
        // Much less aggressive fade for sharper appearance
        baseOpacity *= 0.7;  // Increased from 0.5
      }
      
      const finalOpacity = baseOpacity * fadeOpacity;
      
      if (finalOpacity > 0.01) {
        renderedPoints.push({ x, y, radius, data: d });
        
        ctx.globalAlpha = finalOpacity;
        ctx.fillStyle = color;
        
        // Draw differently if clamped to edge
        if (isOutOfBounds) {
          // Draw as a triangle pointing outward for out-of-bounds points
          ctx.beginPath();
          if (x <= margin.left + 5) {
            // Left edge - triangle pointing left
            ctx.moveTo(x + radius, y);
            ctx.lineTo(x - radius, y - radius);
            ctx.lineTo(x - radius, y + radius);
          } else if (x >= width - margin.right - 5) {
            // Right edge - triangle pointing right
            ctx.moveTo(x - radius, y);
            ctx.lineTo(x + radius, y - radius);
            ctx.lineTo(x + radius, y + radius);
          }
          ctx.closePath();
          ctx.fill();
        } else {
          // Normal circle for in-bounds points
          ctx.beginPath();
          ctx.arc(x, y, radius, 0, 2 * Math.PI);
          ctx.fill();
          
          if (isHighlighted && finalOpacity > 0.5) {
            ctx.globalAlpha = finalOpacity;
            ctx.strokeStyle = COLORS.BLACK;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }
    });
    
    ctx.globalAlpha = 1;
  }
  
  function drawAxes(xScale, yScale) {
    if (!svgRef) return;
    
    const svg = d3.select(svgRef);
    svg.selectAll('*').remove();
    
    const g = svg.append('g');
    
    // Responsive settings
    const isMobile = typeof window !== 'undefined' ? window.innerWidth <= 768 : false;
    const xAxisFontSize = isMobile ? '10px' : '14px';
    const yAxisFontSize = isMobile ? '10px' : '14px';
    
    // X-axis
    const xAxis = g.append('g')
      .attr('transform', `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(xScale)
        .ticks(isMobile ? 5 : 10)
        .tickFormat(d => `${d > 0 ? '+' : ''}${d}%`))
      .style('font-family', getFontFamily('sans'))
      .style('font-size', xAxisFontSize)
      .style('color', COLORS.DARKEST_BLUE);
    
    // Y-axis
    const yAxis = g.append('g')
      .attr('transform', `translate(${margin.left},0)`)
      .call(d3.axisLeft(yScale).ticks(isMobile ? 4 : 6).tickFormat(d => {
        // Shorter format on mobile
        if (isMobile) {
          if (d >= 1000000) return d3.format('$,.0s')(d).replace('M', 'M');
          if (d >= 1000) return d3.format('$,.0s')(d).replace('k', 'K');
          return d3.format('$,')(d);
        }
        return d3.format('$,')(d);
      }))
      .style('font-family', getFontFamily('sans'))
      .style('font-size', yAxisFontSize)
      .style('color', COLORS.DARKEST_BLUE);
    
    // Style axes
    xAxis.select('.domain').style('stroke', COLORS.BLACK).style('stroke-width', 1);
    yAxis.select('.domain').style('stroke', 'none'); // Hide y-axis line
    xAxis.selectAll('.tick line').style('stroke', COLORS.BLACK).style('stroke-width', 0.5);
    yAxis.selectAll('.tick line').style('stroke', COLORS.GRID_LINES).style('stroke-width', 0.5).style('opacity', 0.3);
    
    // Axis labels
    g.append('text')
      .attr('x', width / 2)
      .attr('y', height - margin.bottom + (isMobile ? 35 : 45))
      .attr('text-anchor', 'middle')
      .style('font-family', getFontFamily('sans'))
      .style('font-size', isMobile ? '12px' : '16px')
      .style('font-weight', '400')
      .style('fill', COLORS.DARK_GRAY)
      .text(isMobile ? 'Change in income (2026) →' : 'Change in net income (2026) →');
    
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', isMobile ? 15 : 25)
      .attr('text-anchor', 'middle')
      .style('font-family', getFontFamily('sans'))
      .style('font-size', isMobile ? '12px' : '16px')
      .style('font-weight', '400')
      .style('fill', COLORS.DARK_GRAY)
      .text(isMobile ? 'Annual income →' : 'Annual household market income →');
  }
  
  // Handle resize
  function handleResize() {
    if (typeof window === 'undefined') return; // SSR safety
    
    if (canvasRef && svgRef) {
      const container = canvasRef.parentElement;
      // Get the actual rendered dimensions
      const rect = container.getBoundingClientRect();
      width = Math.floor(rect.width);
      height = Math.floor(rect.height);
      updateMargins(); // Update margins based on viewport
      
      // Set canvas resolution to match CSS size
      canvasRef.width = width;
      canvasRef.height = height;
      canvasRef.style.width = width + 'px';
      canvasRef.style.height = height + 'px';
      
      // Ensure SVG matches exactly
      svgRef.setAttribute('width', width);
      svgRef.setAttribute('height', height);
      svgRef.style.width = width + 'px';
      svgRef.style.height = height + 'px';
      
      renderVisualization();
    }
  }
  
  // Function to reveal reserved points on scroll
  function revealReservedPoints() {
    if (revealedReserved || reservedPoints.size === 0) return;
    
    console.log(`✨ Revealing ${reservedPoints.size} reserved points on scroll`);
    revealedReserved = true;
    
    // Get reserved points and start their animation
    const reservedData = data.filter(point => reservedPoints.has(point.id));
    
    // Clear their reserved state and start animation
    reservedData.forEach(point => {
      const anim = pointAnimations.get(point.id);
      if (anim) {
        anim.isAnimating = true;
        anim.opacity = 0;
        anim.scale = 0.1;
        anim.isReserved = false; // Remove reserved flag
      }
    });
    
    // Animate the reserved points
    initializePointAnimations(reservedData);
  }
  
  // Scroll handler
  function handleScroll() {
    // In iframe, check if currentStateIndex has moved past intro
    const scrollTrigger = window.self !== window.top 
      ? currentStateIndex > 0  // In iframe, trigger on any state change past intro
      : window.scrollY > 100;  // In standalone, trigger on scroll
      
    if (!hasScrolled && scrollTrigger) {
      hasScrolled = true;
      revealReservedPoints();
    }
  }
  
  // Also trigger on state changes
  $: if (currentStateIndex > 0 && !hasScrolled) {
    handleScroll();
  }
  
  onMount(() => {
    // Clear any existing animation state from previous sessions
    pointAnimations.clear();
    lastDatasetLength = 0;
    isInitializingAnimations = false;
    if (animationFrame && typeof window !== 'undefined') {
      cancelAnimationFrame(animationFrame);
      animationFrame = null;
    }
    // Clear any pending batch timeouts
    batchTimeouts.forEach(timeout => clearTimeout(timeout));
    batchTimeouts = [];
    
    handleResize();
    if (typeof window !== 'undefined') {
      window.addEventListener('resize', handleResize);
      window.addEventListener('scroll', handleScroll, { passive: true });
    }
    
    // In iframe contexts, dimensions might settle after initial render
    const isInIframe = window.self !== window.top;
    if (isInIframe) {
      // Double-check dimensions after a short delay
      setTimeout(handleResize, 100);
      setTimeout(handleResize, 300);
    }
  });
  
  onDestroy(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('scroll', handleScroll);
    }
    // Cleanup animations
    if (animationFrame && typeof window !== 'undefined') {
      cancelAnimationFrame(animationFrame);
    }
    // Clear batch timeouts
    batchTimeouts.forEach(timeout => clearTimeout(timeout));
    pointAnimations.clear();
    isInitializingAnimations = false;
  });
  
  // Track if we're currently rendering to prevent loops
  let isRendering = false;
  
  // Re-render when data or state changes
  $: if (data.length && canvasRef && !isRendering) {
    isRendering = true;
    requestAnimationFrame(() => {
      renderVisualization();
      isRendering = false;
    });
  }
  
  // Explicit render function
  export function forceRender() {
    if (canvasRef && !isRendering) {
      isRendering = true;
      requestAnimationFrame(() => {
        renderVisualization();
        isRendering = false;
      });
    }
  }
</script>

<div class="chart-container">
  <canvas
    bind:this={canvasRef}
    class="main-canvas"
    on:click={handleCanvasClick}
    on:touchstart={handleCanvasClick}
  ></canvas>
  <svg
    bind:this={svgRef}
    class="overlay-svg"
  ></svg>
</div>

<style>
  .chart-container {
    position: relative;
    width: 100%;
    height: 100%;
  }
  
  .main-canvas {
    background: var(--app-background);
    cursor: crosshair;
    display: block;
  }
  
  .overlay-svg {
    position: absolute;
    top: 0;
    left: 0;
    pointer-events: none;
    display: block;
  }
</style>