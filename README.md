# CX Futurist AI - Minimal Version

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
