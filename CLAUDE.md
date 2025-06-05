# CX Futurist AI - Claude Development Guide

## Project Overview
Building a multi-agent AI system using CrewAI that acts as a "Customer Experience Futurist" - analyzing emerging trends, technologies, and behavioral shifts to predict how customer-organization interactions will evolve.

## Key Architecture Components

### 1. Core Agents (Priority Order)
1. **AI & Agentic Futurist Agent** - Tracks AI/agent evolution and implications
2. **Trend Scanner Agent** - Identifies weak signals across data sources
3. **Customer Insight Agent** - Analyzes customer behavior evolution
4. **Tech Impact Agent** - Evaluates emerging technology implications
5. **Org Transformation Agent** - Predicts organizational changes
6. **Synthesis Agent** - Creates coherent scenarios and reports

### 2. Real-Time Visualization Frontend
- **Agent Activity Dashboard** - Live view of all agents thinking, analyzing, collaborating
- **Knowledge Graph Visualization** - Interactive 3D graph showing connections being made
- **Trend Flow Visualization** - Animated flow of signals from sources to insights
- **Scenario Builder Interface** - Watch scenarios evolve in real-time
- **Agent Collaboration Theater** - See agents passing insights between each other
- **Thought Stream Display** - Show agent reasoning chains and decision processes

### 3. MCP Server Architecture
- Research MCP Server (academic papers, arxiv)
- AI Research MCP Server (AI papers, benchmarks)
- News & Media MCP Server (real-time trends)
- Social Media MCP Server (sentiment, viral trends)
- Patent MCP Server (innovation tracking)
- Industry Report MCP Server (Gartner, Forrester)

### 4. Vector Database Collections
- `research_papers` - Academic papers with rich metadata
- `ai_generated_insights` - Synthetic insights from agents
- `future_scenarios` - Detailed scenario narratives
- `ai_agentic_research` - AI/agent specific research

### 5. Key Workflows
1. **Emerging Trend Analysis** - Weak signal → impact analysis → report
2. **AI-Driven CX Evolution** - AI breakthrough → adoption roadmap
3. **Future Scenario Planning** - Uncertainties → multiple scenarios
4. **Agentic Economy Assessment** - Agent interactions → business impact
5. **Knowledge Synthesis** - Cross-domain pattern recognition

## Frontend Visualization Architecture

### Real-Time Agent Activity Display
- **WebSocket Integration** - Stream agent thoughts and actions in real-time
- **Agent Avatar System** - Visual representation of each agent with personality
- **Activity Streams** - Show what each agent is reading, thinking, writing
- **Collaboration Visualization** - Animated lines showing data/insight handoffs
- **Progress Indicators** - Visual progress bars for each analysis phase

### Interactive Knowledge Graph
- **3D Force-Directed Graph** - Using Three.js/D3.js for smooth animations
- **Node Types**: Papers, Insights, Trends, Scenarios, Predictions
- **Edge Animations** - Show new connections forming in real-time
- **Zoom & Filter** - Drill into specific domains or time periods
- **Heat Maps** - Show "hot" areas of research activity

### Trend Flow Visualization
- **Sankey Diagrams** - Show how weak signals become strong trends
- **Timeline Animations** - Watch trends emerge and evolve over time
- **Signal Strength Meters** - Real-time gauges showing signal confidence
- **Source Attribution** - Visual links back to originating data

### Agent Collaboration Theater
- **Split-Screen Views** - Watch multiple agents work simultaneously
- **Message Passing Animation** - See insights flow between agents
- **Thinking Bubbles** - Animated thought processes with key decisions
- **Debate Visualization** - When agents disagree, show the resolution process

### Scenario Builder Interface
- **Branching Timelines** - Interactive scenario trees
- **Probability Clouds** - Visualize uncertainty ranges
- **What-If Sliders** - Adjust variables and see scenario changes
- **Milestone Markers** - Key decision points highlighted

### Dashboard Components
```typescript
// Key frontend components to build
- AgentActivityPanel: Real-time agent status and actions
- KnowledgeGraph3D: Interactive knowledge visualization  
- TrendFlowChart: Animated trend evolution
- ScenarioExplorer: Interactive future scenarios
- InsightStream: Live feed of generated insights
- CollaborationMap: Agent interaction patterns
- ConfidenceMeter: Prediction confidence visualization
- SourceTracker: Data provenance visualization
```

### Frontend Tech Stack
- **Framework**: Next.js 14 with App Router
- **Real-time**: Socket.io for WebSocket communication
- **3D Graphics**: Three.js for knowledge graph
- **Charts**: D3.js + Recharts for data viz
- **Animation**: Framer Motion for smooth transitions
- **State**: Zustand for real-time state management
- **Styling**: Tailwind CSS + Radix UI

### User Experience Goals
1. **Transparency** - Users see exactly how insights are generated
2. **Trust Building** - Show sources and confidence levels
3. **Engagement** - Make AI analysis visually compelling
4. **Education** - Help users understand the analysis process
5. **Control** - Allow users to guide and refine analysis

## Development Best Practices

### Agent Development
- Keep agents single-purpose and focused
- Use temperature=0.0 for deterministic outputs
- Implement proper error handling and retries
- Log all agent interactions for debugging
- Use async operations for parallel processing

### Vector Database Strategy
- Create multiple embedding types per document
- Implement hierarchical embeddings (doc → section → paragraph)
- Build knowledge graph relationships
- Use hybrid search (vector + metadata)
- Track temporal evolution of concepts

### MCP Server Integration
- Implement rate limiting and caching
- Handle API failures gracefully
- Use async/await for all external calls
- Validate and sanitize all inputs
- Store raw data before processing

### Testing Strategy
- Unit tests for each agent
- Integration tests for workflows
- Mock external APIs for testing
- Test edge cases and error scenarios
- Performance benchmarking

## Implementation Phases

### Phase 1: Foundation (Days 1-3)
1. Project structure and configuration
2. Base agent classes and tools
3. Vector database setup
4. Basic MCP server stubs
5. Frontend scaffolding with Next.js
6. WebSocket infrastructure setup

### Phase 2: Core Agents & Visualization (Days 4-7)
1. Implement all 6 specialized agents
2. Create agent tools and utilities
3. Basic workflow orchestration
4. Initial testing framework
5. Agent activity streaming to frontend
6. Basic dashboard UI components

### Phase 3: Data Pipeline & Live Updates (Days 8-10)
1. MCP server implementations
2. Data ingestion pipelines
3. Vector database population
4. Knowledge graph construction
5. Real-time knowledge graph visualization
6. Trend flow animations

### Phase 4: Advanced Features & UI (Days 11-14)
1. Weak signal detection
2. Scenario simulation
3. Trend interconnection mapping
4. Semantic search interface
5. Agent collaboration theater
6. Interactive scenario builder

### Phase 5: Integration & Polish (Days 15-17)
1. Full system integration
2. End-to-end testing
3. Performance optimization
4. UI/UX refinements
5. Animation polish
6. Documentation

### Phase 6: Deployment (Days 18-20)
1. Docker containerization
2. API endpoint setup
3. Monitoring configuration
4. Production deployment
5. Frontend deployment
6. Performance monitoring

## Critical Implementation Details

### AI & Agentic Futurist Focus
- Track LLM benchmarks (MMLU, HumanEval, AgentBench)
- Monitor agent capability evolution
- Analyze human-agent collaboration patterns
- Predict agent economy emergence
- Focus on trust and governance implications

### Semantic Search Implementation
```python
# Core search patterns to implement
- find_similar_insights(insight_id)
- trace_idea_evolution(concept)
- find_supporting_evidence(hypothesis)
- find_contradictions(claim)
- bridge_domains(source_domain, target_domain)
```

### Knowledge Building Process
1. Continuous paper ingestion
2. Multi-dimensional embeddings
3. Insight generation and validation
4. Confidence scoring
5. Temporal tracking

## File Creation Order

1. **Configuration Files**
   - requirements.txt ✓
   - .env.example
   - docker-compose.yml
   - README.md
   - package.json (frontend)
   - next.config.js

2. **Base Infrastructure**
   - src/__init__.py files
   - src/config/base_config.py
   - src/tools/base_tool.py
   - src/agents/base_agent.py
   - src/websocket/socket_server.py
   - src/api/base_api.py

3. **Frontend Foundation**
   - frontend/app/layout.tsx
   - frontend/app/page.tsx
   - frontend/components/AgentActivityPanel.tsx
   - frontend/components/KnowledgeGraph3D.tsx
   - frontend/lib/socket.ts
   - frontend/stores/agentStore.ts

4. **Vector Database Layer**
   - src/tools/vector_tools.py
   - src/config/vector_config.py
   - Database initialization scripts

5. **MCP Integration**
   - src/config/mcp_config.py
   - src/tools/mcp_tools.py
   - mcp_servers/base_server.py

6. **Core Agents with Streaming**
   - src/agents/ai_agentic_futurist_agent.py (PRIORITY)
   - src/agents/trend_scanner_agent.py
   - src/agents/customer_insight_agent.py
   - src/agents/tech_impact_agent.py
   - src/agents/org_transformation_agent.py
   - src/agents/synthesis_agent.py

7. **Frontend Visualization Components**
   - frontend/components/TrendFlowChart.tsx
   - frontend/components/ScenarioExplorer.tsx
   - frontend/components/CollaborationMap.tsx
   - frontend/components/InsightStream.tsx
   - frontend/components/ConfidenceMeter.tsx

8. **Orchestration**
   - src/crews/futurist_crew.py
   - src/crews/analysis_workflows.py
   - src/agents/futurist_coordinator.py

9. **Analysis Tools**
   - src/tools/trend_analysis_tools.py
   - src/tools/prediction_tools.py
   - src/knowledge_base/signal_patterns.py

10. **API & Real-time Interface**
    - src/main.py
    - src/api/analysis_endpoints.py
    - src/api/websocket_handlers.py
    - src/streaming/agent_stream.py

## Key Dependencies

### Core Libraries
- crewai>=0.22.0 (agent orchestration)
- langchain>=0.1.0 (LLM tooling)
- chromadb>=0.4.22 (vector database)
- fastapi>=0.108.0 (API framework)

### Critical Integrations
- OpenAI API (GPT-4 for agents)
- Anthropic API (Claude for MCP)
- Pinecone/ChromaDB (vector storage)
- Redis (caching layer)

## Success Metrics to Track
- Prediction accuracy over time
- Signal-to-noise ratio
- Insight generation rate
- Query response time
- Trend detection latency

## Common Pitfalls to Avoid
1. Over-engineering agents (keep them focused)
2. Ignoring rate limits on APIs
3. Not implementing proper error handling
4. Forgetting to test edge cases
5. Not tracking agent performance metrics

## Testing Checklist
- [ ] Unit tests for all agents
- [ ] Integration tests for workflows
- [ ] Vector database performance tests
- [ ] MCP server connection tests
- [ ] End-to-end scenario tests
- [ ] Load testing for concurrent operations
- [ ] Semantic search accuracy tests

## Ready for YOLO Mode
This project is ideal for YOLO mode development because:
- Clear structure and dependencies
- Well-defined agent roles
- Modular architecture
- Extensive testing needs
- Many files to create

## Quick Start Commands
```bash
# After entering YOLO mode
cd /Users/jonatkin/Documents/Agentic/cx-futurist-ai
# Claude will handle the rest
```