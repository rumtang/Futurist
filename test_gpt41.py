#!/usr/bin/env python3
"""Test GPT-4.1 model availability."""

import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

async def test_gpt41():
    """Test if GPT-4.1 model works."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("No API key found")
        return
        
    client = AsyncOpenAI(api_key=api_key)
    
    models_to_test = ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-3.5-turbo"]
    
    for model in models_to_test:
        try:
            print(f"\nTesting {model}...")
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Say 'Model works!' in 3 words"}],
                max_tokens=10
            )
            print(f"✅ {model}: {response.choices[0].message.content}")
        except Exception as e:
            print(f"❌ {model}: {type(e).__name__}: {str(e)[:100]}")

if __name__ == "__main__":
    asyncio.run(test_gpt41())