#!/bin/bash

# CX Futurist AI Frontend Deployment Script
# Builds and deploys the frontend to Google Cloud Run

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
REGION="us-central1"
SERVICE_NAME="cx-futurist-frontend"
BACKEND_SERVICE_NAME="cx-futurist-backend"
ARTIFACT_REGISTRY="us-central1-docker.pkg.dev/${PROJECT_ID}/cx-futurist"
IMAGE_NAME="frontend"
ENVIRONMENT=${ENVIRONMENT:-"production"}

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check if project ID is set
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z "$PROJECT_ID" ]; then
            error "Google Cloud project ID not set. Please set GOOGLE_CLOUD_PROJECT or configure gcloud."
            exit 1
        fi
    fi
    
    log "Using project: $PROJECT_ID"
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        error "Not authenticated with Google Cloud. Please run 'gcloud auth login'"
        exit 1
    fi
    
    # Check if Artifact Registry API is enabled
    if ! gcloud services list --enabled --filter="name:artifactregistry.googleapis.com" --format="value(name)" &> /dev/null; then
        warning "Artifact Registry API may not be enabled. Attempting to enable..."
        gcloud services enable artifactregistry.googleapis.com
    fi
    
    # Check if Cloud Run API is enabled
    if ! gcloud services list --enabled --filter="name:run.googleapis.com" --format="value(name)" &> /dev/null; then
        warning "Cloud Run API may not be enabled. Attempting to enable..."
        gcloud services enable run.googleapis.com
    fi
}

configure_docker() {
    log "Configuring Docker for Artifact Registry..."
    gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
}

get_backend_url() {
    log "Getting backend service URL..."
    
    BACKEND_URL=$(gcloud run services describe ${BACKEND_SERVICE_NAME} \
        --region=${REGION} \
        --format='value(status.url)' 2>/dev/null || echo "")
    
    if [ -z "$BACKEND_URL" ]; then
        warning "Backend service not found. Using placeholder URL."
        BACKEND_URL="https://cx-futurist-backend-placeholder.a.run.app"
    else
        log "Backend URL: $BACKEND_URL"
    fi
    
    # Convert https to wss for WebSocket
    WEBSOCKET_URL=$(echo "$BACKEND_URL" | sed 's/https:/wss:/g')
}

create_entrypoint() {
    log "Creating entrypoint script..."
    
    cat > entrypoint.sh << 'EOF'
#!/bin/sh

# Frontend entrypoint script
# Handles runtime environment variable injection

set -e

echo "Starting CX Futurist AI Frontend..."
echo "API URL: ${NEXT_PUBLIC_API_URL}"
echo "WebSocket URL: ${NEXT_PUBLIC_WEBSOCKET_URL}"

# Check if required environment variables are set
if [ -z "$NEXT_PUBLIC_API_URL" ]; then
    echo "Warning: NEXT_PUBLIC_API_URL not set, using default"
fi

if [ -z "$NEXT_PUBLIC_WEBSOCKET_URL" ]; then
    echo "Warning: NEXT_PUBLIC_WEBSOCKET_URL not set, using default"
fi

# Start the Next.js server
exec node server.js
EOF
    
    chmod +x entrypoint.sh
}

build_image() {
    log "Building Docker image..."
    
    # Create entrypoint script
    create_entrypoint
    
    # Build with build arguments
    BUILD_TAG="${ARTIFACT_REGISTRY}/${IMAGE_NAME}:build-$(date +%Y%m%d-%H%M%S)"
    LATEST_TAG="${ARTIFACT_REGISTRY}/${IMAGE_NAME}:latest"
    
    docker build \
        --platform linux/amd64 \
        -t "$BUILD_TAG" \
        -t "$LATEST_TAG" \
        --build-arg NEXT_PUBLIC_API_URL="${BACKEND_URL}" \
        --build-arg NEXT_PUBLIC_WEBSOCKET_URL="${WEBSOCKET_URL}" \
        -f Dockerfile \
        .
    
    if [ $? -ne 0 ]; then
        error "Docker build failed"
        exit 1
    fi
    
    log "Docker image built successfully: $BUILD_TAG"
}

push_image() {
    log "Pushing image to Artifact Registry..."
    
    docker push "$BUILD_TAG"
    docker push "$LATEST_TAG"
    
    if [ $? -ne 0 ]; then
        error "Failed to push image to Artifact Registry"
        exit 1
    fi
    
    log "Image pushed successfully"
}

deploy_to_cloud_run() {
    log "Deploying to Cloud Run..."
    
    # Deploy with environment variables
    gcloud run deploy ${SERVICE_NAME} \
        --image="$BUILD_TAG" \
        --platform=managed \
        --region=${REGION} \
        --allow-unauthenticated \
        --port=3000 \
        --memory=1Gi \
        --cpu=1 \
        --max-instances=10 \
        --min-instances=0 \
        --timeout=60 \
        --set-env-vars="NEXT_PUBLIC_API_URL=${BACKEND_URL},NEXT_PUBLIC_WEBSOCKET_URL=${WEBSOCKET_URL},NODE_ENV=production" \
        --service-account="${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" 2>/dev/null || \
    gcloud run deploy ${SERVICE_NAME} \
        --image="$BUILD_TAG" \
        --platform=managed \
        --region=${REGION} \
        --allow-unauthenticated \
        --port=3000 \
        --memory=1Gi \
        --cpu=1 \
        --max-instances=10 \
        --min-instances=0 \
        --timeout=60 \
        --set-env-vars="NEXT_PUBLIC_API_URL=${BACKEND_URL},NEXT_PUBLIC_WEBSOCKET_URL=${WEBSOCKET_URL},NODE_ENV=production"
    
    if [ $? -ne 0 ]; then
        error "Failed to deploy to Cloud Run"
        exit 1
    fi
    
    # Get the service URL
    FRONTEND_URL=$(gcloud run services describe ${SERVICE_NAME} \
        --region=${REGION} \
        --format='value(status.url)')
    
    log "Frontend deployed successfully!"
    log "Frontend URL: $FRONTEND_URL"
}

verify_deployment() {
    log "Verifying deployment..."
    
    # Wait a bit for the service to be ready
    sleep 5
    
    # Check if the service is responding
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        log "Deployment verification successful! Service is responding."
    else
        warning "Service returned HTTP code: $HTTP_CODE. It may take a few moments to be fully ready."
    fi
}

print_summary() {
    echo ""
    echo "========================================="
    echo "Deployment Summary"
    echo "========================================="
    echo "Project ID: $PROJECT_ID"
    echo "Region: $REGION"
    echo "Service Name: $SERVICE_NAME"
    echo "Image: $BUILD_TAG"
    echo "Frontend URL: $FRONTEND_URL"
    echo "Backend URL: $BACKEND_URL"
    echo "WebSocket URL: $WEBSOCKET_URL"
    echo "========================================="
}

# Main execution
main() {
    log "Starting CX Futurist AI Frontend deployment..."
    
    check_prerequisites
    configure_docker
    get_backend_url
    build_image
    push_image
    deploy_to_cloud_run
    verify_deployment
    print_summary
    
    log "Deployment completed successfully!"
}

# Run main function
main "$@"