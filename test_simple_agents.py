"""Test script for simple agents without CrewAI."""

import asyncio
import json
from typing import Dict, Any
from loguru import logger

from src.agents import (
    SimpleAIFuturistAgent,
    SimpleTrendScannerAgent,
    SimpleCustomerInsightAgent,
    SimpleTechImpactAgent,
    SimpleOrgTransformationAgent,
    SimpleSynthesisAgent,
    initialize_all_agents,
    get_all_agents
)


# Stream callback for real-time updates
async def stream_callback(data: Dict[str, Any]):
    """Handle streaming updates from agents."""
    agent_name = data.get("agent", "Unknown")
    update_type = data.get("type", "unknown")
    
    if update_type == "token":
        # Real-time token streaming
        print(data.get("data", ""), end="", flush=True)
    elif update_type == "thought":
        # Agent thoughts
        thought = data.get("data", {})
        print(f"\n💭 [{agent_name}] {thought.get('content')} (confidence: {thought.get('confidence', 1.0):.2f})")
    elif update_type == "collaboration":
        # Agent collaboration
        collab = data.get("data", {})
        print(f"\n🤝 [{agent_name}] → {collab.get('with')}: {collab.get('message')}")
    elif update_type == "state_update":
        # State changes
        state = data.get("data", {})
        if state.get("status") != "idle":
            print(f"\n📊 [{agent_name}] Status: {state.get('status')} | Task: {state.get('current_task')}")


async def test_individual_agent():
    """Test a single agent."""
    print("\n=== Testing Individual Agent ===\n")
    
    # Create AI Futurist agent
    ai_agent = SimpleAIFuturistAgent(stream_callback=stream_callback)
    
    # Test basic thinking
    print("1. Testing basic AI analysis:")
    response = await ai_agent.think(
        "What are the most significant AI breakthroughs in the last 6 months that will impact customer experience?"
    )
    print(f"\nResponse length: {len(response)} characters")
    
    # Test specific method
    print("\n2. Testing AI breakthrough analysis:")
    breakthrough = {
        "name": "GPT-4 Vision",
        "description": "Multimodal AI that can understand images and text together",
        "release_date": "2023",
        "capabilities": ["image understanding", "visual reasoning", "OCR", "diagram analysis"]
    }
    
    analysis = await ai_agent.analyze_ai_breakthrough(breakthrough)
    print(f"\nAnalysis complete. Agent: {analysis['agent']}")
    
    # Save agent state
    state = await ai_agent.save_state()
    print(f"\n3. Agent state saved. Thoughts recorded: {len(state['state']['thoughts'])}")


async def test_agent_collaboration():
    """Test multiple agents collaborating."""
    print("\n\n=== Testing Agent Collaboration ===\n")
    
    # Initialize all agents
    await initialize_all_agents(stream_callback=stream_callback)
    agents = get_all_agents()
    
    print(f"Initialized {len(agents)} agents: {', '.join(agents.keys())}")
    
    # Scenario: Analyze the future of AI-powered customer service
    scenario_context = {
        "topic": "AI-powered customer service",
        "timeframe": "2025-2030",
        "focus": "retail and e-commerce"
    }
    
    # 1. AI Futurist analyzes AI capabilities
    print("\n1. AI Futurist analyzing future capabilities...")
    ai_predictions = await agents["ai_futurist"].predict_agent_economy("5_years")
    
    # 2. Trend Scanner identifies signals
    print("\n2. Trend Scanner identifying weak signals...")
    signals = await agents["trend_scanner"].scan_for_signals(
        ["customer_service", "retail_technology", "ai_adoption"],
        "last_quarter"
    )
    
    # 3. Customer Insight predicts expectations
    print("\n3. Customer Insight analyzing expectation evolution...")
    expectations = await agents["customer_insight"].predict_expectation_evolution(
        "3_years", 
        "digital_natives"
    )
    
    # 4. Tech Impact evaluates technologies
    print("\n4. Tech Impact assessing technology convergence...")
    tech_assessment = await agents["tech_impact"].assess_convergence_impact([
        "Conversational AI",
        "Computer Vision", 
        "Predictive Analytics",
        "Emotion Recognition"
    ])
    
    # 5. Org Transformation designs future model
    print("\n5. Org Transformation designing future organization...")
    org_design = await agents["org_transformation"].design_future_organization(
        "retail",
        "2030",
        "large"
    )
    
    # 6. Synthesis creates coherent scenario
    print("\n6. Synthesis creating future scenario...")
    
    # Prepare insights for synthesis
    all_insights = [
        {"agent": "ai_futurist", "type": "prediction", "content": ai_predictions},
        {"agent": "trend_scanner", "type": "signals", "content": signals},
        {"agent": "customer_insight", "type": "expectations", "content": expectations},
        {"agent": "tech_impact", "type": "assessment", "content": tech_assessment},
        {"agent": "org_transformation", "type": "design", "content": org_design}
    ]
    
    synthesis = await agents["synthesis"].synthesize_insights(all_insights)
    
    print("\n\n=== Collaboration Complete ===")
    print(f"Generated {len(all_insights)} insights across {len(agents)} agents")
    print("\nKey themes identified in synthesis")


async def test_scenario_creation():
    """Test creating a complete future scenario."""
    print("\n\n=== Testing Scenario Creation ===\n")
    
    # Create synthesis agent
    synthesis_agent = SimpleSynthesisAgent(stream_callback=stream_callback)
    
    # Create a future scenario
    scenario = await synthesis_agent.create_future_scenario(
        focus_area="AI-Human Collaboration in Customer Service",
        timeframe="2030",
        scenario_type="probable"
    )
    
    print(f"\nScenario created for: {scenario['focus_area']}")
    print(f"Type: {scenario['scenario_type']}")
    print(f"Timeframe: {scenario['timeframe']}")
    
    # Generate recommendations
    print("\n\nGenerating strategic recommendations...")
    
    recommendations = await synthesis_agent.generate_strategic_recommendations(
        context={
            "industry": "retail",
            "current_state": "early AI adoption",
            "resources": "moderate",
            "risk_tolerance": "medium"
        },
        priorities=["customer_experience", "operational_efficiency", "innovation"]
    )
    
    print("\nRecommendations generated with priorities:", recommendations['priorities'])


async def main():
    """Run all tests."""
    logger.info("Starting simple agent tests...")
    
    try:
        # Test 1: Individual agent
        await test_individual_agent()
        
        # Test 2: Agent collaboration
        await test_agent_collaboration()
        
        # Test 3: Scenario creation
        await test_scenario_creation()
        
        print("\n\n✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    # Configure logging
    logger.add("test_agents.log", rotation="10 MB")
    
    # Run tests
    asyncio.run(main())