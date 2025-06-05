#!/usr/bin/env python3
"""Check which models are available with the current API key."""

import os
from pathlib import Path
from dotenv import load_dotenv
import openai

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Initialize client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

print("Checking available models...")
print("="*60)

# Test models
test_models = [
    "gpt-4.1",
    "gpt-4.1-mini", 
    "gpt-4.1-nano",
    "o3",
    "gpt-4",
    "gpt-4-turbo",
    "gpt-4-turbo-preview",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-3.5-turbo"
]

available_models = []

for model in test_models:
    try:
        # Try a minimal completion
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        print(f"✅ {model:<20} - Available")
        available_models.append(model)
    except openai.NotFoundError:
        print(f"❌ {model:<20} - Not found")
    except Exception as e:
        print(f"⚠️  {model:<20} - Error: {type(e).__name__}")

print("\n" + "="*60)
print(f"Available models: {', '.join(available_models)}")

# Suggest fallback models
print("\nSuggested fallback configuration:")
if "gpt-4o" in available_models:
    print("- Use gpt-4o instead of gpt-4.1")
if "gpt-4o-mini" in available_models:
    print("- Use gpt-4o-mini instead of gpt-4.1-mini")
if "gpt-4-turbo" in available_models:
    print("- Use gpt-4-turbo for synthesis instead of o3")