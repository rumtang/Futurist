#!/usr/bin/env python3
"""
Create a minimal version of CX Futurist AI with only the actively used code
"""
import os
import shutil

# Define what we actually need
ESSENTIAL_FILES = {
    # Core backend files (only the simple agents are used)
    'src/main.py': 'src/main.py',
    'src/__init__.py': 'src/__init__.py',
    
    # Config
    'src/config/__init__.py': 'src/config/__init__.py', 
    'src/config/base_config.py': 'src/config/base_config.py',
    
    # Only the simple agents (the others aren't used)
    'src/agents/__init__.py': 'src/agents/__init__.py',
    'src/agents/simple_agent.py': 'src/agents/simple_agent.py',
    'src/agents/simple_ai_futurist_agent.py': 'src/agents/simple_ai_futurist_agent.py',
    'src/agents/simple_customer_insight_agent.py': 'src/agents/simple_customer_insight_agent.py',
    'src/agents/simple_org_transformation_agent.py': 'src/agents/simple_org_transformation_agent.py',
    'src/agents/simple_synthesis_agent.py': 'src/agents/simple_synthesis_agent.py',
    'src/agents/simple_tech_impact_agent.py': 'src/agents/simple_tech_impact_agent.py',
    'src/agents/simple_trend_scanner_agent.py': 'src/agents/simple_trend_scanner_agent.py',
    
    # Orchestrator
    'src/orchestrator/__init__.py': 'src/orchestrator/__init__.py',
    'src/orchestrator/simple_orchestrator.py': 'src/orchestrator/simple_orchestrator.py',
    
    # API endpoints
    'src/api/__init__.py': 'src/api/__init__.py',
    'src/api/base_api.py': 'src/api/base_api.py',
    'src/api/agent_endpoints.py': 'src/api/agent_endpoints.py',
    'src/api/analysis_endpoints.py': 'src/api/analysis_endpoints.py',
    'src/api/analysis_direct.py': 'src/api/analysis_direct.py',
    
    # WebSocket
    'src/websocket/__init__.py': 'src/websocket/__init__.py',
    'src/websocket/socket_server.py': 'src/websocket/socket_server.py',
    'src/websocket/socketio_server.py': 'src/websocket/socketio_server.py',
    
    # Frontend - only actively used components
    'frontend/app/layout.tsx': 'frontend/app/layout.tsx',
    'frontend/app/page.tsx': 'frontend/app/page.tsx',
    'frontend/app/dashboard/page.tsx': 'frontend/app/dashboard/page.tsx',
    'frontend/app/analysis/page.tsx': 'frontend/app/analysis/page.tsx',
    'frontend/app/globals.css': 'frontend/app/globals.css',
    
    'frontend/components/AgentActivityPanel.tsx': 'frontend/components/AgentActivityPanel.tsx',
    'frontend/components/AnalysisControl.tsx': 'frontend/components/AnalysisControl.tsx',
    'frontend/components/InsightStream.tsx': 'frontend/components/InsightStream.tsx',
    'frontend/components/TrendFlowChart.tsx': 'frontend/components/TrendFlowChart.tsx',
    
    'frontend/lib/socket.ts': 'frontend/lib/socket.ts',
    'frontend/lib/config.ts': 'frontend/lib/config.ts',
    'frontend/lib/utils.ts': 'frontend/lib/utils.ts',
    
    'frontend/stores/agentStore.ts': 'frontend/stores/agentStore.ts',
    
    # Config files
    'frontend/package.json': 'frontend/package.json',
    'frontend/next.config.js': 'frontend/next.config.js',
    'frontend/tsconfig.json': 'frontend/tsconfig.json',
    'frontend/tailwind.config.js': 'frontend/tailwind.config.js',
    'frontend/postcss.config.js': 'frontend/postcss.config.js',
    
    'requirements.txt': 'requirements.txt',
    '.env.example': '.env.example',
    '.gitignore': '.gitignore',
}

# Create minimal structure
os.makedirs('minimal-version', exist_ok=True)

for src, dst in ESSENTIAL_FILES.items():
    dst_path = os.path.join('minimal-version', dst)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    
    try:
        shutil.copy2(src, dst_path)
        print(f"✓ Copied {src}")
    except FileNotFoundError:
        print(f"✗ Skipped {src} (not found)")

# Create minimal README
readme_content = """# CX Futurist AI - Minimal Version

This is a minimal version containing only the essential, actively used code.

## Structure

```
src/
├── main.py                 # Main FastAPI application
├── agents/                 # AI agents (only simple_* agents are used)
│   └── simple_*.py        # 6 specialized agents
├── orchestrator/          # Agent coordination
│   └── simple_orchestrator.py
├── api/                   # REST endpoints
└── websocket/             # Real-time communication

frontend/
├── app/                   # Next.js pages
├── components/            # React components
├── lib/                   # Utilities
└── stores/               # State management
```

## Quick Start

1. Backend: `python -m src.main`
2. Frontend: `cd frontend && npm install && npm run dev`
"""

with open('minimal-version/README.md', 'w') as f:
    f.write(readme_content)

# Count results
import subprocess
result = subprocess.run(['find', 'minimal-version', '-type', 'f', '-name', '*.py', '-o', '-name', '*.ts', '-o', '-name', '*.tsx'], 
                       capture_output=True, text=True)
file_count = len(result.stdout.strip().split('\n'))

size_result = subprocess.run(['du', '-sh', 'minimal-version'], capture_output=True, text=True)
size = size_result.stdout.split('\t')[0]

print(f"\n✅ Created minimal version:")
print(f"   Files: {file_count} code files")
print(f"   Size: {size}")
print(f"   Location: minimal-version/")