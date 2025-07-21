<script>
  import { onMount } from 'svelte';
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
  
  // Chart dimensions
  let margin = { top: 60, right: 100, bottom: 100, left: 120 };
  let width = 900;
  let height = 600;
  
  // Responsive margins
  function updateMargins() {
    const viewportWidth = window.innerWidth;
    if (viewportWidth <= 480) {
      margin = { top: 40, right: 15, bottom: 50, left: 50 };
    } else if (viewportWidth <= 768) {
      margin = { top: 50, right: 30, bottom: 70, left: 65 };
    } else {
      margin = { top: 60, right: 100, bottom: 100, left: 120 };
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
  
  // Main rendering function
  export function renderVisualization() {
    if (!canvasRef || !data.length) return;
    
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
      const x = xScale(d['Percentage Change in Net Income']);
      const y = yScale(d['Gross Income']);
      
      if (x >= margin.left && x <= width - margin.right && 
          y >= margin.top && y <= height - margin.bottom) {
        const weight = d['Household weight'] || d['Household Weight'] || 1;
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
    
    // Limit rendering for performance on Safari
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    const maxPointsToRender = isSafari ? 10000 : data.length;
    const dataToRender = data.slice(0, maxPointsToRender);
    
    dataToRender.forEach(d => {
      let x = xScale(d['Percentage Change in Net Income']);
      let y = yScale(d['Gross Income']);
      
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
      const color = getPointColor(d['Percentage Change in Net Income']);
      
      // Determine if highlighted
      const isGroupHighlighted = d.isHighlighted && d.stateIndex === Math.floor(currentStateIndex / 2);
      const baseViewId = scrollStates[Math.floor(currentStateIndex / 2)]?.id?.replace('-individual', '');
      const currentRandomHousehold = randomHouseholds[baseViewId];
      const isIndividualHighlighted = currentState?.viewType === 'individual' && 
                                     currentRandomHousehold && 
                                     d.id === currentRandomHousehold.id;
      const isSelectedHousehold = selectedHousehold && d.id === selectedHousehold.id;
      const isHighlighted = isGroupHighlighted || isIndividualHighlighted || isSelectedHousehold;
      
      // Set radius
      const weight = d['Household weight'] || d['Household Weight'] || 1;
      let radius = isHighlighted ? (isIndividualHighlighted || isSelectedHousehold ? 6 : 4) : 2;
      
      // Calculate opacity based on weight
      const logWeight = Math.log10(weight + 1);
      const logMinWeight = Math.log10(minWeight + 1);
      const logMaxWeight = Math.log10(maxWeight + 1);
      const normalizedWeight = (logWeight - logMinWeight) / (logMaxWeight - logMinWeight);
      const weightBasedOpacity = 0.3 + (0.55 * normalizedWeight);
      let baseOpacity = isHighlighted ? 1 : Math.min(Math.max(weightBasedOpacity, 0.3), 0.85);
      
      // Apply animation effects
      const animationState = animatedHouseholds.get(d.id);
      if (animationState && animationState.isAnimating) {
        radius = radius * animationState.scale;
        baseOpacity = Math.min(baseOpacity * animationState.opacity, 1);
      }
      
      // Fade other points during individual view
      if (currentState?.viewType === 'individual' && !isIndividualHighlighted) {
        baseOpacity *= 0.3;
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
    const isMobile = window.innerWidth <= 768;
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
      .attr('y', height - (isMobile ? 5 : 30))
      .attr('text-anchor', 'middle')
      .style('font-family', getFontFamily('sans'))
      .style('font-size', isMobile ? '12px' : '16px')
      .style('font-weight', '400')
      .style('fill', COLORS.DARK_GRAY)
      .text(isMobile ? 'Change in income →' : 'Change in net income →');
    
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
    if (canvasRef && svgRef) {
      const container = canvasRef.parentElement;
      width = container.clientWidth;
      height = container.clientHeight;
      updateMargins(); // Update margins based on viewport
      canvasRef.width = width;
      canvasRef.height = height;
      svgRef.setAttribute('width', width);
      svgRef.setAttribute('height', height);
      renderVisualization();
    }
  }
  
  onMount(() => {
    handleResize();
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  });
  
  // Re-render when data or state changes
  $: if (data.length && canvasRef) {
    renderVisualization();
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
    width: 100%;
    height: 100%;
  }
  
  .overlay-svg {
    position: absolute;
    top: 0;
    left: 0;
    pointer-events: none;
  }
</style>