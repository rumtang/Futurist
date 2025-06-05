#!/usr/bin/env python3
"""Test analysis endpoint cleanly."""

import httpx
import json

def test_analysis():
    """Test the analysis endpoint without extra params."""
    base_url = "http://localhost:8100"
    
    print("Testing Analysis Endpoint (Clean)")
    print("=" * 40)
    
    # Test data
    request_data = {
        "topic": "AI agents transforming customer service",
        "scope": "emerging_trends",
        "priority": "normal",
        "include_sources": True
    }
    
    print(f"Request data: {json.dumps(request_data, indent=2)}")
    
    # Make request without query params
    print("\nMaking POST request to /api/analysis/...")
    try:
        response = httpx.post(
            f"{base_url}/api/analysis/",
            json=request_data,
            timeout=10
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nSuccess! Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"\nError response:")
            print(response.text)
            
    except Exception as e:
        print(f"\nException: {e}")

if __name__ == "__main__":
    test_analysis()