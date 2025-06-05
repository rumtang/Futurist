#!/bin/bash
# WebSocket-optimized deployment script for CX Futurist AI

set -euo pipefail

# Configuration
PROJECT_ID="insightcommand-461701"
REGION="us-central1"
BACKEND_SERVICE="cx-futurist-backend"
FRONTEND_SERVICE="cx-futurist-frontend"
REPO_NAME="cx-futurist"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting WebSocket-optimized deployment...${NC}"

# Step 1: Set up project
echo -e "${YELLOW}Setting up GCP project...${NC}"
gcloud config set project $PROJECT_ID

# Step 2: Enable required services
echo -e "${YELLOW}Enabling required GCP services...${NC}"
gcloud services enable run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com

# Step 3: Create Artifact Registry repository if it doesn't exist
echo -e "${YELLOW}Setting up Artifact Registry...${NC}"
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION --format="value(name)" 2>/dev/null; then
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="CX Futurist AI Docker images"
fi

# Step 4: Create simplified Dockerfile for backend
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

# Use the simple WebSocket server
CMD ["python", "-m", "uvicorn", "src.main_simple_ws:app", "--host", "0.0.0.0", "--port", "8080", "--ws-ping-interval", "20", "--ws-ping-timeout", "60"]
EOF

# Step 5: Build and push backend image
echo -e "${YELLOW}Building backend Docker image...${NC}"
docker build -f Dockerfile.backend -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest .

echo -e "${YELLOW}Pushing backend image...${NC}"
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest

# Step 6: Deploy backend with WebSocket support
echo -e "${YELLOW}Deploying backend service...${NC}"
gcloud run deploy $BACKEND_SERVICE \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --port=8080 \
    --timeout=3600 \
    --memory=2Gi \
    --cpu=2 \
    --max-instances=10 \
    --min-instances=1 \
    --set-env-vars="API_HOST=0.0.0.0,DEV_MODE=false,LOG_LEVEL=INFO" \
    --session-affinity \
    --use-http2

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format="value(status.url)")
echo -e "${GREEN}Backend deployed at: $BACKEND_URL${NC}"

# Step 7: Build frontend with correct WebSocket URL
echo -e "${YELLOW}Building frontend with WebSocket configuration...${NC}"

# Update frontend environment
cd frontend
cat > .env.production.local <<EOF
NEXT_PUBLIC_API_URL=$BACKEND_URL
NEXT_PUBLIC_WEBSOCKET_URL=$BACKEND_URL
EOF

# Build frontend
npm install
npm run build

# Step 8: Deploy frontend
echo -e "${YELLOW}Building frontend Docker image...${NC}"
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest

echo -e "${YELLOW}Deploying frontend service...${NC}"
gcloud run deploy $FRONTEND_SERVICE \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --port=3000 \
    --memory=1Gi \
    --cpu=1 \
    --max-instances=5 \
    --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL,NEXT_PUBLIC_WEBSOCKET_URL=$BACKEND_URL"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format="value(status.url)")

# Step 9: Test WebSocket connection
echo -e "${YELLOW}Testing WebSocket connection...${NC}"
cd ..

# Create test script
cat > test-websocket-connection.js <<'EOF'
const WebSocket = require('ws');

const backendUrl = process.argv[2];
const wsUrl = backendUrl.replace('https://', 'wss://') + '/simple-ws';

console.log('Testing WebSocket connection to:', wsUrl);

const ws = new WebSocket(wsUrl);

ws.on('open', () => {
    console.log('✅ WebSocket connected successfully!');
    
    // Test subscribe
    ws.send(JSON.stringify({ type: 'subscribe', channel: 'all' }));
    
    // Test ping
    setTimeout(() => {
        ws.send(JSON.stringify({ type: 'ping' }));
    }, 1000);
    
    // Close after 5 seconds
    setTimeout(() => {
        ws.close();
        process.exit(0);
    }, 5000);
});

ws.on('message', (data) => {
    console.log('📨 Received:', data.toString());
});

ws.on('error', (error) => {
    console.error('❌ WebSocket error:', error);
    process.exit(1);
});

ws.on('close', () => {
    console.log('WebSocket closed');
});

setTimeout(() => {
    console.error('❌ Connection timeout');
    process.exit(1);
}, 10000);
EOF

# Install ws module if needed
npm install ws

# Run test
node test-websocket-connection.js "$BACKEND_URL"

# Step 10: Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Backend URL: $BACKEND_URL"
echo -e "Frontend URL: $FRONTEND_URL"
echo -e "WebSocket endpoint: ${BACKEND_URL}/simple-ws"
echo -e ""
echo -e "Test the connection:"
echo -e "  1. Open: $FRONTEND_URL"
echo -e "  2. Check browser console for WebSocket connection"
echo -e "  3. Look for 'WebSocket connected' message"
echo -e "${GREEN}========================================${NC}"