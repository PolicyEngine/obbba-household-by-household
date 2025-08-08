#!/bin/bash

echo "🚀 Building app with PolicyEngine base path..."
npm run build:policyengine

echo ""
echo "✅ Build complete!"
echo ""
echo "📦 Starting preview server..."
npm run preview:policyengine &

# Wait a moment for server to start
sleep 2

echo ""
echo "🌐 Server is running!"
echo ""
echo "👉 To test the app, open your browser to:"
echo "   http://localhost:4173/us/obbba-household-by-household/"
echo ""
echo "🔗 Test these deep links:"
echo "   http://localhost:4173/us/obbba-household-by-household/?household=39519&baseline=tcja-expiration"
echo "   http://localhost:4173/us/obbba-household-by-household/?household=12345&baseline=tcja-extension"
echo ""
echo "📝 Note: The app won't load at http://localhost:4173/ because it's built with a base path"
echo ""
echo "Press Ctrl+C to stop the server"

# Keep script running
wait 