#!/bin/bash
# Quick activation script for CX Futurist AI virtual environment

if [ -d "venv" ]; then
    echo "🔌 Activating CX Futurist AI virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated!"
    echo "Python: $(python --version)"
    echo "Location: $(which python)"
else
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup_env.sh first"
fi