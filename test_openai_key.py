#!/usr/bin/env python3
"""Test the OpenAI API key from .env file"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import openai

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Get API key
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("❌ No OpenAI API key found in .env file")
    sys.exit(1)

print(f"✅ Found API key: {api_key[:8]}...{api_key[-4:]}")

# Test the key
try:
    client = openai.OpenAI(api_key=api_key)
    
    # Make a simple test call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'API key is working!' if you can read this."}
        ],
        max_tokens=20
    )
    
    print(f"✅ API Response: {response.choices[0].message.content}")
    print("✅ OpenAI API key is valid and working!")
    
except openai.AuthenticationError as e:
    print(f"❌ Authentication Error: {e}")
    print("The API key appears to be invalid or expired.")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    
print("\nNow testing model availability...")
try:
    # Check if GPT-4 is available
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=5
    )
    print("✅ GPT-4 is available on this API key")
except Exception as e:
    print(f"⚠️  GPT-4 not available: {e}")
    print("   The agents may need to use gpt-3.5-turbo instead")