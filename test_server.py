"""Minimal test server to verify basic functionality."""

import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="CX Futurist AI Test Server")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CX Futurist AI Test Server",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    # Check API keys
    openai_key = "✅" if os.getenv("OPENAI_API_KEY") else "❌"
    pinecone_key = "✅" if os.getenv("PINECONE_API_KEY") else "❌"
    
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "openai": openai_key,
            "pinecone": pinecone_key
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/test-analysis")
async def test_analysis(topic: str = "AI in customer service"):
    """Test analysis endpoint."""
    try:
        from openai import OpenAI
        
        # Test OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a CX Futurist AI analyzing trends."},
                {"role": "user", "content": f"Provide a brief analysis of: {topic}"}
            ],
            max_tokens=200
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "status": "success",
            "topic": topic,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/api/test-pinecone")
async def test_pinecone():
    """Test Pinecone connection."""
    try:
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        indexes = pc.list_indexes()
        
        return {
            "status": "success",
            "indexes": [idx.name for idx in indexes],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

if __name__ == "__main__":
    print("🚀 Starting CX Futurist AI Test Server...")
    print("📍 API: http://localhost:8080")
    print("📍 Docs: http://localhost:8080/docs")
    print("✅ API Keys loaded from .env")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)