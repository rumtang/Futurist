#!/bin/bash
# Unified deployment script for CX Futurist AI
# This script performs a complete system relaunch with proper configuration

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_ID="insightcommand-461701"
REGION="us-central1"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${BLUE}🚀 CX Futurist AI - Complete System Relaunch${NC}"
echo -e "${BLUE}================================================${NC}"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Timestamp: $TIMESTAMP"
echo ""

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install it first.${NC}"
    exit 1
fi

# Check if logged in to gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${RED}❌ Not logged in to gcloud. Please run 'gcloud auth login'${NC}"
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Check if OpenAI API key exists in Secret Manager
echo -e "${YELLOW}🔐 Checking API key in Secret Manager...${NC}"
if ! gcloud secrets describe openai-api-key --project=$PROJECT_ID &> /dev/null; then
    echo -e "${RED}❌ OpenAI API key not found in Secret Manager${NC}"
    echo "Please create it with: gcloud secrets create openai-api-key --data-file=<file-with-key>"
    exit 1
fi

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    containerregistry.googleapis.com \
    --project=$PROJECT_ID

# Grant Cloud Build permissions for Secret Manager
echo -e "${YELLOW}🔐 Granting Cloud Build access to secrets...${NC}"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

# Grant Cloud Build permissions for Cloud Run
echo -e "${YELLOW}🔧 Granting Cloud Build permissions for Cloud Run...${NC}"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/run.invoker"

# Create production requirements if not exists
if [ ! -f requirements-production.txt ]; then
    echo -e "${YELLOW}📦 Creating production requirements...${NC}"
    cat > requirements-production.txt << 'EOF'
# Core dependencies for production
fastapi==0.108.0
uvicorn[standard]==0.25.0
websockets==12.0
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0

# OpenAI and AI
openai>=1.6.1
langchain==0.1.0
crewai==0.22.5

# Utilities
loguru==0.7.2
httpx==0.25.2
python-dotenv==1.0.0
requests==2.31.0

# Async support
asyncio==3.4.3
aiofiles==23.2.1
EOF
fi

# Update frontend configuration
echo -e "${YELLOW}🎨 Updating frontend configuration...${NC}"
cat > frontend/.env.production << EOF
NEXT_PUBLIC_API_URL=https://cx-futurist-backend-407245526867.us-central1.run.app
NEXT_PUBLIC_WS_URL=wss://cx-futurist-backend-407245526867.us-central1.run.app
EOF

# Start deployment
echo -e "${GREEN}🚀 Starting unified deployment...${NC}"
echo ""

# Submit the build
BUILD_ID=$(gcloud builds submit \
    --config=cloudbuild-unified.yaml \
    --substitutions=SHORT_SHA=${TIMESTAMP} \
    --project=$PROJECT_ID \
    --format="value(id)")

echo -e "${YELLOW}📊 Build submitted with ID: $BUILD_ID${NC}"
echo "You can monitor the build at: https://console.cloud.google.com/cloud-build/builds/${BUILD_ID}?project=${PROJECT_ID}"
echo ""

# Wait for build completion
echo -e "${YELLOW}⏳ Waiting for deployment to complete...${NC}"
gcloud builds log $BUILD_ID --stream --project=$PROJECT_ID

# Check build status
BUILD_STATUS=$(gcloud builds describe $BUILD_ID --project=$PROJECT_ID --format="value(status)")

if [ "$BUILD_STATUS" = "SUCCESS" ]; then
    echo ""
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}🌐 Service URLs:${NC}"
    echo "Backend API: https://cx-futurist-backend-407245526867.us-central1.run.app"
    echo "Frontend: https://cx-futurist-frontend-407245526867.us-central1.run.app"
    echo ""
    echo -e "${BLUE}📊 API Endpoints:${NC}"
    echo "Health Check: https://cx-futurist-backend-407245526867.us-central1.run.app/health"
    echo "API Docs: https://cx-futurist-backend-407245526867.us-central1.run.app/docs"
    echo "WebSocket: wss://cx-futurist-backend-407245526867.us-central1.run.app/ws"
    echo ""
    echo -e "${GREEN}🎉 System relaunch complete! Your CX Futurist AI is ready.${NC}"
    
    # Test the deployment
    echo ""
    echo -e "${YELLOW}🧪 Running deployment tests...${NC}"
    
    # Test health endpoint
    echo -n "Testing health endpoint... "
    if curl -s https://cx-futurist-backend-407245526867.us-central1.run.app/health | grep -q "healthy"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
    
    # Test WebSocket endpoint
    echo -n "Testing WebSocket connectivity... "
    if curl -s -o /dev/null -w "%{http_code}" https://cx-futurist-backend-407245526867.us-central1.run.app/ws | grep -q "426"; then
        echo -e "${GREEN}✓ (Upgrade Required - WebSocket endpoint exists)${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
    
else
    echo -e "${RED}❌ Deployment failed with status: $BUILD_STATUS${NC}"
    echo "Check the build logs for more details."
    exit 1
fi