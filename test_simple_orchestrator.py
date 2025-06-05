"""Simple test for orchestrator without external dependencies."""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set dummy environment variables for testing
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['PINECONE_API_KEY'] = 'test-key'
os.environ['PINECONE_INDEX_NAME'] = 'test-index'
os.environ['REDIS_HOST'] = 'localhost'


async def mock_stream_callback(data):
    """Mock stream callback for testing."""
    print(f"[STREAM] {data['type']}: {data.get('agent', 'system')} - {data.get('data', '')[:100]}")


async def test_basic_orchestrator():
    """Test basic orchestrator initialization."""
    try:
        from src.orchestrator.simple_orchestrator import SimpleOrchestrator
        
        print("Creating SimpleOrchestrator...")
        orchestrator = SimpleOrchestrator(stream_callback=mock_stream_callback)
        
        print("\nAgents initialized:")
        for name, agent in orchestrator.agents.items():
            print(f"  - {name}: {agent.role}")
        
        print("\nGetting agent states...")
        states = await orchestrator.get_agent_states()
        for agent_name, state in states.items():
            print(f"  - {agent_name}: status={state['status']}, thoughts={state['thought_count']}")
        
        print("\nTesting agent thinking...")
        ai_futurist = orchestrator.ai_futurist
        response = await ai_futurist.think("What are the key trends in AI agents for 2025?")
        print(f"\nAI Futurist response:\n{response[:200]}...")
        
        print("\nOrchestrator test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_basic_orchestrator())