#!/bin/bash

# CX Futurist AI - Environment Setup Script
# This script creates a clean Python 3.11 virtual environment and installs dependencies

set -e  # Exit on error

echo "🚀 CX Futurist AI - Environment Setup"
echo "===================================="

# Check if Python 3.11 is available
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Error: Python 3.11 is required but not installed."
    echo "Please install Python 3.11 first:"
    echo "  macOS: brew install python@3.11"
    echo "  Ubuntu: sudo apt install python3.11 python3.11-venv"
    exit 1
fi

echo "✅ Python 3.11 found: $(python3.11 --version)"

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "📦 Creating virtual environment with Python 3.11..."
python3.11 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install wheel for better package building
echo "🛠️  Installing wheel..."
pip install wheel

# Install requirements
echo "📥 Installing dependencies from requirements.txt..."
# First uninstall pinecone-client if it exists
pip uninstall -y pinecone-client 2>/dev/null || true
# Install requirements
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cat > .env << EOF
# CX Futurist AI Environment Variables

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=cx-futurist-knowledge

# Tavily Search
TAVILY_API_KEY=your_tavily_api_key_here

# Twitter API (Optional)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Environment
ENVIRONMENT=development
DEBUG=true
EOF
    echo "⚠️  Please update .env with your actual API keys!"
fi

# Test imports
echo "🧪 Testing basic imports..."
python -c "
import sys
print(f'Python: {sys.version}')
print('Testing core imports...')
try:
    import openai
    print('✅ OpenAI imported successfully')
    from pinecone import Pinecone
    print('✅ Pinecone imported successfully')
    import fastapi
    print('✅ FastAPI imported successfully')
    import websockets
    print('✅ WebSockets imported successfully')
    import pandas
    print('✅ Pandas imported successfully')
    import numpy
    print('✅ NumPy imported successfully')
    print('\n🎉 All core imports successful!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✨ Environment setup complete!"
    echo ""
    echo "To activate the environment in the future, run:"
    echo "  source venv/bin/activate"
    echo ""
    echo "To deactivate, run:"
    echo "  deactivate"
    echo ""
    echo "Next steps:"
    echo "1. Update the .env file with your API keys"
    echo "2. Run 'python src/main.py' to start the application"
else
    echo ""
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi