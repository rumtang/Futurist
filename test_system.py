"""Quick test script to verify system functionality."""

import asyncio
import httpx
from loguru import logger

async def test_system():
    """Test the CX Futurist AI system."""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        logger.info("Testing health endpoint...")
        response = await client.get(f"{base_url}/health")
        logger.info(f"Health check: {response.status_code} - {response.json()}")
        
        # Test analysis endpoint
        logger.info("\nTesting analysis endpoint...")
        analysis_data = {
            "topic": "AI agents transforming customer service",
            "depth": "standard",
            "timeframe": "3-5 years"
        }
        
        response = await client.post(
            f"{base_url}/api/analysis/",
            json=analysis_data
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Analysis started: {result}")
            
            # Check status
            request_id = result["request_id"]
            await asyncio.sleep(5)
            
            status_response = await client.get(
                f"{base_url}/api/analysis/{request_id}"
            )
            logger.info(f"Analysis status: {status_response.json()}")
        else:
            logger.error(f"Analysis failed: {response.status_code} - {response.text}")
        
        # Test knowledge search
        logger.info("\nTesting knowledge search...")
        search_data = {
            "query": "AI customer experience",
            "limit": 5
        }
        
        response = await client.post(
            f"{base_url}/api/knowledge/search",
            json=search_data
        )
        logger.info(f"Search results: {response.status_code}")
        
        # Test trends endpoint
        logger.info("\nTesting trends endpoint...")
        response = await client.get(f"{base_url}/api/trends/active")
        logger.info(f"Active trends: {response.status_code}")

if __name__ == "__main__":
    logger.info("Starting CX Futurist AI system test...")
    asyncio.run(test_system())
    logger.info("Test complete!")