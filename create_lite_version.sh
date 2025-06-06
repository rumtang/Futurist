#!/bin/bash

# Create a lite version with only essential files

echo "Creating lite version of CX Futurist AI..."

# Create target directory
TARGET_DIR="../cx-futurist-lite"
rm -rf $TARGET_DIR
mkdir -p $TARGET_DIR

# Copy essential Python source files
echo "Copying Python source files..."
mkdir -p $TARGET_DIR/src
cp -r src/agents $TARGET_DIR/src/
cp -r src/api $TARGET_DIR/src/
cp -r src/config $TARGET_DIR/src/
cp -r src/orchestrator $TARGET_DIR/src/
cp -r src/tools $TARGET_DIR/src/
cp -r src/websocket $TARGET_DIR/src/
cp src/__init__.py $TARGET_DIR/src/
cp src/main.py $TARGET_DIR/src/

# Copy essential frontend files
echo "Copying frontend files..."
mkdir -p $TARGET_DIR/frontend
cp -r frontend/app $TARGET_DIR/frontend/
cp -r frontend/components $TARGET_DIR/frontend/
cp -r frontend/lib $TARGET_DIR/frontend/
cp -r frontend/stores $TARGET_DIR/frontend/
cp frontend/package.json $TARGET_DIR/frontend/
cp frontend/tsconfig.json $TARGET_DIR/frontend/
cp frontend/next.config.js $TARGET_DIR/frontend/
cp frontend/tailwind.config.js $TARGET_DIR/frontend/
cp frontend/postcss.config.js $TARGET_DIR/frontend/

# Copy minimal config files
echo "Copying configuration files..."
cp requirements.txt $TARGET_DIR/
cp .env.example $TARGET_DIR/
cp .gitignore $TARGET_DIR/
cp README.md $TARGET_DIR/ 2>/dev/null || echo "No README.md found"

# Copy minimal deployment files
cp Dockerfile.production $TARGET_DIR/Dockerfile
cp docker-compose.yml $TARGET_DIR/

# Create a minimal README
cat > $TARGET_DIR/README.md << 'EOF'
# CX Futurist AI - Lite Version

A streamlined version of the CX Futurist AI system with only essential files.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
cd frontend && npm install
```

2. Set up environment:
```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

3. Run the system:
```bash
# Backend
python -m src.main

# Frontend (in another terminal)
cd frontend && npm run dev
```

## Features
- 6 AI agents for customer experience analysis
- Real-time visualization dashboard
- WebSocket support for live updates
- Cloud-ready deployment

## Structure
- `src/` - Backend Python code
- `frontend/` - Next.js dashboard
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Docker setup
EOF

# Remove test files and __pycache__
find $TARGET_DIR -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find $TARGET_DIR -name "test_*.py" -delete
find $TARGET_DIR -name "*_test.py" -delete
find $TARGET_DIR -name "*.pyc" -delete

# Count files
TOTAL_FILES=$(find $TARGET_DIR -type f | wc -l)
echo "Created lite version with $TOTAL_FILES files"
echo "Location: $TARGET_DIR"

# Show size
SIZE=$(du -sh $TARGET_DIR | cut -f1)
echo "Total size: $SIZE"