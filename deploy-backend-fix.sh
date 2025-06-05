#!/bin/bash
set -e

echo "🚀 Deploying backend with WebSocket support..."

# Use the existing main.py which has WebSocket endpoints
gcloud run deploy cx-futurist-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --timeout 3600 \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 1 \
  --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY:-dummy},VERSION=websocket-production" \
  --command "python,-m,uvicorn,src.main:app,--host,0.0.0.0,--port,8080"

echo "✅ Deployment complete!"