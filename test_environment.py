#!/usr/bin/env python3
"""Test script to verify CX Futurist AI environment setup."""

import sys
import importlib
from pathlib import Path

def test_import(module_name, display_name=None):
    """Test if a module can be imported."""
    if display_name is None:
        display_name = module_name
    
    try:
        if module_name == "pinecone":
            # Special handling for Pinecone
            from pinecone import Pinecone
            print(f"✅ {display_name} imported successfully")
            return True
        else:
            importlib.import_module(module_name)
            print(f"✅ {display_name} imported successfully")
            return True
    except ImportError as e:
        print(f"❌ {display_name} import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {display_name} imported but with warning: {e}")
        return True

def main():
    """Run all import tests."""
    print("🧪 Testing CX Futurist AI Environment")
    print("=" * 40)
    print(f"Python: {sys.version}")
    print(f"Python Path: {sys.executable}")
    print("=" * 40)
    
    # Core dependencies
    print("\n📦 Core Dependencies:")
    core_modules = [
        ("openai", "OpenAI"),
        ("pinecone", "Pinecone"),
        ("fastapi", "FastAPI"),
        ("websockets", "WebSockets"),
        ("tavily", "Tavily Search"),
    ]
    
    # Data processing
    print("\n📊 Data Processing:")
    data_modules = [
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("sklearn", "Scikit-learn"),
    ]
    
    # Web and API
    print("\n🌐 Web & API:")
    web_modules = [
        ("aiohttp", "AioHTTP"),
        ("bs4", "BeautifulSoup"),
        ("feedparser", "FeedParser"),
        ("tweepy", "Tweepy"),
    ]
    
    # NLP
    print("\n🧠 NLP & Analysis:")
    nlp_modules = [
        ("spacy", "SpaCy"),
        ("textblob", "TextBlob"),
        ("sentence_transformers", "Sentence Transformers"),
    ]
    
    # Visualization
    print("\n📈 Visualization:")
    viz_modules = [
        ("matplotlib", "Matplotlib"),
        ("seaborn", "Seaborn"),
        ("plotly", "Plotly"),
    ]
    
    # Database
    print("\n💾 Database & Storage:")
    db_modules = [
        ("sqlalchemy", "SQLAlchemy"),
        ("redis", "Redis"),
        ("pymongo", "PyMongo"),
    ]
    
    # Testing
    print("\n🧪 Testing:")
    test_modules = [
        ("pytest", "Pytest"),
        ("pytest_asyncio", "Pytest Asyncio"),
    ]
    
    # Utilities
    print("\n🛠️ Utilities:")
    util_modules = [
        ("dotenv", "Python-dotenv"),
        ("click", "Click"),
        ("rich", "Rich"),
        ("loguru", "Loguru"),
    ]
    
    all_modules = (
        core_modules + data_modules + web_modules + nlp_modules + 
        viz_modules + db_modules + test_modules + util_modules
    )
    
    success_count = 0
    total_count = len(all_modules)
    
    # Test each category
    for modules in [core_modules, data_modules, web_modules, nlp_modules, 
                   viz_modules, db_modules, test_modules, util_modules]:
        for module_name, display_name in modules:
            if test_import(module_name, display_name):
                success_count += 1
    
    # Summary
    print("\n" + "=" * 40)
    print(f"📊 Summary: {success_count}/{total_count} modules imported successfully")
    
    if success_count == total_count:
        print("🎉 All modules imported successfully!")
        print("\n✨ Environment setup complete! You're ready to start developing.")
        return 0
    else:
        print(f"\n⚠️  {total_count - success_count} modules failed to import.")
        print("Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())