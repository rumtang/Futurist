#!/usr/bin/env python3
"""
Test script to demonstrate full crew execution in CX Futurist AI
"""

import asyncio
import json
import requests
import websocket
import threading
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8100"
WS_URL = "ws://localhost:8100/simple-ws"

class CXFuturistTester:
    def __init__(self):
        self.ws = None
        self.messages = []
        self.analysis_complete = False
        
    def on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            msg_type = data.get('type', '')
            
            # Print key messages
            if msg_type == 'connection:established':
                print("✅ WebSocket connected successfully")
            elif msg_type == 'agent:thought':
                agent = data.get('agent', 'unknown')
                thought = data.get('thought', {}).get('content', '')
                print(f"🤖 [{agent}] {thought}")
            elif msg_type == 'agent:status':
                agent = data.get('agent', 'unknown')
                status = data.get('data', {}).get('status', '')
                task = data.get('data', {}).get('current_task', '')
                print(f"📊 [{agent}] Status: {status} - {task}")
            elif msg_type == 'analysis:started':
                print(f"🚀 Analysis started - ID: {data.get('request_id')}")
            elif msg_type == 'analysis:completed':
                print("\n✅ ANALYSIS COMPLETE!")
                results = data.get('results', {})
                print(f"Summary: {results.get('summary', 'N/A')}")
                print("\nInsights:")
                for insight in results.get('insights', []):
                    print(f"  • {insight}")
                self.analysis_complete = True
                
            self.messages.append(data)
        except Exception as e:
            print(f"Error parsing message: {e}")
            
    def on_error(self, ws, error):
        print(f"❌ WebSocket error: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        print(f"🔌 WebSocket closed: {close_status_code} - {close_msg}")
        
    def on_open(self, ws):
        print("🔌 WebSocket connection opened")
        
    def test_health_check(self):
        """Test API health check"""
        print("\n1️⃣ Testing API Health Check...")
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API is healthy - Status: {data.get('status')} - Message: {data.get('message')}")
                return True
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Could not connect to API: {e}")
            return False
            
    def test_system_status(self):
        """Test system status endpoint"""
        print("\n2️⃣ Testing System Status...")
        try:
            response = requests.get(f"{API_BASE_URL}/api/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ System Status: {data.get('status')}")
                services = data.get('services', {})
                print(f"   • OpenAI: {'✅' if services.get('openai') else '❌'}")
                print(f"   • Pinecone: {'✅' if services.get('pinecone') else '⚠️ Optional'}")
                print(f"   • Redis: {'✅' if services.get('redis') else '⚠️ Optional'}")
                print(f"   • Orchestrator: {'✅' if data.get('orchestrator') else '❌'}")
                return True
            else:
                print(f"❌ System status check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Could not get system status: {e}")
            return False
            
    def test_agents(self):
        """Test agent endpoints"""
        print("\n3️⃣ Testing Agent Status...")
        try:
            response = requests.get(f"{API_BASE_URL}/api/agents")
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents', [])
                print(f"✅ Found {len(agents)} agents:")
                for agent in agents:
                    print(f"   • {agent['name']}: {agent['status']} - {agent['description']}")
                return True
            else:
                print(f"❌ Agent status check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Could not get agent status: {e}")
            return False
            
    def connect_websocket(self):
        """Connect to WebSocket for real-time updates"""
        print("\n4️⃣ Connecting to WebSocket...")
        try:
            self.ws = websocket.WebSocketApp(
                WS_URL,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Run WebSocket in a separate thread
            wst = threading.Thread(target=self.ws.run_forever)
            wst.daemon = True
            wst.start()
            
            # Wait for connection
            time.sleep(2)
            return True
        except Exception as e:
            print(f"❌ Could not connect to WebSocket: {e}")
            return False
            
    def start_analysis(self, topic):
        """Start a new analysis via WebSocket"""
        print(f"\n5️⃣ Starting Analysis: '{topic}'...")
        
        if not self.ws:
            print("❌ WebSocket not connected")
            return False
            
        message = {
            "type": "request_analysis",
            "id": f"test_analysis_{int(time.time())}",
            "topic": topic,
            "depth": "comprehensive",
            "timeframe": "2-5 years"
        }
        
        try:
            self.ws.send(json.dumps(message))
            print("📤 Analysis request sent")
            return True
        except Exception as e:
            print(f"❌ Could not send analysis request: {e}")
            return False
            
    def start_analysis_via_api(self, topic):
        """Start analysis via REST API"""
        print(f"\n5️⃣ Starting Analysis via API: '{topic}'...")
        
        try:
            payload = {
                "topic": topic,
                "scope": "emerging_trends",
                "priority": "normal",
                "include_sources": True
            }
            
            response = requests.post(f"{API_BASE_URL}/api/analysis/", json=payload)
            if response.status_code == 200:
                data = response.json()
                request_id = data.get('request_id')
                print(f"✅ Analysis started - Request ID: {request_id}")
                return request_id
            else:
                print(f"❌ Failed to start analysis: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error starting analysis: {e}")
            return None
            
    def check_analysis_status(self, request_id):
        """Check analysis status"""
        print(f"\n6️⃣ Checking Analysis Status...")
        
        max_checks = 30  # Check for up to 5 minutes
        check_count = 0
        
        while check_count < max_checks:
            try:
                response = requests.get(f"{API_BASE_URL}/api/analysis/{request_id}")
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status')
                    print(f"   Status: {status}")
                    
                    if status == 'completed':
                        print("\n✅ ANALYSIS COMPLETE via API!")
                        results = data.get('results', {})
                        if results:
                            print(f"\nSummary: {results.get('summary', 'No summary available')}")
                            print("\nKey Findings:")
                            for finding in results.get('key_findings', []):
                                print(f"  • {finding}")
                            print("\nRecommendations:")
                            for rec in results.get('recommendations', []):
                                print(f"  • {rec}")
                        return True
                    elif status == 'failed':
                        print(f"❌ Analysis failed: {data.get('error', 'Unknown error')}")
                        return False
                        
                    time.sleep(10)  # Wait 10 seconds before next check
                    check_count += 1
                else:
                    print(f"❌ Could not check status: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Error checking status: {e}")
                return False
                
        print("⏱️ Analysis timed out")
        return False
        
    def run_full_test(self):
        """Run the complete test suite"""
        print("🚀 CX FUTURIST AI - FULL CREW EXECUTION TEST")
        print("=" * 50)
        
        # 1. Health check
        if not self.test_health_check():
            print("\n❌ API is not running. Please start the backend first:")
            print("   cd /Users/jonatkin/Documents/Agentic/cx-futurist-ai")
            print("   python -m uvicorn src.main:app --host 0.0.0.0 --port 8100")
            return
            
        # 2. System status
        self.test_system_status()
        
        # 3. Agent status
        self.test_agents()
        
        # 4. Connect WebSocket
        self.connect_websocket()
        
        # 5. Start analysis
        topic = "How will AI agents transform customer experience in retail over the next 3 years?"
        
        # Try WebSocket first
        if self.ws:
            self.start_analysis(topic)
            
            # Wait for completion
            print("\n⏳ Waiting for analysis to complete...")
            timeout = 300  # 5 minutes
            start_time = time.time()
            
            while not self.analysis_complete and (time.time() - start_time) < timeout:
                time.sleep(1)
                
            if self.analysis_complete:
                print("\n🎉 CREW EXECUTION COMPLETE!")
            else:
                print("\n⏱️ Analysis timed out via WebSocket, trying API...")
                # Try API method
                request_id = self.start_analysis_via_api(topic)
                if request_id:
                    self.check_analysis_status(request_id)
        else:
            # Fallback to API
            request_id = self.start_analysis_via_api(topic)
            if request_id:
                self.check_analysis_status(request_id)
                
        print("\n" + "=" * 50)
        print("TEST COMPLETE")
        
        # Close WebSocket
        if self.ws:
            self.ws.close()


if __name__ == "__main__":
    tester = CXFuturistTester()
    tester.run_full_test()