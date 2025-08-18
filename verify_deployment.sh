#!/bin/bash

echo "🔍 Verifying Monkey Coder deployment..."
echo ""

# Check if frontend is being served
echo "1. Checking frontend at root URL:"
RESPONSE=$(curl -s https://coder.fastmonkey.au/ | head -50)
if echo "$RESPONSE" | grep -q "root"; then
    echo "   ✅ Frontend detected (found root element)"
elif echo "$RESPONSE" | grep -q "Monkey Coder API"; then
    echo "   ❌ Still serving API fallback page"
else
    echo "   ⚠️  Unknown response"
fi

echo ""
echo "2. Checking API health endpoint:"
curl -s https://coder.fastmonkey.au/health | jq '.' 2>/dev/null || echo "   ❌ API health check failed"

echo ""
echo "3. Checking for Next.js static assets:"
ASSET_CHECK=$(curl -sI https://coder.fastmonkey.au/_next/static/chunks/main.js | head -1)
if echo "$ASSET_CHECK" | grep -q "200"; then
    echo "   ✅ Next.js assets are being served"
else
    echo "   ❌ Next.js assets not found"
fi

echo ""
echo "4. Checking for index.html:"
INDEX_CHECK=$(curl -sI https://coder.fastmonkey.au/index.html | head -1)
if echo "$INDEX_CHECK" | grep -q "200"; then
    echo "   ✅ index.html is accessible"
else
    echo "   ❌ index.html not found"
fi

echo ""
echo "Deployment verification complete!"