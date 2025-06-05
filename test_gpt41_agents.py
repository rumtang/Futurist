#!/usr/bin/env python3
"""Test agents with GPT-4.1 and o3 models."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Import agents
from src.agents.simple_ai_futurist_agent import SimpleAIFuturistAgent
from src.agents.simple_trend_scanner_agent import SimpleTrendScannerAgent
from src.agents.simple_customer_insight_agent import SimpleCustomerInsightAgent
from src.agents.simple_tech_impact_agent import SimpleTechImpactAgent
from src.agents.simple_org_transformation_agent import SimpleOrgTransformationAgent
from src.agents.simple_synthesis_agent import SimpleSynthesisAgent


async def test_agent(agent, test_prompt):
    """Test an individual agent."""
    print(f"\n{'='*60}")
    print(f"Testing {agent.name} (Model: {agent.model})")
    print(f"{'='*60}")
    
    try:
        # Test the agent's think method
        response = await agent.think(test_prompt)
        print(f"✅ {agent.name} responded successfully!")
        print(f"Response preview: {response[:200]}...")
        return True
    except Exception as e:
        print(f"❌ {agent.name} failed: {type(e).__name__}: {e}")
        return False


async def main():
    """Test all agents with their assigned models."""
    print("Testing CX Futurist AI Agents with GPT-4.1 and o3 models")
    
    # Initialize agents
    agents = [
        (SimpleAIFuturistAgent(), "What are the latest AI breakthroughs that will impact customer experience?"),
        (SimpleTrendScannerAgent(), "What weak signals are you detecting in customer behavior?"),
        (SimpleCustomerInsightAgent(), "How are customer expectations evolving in 2024?"),
        (SimpleTechImpactAgent(), "What emerging technologies will reshape CX in the next 2 years?"),
        (SimpleOrgTransformationAgent(), "How must organizations transform to meet future CX demands?"),
        (SimpleSynthesisAgent(), "Synthesize the key insights about the future of customer experience.")
    ]
    
    # Test each agent
    results = []
    for agent, prompt in agents:
        result = await test_agent(agent, prompt)
        results.append((agent.name, agent.model, result))
        await asyncio.sleep(1)  # Small delay between tests
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    for name, model, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {name:<25} | Model: {model}")
    
    # Check if all tests passed
    all_passed = all(result[2] for result in results)
    if all_passed:
        print("\n🎉 All agents are working with their assigned GPT-4.1/o3 models!")
    else:
        print("\n⚠️  Some agents failed. Please check the errors above.")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())