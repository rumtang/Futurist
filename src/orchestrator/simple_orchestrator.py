"""Simple orchestrator for coordinating all 6 agents without CrewAI."""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

from src.agents.simple_ai_futurist_agent import SimpleAIFuturistAgent
from src.agents.simple_trend_scanner_agent import SimpleTrendScannerAgent
from src.agents.simple_customer_insight_agent import SimpleCustomerInsightAgent
from src.agents.simple_tech_impact_agent import SimpleTechImpactAgent
from src.agents.simple_org_transformation_agent import SimpleOrgTransformationAgent
from src.agents.simple_synthesis_agent import SimpleSynthesisAgent
from src.websocket.socket_server import agent_stream_callback, broadcast_knowledge_update, broadcast_trend_update, broadcast_scenario_update


class WorkflowStatus(Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""
    workflow_id: str
    workflow_type: str
    status: WorkflowStatus
    start_time: float
    end_time: Optional[float] = None
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    agent_outputs: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate workflow duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "results": self.results,
            "errors": self.errors,
            "agent_outputs": self.agent_outputs
        }


class SimpleOrchestrator:
    """Orchestrates multi-agent workflows without CrewAI."""
    
    def __init__(self, stream_callback: Optional[Callable] = None):
        """Initialize the orchestrator with all 6 agents."""
        self.stream_callback = stream_callback or agent_stream_callback
        
        # Initialize all agents with streaming callbacks
        logger.info("Initializing SimpleOrchestrator with all 6 agents...")
        
        self.ai_futurist = SimpleAIFuturistAgent(stream_callback=self.stream_callback)
        self.trend_scanner = SimpleTrendScannerAgent(stream_callback=self.stream_callback)
        self.customer_insight = SimpleCustomerInsightAgent(stream_callback=self.stream_callback)
        self.tech_impact = SimpleTechImpactAgent(stream_callback=self.stream_callback)
        self.org_transformation = SimpleOrgTransformationAgent(stream_callback=self.stream_callback)
        self.synthesis = SimpleSynthesisAgent(stream_callback=self.stream_callback)
        
        # Agent registry for easy access
        self.agents = {
            "ai_futurist": self.ai_futurist,
            "trend_scanner": self.trend_scanner,
            "customer_insight": self.customer_insight,
            "tech_impact": self.tech_impact,
            "org_transformation": self.org_transformation,
            "synthesis": self.synthesis
        }
        
        # Active workflows
        self.active_workflows: Dict[str, WorkflowResult] = {}
        
        logger.info("SimpleOrchestrator initialized successfully")
    
    async def _broadcast_workflow_update(self, workflow_id: str, status: str, data: Any = None):
        """Broadcast workflow status updates."""
        try:
            await self.stream_callback({
                "type": "workflow_update",
                "workflow_id": workflow_id,
                "status": status,
                "data": data,
                "timestamp": time.time()
            })
        except Exception as e:
            logger.warning(f"Failed to broadcast workflow update: {e}")
    
    async def analyze_trend(self, topic: str, depth: str = "comprehensive") -> WorkflowResult:
        """
        Analyze an emerging trend with multiple agents.
        
        Workflow:
        1. Trend Scanner identifies weak signals
        2. AI Futurist analyzes AI/agent implications
        3. Customer Insight examines behavior changes
        4. Tech Impact evaluates technology implications
        5. Org Transformation predicts organizational changes
        6. Synthesis creates coherent report
        """
        workflow_id = f"trend_analysis_{int(time.time())}"
        result = WorkflowResult(
            workflow_id=workflow_id,
            workflow_type="trend_analysis",
            status=WorkflowStatus.RUNNING,
            start_time=time.time()
        )
        
        self.active_workflows[workflow_id] = result
        
        try:
            await self._broadcast_workflow_update(workflow_id, "started", {"topic": topic, "depth": depth})
            
            # Phase 1: Trend Scanning
            logger.info(f"[{workflow_id}] Phase 1: Scanning for weak signals...")
            # Convert topic to domains and depth to timeframe
            domains = [topic]  # Simple conversion
            timeframe = "last_month" if depth == "quick" else "last_quarter"
            weak_signals = await self.trend_scanner.scan_for_signals(domains, timeframe=timeframe)
            result.agent_outputs["trend_scanner"] = weak_signals
            
            # Broadcast trend updates
            # The signals are in a dictionary format with domain as key and string response as value
            for domain, signal_response in weak_signals.get("signals", {}).items():
                await broadcast_trend_update({
                    "domain": domain,
                    "signal": signal_response[:200] if isinstance(signal_response, str) else str(signal_response)[:200],
                    "strength": 0.7,  # Default strength
                    "trajectory": "emerging"
                })
            
            # Phase 2: Parallel Analysis
            logger.info(f"[{workflow_id}] Phase 2: Parallel multi-agent analysis...")
            
            # Prepare context for all agents
            context = {
                "topic": topic,
                "weak_signals": weak_signals,
                "analysis_depth": depth
            }
            
            # Run analyses in parallel
            # Using the actual methods that exist in the agents
            analysis_tasks = [
                self.ai_futurist.analyze_ai_implications(topic, context),
                self.customer_insight.analyze_behavior_shift({"topic": topic, "signals": weak_signals}),
                self.tech_impact.evaluate_technology({"name": topic, "context": weak_signals}),
                self.org_transformation.assess_transformation_readiness({"topic": topic, "context": context})
            ]
            
            # Enable agent collaboration
            for agent_name in ["ai_futurist", "customer_insight", "tech_impact", "org_transformation"]:
                await self.agents[agent_name].collaborate_with("trend_scanner", "Receiving weak signals", weak_signals)
            
            # Execute parallel analyses
            ai_analysis, customer_analysis, tech_analysis, org_analysis = await asyncio.gather(*analysis_tasks)
            
            result.agent_outputs.update({
                "ai_futurist": ai_analysis,
                "customer_insight": customer_analysis,
                "tech_impact": tech_analysis,
                "org_transformation": org_analysis
            })
            
            # Phase 3: Synthesis
            logger.info(f"[{workflow_id}] Phase 3: Synthesizing insights...")
            
            # Prepare all insights for synthesis
            all_insights = {
                "weak_signals": weak_signals,
                "ai_implications": ai_analysis,
                "customer_evolution": customer_analysis,
                "tech_impact": tech_analysis,
                "org_transformations": org_analysis
            }
            
            # Enable synthesis collaboration
            await self.synthesis.collaborate_with("all_agents", "Gathering insights from all agents", all_insights)
            
            # Create synthesis
            synthesis_result = await self.synthesis.create_synthesis(topic, all_insights)
            result.agent_outputs["synthesis"] = synthesis_result
            
            # Update knowledge graph
            await broadcast_knowledge_update({
                "type": "synthesis_completed",
                "topic": topic,
                "insights_count": len(synthesis_result.get("key_insights", [])),
                "connections_made": synthesis_result.get("cross_domain_connections", [])
            })
            
            # Finalize result
            result.status = WorkflowStatus.COMPLETED
            result.end_time = time.time()
            result.results = {
                "summary": synthesis_result.get("executive_summary"),
                "key_insights": synthesis_result.get("key_insights"),
                "recommendations": synthesis_result.get("strategic_recommendations"),
                "confidence": synthesis_result.get("overall_confidence", 0.7)
            }
            
            await self._broadcast_workflow_update(workflow_id, "completed", result.results)
            
        except Exception as e:
            logger.error(f"Error in trend analysis workflow: {e}")
            result.status = WorkflowStatus.FAILED
            result.end_time = time.time()
            result.errors.append(str(e))
            await self._broadcast_workflow_update(workflow_id, "failed", {"error": str(e)})
            raise
        
        return result
    
    async def create_scenario(self, domain: str, timeframe: str = "5_years", uncertainties: List[str] = None) -> WorkflowResult:
        """
        Create future scenarios for a domain.
        
        Workflow:
        1. AI Futurist identifies key AI/agent drivers
        2. Tech Impact maps technology trajectories
        3. Customer Insight predicts behavior shifts
        4. Org Transformation models organizational evolution
        5. Synthesis creates multiple scenarios
        """
        workflow_id = f"scenario_creation_{int(time.time())}"
        result = WorkflowResult(
            workflow_id=workflow_id,
            workflow_type="scenario_creation",
            status=WorkflowStatus.RUNNING,
            start_time=time.time()
        )
        
        self.active_workflows[workflow_id] = result
        uncertainties = uncertainties or []
        
        try:
            await self._broadcast_workflow_update(workflow_id, "started", {
                "domain": domain,
                "timeframe": timeframe,
                "uncertainties": uncertainties
            })
            
            # Phase 1: Identify key drivers
            logger.info(f"[{workflow_id}] Phase 1: Identifying key drivers...")
            
            driver_tasks = [
                self.ai_futurist.identify_ai_drivers(domain, timeframe),
                self.tech_impact.evaluate_technology({"name": f"{domain} technologies", "timeframe": timeframe}),
                self.customer_insight.predict_expectation_evolution(timeframe, domain),
                self.org_transformation.design_future_organization(domain, timeframe)
            ]
            
            ai_drivers, tech_trajectories, behavior_shifts, org_evolution = await asyncio.gather(*driver_tasks)
            
            result.agent_outputs.update({
                "ai_drivers": ai_drivers,
                "tech_trajectories": tech_trajectories,
                "behavior_shifts": behavior_shifts,
                "org_evolution": org_evolution
            })
            
            # Phase 2: Create scenarios
            logger.info(f"[{workflow_id}] Phase 2: Creating scenarios...")
            
            scenario_inputs = {
                "domain": domain,
                "timeframe": timeframe,
                "uncertainties": uncertainties,
                "ai_drivers": ai_drivers,
                "tech_trajectories": tech_trajectories,
                "behavior_shifts": behavior_shifts,
                "org_evolution": org_evolution
            }
            
            scenarios = await self.synthesis.create_scenarios(scenario_inputs)
            result.agent_outputs["scenarios"] = scenarios
            
            # Broadcast scenario updates
            for scenario in scenarios.get("scenarios", []):
                await broadcast_scenario_update({
                    "id": scenario.get("id"),
                    "name": scenario.get("name"),
                    "probability": scenario.get("probability", 0.5),
                    "branch": scenario.get("branch_point")
                })
            
            # Finalize result
            result.status = WorkflowStatus.COMPLETED
            result.end_time = time.time()
            result.results = scenarios
            
            await self._broadcast_workflow_update(workflow_id, "completed", result.results)
            
        except Exception as e:
            logger.error(f"Error in scenario creation workflow: {e}")
            result.status = WorkflowStatus.FAILED
            result.end_time = time.time()
            result.errors.append(str(e))
            await self._broadcast_workflow_update(workflow_id, "failed", {"error": str(e)})
            raise
        
        return result
    
    async def assess_ai_economy(self, industry: str, focus_areas: List[str] = None) -> WorkflowResult:
        """
        Assess the emerging AI/agent economy for an industry.
        
        Workflow:
        1. AI Futurist analyzes agent capability evolution
        2. Trend Scanner identifies adoption patterns
        3. Org Transformation models business impact
        4. Synthesis creates strategic recommendations
        """
        workflow_id = f"ai_economy_assessment_{int(time.time())}"
        result = WorkflowResult(
            workflow_id=workflow_id,
            workflow_type="ai_economy_assessment",
            status=WorkflowStatus.RUNNING,
            start_time=time.time()
        )
        
        self.active_workflows[workflow_id] = result
        focus_areas = focus_areas or ["automation", "human_agent_collaboration", "new_business_models"]
        
        try:
            await self._broadcast_workflow_update(workflow_id, "started", {
                "industry": industry,
                "focus_areas": focus_areas
            })
            
            # Phase 1: Agent capability analysis
            logger.info(f"[{workflow_id}] Phase 1: Analyzing agent capabilities...")
            agent_capabilities = await self.ai_futurist.analyze_agent_capabilities(industry)
            result.agent_outputs["agent_capabilities"] = agent_capabilities
            
            # Phase 2: Adoption pattern scanning
            logger.info(f"[{workflow_id}] Phase 2: Scanning adoption patterns...")
            adoption_patterns = await self.trend_scanner.scan_adoption_patterns(
                f"AI agents in {industry}",
                focus_areas=focus_areas
            )
            result.agent_outputs["adoption_patterns"] = adoption_patterns
            
            # Phase 3: Business impact modeling
            logger.info(f"[{workflow_id}] Phase 3: Modeling business impact...")
            
            impact_context = {
                "industry": industry,
                "agent_capabilities": agent_capabilities,
                "adoption_patterns": adoption_patterns
            }
            
            business_impact = await self.org_transformation.model_business_impact(
                "AI agent adoption",
                impact_context
            )
            result.agent_outputs["business_impact"] = business_impact
            
            # Phase 4: Strategic synthesis
            logger.info(f"[{workflow_id}] Phase 4: Creating strategic recommendations...")
            
            synthesis_inputs = {
                "industry": industry,
                "focus_areas": focus_areas,
                "agent_capabilities": agent_capabilities,
                "adoption_patterns": adoption_patterns,
                "business_impact": business_impact
            }
            
            strategic_recommendations = await self.synthesis.create_strategic_recommendations(
                f"AI economy in {industry}",
                synthesis_inputs
            )
            result.agent_outputs["strategic_recommendations"] = strategic_recommendations
            
            # Finalize result
            result.status = WorkflowStatus.COMPLETED
            result.end_time = time.time()
            result.results = {
                "executive_summary": strategic_recommendations.get("executive_summary"),
                "key_opportunities": strategic_recommendations.get("opportunities"),
                "risks": strategic_recommendations.get("risks"),
                "roadmap": strategic_recommendations.get("implementation_roadmap"),
                "timeline": strategic_recommendations.get("timeline")
            }
            
            await self._broadcast_workflow_update(workflow_id, "completed", result.results)
            
        except Exception as e:
            logger.error(f"Error in AI economy assessment workflow: {e}")
            result.status = WorkflowStatus.FAILED
            result.end_time = time.time()
            result.errors.append(str(e))
            await self._broadcast_workflow_update(workflow_id, "failed", {"error": str(e)})
            raise
        
        return result
    
    async def knowledge_synthesis(self, domains: List[str], objective: str) -> WorkflowResult:
        """
        Synthesize knowledge across multiple domains.
        
        Workflow:
        1. Trend Scanner identifies patterns across domains
        2. All specialized agents analyze their perspectives
        3. Synthesis creates cross-domain insights
        """
        workflow_id = f"knowledge_synthesis_{int(time.time())}"
        result = WorkflowResult(
            workflow_id=workflow_id,
            workflow_type="knowledge_synthesis",
            status=WorkflowStatus.RUNNING,
            start_time=time.time()
        )
        
        self.active_workflows[workflow_id] = result
        
        try:
            await self._broadcast_workflow_update(workflow_id, "started", {
                "domains": domains,
                "objective": objective
            })
            
            # Phase 1: Cross-domain pattern recognition
            logger.info(f"[{workflow_id}] Phase 1: Identifying cross-domain patterns...")
            
            pattern_tasks = []
            for domain in domains:
                pattern_tasks.append(self.trend_scanner.scan_for_signals([domain], timeframe="last_quarter"))
            
            domain_patterns = await asyncio.gather(*pattern_tasks)
            
            patterns_by_domain = {
                domains[i]: patterns for i, patterns in enumerate(domain_patterns)
            }
            result.agent_outputs["domain_patterns"] = patterns_by_domain
            
            # Phase 2: Multi-perspective analysis
            logger.info(f"[{workflow_id}] Phase 2: Multi-perspective analysis...")
            
            analysis_context = {
                "domains": domains,
                "objective": objective,
                "patterns": patterns_by_domain
            }
            
            perspective_tasks = [
                self.ai_futurist.analyze_cross_domain_ai_trends(domains, analysis_context),
                self.customer_insight.analyze_cross_domain_behaviors(domains, patterns_by_domain),
                self.tech_impact.assess_convergence_opportunities(domains, patterns_by_domain),
                self.org_transformation.identify_cross_industry_transformations(domains, analysis_context)
            ]
            
            ai_trends, behavior_patterns, tech_convergence, industry_transforms = await asyncio.gather(*perspective_tasks)
            
            result.agent_outputs.update({
                "ai_trends": ai_trends,
                "behavior_patterns": behavior_patterns,
                "tech_convergence": tech_convergence,
                "industry_transforms": industry_transforms
            })
            
            # Phase 3: Knowledge synthesis
            logger.info(f"[{workflow_id}] Phase 3: Synthesizing knowledge...")
            
            synthesis_inputs = {
                "objective": objective,
                "domains": domains,
                "patterns": patterns_by_domain,
                "ai_trends": ai_trends,
                "behavior_patterns": behavior_patterns,
                "tech_convergence": tech_convergence,
                "industry_transforms": industry_transforms
            }
            
            knowledge_synthesis = await self.synthesis.create_knowledge_synthesis(synthesis_inputs)
            result.agent_outputs["synthesis"] = knowledge_synthesis
            
            # Update knowledge graph with connections
            await broadcast_knowledge_update({
                "type": "cross_domain_synthesis",
                "domains": domains,
                "connections_discovered": knowledge_synthesis.get("novel_connections", []),
                "insights_generated": len(knowledge_synthesis.get("key_insights", []))
            })
            
            # Finalize result
            result.status = WorkflowStatus.COMPLETED
            result.end_time = time.time()
            result.results = knowledge_synthesis
            
            await self._broadcast_workflow_update(workflow_id, "completed", result.results)
            
        except Exception as e:
            logger.error(f"Error in knowledge synthesis workflow: {e}")
            result.status = WorkflowStatus.FAILED
            result.end_time = time.time()
            result.errors.append(str(e))
            await self._broadcast_workflow_update(workflow_id, "failed", {"error": str(e)})
            raise
        
        return result
    
    async def get_agent_states(self) -> Dict[str, Any]:
        """Get the current state of all agents."""
        states = {}
        for name, agent in self.agents.items():
            states[name] = {
                "status": agent.state.status,
                "current_task": agent.state.current_task,
                "thought_count": len(agent.state.thoughts),
                "message_count": len(agent.state.messages),
                "last_thought": agent.state.thoughts[-1].content if agent.state.thoughts else None
            }
        return states
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific workflow."""
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id].to_dict()
        return None
    
    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows."""
        return [workflow.to_dict() for workflow in self.active_workflows.values()]
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow."""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            if workflow.status == WorkflowStatus.RUNNING:
                workflow.status = WorkflowStatus.CANCELLED
                workflow.end_time = time.time()
                await self._broadcast_workflow_update(workflow_id, "cancelled")
                return True
        return False
    
    async def reset_all_agents(self):
        """Reset all agents to their initial state."""
        logger.info("Resetting all agents...")
        reset_tasks = [agent.reset_conversation() for agent in self.agents.values()]
        await asyncio.gather(*reset_tasks)
        logger.info("All agents reset successfully")