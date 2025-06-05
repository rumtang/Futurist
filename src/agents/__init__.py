"""Agent initialization and exports."""

from typing import Dict, Any, Optional, Callable
from loguru import logger

# Import simple agents (no CrewAI dependency)
from src.agents.simple_agent import (
    SimpleAgent, 
    AnalyticalSimpleAgent, 
    ResearchSimpleAgent,
    AgentMessage,
    AgentThought,
    AgentState
)
from src.agents.simple_ai_futurist_agent import SimpleAIFuturistAgent
from src.agents.simple_trend_scanner_agent import SimpleTrendScannerAgent
from src.agents.simple_customer_insight_agent import SimpleCustomerInsightAgent
from src.agents.simple_tech_impact_agent import SimpleTechImpactAgent
from src.agents.simple_org_transformation_agent import SimpleOrgTransformationAgent
from src.agents.simple_synthesis_agent import SimpleSynthesisAgent

# Global agent registry
_agent_registry: Dict[str, Any] = {}


async def initialize_all_agents(stream_callback: Optional[Callable] = None):
    """Initialize all simple agents and register them."""
    global _agent_registry
    
    try:
        # Initialize each agent with stream callback
        logger.info("Initializing Simple AI agents...")
        
        _agent_registry["ai_futurist"] = SimpleAIFuturistAgent(stream_callback=stream_callback)
        logger.info("Simple AI & Agentic Futurist agent initialized")
        
        _agent_registry["trend_scanner"] = SimpleTrendScannerAgent(stream_callback=stream_callback)
        logger.info("Simple Trend Scanner agent initialized")
        
        _agent_registry["customer_insight"] = SimpleCustomerInsightAgent(stream_callback=stream_callback)
        logger.info("Simple Customer Insight agent initialized")
        
        _agent_registry["tech_impact"] = SimpleTechImpactAgent(stream_callback=stream_callback)
        logger.info("Simple Tech Impact agent initialized")
        
        _agent_registry["org_transformation"] = SimpleOrgTransformationAgent(stream_callback=stream_callback)
        logger.info("Simple Org Transformation agent initialized")
        
        _agent_registry["synthesis"] = SimpleSynthesisAgent(stream_callback=stream_callback)
        logger.info("Simple Synthesis agent initialized")
        
        logger.info(f"All {len(_agent_registry)} simple agents initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize simple agents: {e}")
        raise


def get_agent(agent_id: str):
    """Get an agent by ID."""
    return _agent_registry.get(agent_id)


def get_all_agents():
    """Get all initialized agents."""
    return _agent_registry


__all__ = [
    # Simple agent base classes
    "SimpleAgent",
    "AnalyticalSimpleAgent",
    "ResearchSimpleAgent",
    "AgentMessage",
    "AgentThought", 
    "AgentState",
    
    # Simple agents
    "SimpleAIFuturistAgent",
    "SimpleTrendScannerAgent",
    "SimpleCustomerInsightAgent",
    "SimpleTechImpactAgent",
    "SimpleOrgTransformationAgent",
    "SimpleSynthesisAgent",
    
    # Agent management functions
    "initialize_all_agents",
    "get_agent",
    "get_all_agents"
]