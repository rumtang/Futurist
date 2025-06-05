#!/bin/bash

# Quick deployment script for CX Futurist AI
# This script assumes you've already run the full deploy.sh setup

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"insightcommand-461701"}
REGION=${GCP_REGION:-"us-central1"}

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 CX Futurist AI - Quick Deployment${NC}"
echo "======================================"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
    echo -e "${RED}❌ Not authenticated with gcloud. Please run: gcloud auth login${NC}"
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Check if secrets exist
echo -e "${BLUE}🔍 Checking secrets...${NC}"
if ! gcloud secrets describe openai-api-key &>/dev/null; then
    echo -e "${YELLOW}⚠️  OpenAI API key secret not found. Run ./deploy.sh first to set up secrets.${NC}"
    exit 1
fi

# Start deployment
echo -e "${BLUE}🏗️  Starting Cloud Build deployment...${NC}"
echo "This will:"
echo "  1. Build backend and frontend Docker images"
echo "  2. Push images to Artifact Registry"
echo "  3. Deploy backend to Cloud Run"
echo "  4. Deploy frontend to Cloud Run with backend URL"
echo ""

# Run Cloud Build
gcloud builds submit \
    --config cloudbuild.yaml \
    --substitutions _REGION=$REGION \
    --timeout=1800s

# Get service URLs
echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "======================="

# Get backend URL
BACKEND_URL=$(gcloud run services describe cx-futurist-api \
    --region=$REGION \
    --format='value(status.url)' 2>/dev/null || echo "Not deployed")

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe cx-futurist-frontend \
    --region=$REGION \
    --format='value(status.url)' 2>/dev/null || echo "Not deployed")

echo -e "${BLUE}🌐 Frontend:${NC} $FRONTEND_URL"
echo -e "${BLUE}🔧 Backend API:${NC} $BACKEND_URL"
echo -e "${BLUE}📚 API Docs:${NC} $BACKEND_URL/docs"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "- View logs: gcloud run services logs read cx-futurist-api --region=$REGION"
echo "- Check status: gcloud run services describe cx-futurist-api --region=$REGION"
echo "- Update env vars: gcloud run services update cx-futurist-frontend --region=$REGION --update-env-vars KEY=VALUE"