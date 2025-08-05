// Base view configurations for scroll states
export const baseViews = [
  {
    id: 'intro',
    title: "The One Big Beautiful Bill Act, household by household",
    groupText: "On July 4, President Donald Trump signed into law the One Big Beautiful Bill Act (OBBBA). The bill extended the 2017 tax cuts, enacted additional tax reforms, and reduced spending on programs like Medicaid.<br><br>We've calculated how these changes will affect 20,000 representative households in 2026. As you scroll, you'll see how impacts vary across income levels—with patterns emerging as incomes rise.",
    view: {
      xDomain: [-20, 20],
      yDomain: [0, 350000],
      filter: d => d['Market Income'] < 350000,
      highlightGroup: null
    }
  },
  {
    id: 'lower-income', 
    title: "Households with income below $50,000",
    groupText: null, // Will be dynamically generated with statistics
    view: {
      xDomain: [-20, 20],
      yDomain: [0, 50000],
      filter: d => d['Market Income'] >= 0 && d['Market Income'] < 50000,
      highlightGroup: 'lower'
    }
  },
  {
    id: 'middle-income',
    title: "Households with income $50,000 to $200,000", 
    groupText: null, // Will be dynamically generated with statistics
    view: {
      xDomain: [-20, 20],
      yDomain: [50000, 200000],
      filter: d => d['Market Income'] >= 50000 && d['Market Income'] < 200000,
      highlightGroup: 'middle'
    }
  },
  {
    id: 'upper-income',
    title: "Households with income $200,000 to $1 million",
    groupText: null, // Will be dynamically generated with statistics
    view: {
      xDomain: [-20, 20],
      yDomain: [200000, 1000000],
      filter: d => d['Market Income'] >= 200000 && d['Market Income'] < 1000000,
      highlightGroup: 'upper'
    }
  },
  {
    id: 'highest-income',
    title: "Households with income over $1 million",
    groupText: null, // Will be dynamically generated with statistics
    view: {
      xDomain: [-20, 20],
      yDomain: [1000000, 10000000],
      filter: d => d['Market Income'] >= 1000000,
      highlightGroup: 'highest'
    }
  },
  {
    id: 'all-households',
    title: "All households",
    groupText: "Overall, OBBBA affects {totalPercentage}% of households. The median household gains {medianImpact}% in net income.<br><br>Visit <a href='https://policyengine.org' target='_blank' style='color: var(--primary-blue); text-decoration: underline;'>PolicyEngine.org</a> to explore more of our free, open source tools and policy research. Calculate your own tax impact, design custom reforms, and analyze their effects on poverty, inequality, and government revenues.",
    view: {
      xDomain: [-20, 20],
      yDomain: [0, 10000000],
      filter: d => true,
      highlightGroup: null
    }
  }
];

// Generate scroll states from base views (group + individual views)
export function generateScrollStates() {
  const scrollStates = [];
  
  baseViews.forEach((baseView, baseIndex) => {
    // Add group view
    scrollStates.push({
      id: baseView.id,
      ...baseView.view,
      title: baseView.title,
      description: baseView.groupText,
      viewType: 'group'
    });
    
    // Skip individual views - all income sections now have integrated profiles
  });
  
  return scrollStates;
}

// Export the generated scroll states
export const scrollStates = generateScrollStates();