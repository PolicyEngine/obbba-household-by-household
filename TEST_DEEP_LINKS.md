# Testing Deep Links

## Quick Start Testing

### 1. Test Direct Links (Local Development)

First, start your dev server:
```bash
npm run dev
```

Then test these URLs directly in your browser:
- http://localhost:5173/?household=39519&baseline=tcja-expiration
- http://localhost:5173/?household=12345&baseline=tcja-extension
- http://localhost:5173/?household=67890

**Expected behavior:**
- The app should load and automatically navigate to the specified household
- The scatter plot should highlight the selected household
- The page should scroll to the appropriate income section

### 2. Test Iframe Integration (Simulates PolicyEngine)

1. Open `test-deployment.html` in your browser (just double-click the file)
2. Make sure your dev server is running (`npm run dev`)
3. Click the test links to see how deep linking works in an iframe

**What to look for:**
- The status box shows current URLs and parameters
- Clicking links updates both parent and iframe URLs
- The app responds to parameter changes
- Console shows message passing between parent and iframe

### 3. Test Production Build

Build with PolicyEngine path:
```bash
npm run build:policyengine
```

Then serve the build locally:
```bash
npm run preview
```

Test with these URLs (adjust port if needed):
- http://localhost:4173/us/obbba-household-explorer/?household=39519&baseline=tcja-expiration

## Detailed Test Cases

### Test Case 1: Direct Navigation
1. Go to: http://localhost:5173/?household=39519&baseline=tcja-expiration
2. **Verify:**
   - Household 39519 is selected (highlighted in chart)
   - Baseline is set to "TCJA Expiration"
   - Page scrolls to appropriate section based on household income

### Test Case 2: URL Updates When Selecting Household
1. Start at: http://localhost:5173/
2. Click on any household in the scatter plot
3. **Verify:**
   - URL updates to include household ID and baseline
   - Browser back button works to deselect

### Test Case 3: Switching Baselines Preserves Selection
1. Go to: http://localhost:5173/?household=39519&baseline=tcja-expiration
2. Use the baseline switcher in the header
3. **Verify:**
   - Household remains selected
   - URL updates with new baseline
   - Same household is highlighted in new dataset

### Test Case 4: Copy Link Functionality
1. Select any household
2. Click "Copy link" button in household profile
3. **Verify:**
   - Link is copied to clipboard
   - When in iframe, link uses PolicyEngine URL
   - Pasted link includes household and baseline parameters

### Test Case 5: Iframe Message Passing
1. Open `test-deployment.html`
2. Open browser console (F12)
3. Click different test links
4. **Verify in console:**
   - "Received message from iframe" logs
   - "Updated parent URL" logs
   - URLs sync between parent and iframe

## Debugging Tips

### Check Console for Errors
Open browser console (F12) and look for:
- "Found parameters in parent URL" - indicates iframe parameter detection
- "handleUrlParams called with" - shows parameter parsing
- Any error messages

### Verify Parameter Detection
Add this to your browser console:
```javascript
// Check current parameters
console.log('Current URL:', window.location.href);
console.log('Query params:', new URLSearchParams(window.location.search).toString());
console.log('Is in iframe:', window.self !== window.top);
```

### Test URL Building
In the app, open console and type:
```javascript
// See what URL would be copied
const url = new URL(window.location.href);
url.searchParams.set('household', '12345');
url.searchParams.set('baseline', 'tcja-expiration');
console.log('Built URL:', url.toString());
```

## Common Issues and Solutions

### Issue: Parameters not detected in iframe
**Solution:** Check that parent page is passing parameters to iframe src

### Issue: URL updates but household not selected
**Solution:** Check if household ID exists in current dataset

### Issue: Copy link uses wrong domain
**Solution:** The app detects iframe context and uses PolicyEngine URL automatically

## Testing Checklist

- [ ] Direct URL navigation works
- [ ] URL updates when selecting households
- [ ] Browser back/forward navigation works
- [ ] Copy link produces correct URLs
- [ ] Iframe parameter passing works
- [ ] Switching datasets preserves selection
- [ ] Deep links scroll to correct section
- [ ] Console shows no errors 