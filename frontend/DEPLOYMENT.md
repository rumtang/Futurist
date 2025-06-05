# CX Futurist AI Frontend - Deployment Guide

## Overview
This is the production-ready frontend for the CX Futurist AI system. It's built with Next.js 14 and designed to run on Google Cloud Run.

## Key Features for Production
- ✅ Proper landing page with clear CTAs
- ✅ Error handling and connection status
- ✅ Loading states and progress indicators
- ✅ Runtime environment variable injection
- ✅ Health check endpoints
- ✅ WebSocket auto-reconnection
- ✅ Responsive design

## Production URLs

### API Endpoints
- `/api/health` - Health check endpoint
- `/api/config` - Current configuration (for debugging)

### Pages
- `/` - Landing page with system overview
- `/analysis` - Main analysis interface
- `/dashboard` - Live agent activity dashboard

## Environment Variables
Configure these in Cloud Run:
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.run.app
NEXT_PUBLIC_WEBSOCKET_URL=wss://your-backend-url.run.app
```

## Deployment Steps

### 1. Build and Push Docker Image
```bash
# Build the image
docker build -t gcr.io/your-project/cx-futurist-frontend:latest .

# Push to GCR
docker push gcr.io/your-project/cx-futurist-frontend:latest
```

### 2. Deploy to Cloud Run
```bash
gcloud run deploy cx-futurist-frontend \
  --image gcr.io/your-project/cx-futurist-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_API_URL=https://your-backend-url.run.app,NEXT_PUBLIC_WEBSOCKET_URL=wss://your-backend-url.run.app" \
  --port 3000 \
  --memory 512Mi \
  --cpu 1
```

### 3. Verify Deployment
1. Check health endpoint: `https://your-frontend-url.run.app/api/health`
2. Check config endpoint: `https://your-frontend-url.run.app/api/config`
3. Visit landing page: `https://your-frontend-url.run.app`
4. Test analysis page: `https://your-frontend-url.run.app/analysis`

## Troubleshooting

### Blank Page Issues
- Check browser console for errors
- Verify environment variables are set correctly
- Check `/api/config` endpoint to see actual configuration
- Ensure backend is running and accessible

### Connection Issues
- Verify backend URL is correct (should be HTTPS in production)
- Check CORS settings on backend
- Ensure WebSocket URL uses `wss://` for HTTPS sites
- Check browser console for WebSocket errors

### Build Issues
- Ensure all dependencies are installed: `npm ci`
- Check for TypeScript errors: `npm run type-check`
- Verify build locally: `npm run build && npm start`

## Production Features

### Runtime Configuration
The frontend uses a runtime configuration script (`/runtime-config.js`) that allows environment variables to be injected at container startup without rebuilding the image.

### Error Handling
- Connection status indicators on all pages
- Graceful fallbacks for failed API calls
- User-friendly error messages
- Automatic reconnection for WebSocket

### Performance
- Static asset optimization
- Code splitting for faster initial load
- Lazy loading of components
- Optimized bundle size

## Monitoring
- Check `/api/health` regularly
- Monitor Cloud Run metrics
- Set up uptime monitoring
- Track WebSocket connection failures

## Security
- All API calls use HTTPS in production
- WebSocket connections use WSS
- No sensitive data in frontend code
- Environment variables handled securely