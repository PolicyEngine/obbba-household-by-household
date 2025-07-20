# OBBBA Scatter

Data visualization application showing how tax changes affect American households.

## Features

### Deep Linking for Households

The application now supports deep linking to specific households, allowing users to:

- **Share specific household profiles**: Each household can be directly linked via URL
- **Bookmark interesting cases**: Users can save links to specific households for later reference
- **Navigate directly to households**: URLs automatically navigate to the appropriate section and household

#### How to Use Deep Links

1. **Automatic URL updates**: 
   - Navigate to any individual household view
   - The URL automatically updates to include the selected household
   - Copy the URL from your browser's address bar

2. **Share the link**: 
   - Send the URL to others
   - The link will take them directly to that specific household

3. **URL format**:
   ```
   /obbba-scatter/?household=HOUSEHOLD_ID&dataset=DATASET_NAME&section=SECTION_NAME
   ```

#### URL Parameters

- `household`: The unique household ID from the dataset
- `dataset`: The policy scenario (`tcja-expiration` or `tcja-extension`)
- `section`: The section/view name (optional - will auto-determine based on household income if not provided)

#### Example URLs

```url
# Direct link to a specific household in the middle-income individual view with TCJA expiration scenario
/obbba-scatter/?household=12345&dataset=tcja-expiration&section=middle-income-individual

# Link to household with TCJA extension scenario and automatic section detection
/obbba-scatter/?household=12345&dataset=tcja-extension

# Link to household with automatic dataset and section detection (defaults to tcja-expiration)
/obbba-scatter/?household=12345
```

#### Technical Implementation

- Uses SvelteKit's built-in URL parameter handling
- Automatically maps household income to appropriate sections
- Preserves application state across page reloads
- Smooth scrolling and transitions to the linked household

## Development

Run the development server:

```bash
npm run dev
```

## Build

Create a production build:

```bash
npm run build
```
