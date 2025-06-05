#!/usr/bin/env python3
"""Simple WebSocket test for CX Futurist AI."""

import asyncio
import websockets
import json
from loguru import logger

async def test_simple_websocket():
    """Test the simple WebSocket endpoint."""
    uri = "ws://localhost:8100/simple-ws"
    
    try:
        logger.info(f"Connecting to {uri}")
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connected successfully!")
            
            # Send test message
            test_message = {"type": "ping", "timestamp": "test"}
            await websocket.send(json.dumps(test_message))
            logger.info(f"📤 Sent: {test_message}")
            
            # Receive response
            response = await websocket.recv()
            logger.info(f"📨 Received: {response}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        return False

async def test_socketio_endpoint():
    """Test Socket.io endpoint."""
    # Install python-socketio-client for this test
    try:
        import socketio
        
        sio = socketio.AsyncClient()
        
        @sio.event
        async def connect():
            logger.info("✅ Socket.io connected!")
            return True
            
        @sio.event
        async def system_state(data):
            logger.info(f"📨 System state: {data}")
            
        try:
            await sio.connect('http://localhost:8100/ws')
            await asyncio.sleep(2)  # Wait for initial state
            await sio.disconnect()
            return True
            
        except Exception as e:
            logger.error(f"❌ Socket.io error: {e}")
            return False
            
    except ImportError:
        logger.warning("⚠️ Socket.io client not available, skipping")
        return None

async def main():
    """Run all WebSocket tests."""
    logger.info("🧪 Testing WebSocket connectivity...")
    
    # Test simple WebSocket
    simple_result = await test_simple_websocket()
    
    # Test Socket.io
    socketio_result = await test_socketio_endpoint()
    
    logger.info("📊 Test Results:")
    logger.info(f"  Simple WebSocket: {'✅ Pass' if simple_result else '❌ Fail'}")
    if socketio_result is not None:
        logger.info(f"  Socket.io: {'✅ Pass' if socketio_result else '❌ Fail'}")
    else:
        logger.info(f"  Socket.io: ⚠️ Skipped")
    
    return simple_result and (socketio_result is None or socketio_result)

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)