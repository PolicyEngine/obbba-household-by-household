import { createServer } from 'http';
import { readFileSync } from 'fs';
import { join, extname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
const buildDir = join(__dirname, 'build');
const basePath = '/us/obbba-household-explorer';

const mimeTypes = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpg',
  '.svg': 'image/svg+xml',
  '.csv': 'text/csv'
};

const server = createServer((req, res) => {
  let filePath = req.url;
  
  // Remove base path if present
  if (filePath.startsWith(basePath)) {
    filePath = filePath.slice(basePath.length);
  }
  
  // Default to index.html for root
  if (filePath === '/' || filePath === '') {
    filePath = '/index.html';
  }
  
  // For any route without extension, serve index.html (SPA fallback)
  if (!extname(filePath)) {
    filePath = '/index.html';
  }
  
  // Remove query string
  filePath = filePath.split('?')[0];
  
  try {
    const fullPath = join(buildDir, filePath);
    const content = readFileSync(fullPath);
    const ext = extname(filePath);
    const contentType = mimeTypes[ext] || 'application/octet-stream';
    
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(content);
  } catch (error) {
    // Serve index.html for 404s (SPA fallback)
    try {
      const indexPath = join(buildDir, 'index.html');
      const indexContent = readFileSync(indexPath);
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(indexContent);
    } catch (indexError) {
      res.writeHead(404);
      res.end('Not found');
    }
  }
});

const PORT = 4173;
server.listen(PORT, () => {
  console.log(`
🚀 PolicyEngine test server running!

📍 Base URL:
   http://localhost:${PORT}${basePath}/

🔗 Test these deep links:
   http://localhost:${PORT}${basePath}/?household=39519&baseline=tcja-expiration
   http://localhost:${PORT}${basePath}/?household=12345&baseline=tcja-extension

Press Ctrl+C to stop the server
  `);
}); 