#!/usr/bin/env node

const WebSocket = require('ws');

const API_URL = 'https://cx-futurist-api-407245526867.us-central1.run.app';
const WS_URL = 'wss://cx-futurist-api-407245526867.us-central1.run.app';

console.log('🚀 Testing WebSocket connections...');

// Test 1: Simple WebSocket
console.log('\n1. Testing Simple WebSocket (/simple-ws)');
const ws1 = new WebSocket(`${WS_URL}/simple-ws`);

ws1.on('open', () => {
    console.log('✅ Simple WebSocket connected!');
    ws1.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
});

ws1.on('message', (data) => {
    console.log('📨 Received:', data.toString());
    ws1.close();
});

ws1.on('error', (error) => {
    console.log('❌ Simple WebSocket error:', error.message);
});

ws1.on('close', () => {
    console.log('🔌 Simple WebSocket closed');
    
    // Test 2: Try Socket.io endpoint with WebSocket
    console.log('\n2. Testing Socket.io WebSocket endpoint (/ws/socket.io/)');
    const ws2 = new WebSocket(`${WS_URL}/ws/socket.io/`);
    
    ws2.on('open', () => {
        console.log('✅ Socket.io WebSocket connected!');
        ws2.send('2probe'); // Socket.io probe message
    });
    
    ws2.on('message', (data) => {
        console.log('📨 Socket.io received:', data.toString());
        ws2.close();
    });
    
    ws2.on('error', (error) => {
        console.log('❌ Socket.io WebSocket error:', error.message);
        
        // Test 3: Test basic /ws endpoint
        console.log('\n3. Testing base /ws endpoint');
        const ws3 = new WebSocket(`${WS_URL}/ws`);
        
        ws3.on('open', () => {
            console.log('✅ Base /ws connected!');
            ws3.close();
        });
        
        ws3.on('error', (error) => {
            console.log('❌ Base /ws error:', error.message);
            process.exit(1);
        });
    });
    
    ws2.on('close', () => {
        console.log('🔌 Socket.io WebSocket closed');
    });
});

// Timeout after 10 seconds
setTimeout(() => {
    console.log('\n⏰ Test timeout reached');
    process.exit(0);
}, 10000);