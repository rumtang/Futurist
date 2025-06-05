#!/bin/bash

# CX Futurist AI - Production Fix Deployment Script
# This script deploys the Socket.IO fixes to production

set -e

echo "🚀 Deploying CX Futurist AI Production Fixes..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gcloud is configured
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install it first.${NC}"
    exit 1
fi

# Set project
PROJECT_ID="insightcommand-461701"
echo -e "${YELLOW}📋 Using project: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Deploy backend with Socket.IO fix
echo -e "${GREEN}🔧 Deploying backend with Socket.IO support...${NC}"
gcloud builds submit \
    --config cloudbuild-production-fix.yaml \
    --project=$PROJECT_ID

# Wait for backend to be ready
echo -e "${YELLOW}⏳ Waiting for backend to stabilize...${NC}"
sleep 30

# Test backend health
echo -e "${GREEN}🏥 Testing backend health...${NC}"
BACKEND_URL="https://cx-futurist-api-407245526867.us-central1.run.app"
if curl -f "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    exit 1
fi

# Deploy frontend with updated URLs
echo -e "${GREEN}🎨 Deploying frontend with corrected URLs...${NC}"
gcloud builds submit \
    --config cloudbuild-frontend.yaml \
    --project=$PROJECT_ID

# Wait for frontend
echo -e "${YELLOW}⏳ Waiting for frontend to deploy...${NC}"
sleep 30

# Final checks
echo -e "${GREEN}🔍 Running final checks...${NC}"

FRONTEND_URL="https://cx-futurist-frontend-407245526867.us-central1.run.app"

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📋 Service URLs:"
echo "   Backend API: $BACKEND_URL"
echo "   Frontend: $FRONTEND_URL"
echo ""
echo "🧪 Test the WebSocket connection:"
echo "   1. Open $FRONTEND_URL/test-connection.html"
echo "   2. Check the WebSocket connection status"
echo ""
echo "📊 View logs:"
echo "   Backend: gcloud run logs read cx-futurist-api --project=$PROJECT_ID"
echo "   Frontend: gcloud run logs read cx-futurist-frontend --project=$PROJECT_ID"