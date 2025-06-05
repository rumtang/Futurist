"""Test endpoints for debugging."""

from fastapi import APIRouter
from openai import AsyncOpenAI
import os
from loguru import logger

from src.config.base_config import settings

router = APIRouter()

@router.get("/test-openai")
async def test_openai_connection():
    """Test OpenAI API connectivity."""
    try:
        # Get API key
        api_key = settings.openai_api_key
        if not api_key:
            return {"error": "No API key configured"}
        
        # Initialize client
        client = AsyncOpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test successful' in 2 words"}],
            max_tokens=10
        )
        
        return {
            "status": "success",
            "model": "gpt-3.5-turbo",
            "response": response.choices[0].message.content,
            "api_key_last_4": api_key[-4:] if len(api_key) > 4 else "****"
        }
        
    except Exception as e:
        logger.error(f"OpenAI test failed: {type(e).__name__}: {str(e)}")
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "api_key_last_4": api_key[-4:] if api_key and len(api_key) > 4 else "None"
        }

@router.get("/test-env")
async def test_environment():
    """Test environment variables."""
    return {
        "openai_api_key_present": bool(settings.openai_api_key),
        "openai_api_key_last_4": settings.openai_api_key[-4:] if settings.openai_api_key and len(settings.openai_api_key) > 4 else "None",
        "agent_model": settings.agent_model,
        "available_models": settings.available_models,
        "port": os.environ.get("PORT", "not set"),
        "env_vars": {k: v[:10] + "..." if len(v) > 10 else v for k, v in os.environ.items() if "KEY" not in k}
    }