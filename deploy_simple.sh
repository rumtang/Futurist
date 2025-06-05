#!/bin/bash
# Simple deployment script that avoids Cloud Build issues

echo "Deploying CX Futurist backend with GPT-4.1 support (simplified)..."

# Build locally first
echo "Building Docker image locally..."
docker build -t cx-futurist-backend .

# Tag for Google Container Registry
docker tag cx-futurist-backend gcr.io/cx-futurist/cx-futurist-backend

# Push to Container Registry
echo "Pushing to Container Registry..."
docker push gcr.io/cx-futurist/cx-futurist-backend

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy cx-futurist-backend \
    --image gcr.io/cx-futurist/cx-futurist-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars="AGENT_MODEL=gpt-4.1,AGENT_TEMPERATURE=0.0,LOG_LEVEL=INFO" \
    --set-secrets="OPENAI_API_KEY=cx-futurist-openai-key:latest" \
    --project cx-futurist

if [ $? -eq 0 ]; then
    echo "✅ Backend deployed successfully!"
    SERVICE_URL=$(gcloud run services describe cx-futurist-backend --region us-central1 --format "value(status.url)" --project cx-futurist)
    echo "Service URL: $SERVICE_URL"
    
    # Test the backend
    echo "Testing backend health..."
    curl -s "$SERVICE_URL/health" | jq .
else
    echo "❌ Deployment failed"
    exit 1
fi