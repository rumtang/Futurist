#!/bin/bash
# Quick deployment script for WebSocket fix

set -e

echo "🚀 Building and deploying CX Futurist API with WebSocket support..."

# Build and deploy using Cloud Build
gcloud builds submit --tag gcr.io/insightcommand-461701/cx-futurist-api:websocket-fix \
  --timeout=600s

# Deploy the built image
gcloud run deploy cx-futurist-api \
  --image gcr.io/insightcommand-461701/cx-futurist-api:websocket-fix \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --timeout 3600 \
  --memory 1Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 1 \
  --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY:-dummy},VERSION=websocket-fix-final"

echo "✅ Deployment complete!"
echo "🔗 Testing WebSocket endpoint..."

# Wait a moment for service to be ready
sleep 5

# Test the endpoint
curl -s https://cx-futurist-api-407245526867.us-central1.run.app/health | jq