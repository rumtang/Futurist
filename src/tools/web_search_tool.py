"""Web search tool using Tavily API for real-time information gathering."""

from typing import Optional, List, Dict, Any
import httpx
from tavily import TavilyClient
from pydantic import Field
from loguru import logger
import os

from src.tools.base_tool import SearchToolBase, ToolResult
from src.config.base_config import settings


class WebSearchTool(SearchToolBase):
    """Tool for searching the web using Tavily API."""
    
    name: str = "web_search"
    description: str = "Search the web for current information, news, research papers, and trends"
    
    # Tavily-specific settings
    search_depth: str = Field("advanced", description="Search depth: basic or advanced")
    include_images: bool = Field(False, description="Include images in results")
    include_answer: bool = Field(True, description="Include AI-generated answer")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize Tavily client
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        if self.tavily_api_key:
            self.client = TavilyClient(api_key=self.tavily_api_key)
        else:
            logger.warning("TAVILY_API_KEY not found, using mock search")
            self.client = None
    
    async def _arun(self, query: str, **kwargs) -> ToolResult:
        """Execute web search asynchronously."""
        try:
            logger.info(f"Searching web for: {query}")
            
            if self.client:
                # Use Tavily API
                search_params = {
                    "query": query,
                    "search_depth": kwargs.get("search_depth", self.search_depth),
                    "max_results": kwargs.get("max_results", self.max_results),
                    "include_images": kwargs.get("include_images", self.include_images),
                    "include_answer": kwargs.get("include_answer", self.include_answer)
                }
                
                # Add optional parameters
                if "include_domains" in kwargs:
                    search_params["include_domains"] = kwargs["include_domains"]
                if "exclude_domains" in kwargs:
                    search_params["exclude_domains"] = kwargs["exclude_domains"]
                
                # Execute search
                results = await self._tavily_search(search_params)
                
            else:
                # Use mock search for development
                results = await self._mock_search(query)
            
            # Format results
            formatted_results = await self.format_results(results)
            
            return ToolResult(
                success=True,
                data=formatted_results,
                metadata={
                    "query": query,
                    "result_count": len(results),
                    "source": "tavily" if self.client else "mock"
                }
            )
            
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return ToolResult(
                success=False,
                error=f"Search failed: {str(e)}",
                metadata={"query": query}
            )
    
    async def _tavily_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute search using Tavily API."""
        # Tavily client is synchronous, so we run it in a thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        
        def search():
            response = self.client.search(**params)
            results = []
            
            # Extract results
            if response.get("results"):
                for result in response["results"]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "score": result.get("score", 0),
                        "published_date": result.get("published_date"),
                        "source": self._extract_source(result.get("url", ""))
                    })
            
            # Include AI-generated answer if available
            if response.get("answer"):
                results.insert(0, {
                    "title": "AI Summary",
                    "content": response["answer"],
                    "source": "Tavily AI",
                    "score": 1.0
                })
            
            return results
        
        return await loop.run_in_executor(None, search)
    
    async def _mock_search(self, query: str) -> List[Dict[str, Any]]:
        """Mock search for development/testing."""
        logger.debug(f"Using mock search for: {query}")
        
        # Generate mock results based on query
        mock_results = []
        
        if "ai" in query.lower() or "artificial intelligence" in query.lower():
            mock_results.extend([
                {
                    "title": "GPT-5 Rumored to Launch in 2024 with Unprecedented Capabilities",
                    "url": "https://example.com/gpt5-launch",
                    "content": "Industry insiders suggest OpenAI's next model will feature enhanced reasoning, multimodal capabilities, and significant improvements in autonomous agent functionality.",
                    "score": 0.95,
                    "source": "TechNews Daily"
                },
                {
                    "title": "New Benchmark Shows 40% Improvement in AI Agent Performance",
                    "url": "https://example.com/agent-benchmark",
                    "content": "The latest AgentBench results show dramatic improvements in task completion rates for autonomous AI agents, with top models achieving human-level performance on routine tasks.",
                    "score": 0.92,
                    "source": "AI Research Hub"
                }
            ])
        
        if "customer experience" in query.lower() or "cx" in query.lower():
            mock_results.extend([
                {
                    "title": "AI Transforms Customer Service: 73% Satisfaction Rate Achieved",
                    "url": "https://example.com/ai-customer-service",
                    "content": "Major retailers report significant improvements in customer satisfaction after deploying AI-powered service agents capable of handling complex queries.",
                    "score": 0.88,
                    "source": "CX Magazine"
                },
                {
                    "title": "The Future of Personalization: AI-Driven Customer Journeys",
                    "url": "https://example.com/ai-personalization",
                    "content": "New research shows AI can predict customer needs with 85% accuracy, enabling proactive service and personalized experiences at scale.",
                    "score": 0.85,
                    "source": "Business Innovation Weekly"
                }
            ])
        
        if "trend" in query.lower():
            mock_results.extend([
                {
                    "title": "Top 10 Emerging Tech Trends for 2024-2025",
                    "url": "https://example.com/tech-trends",
                    "content": "Analysts identify autonomous AI agents, quantum computing breakthroughs, and brain-computer interfaces as the most impactful emerging technologies.",
                    "score": 0.90,
                    "source": "Future Tech Report"
                }
            ])
        
        # Add a general result if no specific matches
        if not mock_results:
            mock_results.append({
                "title": f"Search Results for: {query}",
                "url": "https://example.com/search",
                "content": f"Various sources discuss {query} with emerging patterns and implications for future development.",
                "score": 0.75,
                "source": "General Search"
            })
        
        return mock_results
    
    def _extract_source(self, url: str) -> str:
        """Extract source name from URL."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Remove common prefixes
            domain = domain.replace("www.", "").replace(".com", "").replace(".org", "")
            # Capitalize
            return domain.title()
        except:
            return "Unknown Source"
    
    async def format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for agent consumption."""
        if not results:
            return "No results found for the search query."
        
        formatted = []
        formatted.append(f"Found {len(results)} relevant results:\n")
        
        for i, result in enumerate(results[:self.max_results], 1):
            formatted.append(f"{i}. {result.get('title', 'Untitled')}")
            formatted.append(f"   Source: {result.get('source', 'Unknown')}")
            if result.get('published_date'):
                formatted.append(f"   Date: {result['published_date']}")
            formatted.append(f"   Relevance: {result.get('score', 0):.1%}")
            formatted.append(f"   Summary: {result.get('content', 'No summary available')[:200]}...")
            if result.get('url'):
                formatted.append(f"   URL: {result['url']}")
            formatted.append("")
        
        return "\n".join(formatted)


class SpecializedWebSearchTool(WebSearchTool):
    """Specialized version of web search for specific domains."""
    
    def __init__(self, 
                 name: str,
                 focus_area: str,
                 include_domains: Optional[List[str]] = None,
                 exclude_domains: Optional[List[str]] = None,
                 **kwargs):
        super().__init__(name=name, **kwargs)
        self.focus_area = focus_area
        self.include_domains = include_domains or []
        self.exclude_domains = exclude_domains or []
        self.description = f"Specialized web search for {focus_area}"
    
    async def _arun(self, query: str, **kwargs) -> ToolResult:
        """Execute specialized search."""
        # Enhance query with focus area
        enhanced_query = f"{query} {self.focus_area}"
        
        # Add domain filters
        if self.include_domains:
            kwargs["include_domains"] = self.include_domains
        if self.exclude_domains:
            kwargs["exclude_domains"] = self.exclude_domains
        
        return await super()._arun(enhanced_query, **kwargs)