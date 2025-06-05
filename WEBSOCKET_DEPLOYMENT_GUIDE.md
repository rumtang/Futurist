# WebSocket Deployment Guide for CX Futurist AI

This guide provides a permanent, production-ready solution for deploying the CX Futurist AI with full WebSocket support.

## Overview

The system consists of:
- **Backend**: FastAPI with native WebSocket support at `/simple-ws`
- **Frontend**: Next.js with WebSocket client connecting to backend
- **Deployment**: Google Cloud Run with HTTP/2 and session affinity for WebSocket support

## Local Development

### Quick Start with Docker Compose

```bash
# Using the simplified docker-compose
docker-compose -f docker-compose-simple.yml up

# Backend will be available at: http://localhost:8080
# Frontend will be available at: http://localhost:3000
# WebSocket endpoint: ws://localhost:8080/simple-ws
```

### Manual Local Setup

```bash
# Run the local deployment script
./deploy-local-docker.sh

# Or manually:
# 1. Start backend
cd src
python -m uvicorn src.main_simple_ws:app --host 0.0.0.0 --port 8080

# 2. Start frontend
cd frontend
npm install
npm run dev
```

## Production Deployment (Google Cloud Run)

### Prerequisites

1. Google Cloud Project with billing enabled
2. `gcloud` CLI installed and authenticated
3. Required APIs enabled:
   ```bash
   gcloud services enable run.googleapis.com \
       artifactregistry.googleapis.com \
       cloudbuild.googleapis.com \
       secretmanager.googleapis.com
   ```

### Option 1: Using Cloud Build (Recommended)

```bash
# Deploy using the optimized Cloud Build configuration
gcloud builds submit --config=cloudbuild-websocket.yaml
```

### Option 2: Manual Deployment

```bash
# Run the deployment script
./deploy-websocket-fix.sh
```

### Option 3: Step-by-Step Manual Deployment

1. **Build and push backend image:**
   ```bash
   docker build -f Dockerfile.backend -t us-central1-docker.pkg.dev/cx-futurist-ai/cx-futurist/backend:latest .
   docker push us-central1-docker.pkg.dev/cx-futurist-ai/cx-futurist/backend:latest
   ```

2. **Deploy backend with WebSocket support:**
   ```bash
   gcloud run deploy cx-futurist-backend \
       --image=us-central1-docker.pkg.dev/cx-futurist-ai/cx-futurist/backend:latest \
       --region=us-central1 \
       --allow-unauthenticated \
       --port=8080 \
       --timeout=3600 \
       --memory=2Gi \
       --cpu=2 \
       --min-instances=1 \
       --max-instances=10 \
       --session-affinity \
       --use-http2
   ```

3. **Get backend URL:**
   ```bash
   BACKEND_URL=$(gcloud run services describe cx-futurist-backend --region=us-central1 --format="value(status.url)")
   ```

4. **Build and deploy frontend:**
   ```bash
   cd frontend
   docker build \
       --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL \
       --build-arg NEXT_PUBLIC_WEBSOCKET_URL=$BACKEND_URL \
       -t us-central1-docker.pkg.dev/cx-futurist-ai/cx-futurist/frontend:latest .
   docker push us-central1-docker.pkg.dev/cx-futurist-ai/cx-futurist/frontend:latest
   
   gcloud run deploy cx-futurist-frontend \
       --image=us-central1-docker.pkg.dev/cx-futurist-ai/cx-futurist/frontend:latest \
       --region=us-central1 \
       --allow-unauthenticated \
       --port=3000 \
       --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL,NEXT_PUBLIC_WEBSOCKET_URL=$BACKEND_URL"
   ```

## Configuration

### Backend Environment Variables

- `PORT`: Server port (default: 8080)
- `API_HOST`: Host to bind to (default: 0.0.0.0)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DEV_MODE`: Development mode flag (default: false)
- `OPENAI_API_KEY`: OpenAI API key (required)

### Frontend Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_WEBSOCKET_URL`: WebSocket URL (same as API URL)

### Cloud Run Configuration

Key settings for WebSocket support:
- `--session-affinity`: Ensures WebSocket connections stay on same instance
- `--use-http2`: Enables HTTP/2 for better WebSocket performance
- `--timeout=3600`: Allows long-lived connections
- `--min-instances=1`: Keeps at least one instance warm

## Testing WebSocket Connection

### Browser Test

Open the frontend URL and check browser console for:
```
WebSocket connected successfully!
```

### Python Test Script

```bash
# Test local deployment
python test-websocket-live.py http://localhost:8080

# Test production deployment
python test-websocket-live.py https://cx-futurist-backend-xxx.run.app
```

### Manual WebSocket Test

```javascript
// In browser console
const ws = new WebSocket('wss://cx-futurist-backend-xxx.run.app/simple-ws');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log('Message:', e.data);
ws.send(JSON.stringify({type: 'ping'}));
```

## Troubleshooting

### WebSocket Connection Fails

1. **Check backend logs:**
   ```bash
   gcloud run logs read --service=cx-futurist-backend --region=us-central1
   ```

2. **Verify WebSocket endpoint:**
   ```bash
   curl https://your-backend-url/health/websocket
   ```

3. **Check CORS settings:**
   Ensure backend allows frontend origin

4. **Verify Cloud Run settings:**
   - Session affinity enabled
   - HTTP/2 enabled
   - Sufficient timeout

### Connection Drops

1. **Increase ping intervals:**
   Backend: `--ws-ping-interval 20 --ws-ping-timeout 60`

2. **Check instance scaling:**
   Ensure min-instances > 0

3. **Monitor memory usage:**
   May need to increase memory allocation

### Frontend Can't Connect

1. **Verify environment variables:**
   ```bash
   # In frontend container
   echo $NEXT_PUBLIC_WEBSOCKET_URL
   ```

2. **Check WebSocket URL format:**
   - Should be `wss://` for HTTPS
   - Should be `ws://` for HTTP

## Monitoring

### Health Checks

- Backend health: `/health`
- WebSocket health: `/health/websocket`
- Frontend health: Check port 3000

### Logging

```bash
# Backend logs
gcloud run logs read --service=cx-futurist-backend --region=us-central1

# Frontend logs
gcloud run logs read --service=cx-futurist-frontend --region=us-central1
```

### Metrics

Monitor in Cloud Console:
- Request count
- WebSocket connections
- Error rate
- Latency

## Best Practices

1. **Always use session affinity** for WebSocket on Cloud Run
2. **Set appropriate timeouts** (at least 3600s for long connections)
3. **Implement reconnection logic** in frontend
4. **Use connection pooling** for better resource usage
5. **Monitor WebSocket health** separately from HTTP health
6. **Use HTTP/2** for better performance
7. **Keep at least one instance warm** with min-instances

## Security Considerations

1. **Authentication**: Implement JWT tokens for WebSocket auth
2. **Rate limiting**: Limit connections per IP
3. **Message validation**: Validate all WebSocket messages
4. **HTTPS only**: Always use wss:// in production
5. **CORS**: Configure appropriate CORS headers

## Performance Optimization

1. **Message batching**: Group multiple updates
2. **Compression**: Enable WebSocket compression
3. **Binary protocols**: Use binary format for large data
4. **Connection pooling**: Reuse connections when possible
5. **CDN**: Use Cloud CDN for static assets

## Next Steps

1. Implement authentication for WebSocket connections
2. Add message queuing for reliability
3. Set up monitoring dashboards
4. Implement auto-scaling policies
5. Add WebSocket load testing

## Support

For issues:
1. Check logs in Cloud Console
2. Verify all environment variables
3. Test with the provided test scripts
4. Check Cloud Run quotas and limits