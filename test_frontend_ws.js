#!/usr/bin/env node

const WebSocket = require('ws');

const WS_URL = 'wss://cx-futurist-api-407245526867.us-central1.run.app/simple-ws';

console.log('🧪 Testing Frontend WebSocket Connection...');
console.log(`Connecting to: ${WS_URL}`);

const ws = new WebSocket(WS_URL);

ws.on('open', () => {
    console.log('✅ WebSocket connected successfully!');
    
    // Send subscribe message like the frontend would
    ws.send(JSON.stringify({ 
        type: 'subscribe', 
        channel: 'all',
        timestamp: Date.now()
    }));
    
    // Test agent status request
    setTimeout(() => {
        ws.send(JSON.stringify({
            type: 'request_analysis',
            id: 'test_analysis_123',
            topic: 'AI trends in customer experience',
            timestamp: Date.now()
        }));
    }, 1000);
    
    // Close after testing
    setTimeout(() => {
        console.log('🏁 Test complete - closing connection');
        ws.close();
    }, 3000);
});

ws.on('message', (data) => {
    console.log('📨 Received message:', data.toString());
    try {
        const parsed = JSON.parse(data.toString());
        console.log('📊 Parsed data:', JSON.stringify(parsed, null, 2));
    } catch (e) {
        console.log('💬 Raw message (not JSON)');
    }
});

ws.on('error', (error) => {
    console.log('❌ WebSocket error:', error.message);
});

ws.on('close', (code, reason) => {
    console.log(`🔌 WebSocket closed: ${code} - ${reason}`);
    console.log('✅ Frontend WebSocket integration test complete!');
});

// Timeout after 10 seconds
setTimeout(() => {
    console.log('\n⏰ Test timeout - forcing exit');
    process.exit(0);
}, 10000);