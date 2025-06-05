# CX Futurist AI - Deployment Guide

## Overview

This guide covers deploying the CX Futurist AI application to Google Cloud Run using optimized Docker containers and automated deployment scripts.

## Prerequisites

### Required Tools
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Docker](https://docs.docker.com/get-docker/)
- Git
- A Google Cloud Project with billing enabled

### Required API Keys
- **OpenAI API Key** - For AI agents and analysis
- **Pinecone API Key** - For vector database storage
- **Pinecone Environment** - Your Pinecone environment (e.g., `us-west1-gcp`)
- **Tavily API Key** (optional) - For web search capabilities

## Local Development

### Quick Start
```bash
# Clone and setup
git clone <repository-url>
cd cx-futurist-ai

# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up --build
```

### Available Services
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redis**: localhost:6379

### Development Commands
```bash
# Start with hot reload
docker-compose up

# Production-like setup with nginx
docker-compose --profile production-like up

# Run tests
docker-compose exec api python -m pytest

# View logs
docker-compose logs -f api
docker-compose logs -f frontend
```

## Google Cloud Deployment

### Automated Deployment

The easiest way to deploy is using the automated deployment script:

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment (will prompt for configuration)
./deploy.sh
```

The script will:
1. ✅ Check prerequisites
2. ✅ Set up Google Cloud project
3. ✅ Enable required APIs
4. ✅ Create Artifact Registry repository
5. ✅ Set up service account with proper permissions
6. ✅ Configure secrets management
7. ✅ Build and deploy containers
8. ✅ Provide service URLs

### Manual Deployment

If you prefer manual deployment:

1. **Set up Google Cloud Project**
```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"

gcloud config set project $PROJECT_ID
```

2. **Enable APIs**
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

3. **Create Artifact Registry**
```bash
gcloud artifacts repositories create cx-futurist \
    --repository-format=docker \
    --location=$REGION
```

4. **Set up Secrets**
```bash
# Create secrets
echo -n "your-openai-key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your-pinecone-key" | gcloud secrets create pinecone-api-key --data-file=-
echo -n "us-west1-gcp" | gcloud secrets create pinecone-environment --data-file=-
```

5. **Build and Deploy**
```bash
# Configure Docker for Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Submit build
gcloud builds submit --config cloudbuild.yaml
```

## Architecture

### Container Images

#### Backend Container (API)
- **Base Image**: `python:3.12-slim`
- **Multi-stage build** for optimized size
- **Non-root user** for security
- **Health checks** for reliability
- **Optimized layers** for fast builds

#### Frontend Container
- **Base Image**: `node:18-alpine`
- **Multi-stage build** with separate dev dependencies
- **Standalone Next.js build** for minimal runtime
- **Non-root user** for security
- **Built-in health checks**

### Cloud Run Configuration

#### Backend Service
- **Memory**: 2 GB
- **CPU**: 2 vCPU
- **Concurrency**: 100 requests
- **Timeout**: 3600 seconds (1 hour)
- **Auto-scaling**: 0-10 instances

#### Frontend Service
- **Memory**: 1 GB
- **CPU**: 1 vCPU
- **Concurrency**: 100 requests
- **Auto-scaling**: 0-10 instances

## Security

### Service Account
A dedicated service account is created with minimal required permissions:
- `roles/secretmanager.secretAccessor`
- `roles/logging.logWriter`
- `roles/monitoring.metricWriter`
- `roles/cloudtrace.agent`

### Secrets Management
All sensitive data is stored in Google Secret Manager:
- API keys are never exposed in container images
- Secrets are mounted at runtime
- Service account has least-privilege access

### Network Security
- Services run on Google's secure infrastructure
- HTTPS termination handled by Cloud Run
- No direct database connections exposed

## Monitoring and Logging

### Built-in Monitoring
- **Cloud Logging**: All application logs
- **Cloud Monitoring**: Performance metrics
- **Cloud Trace**: Request tracing
- **Health Checks**: Service availability

### Useful Commands
```bash
# View service logs
gcloud run services logs read cx-futurist-api --region=$REGION

# Check service status
gcloud run services describe cx-futurist-api --region=$REGION

# Update service configuration
gcloud run services update cx-futurist-api --region=$REGION --memory=4Gi
```

## Scaling and Performance

### Auto-scaling
- **Cold start mitigation**: Min instances set to 0 for cost efficiency
- **Traffic-based scaling**: Scales based on concurrent requests
- **CPU-based scaling**: Additional scaling based on CPU usage

### Performance Optimizations
- **Container image caching**: Layers cached for faster builds
- **Multi-stage builds**: Smaller production images
- **Health checks**: Fast failure detection and recovery
- **Connection pooling**: Efficient database connections

## Cost Optimization

### Development
- Use local Docker Compose for development
- Only deploy to Cloud Run for testing/production

### Production
- **Min instances**: Set to 0 to avoid idle costs
- **Request-based billing**: Pay only for actual usage
- **Shared resources**: Frontend and backend can share infrastructure

### Estimated Costs (Monthly)
- **Light usage** (1000 requests/day): ~$5-10
- **Medium usage** (10,000 requests/day): ~$20-40
- **Heavy usage** (100,000 requests/day): ~$100-200

*Costs depend on actual resource usage and request patterns*

## Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check build logs
gcloud builds log [BUILD_ID]

# Common fixes:
# 1. Ensure Docker context is correct
# 2. Check .dockerignore excludes necessary files
# 3. Verify base images are accessible
```

#### Deployment Failures
```bash
# Check service logs
gcloud run services logs read [SERVICE_NAME] --region=[REGION]

# Common fixes:
# 1. Verify secrets exist and are accessible
# 2. Check service account permissions
# 3. Ensure health check endpoints work
```

#### Runtime Issues
```bash
# Check real-time logs
gcloud run services logs tail [SERVICE_NAME] --region=[REGION]

# Common fixes:
# 1. Verify environment variables
# 2. Check API key validity
# 3. Monitor memory/CPU usage
```

### Debug Mode
Enable debug logging by setting environment variables:
```bash
gcloud run services update [SERVICE_NAME] \
    --set-env-vars LOG_LEVEL=DEBUG \
    --region=[REGION]
```

## Cleanup

### Remove Services
```bash
# Delete Cloud Run services
gcloud run services delete cx-futurist-api --region=$REGION
gcloud run services delete cx-futurist-frontend --region=$REGION

# Delete container images
gcloud artifacts repositories delete cx-futurist --location=$REGION

# Delete secrets
gcloud secrets delete openai-api-key
gcloud secrets delete pinecone-api-key
gcloud secrets delete pinecone-environment
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Google Cloud Run documentation
3. Check application logs for specific errors
4. Consult the project's issue tracker

## Next Steps

After successful deployment:
1. **Monitor performance** using Cloud Console
2. **Set up alerts** for service availability
3. **Configure custom domain** if needed
4. **Implement CI/CD pipeline** for automated deployments
5. **Scale resources** based on usage patterns