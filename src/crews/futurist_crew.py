"""CrewAI orchestration for CX Futurist multi-agent system."""

from typing import Dict, Any, List, Optional
from crewai import Crew, Task, Process
from loguru import logger
import asyncio

from src.agents import get_all_agents, get_agent
from src.websocket.socket_server import agent_stream_callback
from src.tools.vector_tools import store_insight, store_trend


class CXFuturistCrew:
    """Orchestrates the CX Futurist multi-agent crew."""
    
    def __init__(self):
        """Initialize the crew."""
        self.agents = get_all_agents()
        self.crew = None
        self.process_type = Process.sequential  # Can be changed to hierarchical
        
    def create_crew(self, topic: str, analysis_type: str = "comprehensive") -> Crew:
        """Create a crew for specific analysis."""
        # Select agents based on analysis type
        selected_agents = self._select_agents(topic, analysis_type)
        
        # Create tasks for each agent
        tasks = self._create_tasks(topic, selected_agents, analysis_type)
        
        # Create crew
        self.crew = Crew(
            agents=[agent.agent for agent in selected_agents.values()],
            tasks=tasks,
            process=self.process_type,
            verbose=True,
            memory=True,
            embedder={
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            },
            full_output=True
        )
        
        return self.crew
    
    def _select_agents(self, topic: str, analysis_type: str) -> Dict[str, Any]:
        """Select appropriate agents for the analysis."""
        # Always include core agents
        selected = {
            "ai_futurist": self.agents["ai_futurist"],
            "trend_scanner": self.agents["trend_scanner"],
            "synthesis": self.agents["synthesis"]
        }
        
        # Add specialized agents based on topic
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ["customer", "cx", "experience", "user"]):
            selected["customer_insight"] = self.agents["customer_insight"]
        
        if any(word in topic_lower for word in ["tech", "technology", "digital", "ai"]):
            selected["tech_impact"] = self.agents["tech_impact"]
        
        if any(word in topic_lower for word in ["business", "organization", "company"]):
            selected["org_transformation"] = self.agents["org_transformation"]
        
        # For comprehensive analysis, include all agents
        if analysis_type == "comprehensive" and len(selected) < 5:
            for agent_id, agent in self.agents.items():
                if agent_id not in selected:
                    selected[agent_id] = agent
        
        logger.info(f"Selected {len(selected)} agents for analysis: {list(selected.keys())}")
        return selected
    
    def _create_tasks(self, topic: str, agents: Dict[str, Any], analysis_type: str) -> List[Task]:
        """Create tasks for the selected agents."""
        tasks = []
        
        # 1. AI & Agentic Futurist Task (if selected)
        if "ai_futurist" in agents:
            tasks.append(Task(
                description=f"""Analyze the AI and autonomous agent implications for: {topic}
                
                Focus on:
                - Current AI capabilities relevant to this topic
                - Emerging agent frameworks and their potential
                - Human-AI collaboration patterns
                - Governance and trust implications
                - Timeline predictions with confidence levels
                
                Provide specific examples and cite sources where possible.""",
                expected_output="Detailed analysis of AI/agent evolution related to the topic",
                agent=agents["ai_futurist"].agent,
                async_execution=True
            ))
        
        # 2. Trend Scanner Task (if selected)
        if "trend_scanner" in agents:
            tasks.append(Task(
                description=f"""Scan for weak signals and emerging trends related to: {topic}
                
                Focus on:
                - Weak signals that could become major trends
                - Cross-domain pattern matching
                - Signal strength and trajectory analysis
                - Trend interconnections
                - Future implications
                
                Categorize findings by strength and timeframe.""",
                expected_output="Comprehensive trend analysis with weak signals identified",
                agent=agents["trend_scanner"].agent,
                async_execution=True
            ))
        
        # 3. Customer Insight Task (if selected)
        if "customer_insight" in agents:
            tasks.append(Task(
                description=f"""Analyze customer behavior evolution for: {topic}
                
                Focus on:
                - Changing customer expectations
                - Generational differences
                - Behavioral shifts and drivers
                - Journey evolution
                - Future customer needs
                
                Provide actionable insights for organizations.""",
                expected_output="Deep customer behavior analysis with future predictions",
                agent=agents["customer_insight"].agent,
                async_execution=True
            ))
        
        # 4. Tech Impact Task (if selected)
        if "tech_impact" in agents:
            tasks.append(Task(
                description=f"""Evaluate technology impact on: {topic}
                
                Focus on:
                - Emerging technologies and maturity
                - Adoption barriers and accelerators
                - Integration requirements
                - Transformation timeline
                - Risk factors
                
                Assess both opportunities and challenges.""",
                expected_output="Technology impact assessment with adoption roadmap",
                agent=agents["tech_impact"].agent,
                async_execution=True
            ))
        
        # 5. Org Transformation Task (if selected)
        if "org_transformation" in agents:
            tasks.append(Task(
                description=f"""Analyze organizational transformation needs for: {topic}
                
                Focus on:
                - Capability gaps
                - Cultural changes required
                - New roles and skills
                - Transformation roadmap
                - Success factors
                
                Provide practical transformation guidance.""",
                expected_output="Organizational transformation blueprint",
                agent=agents["org_transformation"].agent,
                async_execution=True
            ))
        
        # 6. Synthesis Task (always last)
        if "synthesis" in agents:
            # Wait for all previous tasks
            context_agents = [a for a in agents.keys() if a != "synthesis"]
            
            tasks.append(Task(
                description=f"""Synthesize all agent insights on: {topic}
                
                Create:
                - Coherent future scenarios (optimistic, pessimistic, most likely)
                - Key decision points and milestones
                - Strategic recommendations
                - Risk mitigation strategies
                - Executive summary
                
                Ensure scenarios are plausible and actionable.""",
                expected_output="Comprehensive synthesis with future scenarios and recommendations",
                agent=agents["synthesis"].agent,
                context=context_agents,  # Reference other agents
                async_execution=False  # Run after others complete
            ))
        
        return tasks
    
    async def run_analysis(self, topic: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the crew analysis."""
        try:
            options = options or {}
            analysis_type = options.get("depth", "comprehensive")
            
            # Create crew
            crew = self.create_crew(topic, analysis_type)
            
            # Notify start
            await agent_stream_callback({
                "agent": "coordinator",
                "type": "state_update",
                "state": {"status": "starting", "current_task": "crew_initialization"}
            })
            
            # Run crew (synchronous but agents can work async)
            logger.info(f"Starting crew analysis for: {topic}")
            result = crew.kickoff()
            
            # Process results
            processed_results = await self._process_results(result, topic)
            
            # Store insights and trends
            await self._store_results(processed_results)
            
            logger.info("Crew analysis completed successfully")
            return processed_results
            
        except Exception as e:
            logger.error(f"Crew analysis error: {e}")
            raise
    
    async def _process_results(self, crew_output: Any, topic: str) -> Dict[str, Any]:
        """Process crew output into structured results."""
        results = {
            "topic": topic,
            "agent_outputs": {},
            "insights": [],
            "trends": [],
            "scenarios": [],
            "recommendations": [],
            "executive_summary": ""
        }
        
        # Extract individual agent outputs
        if hasattr(crew_output, 'tasks_output'):
            for i, task_output in enumerate(crew_output.tasks_output):
                agent_name = self._get_agent_name_from_task(i)
                if agent_name:
                    results["agent_outputs"][agent_name] = {
                        "output": task_output.raw,
                        "summary": task_output.summary if hasattr(task_output, 'summary') else None
                    }
        
        # Extract insights
        results["insights"] = self._extract_insights(results["agent_outputs"])
        
        # Extract trends
        results["trends"] = self._extract_trends(results["agent_outputs"])
        
        # Extract scenarios and recommendations from synthesis
        if "synthesis" in results["agent_outputs"]:
            synthesis_output = results["agent_outputs"]["synthesis"]["output"]
            results["scenarios"] = self._extract_scenarios(synthesis_output)
            results["recommendations"] = self._extract_recommendations(synthesis_output)
            results["executive_summary"] = self._create_executive_summary(synthesis_output)
        
        return results
    
    def _get_agent_name_from_task(self, task_index: int) -> Optional[str]:
        """Map task index to agent name."""
        # This is a simplified mapping - in production, track this properly
        task_agent_map = [
            "ai_futurist", "trend_scanner", "customer_insight",
            "tech_impact", "org_transformation", "synthesis"
        ]
        
        if task_index < len(task_agent_map):
            return task_agent_map[task_index]
        return None
    
    def _extract_insights(self, agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key insights from agent outputs."""
        insights = []
        
        for agent_name, output in agent_outputs.items():
            # Simple extraction - would use NLP in production
            content = str(output.get("output", ""))
            
            # Look for insight patterns
            if "insight" in content.lower() or "finding" in content.lower():
                insights.append({
                    "agent": agent_name,
                    "content": f"Key insight from {agent_name}",  # Simplified
                    "confidence": 0.8,
                    "category": "analysis"
                })
        
        return insights
    
    def _extract_trends(self, agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract trends from agent outputs."""
        trends = []
        
        # Focus on trend scanner output
        if "trend_scanner" in agent_outputs:
            # Simplified extraction
            trends.extend([
                {
                    "name": "Emerging Trend 1",
                    "strength": 0.7,
                    "trajectory": "rising",
                    "category": "technology"
                },
                {
                    "name": "Emerging Trend 2",
                    "strength": 0.6,
                    "trajectory": "stable",
                    "category": "behavior"
                }
            ])
        
        return trends
    
    def _extract_scenarios(self, synthesis_output: str) -> List[Dict[str, Any]]:
        """Extract scenarios from synthesis output."""
        # Simplified extraction
        return [
            {
                "type": "optimistic",
                "title": "Best Case Scenario",
                "description": "Rapid adoption with positive outcomes",
                "probability": 0.3,
                "timeline": "2-3 years"
            },
            {
                "type": "realistic",
                "title": "Most Likely Scenario",
                "description": "Gradual adoption with mixed results",
                "probability": 0.5,
                "timeline": "3-5 years"
            },
            {
                "type": "pessimistic",
                "title": "Worst Case Scenario",
                "description": "Slow adoption with challenges",
                "probability": 0.2,
                "timeline": "5+ years"
            }
        ]
    
    def _extract_recommendations(self, synthesis_output: str) -> List[Dict[str, Any]]:
        """Extract recommendations from synthesis output."""
        # Simplified extraction
        return [
            {
                "recommendation": "Invest in AI capabilities",
                "priority": "high",
                "timeline": "immediate",
                "rationale": "Critical for competitive advantage"
            },
            {
                "recommendation": "Develop talent strategy",
                "priority": "high",
                "timeline": "3-6 months",
                "rationale": "Skills gap must be addressed"
            }
        ]
    
    def _create_executive_summary(self, synthesis_output: str) -> str:
        """Create executive summary from synthesis."""
        # Simplified - would use summarization in production
        return "Analysis reveals significant opportunities in AI-driven customer experience transformation."
    
    async def _store_results(self, results: Dict[str, Any]):
        """Store insights and trends in vector database."""
        # Store insights
        for insight in results["insights"]:
            await store_insight(insight)
        
        # Store trends
        for trend in results["trends"]:
            await store_trend(trend)
        
        logger.info(f"Stored {len(results['insights'])} insights and {len(results['trends'])} trends")


# Global crew instance
cx_futurist_crew = CXFuturistCrew()


async def run_futurist_analysis(topic: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run a complete futurist analysis."""
    return await cx_futurist_crew.run_analysis(topic, options)