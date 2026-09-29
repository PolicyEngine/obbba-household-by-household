#!/bin/bash
# Build the policyengine.org bundle and serve it the way the Vercel origin
# does (vercel.json redirects and rewrites, via serve-policyengine.js).
set -euo pipefail

PORT="${PORT:-4173}"
ORIGIN="http://localhost:${PORT}"

if [ ! -d node_modules/@vercel/routing-utils ]; then
  echo "Installing @vercel/routing-utils (not saved to package.json)..."
  npm install --no-save @vercel/routing-utils@6.6.0
fi

echo "Building with BASE_PATH=/us/obbba-households..."
npm run build:policyengine

echo ""
echo "Try:"
echo "  ${ORIGIN}/us/obbba-households"
echo "  ${ORIGIN}/us/obbba-households?household=39519&baseline=tcja-expiration"
echo "  ${ORIGIN}/us/obbba-households/explore"
echo "  ${ORIGIN}/us/obbba-households/paper"
echo "  ${ORIGIN}/us/obbba-household-explorer?household=39519  (old slug: redirects)"
echo ""

PORT="${PORT}" npm run serve:policyengine
