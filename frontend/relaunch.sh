#!/bin/bash

# CX Futurist AI Frontend Re-launch Script
# This script optimizes and redeploys the frontend to fix timeout issues

set -e

echo "🚀 Starting CX Futurist AI Frontend Re-launch..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: Not in frontend directory${NC}"
    exit 1
fi

# Step 1: Clean previous builds
echo -e "${YELLOW}Step 1: Cleaning previous builds...${NC}"
rm -rf .next node_modules package-lock.json
echo -e "${GREEN}✓ Cleaned build artifacts${NC}"

# Step 2: Install dependencies with clean cache
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
npm cache clean --force
npm install --legacy-peer-deps
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Replace config with optimized version
echo -e "${YELLOW}Step 3: Applying optimized configuration...${NC}"
cp next.config.optimized.js next.config.js
echo -e "${GREEN}✓ Configuration optimized${NC}"

# Step 4: Build locally to test
echo -e "${YELLOW}Step 4: Testing build locally...${NC}"
npm run build
echo -e "${GREEN}✓ Local build successful${NC}"

# Step 5: Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Using project: $PROJECT_ID${NC}"

# Step 6: Submit optimized build to Cloud Build
echo -e "${YELLOW}Step 6: Submitting to Cloud Build...${NC}"
gcloud builds submit \
    --config=cloudbuild-optimized.yaml \
    --substitutions=_PROJECT_ID=$PROJECT_ID \
    --timeout=30m

# Step 7: Check deployment status
echo -e "${YELLOW}Step 7: Checking deployment status...${NC}"
SERVICE_URL=$(gcloud run services describe cx-futurist-frontend --region=us-central1 --format='value(status.url)')

if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}Error: Could not get service URL${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Frontend deployed successfully!${NC}"
echo -e "${GREEN}Frontend URL: $SERVICE_URL${NC}"

# Step 8: Test the deployment
echo -e "${YELLOW}Step 8: Testing deployment...${NC}"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Frontend is responding correctly${NC}"
else
    echo -e "${RED}Warning: Frontend returned HTTP $HTTP_STATUS${NC}"
fi

# Step 9: Test the analysis page
echo -e "${YELLOW}Step 9: Testing analysis page...${NC}"
ANALYSIS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/analysis")

if [ "$ANALYSIS_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Analysis page is working${NC}"
else
    echo -e "${RED}Warning: Analysis page returned HTTP $ANALYSIS_STATUS${NC}"
fi

# Final summary
echo -e "\n${GREEN}🎉 Re-launch Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Frontend URL: $SERVICE_URL${NC}"
echo -e "${GREEN}Analysis Page: $SERVICE_URL/analysis${NC}"
echo -e "${GREEN}Dashboard: $SERVICE_URL/dashboard${NC}"
echo -e "${GREEN}Backend API: https://cx-futurist-api-407245526867.us-central1.run.app${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Visit the frontend URL to verify it's working"
echo "2. Test the analysis functionality"
echo "3. Monitor Cloud Run logs if issues persist"