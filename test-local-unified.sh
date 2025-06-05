#!/bin/bash
# Test the unified system locally before deployment

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🧪 Testing Unified CX Futurist AI System Locally${NC}"
echo -e "${BLUE}================================================${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
fi

# Source environment variables
export $(cat .env | grep -v '^#' | xargs)

# Kill any existing processes on port 8080
echo -e "${YELLOW}🔧 Cleaning up existing processes...${NC}"
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# Start the backend
echo -e "${GREEN}🚀 Starting unified backend with WebSocket support...${NC}"
python -m uvicorn src.main_simple_ws:app --host 0.0.0.0 --port 8080 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
sleep 5

# Test health endpoint
echo -e "${BLUE}📋 Testing health endpoint...${NC}"
if curl -s http://localhost:8080/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    kill $BACKEND_PID
    exit 1
fi

# Test WebSocket endpoint
echo -e "${BLUE}📋 Testing WebSocket endpoint...${NC}"
python3 << 'EOF'
import asyncio
import websockets
import json

async def test_websocket():
    try:
        async with websockets.connect('ws://localhost:8080/ws') as websocket:
            # Wait for connection message
            msg = await websocket.recv()
            data = json.loads(msg)
            if data.get('type') == 'connection:established':
                print("✅ WebSocket connection established")
                
                # Test ping
                await websocket.send(json.dumps({'type': 'ping'}))
                response = await websocket.recv()
                data = json.loads(response)
                if data.get('type') == 'pong':
                    print("✅ WebSocket ping/pong working")
                    return True
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
    return False

asyncio.run(test_websocket())
EOF

# Test API endpoints
echo -e "${BLUE}📋 Testing API endpoints...${NC}"

# Test agent status
echo -n "Testing agent status endpoint... "
if curl -s http://localhost:8080/api/agents/status | grep -q "ai_futurist"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# Test analysis endpoint
echo -n "Testing analysis endpoint... "
RESPONSE=$(curl -s -X POST http://localhost:8080/api/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Test query", "analysis_type": "trend_analysis"}')

if echo "$RESPONSE" | grep -q "analysis_id"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Local testing complete!${NC}"
echo ""
echo -e "${BLUE}📊 System Information:${NC}"
echo "Backend running on: http://localhost:8080"
echo "API Docs: http://localhost:8080/docs"
echo "WebSocket: ws://localhost:8080/ws"
echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo "1. Open test-unified-system.html in a browser"
echo "2. Update URLs to use localhost:8080"
echo "3. Run comprehensive tests"
echo "4. When ready, run ./deploy-unified.sh for production deployment"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the backend${NC}"

# Keep the script running
wait $BACKEND_PID