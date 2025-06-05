#!/bin/bash
# Local Docker deployment with WebSocket support for testing

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting local Docker deployment with WebSocket support...${NC}"

# Step 1: Stop any existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Step 2: Create optimized backend Dockerfile
echo -e "${YELLOW}Creating optimized backend Dockerfile...${NC}"
cat > Dockerfile.backend <<'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY src/ ./src/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV API_HOST=0.0.0.0
ENV DEV_MODE=false
ENV LOG_LEVEL=INFO

# Expose port
EXPOSE 8080

# Use the simple WebSocket server
CMD ["python", "-m", "uvicorn", "src.main_simple_ws:app", "--host", "0.0.0.0", "--port", "8080", "--ws-ping-interval", "20", "--ws-ping-timeout", "60"]
EOF

# Step 3: Build backend
echo -e "${YELLOW}Building backend Docker image...${NC}"
docker build -f Dockerfile.backend -t cx-futurist-backend:local .

# Step 4: Run backend
echo -e "${YELLOW}Starting backend container...${NC}"
docker run -d \
    --name cx-futurist-backend \
    -p 8080:8080 \
    -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    -e API_HOST=0.0.0.0 \
    -e PORT=8080 \
    -e DEV_MODE=false \
    -e LOG_LEVEL=INFO \
    cx-futurist-backend:local

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 5

# Check backend health
if curl -s http://localhost:8080/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    docker logs cx-futurist-backend
    exit 1
fi

# Step 5: Build frontend
echo -e "${YELLOW}Building frontend...${NC}"
cd frontend

# Create production environment file
cat > .env.production.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8080
EOF

# Install dependencies and build
npm install
npm run build

# Step 6: Run frontend
echo -e "${YELLOW}Starting frontend...${NC}"
docker build -t cx-futurist-frontend:local .
docker run -d \
    --name cx-futurist-frontend \
    -p 3000:3000 \
    -e NEXT_PUBLIC_API_URL=http://localhost:8080 \
    -e NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8080 \
    cx-futurist-frontend:local

cd ..

# Wait for frontend to start
echo -e "${YELLOW}Waiting for frontend to start...${NC}"
sleep 5

# Step 7: Test WebSocket connection
echo -e "${YELLOW}Testing WebSocket connection...${NC}"

# Create test script
cat > test-local-websocket.html <<'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
</head>
<body>
    <h1>WebSocket Connection Test</h1>
    <div id="status">Connecting...</div>
    <div id="messages"></div>
    
    <script>
        const ws = new WebSocket('ws://localhost:8080/simple-ws');
        const status = document.getElementById('status');
        const messages = document.getElementById('messages');
        
        ws.onopen = () => {
            status.textContent = '✅ Connected!';
            status.style.color = 'green';
            
            // Send test message
            ws.send(JSON.stringify({ type: 'subscribe', channel: 'all' }));
        };
        
        ws.onmessage = (event) => {
            const msg = document.createElement('div');
            msg.textContent = `📨 ${new Date().toLocaleTimeString()}: ${event.data}`;
            messages.appendChild(msg);
        };
        
        ws.onerror = (error) => {
            status.textContent = '❌ Connection error';
            status.style.color = 'red';
            console.error('WebSocket error:', error);
        };
        
        ws.onclose = () => {
            status.textContent = '🔌 Disconnected';
            status.style.color = 'orange';
        };
    </script>
</body>
</html>
EOF

# Step 8: Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Local Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Backend URL: http://localhost:8080"
echo -e "Frontend URL: http://localhost:3000"
echo -e "WebSocket endpoint: ws://localhost:8080/simple-ws"
echo -e ""
echo -e "To test:"
echo -e "  1. Open http://localhost:3000 in your browser"
echo -e "  2. Check the browser console for WebSocket connection"
echo -e "  3. Or open test-local-websocket.html in a browser"
echo -e ""
echo -e "To view logs:"
echo -e "  Backend: docker logs cx-futurist-backend"
echo -e "  Frontend: docker logs cx-futurist-frontend"
echo -e ""
echo -e "To stop:"
echo -e "  docker stop cx-futurist-backend cx-futurist-frontend"
echo -e "  docker rm cx-futurist-backend cx-futurist-frontend"
echo -e "${GREEN}========================================${NC}"