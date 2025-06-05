# Simple Orchestrator for CX Futurist AI

## Overview

The `SimpleOrchestrator` coordinates all 6 specialized agents to perform complex multi-agent workflows without requiring CrewAI. It manages agent collaboration, streams real-time updates via WebSocket, and supports multiple workflow types.

## Architecture

### Core Components

1. **SimpleOrchestrator** - Main orchestration class
2. **6 Specialized Agents**:
   - AI & Agentic Futurist Agent
   - Trend Scanner Agent
   - Customer Insight Agent
   - Tech Impact Agent
   - Org Transformation Agent
   - Synthesis Agent
3. **WebSocket Integration** - Real-time streaming of agent activities
4. **Workflow Management** - Tracks and manages active workflows

### Key Features

- **Concurrent Agent Operations** - Agents can work in parallel for efficiency
- **Real-time Streaming** - All agent thoughts, collaborations, and progress streamed via WebSocket
- **Error Handling** - Graceful error handling with proper status updates
- **Agent Collaboration** - Agents can share insights and data with each other
- **Workflow Tracking** - Complete tracking of workflow status and results

## Workflows

### 1. Trend Analysis (`analyze_trend`)

Analyzes emerging trends with multiple perspectives:

```python
result = await orchestrator.analyze_trend(
    topic="AI agents in customer service",
    depth="comprehensive"  # or "focused", "quick"
)
```

**Workflow Steps**:
1. Trend Scanner identifies weak signals
2. Parallel analysis by 4 specialized agents
3. Synthesis creates coherent report
4. Knowledge graph updated with findings

### 2. Scenario Creation (`create_scenario`)

Creates future scenarios for a domain:

```python
result = await orchestrator.create_scenario(
    domain="retail",
    timeframe="5_years",
    uncertainties=["AI adoption rate", "consumer privacy"]
)
```

**Workflow Steps**:
1. Identify key drivers (AI, tech, behavior, org)
2. Map trajectories and evolution paths
3. Create multiple scenarios with probabilities
4. Broadcast scenario updates

### 3. AI Economy Assessment (`assess_ai_economy`)

Assesses the emerging AI/agent economy:

```python
result = await orchestrator.assess_ai_economy(
    industry="healthcare",
    focus_areas=["automation", "human_agent_collaboration"]
)
```

**Workflow Steps**:
1. Analyze agent capabilities evolution
2. Scan adoption patterns
3. Model business impact
4. Create strategic recommendations

### 4. Knowledge Synthesis (`knowledge_synthesis`)

Synthesizes knowledge across domains:

```python
result = await orchestrator.knowledge_synthesis(
    domains=["healthcare", "finance", "retail"],
    objective="identify cross-industry AI patterns"
)
```

**Workflow Steps**:
1. Cross-domain pattern recognition
2. Multi-perspective analysis
3. Knowledge synthesis
4. Novel connection discovery

## API Integration

### Starting a Workflow

```python
# Via API endpoint
POST /api/workflows/scenario
{
    "domain": "retail",
    "timeframe": "5_years",
    "uncertainties": ["AI adoption", "regulation"]
}
```

### Checking Workflow Status

```python
GET /api/workflows/status/{workflow_id}
```

### WebSocket Events

Connect to `/ws/socket.io/` to receive real-time updates:

```javascript
// Agent thinking
{
    "event": "agent:thinking",
    "agent": "ai_futurist",
    "data": "Analyzing AI capability evolution..."
}

// Agent collaboration
{
    "event": "agent:collaboration",
    "agent": "trend_scanner",
    "data": {
        "with": "synthesis",
        "message": "Sharing weak signals"
    }
}

// Workflow updates
{
    "event": "workflow:completed",
    "workflow_id": "trend_analysis_1234",
    "results": {...}
}
```

## Usage Example

```python
from src.orchestrator.simple_orchestrator import SimpleOrchestrator
from src.websocket.socket_server import agent_stream_callback

# Initialize orchestrator
orchestrator = SimpleOrchestrator(stream_callback=agent_stream_callback)

# Run trend analysis
result = await orchestrator.analyze_trend(
    topic="Generative AI in customer experience",
    depth="comprehensive"
)

# Access results
print(f"Summary: {result.results['summary']}")
print(f"Key Insights: {result.results['key_insights']}")
print(f"Duration: {result.duration} seconds")

# Check agent outputs
for agent_name, output in result.agent_outputs.items():
    print(f"\n{agent_name} output: {output}")
```

## Agent Coordination

Agents collaborate through:

1. **Direct Data Passing** - Agents share analysis results
2. **Context Enrichment** - Each agent adds to shared context
3. **Synthesis Integration** - Final agent combines all insights
4. **Real-time Updates** - All collaboration streamed via WebSocket

## Error Handling

The orchestrator handles errors gracefully:

- Failed workflows update status to `FAILED`
- Errors are logged and broadcast via WebSocket
- Partial results are preserved when possible
- Workflows can be cancelled mid-execution

## Performance Considerations

- Agents run in parallel where possible using `asyncio.gather()`
- WebSocket streaming is non-blocking
- Each agent maintains its own conversation history
- Workflows are tracked in memory (production would use database)

## Testing

Run the test scripts:

```bash
# Basic test
python test_simple_orchestrator.py

# Full integration test (requires API keys)
python test_orchestrator.py
```

## Future Enhancements

1. **Persistent Workflow Storage** - Save workflows to database
2. **Agent Performance Metrics** - Track agent efficiency
3. **Dynamic Agent Selection** - Choose agents based on task
4. **Workflow Templates** - Predefined workflow configurations
5. **Agent Learning** - Agents improve based on feedback