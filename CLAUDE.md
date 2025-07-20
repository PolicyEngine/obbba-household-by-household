# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
- **Start dev server**: `npm run dev` - Runs the SvelteKit development server with hot reload
- **Build for production**: `npm run build` - Creates an optimized production build in the `build/` directory
- **Preview production build**: `npm run preview` - Serves the production build locally for testing

### Code Quality
- No linting or type checking commands are currently configured. Consider asking the user if they want to add these.

## Architecture Overview

This is a SvelteKit-based data visualization application that shows how tax policy changes affect American households through an interactive scatter plot.

### Key Technologies
- **SvelteKit 2.0** with static adapter for GitHub Pages deployment
- **Svelte 5** for reactive UI components
- **D3.js v7.9** for data visualization and chart rendering
- **PapaParse** for CSV data parsing
- **Canvas + SVG hybrid rendering** for performance with large datasets

### Application Structure

The app is a single-page application (`src/routes/+page.svelte`) that:
1. Loads household tax data from CSV files in `/static/`
2. Renders an interactive scatter plot showing income vs. tax changes
3. Implements scroll-based storytelling to reveal different income groups
4. Supports deep linking to specific households via URL parameters
5. Allows switching between TCJA expiration and extension scenarios

### Key Features Implementation

**Data Visualization**:
- Canvas rendering for performance with thousands of data points
- SVG overlay for interactive elements and selections
- Custom hit detection for mouse interactions with canvas points

**URL-based Navigation**:
- Parameters: `household`, `dataset`, `section`
- Automatic section detection based on household income
- State preservation across page reloads

**Scroll-based Sections**:
- Progressive disclosure of income groups (lowest 20%, middle class, etc.)
- Animated transitions between sections
- Random household spotlights for each group

### Important Patterns

1. **State Management**: Uses Svelte stores and reactive statements for URL synchronization
2. **Performance**: Canvas for bulk rendering, SVG for interactivity
3. **Responsive Design**: Adapts to mobile and desktop viewports
4. **Color Scheme**: Uses PolicyEngine's brand colors defined in COLORS constant

### Data Files
- `/static/Detailed_Reform_Effect_of_TCJA_Expiration.csv`
- `/static/Detailed_Current_Law_TCJA_Extension.csv`

Each CSV contains household-level tax impact data with columns for income, tax changes, and demographic information.

## Development Notes

- The app is configured for deployment to GitHub Pages with base path `/obbba-scatter`
- No TypeScript despite presence of tsconfig in temp files
- No test framework configured
- Uses ES modules throughout (`"type": "module"` in package.json)