# CX Futurist AI

An advanced multi-agent AI system that analyzes emerging trends, technologies, and behavioral shifts to predict how customer-organization interactions will evolve.

## 🚀 Features

- **6 Specialized AI Agents**: Each focused on different aspects of future CX analysis
- **Real-time Visualization**: Watch agents think, collaborate, and generate insights live
- **3D Knowledge Graph**: Interactive visualization of connections between concepts
- **Trend Analysis**: Track weak signals evolving into strong trends
- **Scenario Planning**: Explore multiple future scenarios with branching timelines
- **Web Search Integration**: Real-time data gathering using OpenAI's web search capabilities
- **Vector Database**: Semantic search powered by Pinecone

## 🏗️ Architecture

### AI Agents
1. **AI & Agentic Futurist Agent** - Tracks AI/agent evolution and implications
2. **Trend Scanner Agent** - Identifies weak signals across data sources
3. **Customer Insight Agent** - Analyzes customer behavior evolution
4. **Tech Impact Agent** - Evaluates emerging technology implications
5. **Org Transformation Agent** - Predicts organizational changes
6. **Synthesis Agent** - Creates coherent scenarios and reports

### Technology Stack
- **Backend**: FastAPI, CrewAI, OpenAI API
- **Frontend**: Next.js 14, Three.js, D3.js, Framer Motion
- **Database**: Pinecone (vector), Redis (cache)
- **Real-time**: WebSocket, Socket.io
- **Search**: Tavily API for web search

## 🛠️ Installation

### Prerequisites

#### Required
- Python 3.12+
- Node.js 18+ (for frontend)
- OpenAI API Key

#### Optional (for enhanced features)
- Pinecone API Key (for vector search capabilities)
- Redis (for caching)
- Docker & Docker Compose (for containerized deployment)

### Quick Start

#### Minimal Setup (OpenAI only)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cx-futurist-ai.git
cd cx-futurist-ai
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Start the backend:
```bash
python -m uvicorn src.main:app --reload --port 8000
```

The system will start with:
- ✅ Full agent functionality using OpenAI
- ⚠️ No vector search (Pinecone not configured)
- ⚠️ No caching (Redis not running)

#### Full Setup (with all features)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cx-futurist-ai.git
cd cx-futurist-ai
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
```

4. Start with Docker Compose:
```bash
docker-compose up -d
```

5. Access the dashboard:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Run backend:
```bash
python -m uvicorn src.main:app --reload --port 8000
```

4. Run frontend:
```bash
cd frontend
npm run dev
```

## 📊 Dashboard Features

### Agent Activity Panel
- Real-time status of all agents
- Live thought streams
- Collaboration visualization

### Knowledge Graph 3D
- Interactive force-directed graph
- Zoom, rotate, and filter
- Heat maps showing research activity

### Trend Flow Chart
- Animated visualization of trend evolution
- Signal strength indicators
- Source attribution

### Scenario Explorer
- Interactive branching timelines
- Probability clouds
- What-if analysis tools

## 🔧 Configuration

### Service Availability & Graceful Degradation

The system is designed to run with minimal dependencies. Only OpenAI API is required.

| Service | Required | Impact if Unavailable |
|---------|----------|----------------------|
| OpenAI API | ✅ Yes | System won't start |
| Pinecone | ❌ No | No vector search, semantic search disabled |
| Redis | ❌ No | No caching, slower repeated operations |

Check service status:
```bash
curl http://localhost:8000/api/status
```

### Agent Settings
Configure agent behavior in `.env`:
- `AGENT_MODEL`: GPT model to use (default: gpt-4o-mini)
- `AGENT_TEMPERATURE`: Creativity level (default: 0.0)
- `AGENT_MAX_TOKENS`: Response length (default: 4096)

### Vector Database (Optional)
Pinecone settings:
- `PINECONE_INDEX_NAME`: Index for storing embeddings
- `PINECONE_DIMENSION`: Embedding dimension (default: 1536)

## 📚 API Documentation

### Core Endpoints

#### Start Analysis
```
POST /api/analyze
{
  "topic": "Future of AI in Customer Service",
  "depth": "comprehensive",
  "timeframe": "5-10 years"
}
```

#### Get Trends
```
GET /api/trends?category=emerging&limit=10
```

#### Search Knowledge Base
```
POST /api/search
{
  "query": "autonomous agents customer interaction",
  "filters": {"date_range": "last_6_months"}
}
```

### WebSocket Events

Connect to `ws://localhost:8001` for real-time updates:

- `agent:thinking` - Agent thought process
- `agent:collaboration` - Inter-agent communication
- `insight:generated` - New insights created
- `graph:update` - Knowledge graph changes

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## 🚀 Deployment

### Production Setup

1. Update production environment variables
2. Build and push Docker images
3. Deploy using docker-compose or Kubernetes

### Monitoring

- Prometheus metrics at `/metrics`
- Health check at `/health`
- Logs in JSON format for aggregation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with:
- CrewAI for agent orchestration
- OpenAI for language models
- Pinecone for vector search
- The open source community

---

**Note**: This is an experimental system exploring the future of customer experience. Predictions and scenarios generated are speculative and should be validated with domain expertise.