"""Test script for the simple orchestrator."""

import asyncio
import sys
from loguru import logger

# Add the src directory to the path
sys.path.append('/Users/jonatkin/Documents/Agentic/cx-futurist-ai')

from src.orchestrator.simple_orchestrator import SimpleOrchestrator
from src.websocket.socket_server import agent_stream_callback


async def test_orchestrator():
    """Test the simple orchestrator functionality."""
    
    # Initialize orchestrator
    logger.info("Initializing SimpleOrchestrator...")
    orchestrator = SimpleOrchestrator(stream_callback=agent_stream_callback)
    
    # Test 1: Get agent states
    logger.info("\n=== Test 1: Getting agent states ===")
    states = await orchestrator.get_agent_states()
    for agent_name, state in states.items():
        logger.info(f"{agent_name}: {state['status']}")
    
    # Test 2: Run a simple trend analysis
    logger.info("\n=== Test 2: Running trend analysis ===")
    try:
        result = await orchestrator.analyze_trend(
            topic="AI agents in customer service",
            depth="focused"
        )
        
        logger.info(f"Workflow ID: {result.workflow_id}")
        logger.info(f"Status: {result.status.value}")
        logger.info(f"Duration: {result.duration:.2f} seconds")
        logger.info(f"Key insights: {len(result.results.get('key_insights', []))}")
        
        # Print summary
        if result.results.get('summary'):
            logger.info(f"\nSummary:\n{result.results['summary']}")
            
    except Exception as e:
        logger.error(f"Trend analysis failed: {e}")
    
    # Test 3: List active workflows
    logger.info("\n=== Test 3: Listing active workflows ===")
    workflows = await orchestrator.list_active_workflows()
    for workflow in workflows:
        logger.info(f"Workflow {workflow['workflow_id']}: {workflow['status']}")
    
    # Test 4: Test scenario creation
    logger.info("\n=== Test 4: Creating future scenario ===")
    try:
        result = await orchestrator.create_scenario(
            domain="retail",
            timeframe="3_years",
            uncertainties=["AI adoption rate", "consumer privacy concerns"]
        )
        
        logger.info(f"Workflow ID: {result.workflow_id}")
        logger.info(f"Status: {result.status.value}")
        logger.info(f"Scenarios created: {len(result.results.get('scenarios', []))}")
        
    except Exception as e:
        logger.error(f"Scenario creation failed: {e}")
    
    # Test 5: Reset agents
    logger.info("\n=== Test 5: Resetting all agents ===")
    await orchestrator.reset_all_agents()
    logger.info("All agents reset successfully")


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    
    # Run tests
    asyncio.run(test_orchestrator())