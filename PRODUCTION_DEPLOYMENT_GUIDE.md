# 🚀 CX Futurist AI - Production Deployment Guide

## Quick Start (If you've already set up the project)

```bash
# Deploy everything with one command
./deploy-quick.sh
```

## First-Time Setup

### 1. Prerequisites
- Google Cloud SDK (`gcloud`) installed
- Docker installed
- A Google Cloud Project with billing enabled
- Your OpenAI API key ready

### 2. Initial Setup (One-time only)

```bash
# Run the full setup script
./deploy.sh
```

This will:
- Enable required Google Cloud APIs
- Create Artifact Registry repository
- Set up service accounts
- Configure secrets (you'll be prompted for API keys)
- Build and deploy both backend and frontend

### 3. Enter Your Secrets When Prompted

- **OpenAI API Key**: Required for AI agents
- **Pinecone API Key**: Optional (system works without it)
- **Pinecone Environment**: Optional
- **Tavily API Key**: Optional

## Deployment Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend      │
│  (Next.js)      │     │   (FastAPI)     │
│ Cloud Run       │     │  Cloud Run      │
└─────────────────┘     └─────────────────┘
       │                         │
       │                         ▼
       │                  ┌─────────────┐
       │                  │  WebSocket  │
       │                  │ /simple-ws  │
       └──────────────────┴─────────────┘
```

## What Gets Deployed

### Backend Service (`cx-futurist-api`)
- FastAPI application with 6 AI agents
- WebSocket endpoint for real-time updates
- REST API for analysis requests
- Runs on port 8100

### Frontend Service (`cx-futurist-frontend`)
- Next.js application with real-time dashboard
- Analysis input interface
- Live agent activity visualization
- Runs on port 3000

## Testing Your Deployment

### Option 1: Use the Test Page
1. Open `test-production.html` in your browser
2. Enter your backend URL (shown after deployment)
3. Click through the tests:
   - API Health Check
   - WebSocket Connection
   - Analysis Request

### Option 2: Direct Access
1. Visit your frontend URL (shown after deployment)
2. You should see the CX Futurist AI landing page
3. Click "Start Analysis" to begin

## Common Issues & Solutions

### Frontend Shows Blank Page
```bash
# Check frontend logs
gcloud run services logs read cx-futurist-frontend --region=us-central1

# Update environment variables
gcloud run services update cx-futurist-frontend \
  --region=us-central1 \
  --update-env-vars NEXT_PUBLIC_API_URL=https://your-backend-url
```

### WebSocket Connection Fails
```bash
# Ensure backend is running
gcloud run services describe cx-futurist-api --region=us-central1

# Check WebSocket endpoint
curl https://your-backend-url/simple-ws
```

### API Key Errors
```bash
# Update secrets
echo -n "your-new-api-key" | gcloud secrets versions add openai-api-key --data-file=-

# Redeploy to pick up new secrets
./deploy-quick.sh
```

## Monitoring & Logs

### View Logs
```bash
# Backend logs
gcloud run services logs read cx-futurist-api --region=us-central1

# Frontend logs
gcloud run services logs read cx-futurist-frontend --region=us-central1

# Stream logs in real-time
gcloud run services logs tail cx-futurist-api --region=us-central1
```

### Check Service Status
```bash
# List all services
gcloud run services list --region=us-central1

# Get detailed info
gcloud run services describe cx-futurist-api --region=us-central1
```

## Updating the Application

### Quick Update After Code Changes
```bash
# Just run the quick deploy script
./deploy-quick.sh
```

### Update Only Frontend
```bash
gcloud builds submit \
  --config cloudbuild-frontend.yaml \
  --substitutions _REGION=us-central1
```

### Update Only Backend
```bash
gcloud builds submit \
  --config cloudbuild-backend-only.yaml \
  --substitutions _REGION=us-central1
```

## Environment Variables

### Backend Environment Variables
- `OPENAI_API_KEY`: From Secret Manager
- `PINECONE_API_KEY`: From Secret Manager (optional)
- `API_HOST`: 0.0.0.0
- `CLOUD_RUN_PORT`: 8100

### Frontend Environment Variables
- `NEXT_PUBLIC_API_URL`: Backend URL (set automatically)
- `NEXT_PUBLIC_WEBSOCKET_URL`: WebSocket URL (set automatically)

## Cost Optimization

### Reduce Costs
```bash
# Set minimum instances to 0
gcloud run services update cx-futurist-api \
  --region=us-central1 \
  --min-instances=0

# Reduce memory allocation
gcloud run services update cx-futurist-frontend \
  --region=us-central1 \
  --memory=256Mi
```

### Monitor Costs
- Check Cloud Run metrics in Google Cloud Console
- Set up budget alerts
- Review logs for excessive API calls

## Cleanup

### Delete Everything
```bash
# Delete services
gcloud run services delete cx-futurist-api --region=us-central1
gcloud run services delete cx-futurist-frontend --region=us-central1

# Delete secrets
gcloud secrets delete openai-api-key
gcloud secrets delete pinecone-api-key
gcloud secrets delete pinecone-environment
gcloud secrets delete tavily-api-key

# Delete Artifact Registry repository
gcloud artifacts repositories delete cx-futurist --location=us-central1
```

## URLs After Deployment

Your services will be available at:
- **Frontend**: `https://cx-futurist-frontend-[hash]-[region].a.run.app`
- **Backend API**: `https://cx-futurist-api-[hash]-[region].a.run.app`
- **API Docs**: `https://cx-futurist-api-[hash]-[region].a.run.app/docs`

## Support

If you encounter issues:
1. Check the logs first
2. Verify all environment variables are set
3. Ensure your API keys are valid
4. Check that all Google Cloud APIs are enabled

Happy deploying! 🚀