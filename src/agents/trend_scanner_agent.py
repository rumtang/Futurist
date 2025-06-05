"""Trend Scanner Agent - Identifies weak signals and emerging patterns."""

from typing import Dict, Any, List
from loguru import logger
import asyncio

from src.agents.base_agent import ResearchAgent
from src.config.base_config import AGENT_INSTRUCTIONS
from src.websocket.socket_server import agent_stream_callback, broadcast_trend_update
from src.tools.web_search_tool import WebSearchTool, SpecializedWebSearchTool
from src.tools.trend_analysis_tool import TrendAnalysisTool, WeakSignalDetector


class TrendScannerAgent(ResearchAgent):
    """Agent specializing in scanning for weak signals and emerging trends."""
    
    def __init__(self):
        """Initialize the Trend Scanner agent."""
        # Initialize tools
        general_search = WebSearchTool(
            name="trend_search",
            description="Search for emerging trends and weak signals"
        )
        
        tech_search = SpecializedWebSearchTool(
            name="tech_trend_search",
            focus_area="emerging technology trends innovations",
            include_domains=["techcrunch.com", "wired.com", "arstechnica.com", "ieee.org"]
        )
        
        social_search = SpecializedWebSearchTool(
            name="social_trend_search",
            focus_area="social media trends consumer behavior",
            include_domains=["twitter.com", "reddit.com", "tiktok.com", "instagram.com"]
        )
        
        trend_analyzer = TrendAnalysisTool(
            name="trend_analyzer",
            description="Analyze trend strength, trajectory, and interconnections"
        )
        
        signal_detector = WeakSignalDetector(
            name="weak_signal_detector",
            description="Detect weak signals that could become major trends"
        )
        
        super().__init__(
            name="trend_scanner",
            role="Trend Scanner and Weak Signal Detector",
            goal="Identify emerging patterns and weak signals across multiple data sources",
            backstory="""You are an expert trend analyst with a keen eye for spotting weak signals 
            before they become mainstream trends. Your expertise includes:
            - Pattern recognition across diverse data sources
            - Distinguishing signal from noise
            - Understanding trend lifecycles and adoption curves
            - Cross-domain pattern matching
            - Temporal analysis of signal evolution
            
            You combine quantitative analysis with qualitative insights to identify trends 
            that others miss. You're especially skilled at finding connections between 
            seemingly unrelated signals.""",
            tools=[general_search, tech_search, social_search, trend_analyzer, signal_detector],
            verbose=True,
            stream_callback=agent_stream_callback
        )
        
        # Track scanning patterns
        self.scan_categories = [
            "technology", "consumer_behavior", "social_patterns",
            "economic_indicators", "regulatory_changes", "cultural_shifts"
        ]
        
        self.signal_threshold = 0.3  # Lower threshold for weak signals
        self.trend_threshold = 0.7   # Higher threshold for established trends
    
    def get_instructions(self) -> str:
        """Get specific instructions for this agent."""
        return AGENT_INSTRUCTIONS["trend_scanner"]
    
    async def _conduct_research(self, topic: str) -> Dict[str, Any]:
        """Conduct trend scanning and analysis."""
        await self.add_thought(f"Initiating comprehensive trend scan for: {topic}", confidence=0.9)
        
        results = {
            "topic": topic,
            "weak_signals": [],
            "emerging_trends": [],
            "established_trends": [],
            "trend_connections": [],
            "future_implications": [],
            "scan_metadata": {}
        }
        
        # Determine scan scope
        scan_scope = self._determine_scan_scope(topic)
        results["scan_metadata"]["scope"] = scan_scope
        
        # Phase 1: Broad signal detection
        await self.add_thought("Phase 1: Scanning for weak signals across domains", confidence=0.85)
        signals = await self._scan_for_signals(topic, scan_scope)
        
        # Phase 2: Signal analysis and categorization
        await self.add_thought("Phase 2: Analyzing and categorizing detected signals", confidence=0.85)
        categorized = await self._analyze_signals(signals)
        
        results["weak_signals"] = categorized["weak"]
        results["emerging_trends"] = categorized["emerging"]
        results["established_trends"] = categorized["established"]
        
        # Phase 3: Pattern matching and connections
        await self.add_thought("Phase 3: Identifying pattern connections", confidence=0.8)
        connections = await self._find_trend_connections(categorized)
        results["trend_connections"] = connections
        
        # Phase 4: Future implications
        await self.add_thought("Phase 4: Projecting future implications", confidence=0.75)
        implications = await self._project_implications(categorized, connections)
        results["future_implications"] = implications
        
        # Broadcast significant trends
        for trend in results["emerging_trends"][:3]:  # Top 3 emerging trends
            await broadcast_trend_update({
                "signal": trend["name"],
                "strength": trend["strength"],
                "trajectory": trend["trajectory"],
                "sources": trend.get("sources", [])
            })
        
        await self.add_thought(
            f"Scan complete: {len(results['weak_signals'])} weak signals, "
            f"{len(results['emerging_trends'])} emerging trends identified",
            confidence=0.9
        )
        
        return results
    
    def _determine_scan_scope(self, topic: str) -> Dict[str, Any]:
        """Determine the scope and parameters for trend scanning."""
        topic_lower = topic.lower()
        
        scope = {
            "categories": [],
            "time_horizon": "6-24 months",
            "geographic_focus": "global",
            "depth": "comprehensive"
        }
        
        # Determine relevant categories
        if "customer" in topic_lower or "cx" in topic_lower:
            scope["categories"].extend(["consumer_behavior", "technology", "social_patterns"])
        
        if "tech" in topic_lower or "digital" in topic_lower:
            scope["categories"].extend(["technology", "economic_indicators"])
        
        if "business" in topic_lower or "organization" in topic_lower:
            scope["categories"].extend(["economic_indicators", "regulatory_changes"])
        
        # Default to all categories if none specific
        if not scope["categories"]:
            scope["categories"] = self.scan_categories
        
        return scope
    
    async def _scan_for_signals(self, topic: str, scope: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan multiple sources for signals."""
        all_signals = []
        
        # Parallel scanning across different tools and queries
        scan_tasks = []
        
        # General trend search
        scan_tasks.append(self._scan_general_trends(topic))
        
        # Category-specific searches
        for category in scope["categories"]:
            scan_tasks.append(self._scan_category(category, topic))
        
        # Technology-specific search if relevant
        if "technology" in scope["categories"]:
            scan_tasks.append(self._scan_tech_trends(topic))
        
        # Social trends if relevant
        if "social_patterns" in scope["categories"] or "consumer_behavior" in scope["categories"]:
            scan_tasks.append(self._scan_social_trends(topic))
        
        # Execute all scans in parallel
        scan_results = await asyncio.gather(*scan_tasks)
        
        # Combine and deduplicate signals
        for result in scan_results:
            if result:
                all_signals.extend(result)
        
        return self._deduplicate_signals(all_signals)
    
    async def _scan_general_trends(self, topic: str) -> List[Dict[str, Any]]:
        """Scan for general trends related to topic."""
        signals = []
        
        # Use general search tool
        result = await self.tools[0]._arun(
            query=f"emerging trends weak signals {topic} 2024 future"
        )
        
        if result.success:
            # Extract signals from search results
            signals.extend(self._extract_signals_from_search(result.data))
        
        return signals
    
    async def _scan_category(self, category: str, topic: str) -> List[Dict[str, Any]]:
        """Scan specific category for signals."""
        signals = []
        
        # Construct category-specific query
        query = f"{category} trends {topic} emerging patterns 2024"
        
        result = await self.tools[0]._arun(query=query)
        
        if result.success:
            extracted = self._extract_signals_from_search(result.data)
            # Tag with category
            for signal in extracted:
                signal["category"] = category
            signals.extend(extracted)
        
        return signals
    
    async def _scan_tech_trends(self, topic: str) -> List[Dict[str, Any]]:
        """Scan technology-specific sources."""
        signals = []
        
        # Use tech-specific search tool
        result = await self.tools[1]._arun(
            query=f"breakthrough technology {topic} innovation startup"
        )
        
        if result.success:
            extracted = self._extract_signals_from_search(result.data)
            for signal in extracted:
                signal["category"] = "technology"
                signal["source_type"] = "tech_media"
            signals.extend(extracted)
        
        return signals
    
    async def _scan_social_trends(self, topic: str) -> List[Dict[str, Any]]:
        """Scan social media and consumer trends."""
        signals = []
        
        # Use social-specific search tool
        result = await self.tools[2]._arun(
            query=f"viral trend consumer behavior {topic} social media"
        )
        
        if result.success:
            extracted = self._extract_signals_from_search(result.data)
            for signal in extracted:
                signal["category"] = "social_patterns"
                signal["source_type"] = "social_media"
            signals.extend(extracted)
        
        return signals
    
    def _extract_signals_from_search(self, search_data: str) -> List[Dict[str, Any]]:
        """Extract potential signals from search results."""
        signals = []
        
        # Simple extraction logic (would be more sophisticated in production)
        lines = search_data.split('\n')
        current_signal = None
        
        for line in lines:
            if line.strip().startswith(tuple(str(i) + '.' for i in range(1, 10))):
                # New result item
                if current_signal:
                    signals.append(current_signal)
                
                current_signal = {
                    "title": line.split('.', 1)[1].strip() if '.' in line else line,
                    "raw_strength": 0.5,  # Default strength
                    "sources": [],
                    "mentions": 1,
                    "first_seen": "2024-01"
                }
            
            elif current_signal and "Source:" in line:
                source = line.split("Source:", 1)[1].strip()
                current_signal["sources"].append(source)
            
            elif current_signal and "Relevance:" in line:
                try:
                    relevance = float(line.split("Relevance:", 1)[1].strip().rstrip('%')) / 100
                    current_signal["raw_strength"] = relevance
                except:
                    pass
        
        if current_signal:
            signals.append(current_signal)
        
        return signals
    
    def _deduplicate_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate signals based on similarity."""
        unique_signals = []
        seen_titles = set()
        
        for signal in signals:
            # Simple deduplication by title similarity
            title_lower = signal.get("title", "").lower()
            if title_lower and title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_signals.append(signal)
            elif title_lower in seen_titles:
                # Merge sources if duplicate
                for existing in unique_signals:
                    if existing.get("title", "").lower() == title_lower:
                        existing["sources"].extend(signal.get("sources", []))
                        existing["mentions"] += 1
                        existing["raw_strength"] = max(
                            existing["raw_strength"],
                            signal.get("raw_strength", 0)
                        )
        
        return unique_signals
    
    async def _analyze_signals(self, signals: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze and categorize signals by strength."""
        categorized = {
            "weak": [],
            "emerging": [],
            "established": []
        }
        
        # Use trend analyzer tool
        if len(self.tools) > 3:  # trend_analyzer is 4th tool
            result = await self.tools[3]._arun(signals=signals)
            
            if result.success:
                analyzed = result.data
                
                for signal in analyzed.get("analyzed_signals", []):
                    strength = signal.get("strength", 0)
                    
                    # Categorize by strength
                    if strength < self.signal_threshold:
                        continue  # Too weak to track
                    elif strength < self.trend_threshold:
                        categorized["weak"].append(signal)
                    elif strength < 0.85:
                        categorized["emerging"].append(signal)
                    else:
                        categorized["established"].append(signal)
        
        # Sort by strength within each category
        for category in categorized:
            categorized[category].sort(key=lambda x: x.get("strength", 0), reverse=True)
        
        return categorized
    
    async def _find_trend_connections(self, categorized: Dict[str, List]) -> List[Dict[str, Any]]:
        """Find connections between trends."""
        connections = []
        
        all_trends = (
            categorized.get("weak", []) + 
            categorized.get("emerging", []) + 
            categorized.get("established", [])
        )
        
        # Look for connections (simplified)
        for i, trend1 in enumerate(all_trends):
            for trend2 in all_trends[i+1:]:
                # Check for category overlap
                cat1 = trend1.get("category", "")
                cat2 = trend2.get("category", "")
                
                if cat1 and cat2 and cat1 != cat2:
                    connections.append({
                        "trend1": trend1.get("name", trend1.get("title", "")),
                        "trend2": trend2.get("name", trend2.get("title", "")),
                        "connection_type": "cross_domain",
                        "strength": min(trend1.get("strength", 0), trend2.get("strength", 0)),
                        "implication": f"{cat1} meets {cat2}"
                    })
        
        return connections[:10]  # Top 10 connections
    
    async def _project_implications(self, categorized: Dict[str, List], 
                                  connections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Project future implications of detected trends."""
        implications = []
        
        # Implications from emerging trends
        for trend in categorized.get("emerging", [])[:5]:  # Top 5
            implications.append({
                "trend": trend.get("name", trend.get("title", "")),
                "timeframe": "6-12 months",
                "impact_level": "medium" if trend.get("strength", 0) < 0.8 else "high",
                "affected_areas": [trend.get("category", "general")],
                "description": f"Expected mainstream adoption of {trend.get('name', 'trend')}"
            })
        
        # Implications from connections
        for connection in connections[:3]:  # Top 3
            implications.append({
                "trend": f"{connection['trend1']} + {connection['trend2']}",
                "timeframe": "12-24 months",
                "impact_level": "transformative",
                "affected_areas": ["cross_functional"],
                "description": f"Convergence creating new opportunities in {connection['implication']}"
            })
        
        return implications