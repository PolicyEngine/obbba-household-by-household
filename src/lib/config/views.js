// Base view configurations for scroll states
export const baseViews = [
  {
    id: 'intro',
    title: "How tax changes affect every American household",
    groupText: "Each dot represents a household, positioned by their income and how much they gain or lose under the proposed tax changes. Green dots show households that benefit, red shows those that face increases.",
    view: {
      xDomain: [-15, 15],
      yDomain: [0, 350000],
      filter: d => d['Gross Income'] < 350000,
      highlightGroup: null
    }
  },
  {
    id: 'lower-income', 
    title: "Lower-income households under $50,000",
    groupText: "Households earning under $50,000 see varied outcomes. While many benefit from Child Tax Credit expansions and TCJA extensions, some undocumented families lose access to credits due to new SSN requirements. Individuals in the bottom decile will gain an average of $213, while the top decile will gain an average of $13,075.",
    view: {
      xDomain: [-15, 15],
      yDomain: [0, 50000],
      filter: d => d['Gross Income'] >= 0 && d['Gross Income'] < 50000,
      highlightGroup: 'lower'
    }
  },
  {
    id: 'middle-income',
    title: "Middle-income households ($50,000 - $200,000)", 
    groupText: "This broad middle class benefits significantly from TCJA extensions, enhanced Child Tax Credits, and new deductions for tips and overtime pay. Seniors in this range gain substantially from the additional $6,000 senior deduction. These households typically see Net Income increases from the tax provisions.",
    view: {
      xDomain: [-25, 25],
      yDomain: [50000, 200000],
      filter: d => d['Gross Income'] >= 50000 && d['Gross Income'] < 200000,
      highlightGroup: 'middle'
    }
  },
  {
    id: 'upper-income',
    title: "Upper-income households ($200,000 - $1 million)",
    groupText: "Higher-income households generally benefit the most in dollar terms from TCJA extensions. Rate reductions, business income deductions, and estate tax reforms provide substantial savings. However, some face increases due to SALT limitations and other targeted provisions.",
    view: {
      xDomain: [-40, 60],
      yDomain: [200000, 1000000],
      filter: d => d['Gross Income'] >= 200000 && d['Gross Income'] < 1000000,
      highlightGroup: 'upper'
    }
  },
  {
    id: 'highest-income',
    title: "The highest-income households (over $1 million)",
    groupText: "The wealthiest Americans see the largest absolute gains from these tax changes. Estate tax reforms, business income deductions, and rate cuts combine to provide significant benefits, though SALT caps and other provisions create some variation in outcomes.",
    view: {
      xDomain: [-50, 300],
      yDomain: [1000000, 10000000],
      filter: d => d['Gross Income'] >= 1000000,
      highlightGroup: 'highest'
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
      text: baseView.groupText,
      viewType: 'group'
    });
    
    // Add individual view (except for intro)
    if (baseIndex > 0) {
      scrollStates.push({
        id: baseView.id + '-individual',
        ...baseView.view,
        title: baseView.title + ' — individual profile',
        text: 'Meet a specific household affected by these changes.',
        viewType: 'individual'
      });
    }
  });
  
  return scrollStates;
}