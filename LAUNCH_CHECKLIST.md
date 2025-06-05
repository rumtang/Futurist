# CX Futurist AI - Launch Checklist

## 🚀 Pre-Launch Requirements

### API Keys & Services
- [ ] OpenAI API Key obtained
- [ ] Pinecone account created with API key
- [ ] Tavily API key (optional, for enhanced web search)
- [ ] Google Cloud Project created (for deployment)

### Local Development Setup
- [ ] Python 3.12+ installed
- [ ] Node.js 18+ installed
- [ ] Docker & Docker Compose installed
- [ ] Redis running locally or via Docker

## 🛠️ Local Development Launch

### 1. Environment Setup
```bash
# Clone the repository
cd cx-futurist-ai

# Copy environment variables
cp .env.example .env

# Edit .env and add your keys
# OPENAI_API_KEY=your-key-here
# PINECONE_API_KEY=your-key-here
# PINECONE_ENVIRONMENT=your-env-here
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis (if not using Docker)
redis-server

# Run the backend
python -m uvicorn src.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

### 4. Docker Compose (Alternative)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🌐 Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8001

## ✅ Verification Steps

### 1. System Health Check
```bash
curl http://localhost:8000/health
```

### 2. Test Analysis
1. Open http://localhost:3000
2. Navigate to Dashboard
3. Enter a test topic: "AI transforming customer service"
4. Click "Start Analysis"
5. Watch agents collaborate in real-time

### 3. Check Visualizations
- [ ] Agent Activity Panel shows all 6 agents
- [ ] Insight Stream updates with new insights
- [ ] Trend Flow shows emerging trends
- [ ] WebSocket connection indicator is green

## 🚀 Production Deployment (Google Cloud Run)

### 1. Prerequisites
```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Deploy
```bash
# Run deployment script
./deploy.sh

# Follow prompts to enter API keys
```

### 3. Post-Deployment
- [ ] Test production URLs
- [ ] Check Cloud Run logs
- [ ] Verify WebSocket connectivity
- [ ] Test an analysis end-to-end

## 🐛 Troubleshooting

### Common Issues

#### "Connection refused" errors
- Ensure Redis is running
- Check if ports 8000, 8001, 3000 are available

#### WebSocket not connecting
- Check CORS settings
- Verify WebSocket URL in frontend env
- Check browser console for errors

#### Pinecone errors
- Verify API key and environment
- Check if index exists
- Ensure dimension matches (1536)

#### Agent errors
- Check OpenAI API key
- Verify model availability
- Check rate limits

### Debug Commands
```bash
# Check backend logs
docker-compose logs api

# Check frontend logs
docker-compose logs frontend

# Test WebSocket
wscat -c ws://localhost:8001

# Check Redis
redis-cli ping
```

## 📊 Performance Optimization

### For Production
1. **Enable Redis caching** - Already configured
2. **Use connection pooling** - Built into Pinecone client
3. **Set appropriate rate limits** - Configured in API
4. **Enable CDN for frontend** - Use Cloudflare or similar
5. **Monitor API usage** - Track OpenAI costs

### Scaling Considerations
- Cloud Run auto-scales based on traffic
- Consider implementing queuing for heavy analysis
- Use Cloud Tasks for long-running analyses
- Monitor Pinecone index size and performance

## 🎯 Success Metrics

Track these metrics to ensure healthy operation:
- **API Response Time**: < 500ms for searches
- **Analysis Completion**: < 2 minutes for standard analysis
- **WebSocket Latency**: < 100ms
- **Agent Success Rate**: > 95%
- **Vector Search Accuracy**: > 80% relevance

## 🚦 Launch Readiness Checklist

### Essential
- [ ] All API keys configured
- [ ] System health check passes
- [ ] Basic analysis completes successfully
- [ ] Frontend loads without errors
- [ ] WebSocket connection stable

### Recommended
- [ ] Error monitoring configured (Sentry)
- [ ] Analytics tracking enabled
- [ ] Backup strategy defined
- [ ] Cost alerts configured
- [ ] Documentation reviewed

### Nice to Have
- [ ] Custom domain configured
- [ ] SSL certificates set up
- [ ] CI/CD pipeline configured
- [ ] Load testing completed
- [ ] Security audit performed

## 📝 Post-Launch Tasks

1. **Monitor First 24 Hours**
   - Check error logs
   - Monitor API usage
   - Track user interactions
   - Gather feedback

2. **Optimize Based on Usage**
   - Adjust rate limits
   - Fine-tune agent prompts
   - Optimize vector search
   - Cache frequently accessed data

3. **Plan Enhancements**
   - Additional agent capabilities
   - More visualization types
   - Enhanced scenario planning
   - Integration possibilities

---

**Ready to launch?** Follow this checklist and you'll have a fully functional CX Futurist AI system analyzing the future of customer experience! 🚀