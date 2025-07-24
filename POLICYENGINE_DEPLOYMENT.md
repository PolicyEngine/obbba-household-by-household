# PolicyEngine Deployment Guide

## Deep Linking Issues and Solutions

### The Problem

Deep links like `https://policyengine.org/us/obbba-household-by-household?household=39519&baseline=tcja-expiration` are not working because:

1. **Base Path Mismatch**: The app is built with base path `/obbba-scatter` but deployed at `/us/obbba-household-by-household`
2. **Iframe Parameter Passing**: When embedded as an iframe, URL parameters from the parent page aren't automatically passed to the iframe src

### Solution 1: Build with Correct Base Path

When building for PolicyEngine deployment, use the correct base path:

```bash
# Build with PolicyEngine base path
BASE_PATH=/us/obbba-household-by-household npm run build
```

### Solution 2: Proper Iframe Integration

PolicyEngine needs to:

1. **Pass parameters to iframe src**:
```javascript
// Instead of:
<iframe src="/us/obbba-household-by-household/"></iframe>

// Use:
<iframe src="/us/obbba-household-by-household/?household=39519&baseline=tcja-expiration"></iframe>
```

2. **Handle parameter synchronization** between parent and iframe (see `policyengine-integration.html` for example)

### Solution 3: Alternative Deployment Approach

If PolicyEngine can't modify their iframe integration, consider:

1. **Direct deployment** (not in iframe) - This would make deep links work naturally
2. **Proxy configuration** to handle the base path mismatch
3. **URL parameter forwarding** via postMessage API

### Testing Deep Links

To test if deep links are working:

1. Direct URL: `https://your-deployment.com/us/obbba-household-by-household/?household=39519&baseline=tcja-expiration`
2. Should automatically:
   - Load the specified household (39519)
   - Set the baseline to "tcja-expiration"
   - Scroll to the appropriate section based on household income

### Quick Fix for PolicyEngine

The quickest fix is to ensure the iframe src includes URL parameters:

```javascript
// In PolicyEngine's code where they embed the iframe
const currentParams = new URLSearchParams(window.location.search);
const iframeSrc = `/us/obbba-household-by-household/${currentParams.toString() ? '?' + currentParams.toString() : ''}`;
document.getElementById('obbba-iframe').src = iframeSrc;
```

### Building for Different Environments

```json
// package.json scripts
{
  "scripts": {
    "build:github": "vite build",
    "build:policyengine": "BASE_PATH=/us/obbba-household-by-household vite build"
  }
}
```

## Contact

If you need help with deployment or have questions about the integration, please open an issue in the repository. 