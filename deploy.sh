#!/bin/bash

# CX Futurist AI - Google Cloud Run Deployment Script
# Optimized for Google Cloud with Artifact Registry and comprehensive setup

set -e

# Default configuration
PROJECT_ID=${GCP_PROJECT_ID:-"cx-futurist"}
REGION=${GCP_REGION:-"us-central1"}
REPOSITORY_NAME="cx-futurist"
SERVICE_ACCOUNT_NAME="cx-futurist-sa"
BACKEND_SERVICE="cx-futurist-api"
FRONTEND_SERVICE="cx-futurist-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_status() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Validate required tools
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI not found. Please install Google Cloud SDK."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Get or validate project ID
setup_project() {
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${YELLOW}Please enter your Google Cloud Project ID:${NC}"
        read -p "Project ID: " PROJECT_ID
        
        if [ -z "$PROJECT_ID" ]; then
            print_error "Project ID is required"
            exit 1
        fi
    fi
    
    print_status "Setting project to: $PROJECT_ID"
    gcloud config set project $PROJECT_ID
    
    # Verify project exists and we have access
    if ! gcloud projects describe $PROJECT_ID &>/dev/null; then
        print_error "Cannot access project $PROJECT_ID. Please check project ID and permissions."
        exit 1
    fi
    
    print_success "Project configured: $PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required Google Cloud APIs..."
    
    local apis=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "secretmanager.googleapis.com"
        "artifactregistry.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        print_status "Enabling $api..."
        gcloud services enable $api --quiet
    done
    
    print_success "All APIs enabled"
}

# Create Artifact Registry repository
setup_artifact_registry() {
    print_status "Setting up Artifact Registry..."
    
    if ! gcloud artifacts repositories describe $REPOSITORY_NAME \
        --location=$REGION &>/dev/null; then
        print_status "Creating Artifact Registry repository..."
        gcloud artifacts repositories create $REPOSITORY_NAME \
            --repository-format=docker \
            --location=$REGION \
            --description="CX Futurist AI container images"
    else
        print_warning "Artifact Registry repository already exists"
    fi
    
    print_success "Artifact Registry configured"
}

# Create service account with necessary permissions
setup_service_account() {
    print_status "Setting up service account..."
    
    local sa_email="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    
    if ! gcloud iam service-accounts describe $sa_email &>/dev/null; then
        print_status "Creating service account..."
        gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
            --display-name="CX Futurist AI Service Account" \
            --description="Service account for CX Futurist AI application"
        
        # Grant necessary permissions
        local roles=(
            "roles/secretmanager.secretAccessor"
            "roles/logging.logWriter"
            "roles/monitoring.metricWriter"
            "roles/cloudtrace.agent"
        )
        
        for role in "${roles[@]}"; do
            gcloud projects add-iam-policy-binding $PROJECT_ID \
                --member="serviceAccount:$sa_email" \
                --role="$role" \
                --quiet
        done
    else
        print_warning "Service account already exists"
    fi
    
    print_success "Service account configured"
}

# Setup secrets
setup_secrets() {
    print_status "Setting up secrets..."
    
    # OpenAI API Key
    if ! gcloud secrets describe openai-api-key &>/dev/null; then
        echo -e "${YELLOW}Enter your OpenAI API key:${NC}"
        read -s -p "OpenAI API Key: " OPENAI_KEY
        echo
        if [ -n "$OPENAI_KEY" ]; then
            echo -n "$OPENAI_KEY" | gcloud secrets create openai-api-key --data-file=-
            print_success "OpenAI API key secret created"
        else
            print_warning "OpenAI API key not provided"
        fi
    else
        print_warning "OpenAI API key secret already exists"
    fi
    
    # Pinecone API Key
    if ! gcloud secrets describe pinecone-api-key &>/dev/null; then
        echo -e "${YELLOW}Enter your Pinecone API key:${NC}"
        read -s -p "Pinecone API Key: " PINECONE_KEY
        echo
        if [ -n "$PINECONE_KEY" ]; then
            echo -n "$PINECONE_KEY" | gcloud secrets create pinecone-api-key --data-file=-
            print_success "Pinecone API key secret created"
        else
            print_warning "Pinecone API key not provided"
        fi
    else
        print_warning "Pinecone API key secret already exists"
    fi
    
    # Pinecone Environment
    if ! gcloud secrets describe pinecone-environment &>/dev/null; then
        echo -e "${YELLOW}Enter your Pinecone environment (e.g., us-west1-gcp):${NC}"
        read -p "Pinecone Environment: " PINECONE_ENV
        if [ -n "$PINECONE_ENV" ]; then
            echo -n "$PINECONE_ENV" | gcloud secrets create pinecone-environment --data-file=-
            print_success "Pinecone environment secret created"
        else
            print_warning "Pinecone environment not provided"
        fi
    else
        print_warning "Pinecone environment secret already exists"
    fi
    
    # Tavily API Key (optional)
    if ! gcloud secrets describe tavily-api-key &>/dev/null; then
        echo -e "${YELLOW}Enter your Tavily API key (optional, press Enter to skip):${NC}"
        read -s -p "Tavily API Key: " TAVILY_KEY
        echo
        if [ -n "$TAVILY_KEY" ]; then
            echo -n "$TAVILY_KEY" | gcloud secrets create tavily-api-key --data-file=-
            print_success "Tavily API key secret created"
        else
            print_warning "Tavily API key not provided (optional)"
        fi
    else
        print_warning "Tavily API key secret already exists"
    fi
    
    # Grant service account access to secrets
    local sa_email="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    local secrets=("openai-api-key" "pinecone-api-key" "pinecone-environment" "tavily-api-key")
    
    for secret in "${secrets[@]}"; do
        if gcloud secrets describe $secret &>/dev/null; then
            gcloud secrets add-iam-policy-binding $secret \
                --member="serviceAccount:$sa_email" \
                --role="roles/secretmanager.secretAccessor" \
                --quiet 2>/dev/null || true
        fi
    done
    
    print_success "Secrets configured"
}

# Build and deploy
deploy_application() {
    print_status "Building and deploying application..."
    
    # Configure Docker to use Artifact Registry
    gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
    
    # Submit build
    print_status "Starting Cloud Build (this may take several minutes)..."
    
    gcloud builds submit \
        --config cloudbuild.yaml \
        --substitutions _REGION=$REGION \
        --timeout=1800s
    
    print_success "Build and deployment completed"
}

# Get service URLs
get_service_urls() {
    print_status "Retrieving service URLs..."
    
    local backend_url=""
    local frontend_url=""
    
    # Get backend URL
    if gcloud run services describe $BACKEND_SERVICE --region=$REGION &>/dev/null; then
        backend_url=$(gcloud run services describe $BACKEND_SERVICE \
            --region=$REGION \
            --format='value(status.url)')
        print_success "Backend deployed at: $backend_url"
    else
        print_warning "Backend service not found"
    fi
    
    # Get frontend URL
    if gcloud run services describe $FRONTEND_SERVICE --region=$REGION &>/dev/null; then
        frontend_url=$(gcloud run services describe $FRONTEND_SERVICE \
            --region=$REGION \
            --format='value(status.url)')
        print_success "Frontend deployed at: $frontend_url"
    else
        print_warning "Frontend service not found"
    fi
    
    # Display final information
    echo ""
    echo -e "${GREEN}🎉 Deployment Complete!${NC}"
    echo "====================================="
    if [ -n "$frontend_url" ]; then
        echo -e "${BLUE}Frontend Dashboard:${NC} $frontend_url"
    fi
    if [ -n "$backend_url" ]; then
        echo -e "${BLUE}Backend API:${NC} $backend_url"
        echo -e "${BLUE}API Documentation:${NC} $backend_url/docs"
    fi
    echo ""
    echo -e "${YELLOW}📝 Next Steps:${NC}"
    echo "1. Visit the frontend URL to access the dashboard"
    echo "2. Monitor logs in Cloud Console if needed"
    echo "3. Check Cloud Run services for scaling and performance"
    echo ""
    echo -e "${YELLOW}💡 Useful Commands:${NC}"
    echo "- View logs: gcloud run services logs read $BACKEND_SERVICE --region=$REGION"
    echo "- Update service: gcloud run services update $BACKEND_SERVICE --region=$REGION"
    echo "- Delete services: gcloud run services delete $BACKEND_SERVICE --region=$REGION"
}

# Main execution
main() {
    echo -e "${GREEN}🚀 CX Futurist AI - Google Cloud Run Deployment${NC}"
    echo "=================================================="
    echo "Region: $REGION"
    echo ""
    
    check_prerequisites
    setup_project
    enable_apis
    setup_artifact_registry
    setup_service_account
    setup_secrets
    deploy_application
    get_service_urls
}

# Handle script interruption
trap 'print_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"