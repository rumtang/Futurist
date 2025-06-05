#!/bin/bash

# Fix dependencies for the frontend build

echo "🔧 Fixing dependencies..."

# Clean npm cache and node_modules
rm -rf node_modules package-lock.json .next
npm cache clean --force

# Install all production dependencies first
npm install --production

# Install dev dependencies separately
npm install --save-dev autoprefixer postcss tailwindcss @types/node @types/react @types/react-dom typescript eslint eslint-config-next

# Install remaining dev dependencies
npm install --save-dev @types/d3 @types/three @types/uuid glob

echo "✅ Dependencies fixed!"