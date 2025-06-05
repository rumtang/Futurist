#!/bin/sh

# Production entrypoint script for Next.js
# This script allows runtime environment variable injection

# Create runtime config from environment variables
cat > /app/public/runtime-config.js << EOF
window.__RUNTIME_CONFIG__ = {
  NEXT_PUBLIC_API_URL: "${NEXT_PUBLIC_API_URL:-http://localhost:8080}",
  NEXT_PUBLIC_WEBSOCKET_URL: "${NEXT_PUBLIC_WEBSOCKET_URL:-ws://localhost:8080}"
};
EOF

echo "Runtime configuration:"
cat /app/public/runtime-config.js

# Start the Next.js application
exec node server.js