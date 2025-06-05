# CX Futurist AI - Unified Deployment Guide

## Overview

This guide describes the complete relaunch of the CX Futurist AI system with a unified architecture that combines API and WebSocket functionality in a single backend service.

## Architecture

### Before (Fragmented)
- Multiple backend services (cx-futurist-api, cx-futurist-api-ws, cx-futurist-websocket)
- Complex routing and configuration
- Inconsistent deployment patterns

### After (Unified)
- Single backend service: `cx-futurist-backend`
- Combined API + WebSocket support
- Simple, consistent deployment
- Production-ready configuration

## Key Files Created

1. **`Dockerfile.unified`** - Single Docker image for the backend with all functionality
2. **`cloudbuild-unified.yaml`** - Complete deployment configuration
3. **`deploy-unified.sh`** - One-command deployment script
4. **`test-unified-system.html`** - Comprehensive testing interface
5. **`test-local-unified.sh`** - Local testing before deployment

## Service Architecture

```
┌─────────────────────────┐     ┌──────────────────────────┐
│   cx-futurist-frontend  │────▶│   cx-futurist-backend    │
│   (Next.js + React)     │     │   (FastAPI + WebSocket)  │
└─────────────────────────┘     └──────────────────────────┘
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │   OpenAI    │
                                    │     API     │
                                    └─────────────┘
```

## Deployment Steps

### 1. Local Testing
```bash
# Test the unified system locally
./test-local-unified.sh

# Open test-unified-system.html in browser
# Update URLs to localhost:8080 for local testing
```

### 2. Production Deployment
```bash
# Deploy to Google Cloud Run
./deploy-unified.sh
```

### 3. Verify Deployment
```bash
# The deployment script will automatically:
# - Enable required APIs
# - Configure secrets
# - Build and deploy both services
# - Clean up old services
# - Run basic health checks
```

## URLs After Deployment

- **Backend API**: https://cx-futurist-backend-407245526867.us-central1.run.app
- **Frontend**: https://cx-futurist-frontend-407245526867.us-central1.run.app
- **API Docs**: https://cx-futurist-backend-407245526867.us-central1.run.app/docs
- **Health Check**: https://cx-futurist-backend-407245526867.us-central1.run.app/health
- **WebSocket**: wss://cx-futurist-backend-407245526867.us-central1.run.app/ws

## Key Features

### Backend Features
- Unified API and WebSocket server
- All 6 AI agents configured and ready
- Real-time updates via WebSocket
- Health monitoring
- Automatic reconnection support
- Session affinity for WebSocket connections
- CPU boost for better performance

### Frontend Features
- Real-time agent activity visualization
- Live analysis updates
- Interactive dashboard
- Responsive design
- WebSocket auto-reconnection

## Testing the System

### Using the Test Interface
1. Open `test-unified-system.html` in a browser
2. Use the provided URLs (or update for local testing)
3. Run through the test suite:
   - Health check
   - Agent status
   - WebSocket connection
   - Full analysis with real-time updates

### Manual Testing
```bash
# Test health endpoint
curl https://cx-futurist-backend-407245526867.us-central1.run.app/health

# Test WebSocket (will return 426 Upgrade Required)
curl https://cx-futurist-backend-407245526867.us-central1.run.app/ws
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY` - Stored in Google Secret Manager
- `ENVIRONMENT` - Set to 'production'
- `PORT` - Set to 8080 (Cloud Run standard)

### Cloud Run Settings
- **CPU**: 2 vCPUs
- **Memory**: 4GB
- **Min Instances**: 1 (always warm)
- **Max Instances**: 10
- **Timeout**: 3600s (1 hour for long analyses)
- **Session Affinity**: Enabled for WebSocket
- **CPU Boost**: Enabled for better performance

## Monitoring

### Health Checks
The system includes comprehensive health monitoring:
- `/health` endpoint for basic health
- `/api/agents/status` for agent system status
- WebSocket connection monitoring

### Logs
View logs in Google Cloud Console:
```bash
gcloud logs read --project=insightcommand-461701 \
  --filter="resource.labels.service_name=cx-futurist-backend"
```

## Troubleshooting

### WebSocket Connection Issues
1. Ensure frontend uses `wss://` protocol
2. Check browser console for errors
3. Verify session affinity is enabled
4. Test with the provided test interface

### API Issues
1. Check health endpoint first
2. Verify API key is properly configured
3. Check Cloud Run logs for errors
4. Ensure all required APIs are enabled

## Next Steps

1. **Test the deployment** using `test-unified-system.html`
2. **Monitor initial usage** via Cloud Run metrics
3. **Scale as needed** by adjusting min/max instances
4. **Add monitoring** with Google Cloud Monitoring
5. **Set up alerts** for system health

## Clean Architecture Benefits

- **Single deployment** reduces complexity
- **Unified logging** makes debugging easier
- **Consistent configuration** across environments
- **Better resource utilization** with shared processes
- **Simplified maintenance** with one codebase

## Success Metrics

After deployment, verify:
- ✅ Health endpoint returns "healthy"
- ✅ All 6 agents show as "ready"
- ✅ WebSocket connections establish successfully
- ✅ Analysis requests complete with real-time updates
- ✅ Frontend displays live agent activity
- ✅ No errors in Cloud Run logs

## Support

For issues or questions:
1. Check Cloud Run logs
2. Use the test interface for diagnostics
3. Review this guide for configuration details
4. Check the TROUBLESHOOTING.md file

---

**Ready to deploy?** Run `./deploy-unified.sh` and watch your unified CX Futurist AI system come to life!