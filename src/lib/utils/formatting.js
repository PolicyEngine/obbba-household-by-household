// Consistent number formatters
export const fmtUSD = new Intl.NumberFormat('en-US', { 
  style: 'currency', 
  currency: 'USD', 
  maximumFractionDigits: 0 
});

export const fmtPct = new Intl.NumberFormat('en-US', { 
  style: 'percent', 
  minimumFractionDigits: 1, 
  maximumFractionDigits: 1 
});

// Formatting functions
export function formatCurrency(value) {
  return fmtUSD.format(Math.round(value));
}

export function formatPercentage(value) {
  const formatted = fmtPct.format(value / 100); // Convert to decimal for Intl formatter
  return value >= 0 ? '+' + formatted : formatted;
}

export function formatDollarChange(value) {
  const formatted = fmtUSD.format(Math.abs(Math.round(value)));
  return value >= 0 ? '+' + formatted : '-' + formatted;
}

// Get font family from type
export function getFontFamily(type = 'sans') {
  const fontMap = {
    'serif': "'Roboto Serif', serif",
    'sans': "'Roboto', sans-serif",
    'mono': "'Roboto Mono', monospace"
  };
  return fontMap[type] || fontMap['sans'];
}