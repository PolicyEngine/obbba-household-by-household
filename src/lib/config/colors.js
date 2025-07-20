// PolicyEngine Color Constants
export const COLORS = {
  BLACK: "#000000",
  BLUE_98: "#F7FAFD",
  BLUE: "#2C6496",
  BLUE_LIGHT: "#D8E6F3",
  BLUE_PRESSED: "#17354F",
  DARK_BLUE_HOVER: "#1d3e5e",
  DARK_GRAY: "#616161",
  DARK_RED: "#b50d0d",
  DARKEST_BLUE: "#0C1A27",
  GRAY: "#808080",
  LIGHT_GRAY: "#F2F2F2",
  MEDIUM_DARK_GRAY: "#D2D2D2",
  MEDIUM_LIGHT_GRAY: "#BDBDBD",
  TEAL_ACCENT: "#39C6C0",
  TEAL_LIGHT: "#F7FDFC",
  TEAL_MEDIUM: "#2D9E99",
  TEAL_PRESSED: "#227773",
  WHITE: "#FFFFFF"
};

// Application Color Mappings
export const APP_COLORS = {
  background: COLORS.WHITE,
  textPrimary: COLORS.DARKEST_BLUE,
  textSecondary: COLORS.DARK_GRAY,
  axisGrid: COLORS.BLACK,
  gridLines: COLORS.MEDIUM_DARK_GRAY,
  scatterPositive: COLORS.TEAL_MEDIUM,
  scatterNegative: COLORS.DARK_GRAY,
  scatterNeutral: COLORS.MEDIUM_DARK_GRAY,
  border: COLORS.MEDIUM_DARK_GRAY,
  hover: COLORS.BLUE_98
};

// Get color for data point based on change value
export function getPointColor(change) {
  if (Math.abs(change) < 0.1) {
    return APP_COLORS.scatterNeutral;
  } else if (change > 0) {
    return APP_COLORS.scatterPositive;
  } else {
    return APP_COLORS.scatterNegative;
  }
}