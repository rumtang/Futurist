# CX Futurist AI - Troubleshooting Guide

## 🔍 Common Issues and Solutions

### 1. WebSocket Connection Issues

**Problem**: Frontend shows "Connecting..." but never connects
**Solution**: The WebSocket path has been fixed in the latest deployment. The frontend now correctly connects to `/ws/socket.io/`

**To verify WebSocket connection:**
```javascript
// Open browser console on the frontend
// Check for connection messages
// You should see: "Connected to WebSocket server"
```

### 2. API Connection Issues

**Problem**: API calls failing from frontend
**Solution**: Check CORS configuration and ensure the backend is running

**Test API directly:**
```bash
# Health check
curl https://cx-futurist-api-407245526867.us-central1.run.app/health

# Agent status
curl https://cx-futurist-api-407245526867.us-central1.run.app/api/agents/status
```

### 3. Frontend Build Issues

**Problem**: Module not found errors during build
**Solution**: Fixed by:
1. Removing TypeScript path aliases (@/)
2. Using relative imports (../)
3. Ensuring lib/ directory is not excluded in .gcloudignore

### 4. Testing Connection

**Quick Test HTML Page**: Open `/frontend/test-connection.html` in your browser to test:
- API connectivity
- WebSocket connection
- CORS configuration

### 5. Viewing Logs

**Backend logs:**
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=cx-futurist-api" --limit=50 --format=json
```

**Frontend logs:**
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=cx-futurist-frontend" --limit=50 --format=json
```

### 6. Current Status

**Backend**: ✅ Healthy and responding
- Health endpoint working
- All 6 agents initialized
- WebSocket server running

**Frontend**: ✅ Deployed with WebSocket fix
- UI loads correctly
- WebSocket path corrected to `/ws/socket.io/`
- Should now connect properly

### 7. If Issues Persist

1. **Check browser console** for specific error messages
2. **Verify API is accessible** from your network
3. **Clear browser cache** and reload
4. **Check browser developer tools Network tab** for failed requests

### 8. Known Working Configuration

- Backend: Socket.io server at `/ws/socket.io/`
- Frontend: Socket.io client connecting to `https://cx-futurist-api-407245526867.us-central1.run.app` with path `/ws/socket.io/`
- CORS: Configured to allow all origins (*)