#!/bin/bash
# Deploy everything to cx-futurist project

set -e

PROJECT_ID="cx-futurist"
REGION="us-central1"

echo "🚀 Deploying CX Futurist AI to $PROJECT_ID"
echo "================================================"

# Ensure we're using the right project
gcloud config set project $PROJECT_ID

# 1. Deploy Backend
echo ""
echo "📦 Deploying Backend with GPT-4.1 support..."
echo "--------------------------------------------"

gcloud run deploy cx-futurist-backend \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars="AGENT_MODEL=gpt-4.1,AGENT_TEMPERATURE=0.0,LOG_LEVEL=INFO,PINECONE_API_KEY=$PINECONE_API_KEY" \
    --set-secrets="OPENAI_API_KEY=cx-futurist-openai-key:latest" \
    --project $PROJECT_ID \
    --quiet

BACKEND_URL=$(gcloud run services describe cx-futurist-backend --region $REGION --format "value(status.url)" --project $PROJECT_ID)
echo "✅ Backend deployed: $BACKEND_URL"

# 2. Update frontend environment for production
echo ""
echo "📝 Updating frontend configuration..."
echo "--------------------------------------------"

cat > frontend/.env.production << EOF
NEXT_PUBLIC_API_URL=$BACKEND_URL
NEXT_PUBLIC_WEBSOCKET_URL=${BACKEND_URL/https:/wss:}
NEXT_PUBLIC_APP_NAME="CX Futurist AI"
NEXT_PUBLIC_APP_DESCRIPTION="AI-powered analysis of future customer experience trends"
EOF

# Also update runtime config
cat > frontend/public/runtime-config.js << EOF
// Runtime configuration for production
const isProduction = typeof window !== 'undefined' && 
  (window.location.hostname.includes('run.app') || 
   window.location.hostname.includes('cx-futurist'));

window.__RUNTIME_CONFIG__ = {
  NEXT_PUBLIC_API_URL: isProduction 
    ? '$BACKEND_URL'
    : (window.NEXT_PUBLIC_API_URL || 'http://localhost:8080'),
  NEXT_PUBLIC_WEBSOCKET_URL: isProduction
    ? '${BACKEND_URL/https:/wss:}'
    : (window.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8080')
};
EOF

# 3. Deploy Frontend
echo ""
echo "🎨 Deploying Frontend..."
echo "--------------------------------------------"

cd frontend
gcloud run deploy cx-futurist-frontend \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --project $PROJECT_ID \
    --quiet

FRONTEND_URL=$(gcloud run services describe cx-futurist-frontend --region $REGION --format "value(status.url)" --project $PROJECT_ID)
cd ..

echo "✅ Frontend deployed: $FRONTEND_URL"

# 4. Test the deployment
echo ""
echo "🧪 Testing deployment..."
echo "--------------------------------------------"

# Test backend health
echo "Testing backend health..."
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/health" || echo "Failed")
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

# Test backend agent status
echo "Testing agent status endpoint..."
AGENT_RESPONSE=$(curl -s "$BACKEND_URL/api/agents/status" || echo "Failed")
if [[ $AGENT_RESPONSE == *"ai_futurist"* ]]; then
    echo "✅ Agents are responding"
else
    echo "❌ Agent status check failed"
fi

# 5. Summary
echo ""
echo "🎉 Deployment Complete!"
echo "================================================"
echo ""
echo "📋 Service URLs:"
echo "  Backend:  $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"
echo ""
echo "🔍 Key Endpoints:"
echo "  Health Check:    $BACKEND_URL/health"
echo "  API Docs:        $BACKEND_URL/docs"
echo "  Agent Status:    $BACKEND_URL/api/agents/status"
echo "  Dashboard:       $FRONTEND_URL/dashboard"
echo "  Analysis:        $FRONTEND_URL/analysis"
echo ""
echo "🤖 Agent Models:"
echo "  AI Futurist:         gpt-4.1"
echo "  Trend Scanner:       gpt-4.1-mini"
echo "  Customer Insight:    gpt-4.1"
echo "  Tech Impact:         gpt-4.1"
echo "  Org Transformation:  gpt-4.1"
echo "  Synthesis:           gpt-4.1"
echo ""
echo "📝 Notes:"
echo "  - All services deployed to project: $PROJECT_ID"
echo "  - Region: $REGION"
echo "  - Using GPT-4.1 family models"
echo "  - OpenAI API key stored in Secret Manager"
echo ""