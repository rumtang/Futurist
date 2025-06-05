#!/bin/bash
# Deploy backend with secret management

echo "Deploying CX Futurist backend with GPT-4.1 support..."

# Set variables
PROJECT_ID="cx-futurist"
REGION="us-central1"
SERVICE_NAME="cx-futurist-backend"

# Deploy the backend
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars="AGENT_MODEL=gpt-4.1,AGENT_TEMPERATURE=0.0,LOG_LEVEL=INFO" \
    --set-secrets="OPENAI_API_KEY=cx-futurist-openai-key:latest" \
    --quiet

if [ $? -eq 0 ]; then
    echo "✅ Backend deployed successfully with GPT-4.1 support!"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)")
    echo "Service URL: $SERVICE_URL"
    
    # Test the backend
    echo "Testing backend health..."
    curl -s "$SERVICE_URL/health" | jq .
else
    echo "❌ Deployment failed"
    exit 1
fi