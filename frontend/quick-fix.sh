#!/bin/bash

# Quick fix script for immediate deployment

set -e

echo "🔧 Applying quick fixes..."

# Replace the analysis page with the fixed version
cp app/analysis/page.fixed.tsx app/analysis/page.tsx

# Use the optimized config
cp next.config.optimized.js next.config.js

# Use the optimized Dockerfile
cp Dockerfile.optimized Dockerfile

echo "✅ Fixes applied!"
echo ""
echo "To deploy, run:"
echo "  ./relaunch.sh"