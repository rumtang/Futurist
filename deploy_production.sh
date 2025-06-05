#!/bin/bash

# Deploy CX Futurist AI Backend with WebSocket support

set -e

echo "🚀 Deploying CX Futurist AI Production Backend with WebSocket Support"
echo "===================================================================="

# Configuration
PROJECT_ID="gen-agentic"
REGION="us-central1"
SERVICE_NAME="cx-futurist-api"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Verify files exist
echo -e "\n${YELLOW}📁 Verifying required files...${NC}"
required_files=(
    "requirements-production.txt"
    "Dockerfile.production"
    "cloudbuild-production.yaml"
    "src/main_production.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ✅ $file"
    else
        echo -e "  ${RED}❌ Missing: $file${NC}"
        exit 1
    fi
done

# Step 2: Test locally (optional)
echo -e "\n${YELLOW}🧪 Do you want to test locally first? (y/N)${NC}"
read -r test_local

if [[ $test_local =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Starting local server for testing...${NC}"
    
    # Create a temporary virtual environment for testing
    python -m venv test_venv
    source test_venv/bin/activate
    pip install -r requirements-production.txt
    
    # Start server in background
    python -m uvicorn src.main_production:app --port 8080 &
    SERVER_PID=$!
    
    # Wait for server to start
    sleep 5
    
    # Run tests
    python test_websocket_local.py
    
    # Stop server
    kill $SERVER_PID
    deactivate
    rm -rf test_venv
    
    echo -e "\n${YELLOW}Continue with deployment? (y/N)${NC}"
    read -r continue_deploy
    
    if [[ ! $continue_deploy =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
fi

# Step 3: Submit to Cloud Build
echo -e "\n${YELLOW}🏗️  Submitting to Cloud Build...${NC}"
echo "This will:"
echo "  1. Build a minimal Docker image (~200MB vs 2GB)"
echo "  2. Deploy with WebSocket endpoints (/ws and /simple-ws)"
echo "  3. Set up with 1 CPU and 1GB RAM"
echo "  4. Enable auto-scaling with min 1 instance"

echo -e "\n${YELLOW}Proceed with deployment? (y/N)${NC}"
read -r proceed

if [[ ! $proceed =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Submit the build
gcloud builds submit \
    --config=cloudbuild-production.yaml \
    --project=$PROJECT_ID \
    --substitutions=_REGION=$REGION

# Step 4: Verify deployment
echo -e "\n${YELLOW}🔍 Verifying deployment...${NC}"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format='value(status.url)')

if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}❌ Failed to get service URL${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Deployment completed successfully!${NC}"
echo "===================================================================="
echo -e "🌐 Backend URL: ${GREEN}$SERVICE_URL${NC}"
echo -e "🔌 WebSocket URL: ${GREEN}${SERVICE_URL/https/wss}/ws${NC}"
echo -e "🔌 Alt WebSocket: ${GREEN}${SERVICE_URL/https/wss}/simple-ws${NC}"
echo ""
echo "Test endpoints:"
echo "  - Health: curl $SERVICE_URL/health"
echo "  - Status: curl $SERVICE_URL/api/status"
echo "  - Agents: curl $SERVICE_URL/api/agents"
echo ""
echo "Test WebSocket:"
echo "  wscat -c ${SERVICE_URL/https/wss}/simple-ws"
echo ""

# Step 5: Quick health check
echo -e "${YELLOW}Running health check...${NC}"
if curl -s "$SERVICE_URL/health" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${RED}❌ Health check failed!${NC}"
fi

# Step 6: Update frontend configuration
echo -e "\n${YELLOW}📝 Update your frontend with these environment variables:${NC}"
echo "NEXT_PUBLIC_API_URL=$SERVICE_URL"
echo "NEXT_PUBLIC_WEBSOCKET_URL=${SERVICE_URL/https/wss}"

echo -e "\n${GREEN}🎉 Deployment complete! WebSocket support is now active in production.${NC}"