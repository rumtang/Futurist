#!/bin/bash
# Deploy CX Futurist backend with proper configuration

set -e

echo "🚀 Deploying CX Futurist Backend to cx-futurist project"
echo "======================================================="

# Ensure we're using the right project
gcloud config set project cx-futurist

# Deploy the backend
echo "📦 Deploying backend service..."
gcloud run deploy cx-futurist-backend \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --port 8080 \
    --set-env-vars="AGENT_MODEL=gpt-4.1,AGENT_TEMPERATURE=0.0,LOG_LEVEL=INFO,PINECONE_API_KEY=${PINECONE_API_KEY}" \
    --set-secrets="OPENAI_API_KEY=cx-futurist-openai-key:latest" \
    --project cx-futurist

if [ $? -eq 0 ]; then
    echo "✅ Backend deployed successfully!"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe cx-futurist-backend --region us-central1 --format "value(status.url)" --project cx-futurist)
    echo "Backend URL: $SERVICE_URL"
    
    # Test the backend
    echo ""
    echo "🧪 Testing backend..."
    echo "---------------------"
    
    # Test health endpoint
    echo -n "Health check: "
    HEALTH=$(curl -s "$SERVICE_URL/health" || echo "Failed")
    if [[ $HEALTH == *"healthy"* ]]; then
        echo "✅ Healthy"
    else
        echo "❌ Failed"
        echo "Response: $HEALTH"
    fi
    
    # Test agent status
    echo -n "Agent status: "
    AGENTS=$(curl -s "$SERVICE_URL/api/agents/status" || echo "Failed")
    if [[ $AGENTS == *"ai_futurist"* ]]; then
        echo "✅ Agents responding"
    else
        echo "❌ Failed"
        echo "Response: $AGENTS"
    fi
    
    echo ""
    echo "📝 Backend Details:"
    echo "  URL: $SERVICE_URL"
    echo "  Health: $SERVICE_URL/health"
    echo "  Docs: $SERVICE_URL/docs"
    echo "  Agents: $SERVICE_URL/api/agents/status"
else
    echo "❌ Deployment failed"
    exit 1
fi