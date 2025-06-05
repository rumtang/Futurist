"""Test script to verify API keys are working."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai():
    """Test OpenAI API key."""
    try:
        import openai
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OpenAI API key not found in .env")
            return False
            
        print(f"✅ OpenAI API key found: {api_key[:8]}...")
        
        # Test the key
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API key works!'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI API test successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def test_pinecone():
    """Test Pinecone API key."""
    try:
        from pinecone import Pinecone
        
        api_key = os.getenv("PINECONE_API_KEY")
        environment = os.getenv("PINECONE_ENVIRONMENT")
        
        if not api_key:
            print("❌ Pinecone API key not found in .env")
            return False
            
        if not environment:
            print("❌ Pinecone environment not found in .env")
            return False
            
        print(f"✅ Pinecone API key found: {api_key[:8]}...")
        print(f"✅ Pinecone environment: {environment}")
        
        # Test the key
        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes()
        print(f"✅ Pinecone API test successful. Indexes: {[idx.name for idx in indexes]}")
        return True
        
    except Exception as e:
        print(f"❌ Pinecone API test failed: {e}")
        return False

def test_tavily():
    """Test Tavily API key (if present)."""
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            print("⚠️  Tavily API key not found (optional)")
            return True  # Optional, so return True
            
        from tavily import TavilyClient
        
        print(f"✅ Tavily API key found: {api_key[:8]}...")
        
        # Test the key
        client = TavilyClient(api_key=api_key)
        results = client.search("test query", max_results=1)
        print(f"✅ Tavily API test successful")
        return True
        
    except Exception as e:
        print(f"⚠️  Tavily API test failed (optional): {e}")
        return True  # Optional, so return True

def main():
    """Run all tests."""
    print("🔍 Testing API Keys...\n")
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        return
    
    results = []
    
    print("1. Testing OpenAI API...")
    results.append(test_openai())
    print()
    
    print("2. Testing Pinecone API...")
    results.append(test_pinecone())
    print()
    
    print("3. Testing Tavily API...")
    results.append(test_tavily())
    print()
    
    if all(results):
        print("✅ All API keys are working correctly!")
    else:
        print("❌ Some API keys failed. Please check your .env file.")

if __name__ == "__main__":
    main()