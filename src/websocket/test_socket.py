"""Test Socket.IO connection locally."""

import socketio
import asyncio

async def test_connection():
    """Test connecting to the Socket.IO server."""
    # Try different URLs and paths
    configs = [
        {
            "url": "https://cx-futurist-api-407245526867.us-central1.run.app",
            "path": "/ws/socket.io/",
            "name": "Production with /ws/socket.io/"
        },
        {
            "url": "https://cx-futurist-api-407245526867.us-central1.run.app/ws",
            "path": "/socket.io/",
            "name": "Production /ws with /socket.io/"
        },
        {
            "url": "https://cx-futurist-api-407245526867.us-central1.run.app",
            "path": "/socket.io/",
            "name": "Production with /socket.io/"
        }
    ]
    
    for config in configs:
        print(f"\n\nTesting: {config['name']}")
        print(f"URL: {config['url']}")
        print(f"Path: {config['path']}")
        print("-" * 50)
        
        sio = socketio.AsyncClient()
        
        @sio.event
        async def connect():
            print("✅ Connected!")
            print(f"Session ID: {sio.sid}")
            
        @sio.event
        async def connect_error(data):
            print(f"❌ Connection error: {data}")
            
        @sio.event
        async def disconnect():
            print("Disconnected")
        
        try:
            await sio.connect(
                config["url"],
                socketio_path=config["path"],
                wait_timeout=10,
                transports=['websocket', 'polling']
            )
            
            # If connected, wait a bit then disconnect
            if sio.connected:
                await asyncio.sleep(2)
                await sio.disconnect()
            
        except Exception as e:
            print(f"❌ Exception: {type(e).__name__}: {e}")
        
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_connection())