# CX Futurist AI - Local Setup Guide

This guide will help you run the CX Futurist AI system locally for testing and development.

## Quick Start

### 1. Prerequisites

- Python 3.12 or higher
- OpenAI API key with GPT-4 access
- Git

### 2. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd cx-futurist-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# The only REQUIRED configuration is:
# OPENAI_API_KEY=your-actual-api-key-here
```

### 4. Run Analysis Locally

```bash
# Run the test script
python test_local_analysis.py
```

## Available Analysis Types

The system supports four main workflow types:

### 1. **Trend Analysis** (`analyze_trend`)
Analyzes emerging trends with multiple agents:
- Trend Scanner identifies weak signals
- AI Futurist analyzes AI/agent implications  
- Customer Insight examines behavior changes
- Tech Impact evaluates technology implications
- Org Transformation predicts organizational changes
- Synthesis creates coherent report

### 2. **Scenario Creation** (`create_scenario`)
Creates future scenarios for a domain:
- Identifies key AI/agent drivers
- Maps technology trajectories
- Predicts behavior shifts
- Models organizational evolution
- Generates multiple plausible scenarios

### 3. **AI Economy Assessment** (`assess_ai_economy`)
Assesses the emerging AI/agent economy for an industry:
- Analyzes agent capability evolution
- Identifies adoption patterns
- Models business impact
- Creates strategic recommendations

### 4. **Knowledge Synthesis** (`knowledge_synthesis`)
Synthesizes knowledge across multiple domains:
- Identifies cross-domain patterns
- Analyzes from multiple perspectives
- Creates cross-domain insights

## Running the Full Web Application

### Option 1: Simple API Server (Recommended for Testing)

```bash
# Start the API server
python -m src.main

# The server will start on http://localhost:8080
# API documentation available at http://localhost:8080/docs
```

### Option 2: With Frontend (Full Experience)

```bash
# Terminal 1: Start the backend
python -m src.main

# Terminal 2: Start the frontend
cd frontend
npm install
npm run dev

# Access at http://localhost:3000
```

## Pre-configured Analysis Prompts

The system includes sophisticated prompt templates for various analyses:

### Example Topics to Try:
1. **AI Agents in Customer Support**
   - "AI agents transforming customer support"
   - "Autonomous support systems and human collaboration"

2. **Personalization & Marketing**
   - "Generative AI in personalized marketing"
   - "AI-driven customer journey optimization"

3. **Conversational Commerce**
   - "Voice AI and conversational commerce"
   - "Natural language shopping assistants"

4. **Retail Innovation**
   - "Autonomous systems in retail experiences"
   - "AI-powered store operations"

5. **Predictive Analytics**
   - "AI-powered predictive customer analytics"
   - "Real-time behavior prediction systems"

## API Endpoints

Once the server is running, you can access:

### Analysis Endpoints
- `POST /api/analysis-direct/` - Start a new analysis
- `GET /api/analysis-direct/{request_id}` - Check analysis status
- `GET /api/analysis-direct/` - List recent analyses

### Workflow Endpoints
- `POST /api/workflows/trend-analysis` - Start trend analysis workflow
- `POST /api/workflows/scenario-creation` - Create future scenarios
- `POST /api/workflows/ai-economy` - Assess AI economy impact
- `POST /api/workflows/knowledge-synthesis` - Synthesize cross-domain knowledge

### System Status
- `GET /api/status` - Check system and service status
- `GET /api/agents/states` - View all agent states

## Direct Python Usage

You can also use the orchestrator directly in Python:

```python
import asyncio
from src.orchestrator.simple_orchestrator import SimpleOrchestrator

async def run_analysis():
    orchestrator = SimpleOrchestrator()
    
    # Run trend analysis
    result = await orchestrator.analyze_trend(
        topic="AI transforming customer experience",
        depth="comprehensive"
    )
    
    print(f"Summary: {result.results['summary']}")
    print(f"Insights: {result.results['key_insights']}")
    print(f"Confidence: {result.results['confidence']}")

asyncio.run(run_analysis())
```

## Understanding the Output

Each analysis produces:

1. **Executive Summary** - High-level overview
2. **Key Insights** - Bullet-point discoveries
3. **Recommendations** - Actionable next steps
4. **Confidence Level** - How certain the AI is (0-100%)
5. **Agent Outputs** - Detailed thoughts from each specialized agent

## Troubleshooting

### Common Issues:

1. **"OPENAI_API_KEY not found"**
   - Make sure you've set the API key in your .env file
   - Ensure the .env file is in the project root

2. **"Rate limit exceeded"**
   - The system uses GPT-4 which has rate limits
   - Wait a minute and try again
   - Consider using shorter analysis depths

3. **"Module not found"**
   - Ensure you've activated the virtual environment
   - Run `pip install -r requirements.txt` again

4. **Slow performance**
   - Each analysis involves multiple AI agents
   - "comprehensive" depth takes 2-5 minutes
   - Use "quick" depth for faster results

## Optional Services

The system runs without these, but they enhance functionality:

### Pinecone (Vector Search)
- Enables semantic search across analyses
- Stores and retrieves similar insights
- Configure in .env if you have an account

### Redis (Caching)
- Speeds up repeated analyses
- Caches intermediate results
- Install locally: `brew install redis` (Mac) or `sudo apt install redis` (Linux)

## Development Tips

1. **Check Logs**: Detailed logs are written to `cx_futurist.log`
2. **API Docs**: Visit http://localhost:8080/docs for interactive API documentation
3. **WebSocket Events**: Connect to ws://localhost:8080/ws for real-time updates
4. **Debug Mode**: Set `LOG_LEVEL=DEBUG` in .env for verbose output

## Next Steps

1. Try different analysis topics and depths
2. Experiment with scenario creation for your industry
3. Use the API to integrate with other tools
4. Explore the agent outputs to understand the AI's reasoning

Happy analyzing! 🚀