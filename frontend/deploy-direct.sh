#!/bin/bash

# Direct deployment script for CX Futurist Frontend

set -e

echo "🚀 Starting direct deployment..."

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "Error: No GCP project set"
    exit 1
fi

echo "Using project: $PROJECT_ID"

# Build Docker image locally
echo "📦 Building Docker image..."
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/cx-futurist/frontend:latest -f Dockerfile .

# Configure Docker for Artifact Registry
echo "🔧 Configuring Docker..."
gcloud auth configure-docker us-central1-docker.pkg.dev

# Push image
echo "⬆️ Pushing image to Artifact Registry..."
docker push us-central1-docker.pkg.dev/$PROJECT_ID/cx-futurist/frontend:latest

# Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy cx-futurist-frontend \
    --image us-central1-docker.pkg.dev/$PROJECT_ID/cx-futurist/frontend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 3000 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --min-instances 1 \
    --concurrency 1000 \
    --cpu-boost \
    --set-env-vars "NEXT_PUBLIC_API_URL=https://cx-futurist-api-407245526867.us-central1.run.app,NEXT_PUBLIC_WEBSOCKET_URL=wss://cx-futurist-api-407245526867.us-central1.run.app,NODE_ENV=production"

# Get service URL
SERVICE_URL=$(gcloud run services describe cx-futurist-frontend --region=us-central1 --format='value(status.url)')

echo "✅ Deployment complete!"
echo "Frontend URL: $SERVICE_URL"
echo "Analysis page: $SERVICE_URL/analysis"