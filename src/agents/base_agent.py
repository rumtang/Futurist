"""Base agent class for CX Futurist AI agents."""

from typing import List, Optional, Dict, Any
from crewai import Agent
from langchain_openai import ChatOpenAI
from loguru import logger
import asyncio
from abc import ABC, abstractmethod

from src.config.base_config import settings


class BaseCustomAgent(ABC):
    """Base class for all custom agents in the CX Futurist system."""
    
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List] = None,
        verbose: bool = True,
        max_iter: int = 10,
        memory: bool = True,
        stream_callback: Optional[callable] = None
    ):
        """Initialize the base agent."""
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.verbose = verbose
        self.max_iter = max_iter
        self.memory = memory
        self.stream_callback = stream_callback
        
        # Initialize LLM
        self.llm = self._create_llm()
        
        # Create CrewAI agent
        self.agent = self._create_agent()
        
        # Track agent state
        self.state = {
            "status": "idle",
            "current_task": None,
            "thoughts": [],
            "collaborations": []
        }
        
        logger.info(f"Initialized agent: {self.name}")
    
    def _create_llm(self) -> ChatOpenAI:
        """Create the language model for the agent."""
        return ChatOpenAI(
            model=settings.agent_model,
            temperature=settings.agent_temperature,
            max_tokens=settings.agent_max_tokens,
            openai_api_key=settings.openai_api_key,
            streaming=True,
            callbacks=[self._stream_handler] if self.stream_callback else None
        )
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent instance."""
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            verbose=self.verbose,
            tools=self.tools,
            llm=self.llm,
            max_iter=self.max_iter,
            memory=self.memory
        )
    
    def _stream_handler(self, token: str):
        """Handle streaming tokens from the LLM."""
        if self.stream_callback:
            asyncio.create_task(self.stream_callback({
                "agent": self.name,
                "type": "token",
                "content": token,
                "timestamp": asyncio.get_event_loop().time()
            }))
    
    async def update_state(self, update: Dict[str, Any]):
        """Update agent state and notify observers."""
        self.state.update(update)
        
        if self.stream_callback:
            await self.stream_callback({
                "agent": self.name,
                "type": "state_update",
                "state": self.state,
                "timestamp": asyncio.get_event_loop().time()
            })
    
    async def add_thought(self, thought: str, confidence: float = 1.0):
        """Add a thought to the agent's thought stream."""
        thought_data = {
            "content": thought,
            "confidence": confidence,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        self.state["thoughts"].append(thought_data)
        
        if self.stream_callback:
            await self.stream_callback({
                "agent": self.name,
                "type": "thought",
                "thought": thought_data
            })
    
    async def collaborate_with(self, other_agent: str, message: str):
        """Record collaboration with another agent."""
        collaboration = {
            "with": other_agent,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        self.state["collaborations"].append(collaboration)
        
        if self.stream_callback:
            await self.stream_callback({
                "agent": self.name,
                "type": "collaboration",
                "collaboration": collaboration
            })
    
    @abstractmethod
    def get_instructions(self) -> str:
        """Get specific instructions for this agent type."""
        pass
    
    def enhance_backstory(self) -> str:
        """Enhance the backstory with current context."""
        return f"{self.backstory}\n\nAdditional Instructions:\n{self.get_instructions()}"


class AnalyticalAgent(BaseCustomAgent):
    """Base class for analytical agents."""
    
    def __init__(self, *args, **kwargs):
        self.analysis_depth = kwargs.pop("analysis_depth", "comprehensive")
        self.confidence_threshold = kwargs.pop("confidence_threshold", 0.7)
        super().__init__(*args, **kwargs)
    
    async def analyze(self, data: Any) -> Dict[str, Any]:
        """Perform analysis on data."""
        await self.update_state({"status": "analyzing", "current_task": "analysis"})
        
        # This would be implemented by specific analytical agents
        result = await self._perform_analysis(data)
        
        await self.update_state({"status": "idle", "current_task": None})
        return result
    
    @abstractmethod
    async def _perform_analysis(self, data: Any) -> Dict[str, Any]:
        """Perform specific analysis - to be implemented by subclasses."""
        pass


class ResearchAgent(BaseCustomAgent):
    """Base class for research-oriented agents."""
    
    def __init__(self, *args, **kwargs):
        self.research_depth = kwargs.pop("research_depth", "thorough")
        self.max_sources = kwargs.pop("max_sources", 10)
        super().__init__(*args, **kwargs)
    
    async def research(self, topic: str) -> Dict[str, Any]:
        """Conduct research on a topic."""
        await self.update_state({"status": "researching", "current_task": f"research_{topic}"})
        
        # This would be implemented by specific research agents
        result = await self._conduct_research(topic)
        
        await self.update_state({"status": "idle", "current_task": None})
        return result
    
    @abstractmethod
    async def _conduct_research(self, topic: str) -> Dict[str, Any]:
        """Conduct specific research - to be implemented by subclasses."""
        pass