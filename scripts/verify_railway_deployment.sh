#!/bin/bash
# Railway deployment verification script
set -e

echo "🔍 Railway Deployment Verification"
echo "=================================="

# Test 1: Health endpoint
echo "Testing health endpoint..."
if curl -f -s https://coder.fastmonkey.au/health > /dev/null; then
    echo "✅ Health endpoint responding"
else
    echo "❌ Health endpoint failed"
    exit 1
fi

# Test 2: Frontend accessibility
echo "Testing frontend availability..."
if curl -f -s https://coder.fastmonkey.au/ > /dev/null; then
    echo "✅ Frontend accessible"
else
    echo "❌ Frontend not accessible"
    exit 1
fi

# Test 3: API functionality
echo "Testing API functionality..."
if curl -f -s https://coder.fastmonkey.au/api/v1/health > /dev/null; then
    echo "✅ API endpoints responding"
else
    echo "❌ API endpoints failed"
    exit 1
fi

echo "🎉 All deployment verification tests passed!"
