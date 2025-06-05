#!/usr/bin/env python3
"""Test API structure and available endpoints."""

import httpx
import json

def test_api_structure():
    """Test API structure and print available endpoints."""
    base_url = "http://localhost:8100"
    
    print("CX Futurist AI - API Structure Test")
    print("=" * 50)
    
    # Test root
    print("\n1. Testing API root:")
    try:
        response = httpx.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test OpenAPI docs
    print("\n2. OpenAPI documentation:")
    print(f"   Interactive docs: {base_url}/docs")
    print(f"   ReDoc: {base_url}/redoc")
    
    # Get OpenAPI schema
    print("\n3. Getting OpenAPI schema:")
    try:
        response = httpx.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            openapi = response.json()
            print(f"   Title: {openapi.get('info', {}).get('title')}")
            print(f"   Version: {openapi.get('info', {}).get('version')}")
            
            # List all paths
            print("\n4. Available endpoints:")
            paths = openapi.get("paths", {})
            for path, methods in paths.items():
                for method in methods:
                    if method in ["get", "post", "put", "delete"]:
                        print(f"   {method.upper():6} {path}")
        else:
            print(f"   Failed to get OpenAPI schema: {response.status_code}")
    except Exception as e:
        print(f"   Error getting OpenAPI schema: {e}")
    
    # Test specific endpoints
    print("\n5. Testing specific endpoints:")
    endpoints = [
        ("GET", "/health"),
        ("GET", "/api/status"),
        ("GET", "/api/agents"),
        ("POST", "/api/workflows/analyze-trend"),
        ("POST", "/api/analysis/"),
    ]
    
    for method, endpoint in endpoints:
        try:
            if method == "GET":
                response = httpx.get(f"{base_url}{endpoint}")
            else:
                response = httpx.post(f"{base_url}{endpoint}", json={"topic": "test"})
            
            print(f"   {method:6} {endpoint:30} -> {response.status_code}")
        except Exception as e:
            print(f"   {method:6} {endpoint:30} -> Error: {e}")

if __name__ == "__main__":
    test_api_structure()