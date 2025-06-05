#!/usr/bin/env python3
"""Test a simple agent operation to debug issues."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Import agent
from src.agents.simple_ai_futurist_agent import SimpleAIFuturistAgent


async def test_agent():
    """Test basic agent functionality."""
    print("Testing AI Futurist Agent with GPT-4.1...")
    
    # Initialize agent
    agent = SimpleAIFuturistAgent()
    print(f"Agent initialized: {agent.name}")
    print(f"Model: {agent.model}")
    print(f"API Key present: {'Yes' if agent.client.api_key else 'No'}")
    
    # Test basic thinking
    try:
        print("\nTesting basic think operation...")
        response = await agent.think("What is 2+2?")
        print(f"Response: {response[:100]}...")
        print("✅ Basic thinking works!")
    except Exception as e:
        print(f"❌ Error in think: {type(e).__name__}: {e}")
        return False
    
    # Test AI implications analysis
    try:
        print("\nTesting AI implications analysis...")
        result = await agent.analyze_ai_implications("customer service automation")
        print(f"Analysis result keys: {list(result.keys())}")
        print("✅ AI implications analysis works!")
    except Exception as e:
        print(f"❌ Error in analysis: {type(e).__name__}: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_agent())