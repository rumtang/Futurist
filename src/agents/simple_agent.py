"""Simple agent implementation using direct OpenAI calls without CrewAI."""

import asyncio
import json
from typing import List, Optional, Dict, Any, Callable
from abc import ABC, abstractmethod
import time
from dataclasses import dataclass, field

import openai
from openai import AsyncOpenAI
from loguru import logger
import backoff

from src.config.base_config import settings


@dataclass
class AgentMessage:
    """Represents a message in the agent's conversation history."""
    role: str  # 'system', 'user', 'assistant'
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentThought:
    """Represents an agent's thought during processing."""
    content: str
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    reasoning_chain: List[str] = field(default_factory=list)


@dataclass
class AgentState:
    """Tracks the current state of an agent."""
    status: str = "idle"  # idle, thinking, researching, analyzing, collaborating
    current_task: Optional[str] = None
    thoughts: List[AgentThought] = field(default_factory=list)
    collaborations: List[Dict[str, Any]] = field(default_factory=list)
    messages: List[AgentMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


class SimpleAgent(ABC):
    """Base class for simple agents using direct OpenAI API calls."""
    
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream_callback: Optional[Callable] = None,
        verbose: bool = True
    ):
        """Initialize the simple agent."""
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools = tools or []
        self.stream_callback = stream_callback
        self.verbose = verbose
        
        # Initialize OpenAI client
        api_key = settings.openai_api_key
        logger.info(f"Initializing OpenAI client with API key: {'***' + api_key[-4:] if api_key and len(api_key) > 4 else 'None'}")
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Initialize agent state
        self.state = AgentState()
        
        # Set up system message
        self.system_message = self._create_system_message()
        self.state.messages.append(AgentMessage(
            role="system",
            content=self.system_message
        ))
        
        logger.info(f"Initialized SimpleAgent: {self.name}")
    
    def _create_system_message(self) -> str:
        """Create the system message that defines the agent's behavior."""
        instructions = self.get_instructions()
        return f"""You are {self.name}, an AI agent with the following characteristics:

Role: {self.role}
Goal: {self.goal}
Backstory: {self.backstory}

{instructions}

Guidelines:
1. Stay focused on your role and goal
2. Think step-by-step through problems
3. Be specific and actionable in your responses
4. Cite sources when possible
5. Express uncertainty when appropriate
6. Collaborate with other agents when beneficial

Current timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
    
    @abstractmethod
    def get_instructions(self) -> str:
        """Get specific instructions for this agent type."""
        pass
    
    async def _stream_update(self, update_type: str, data: Any):
        """Send a streaming update if callback is configured."""
        if self.stream_callback:
            try:
                await self.stream_callback({
                    "agent": self.name,
                    "type": update_type,
                    "data": data,
                    "timestamp": time.time()
                })
            except Exception as e:
                logger.error(f"Error in stream callback: {e}")
    
    async def update_state(self, **kwargs):
        """Update agent state and notify observers."""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        
        await self._stream_update("state_update", {
            "status": self.state.status,
            "current_task": self.state.current_task,
            "thought_count": len(self.state.thoughts),
            "message_count": len(self.state.messages)
        })
    
    async def add_thought(self, content: str, confidence: float = 1.0, reasoning: List[str] = None):
        """Add a thought to the agent's thought stream."""
        thought = AgentThought(
            content=content,
            confidence=confidence,
            reasoning_chain=reasoning or []
        )
        
        self.state.thoughts.append(thought)
        
        await self._stream_update("thought", {
            "content": thought.content,
            "confidence": thought.confidence,
            "reasoning": thought.reasoning_chain
        })
        
        if self.verbose:
            logger.info(f"[{self.name}] Thought: {content} (confidence: {confidence:.2f})")
    
    async def collaborate_with(self, other_agent: str, message: str, data: Any = None):
        """Record collaboration with another agent."""
        collaboration = {
            "with": other_agent,
            "message": message,
            "data": data,
            "timestamp": time.time()
        }
        
        self.state.collaborations.append(collaboration)
        
        await self._stream_update("collaboration", collaboration)
        
        if self.verbose:
            logger.info(f"[{self.name}] Collaborating with {other_agent}: {message}")
    
    @backoff.on_exception(
        backoff.expo,
        (openai.RateLimitError, openai.APIError),
        max_tries=3,
        max_time=60
    )
    async def _call_openai(self, messages: List[Dict[str, str]], stream: bool = True) -> str:
        """Make a call to OpenAI API with retry logic."""
        try:
            if stream:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=True
                )
                
                full_response = ""
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        await self._stream_update("token", content)
                
                return full_response
            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {type(e).__name__}: {str(e)}")
            logger.error(f"Model: {self.model}, Messages: {len(messages)}")
            raise
    
    async def think(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Have the agent think about a prompt and return its response."""
        await self.update_state(status="thinking", current_task=f"thinking about: {prompt[:50]}...")
        
        # Update context if provided
        if context:
            self.state.context.update(context)
        
        # Add user message
        user_message = AgentMessage(role="user", content=prompt)
        self.state.messages.append(user_message)
        
        # Prepare messages for API call
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in self.state.messages
        ]
        
        # Make API call
        try:
            response = await self._call_openai(api_messages)
            
            # Add assistant message to history
            assistant_message = AgentMessage(role="assistant", content=response)
            self.state.messages.append(assistant_message)
            
            # Extract any thoughts from the response
            await self._extract_thoughts(response)
            
            await self.update_state(status="idle", current_task=None)
            return response
            
        except Exception as e:
            logger.error(f"Error in think method: {e}")
            await self.update_state(status="error", current_task=None)
            raise
    
    async def _extract_thoughts(self, response: str):
        """Extract thoughts from the agent's response."""
        # Simple extraction - can be enhanced with more sophisticated parsing
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('THOUGHT:') or line.startswith('THINKING:'):
                thought_content = line.split(':', 1)[1].strip()
                await self.add_thought(thought_content)
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.split(':', 1)[1].strip().rstrip('%')) / 100
                    if self.state.thoughts:
                        self.state.thoughts[-1].confidence = confidence
                except ValueError:
                    pass
    
    async def reset_conversation(self):
        """Reset the conversation history, keeping only the system message."""
        system_msg = self.state.messages[0]
        self.state = AgentState()
        self.state.messages.append(system_msg)
        await self.update_state(status="idle", current_task=None)
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation so far."""
        return f"Agent {self.name} has exchanged {len(self.state.messages)} messages and had {len(self.state.thoughts)} thoughts."
    
    async def save_state(self) -> Dict[str, Any]:
        """Save the current state of the agent."""
        return {
            "name": self.name,
            "role": self.role,
            "state": {
                "status": self.state.status,
                "current_task": self.state.current_task,
                "thoughts": [
                    {
                        "content": t.content,
                        "confidence": t.confidence,
                        "timestamp": t.timestamp,
                        "reasoning": t.reasoning_chain
                    }
                    for t in self.state.thoughts
                ],
                "messages": [
                    {
                        "role": m.role,
                        "content": m.content,
                        "timestamp": m.timestamp
                    }
                    for m in self.state.messages
                ],
                "context": self.state.context
            }
        }
    
    async def load_state(self, state_data: Dict[str, Any]):
        """Load a previously saved state."""
        if state_data.get("name") != self.name:
            logger.warning(f"Loading state from different agent: {state_data.get('name')}")
        
        state = state_data.get("state", {})
        self.state.status = state.get("status", "idle")
        self.state.current_task = state.get("current_task")
        self.state.context = state.get("context", {})
        
        # Restore thoughts
        self.state.thoughts = [
            AgentThought(
                content=t["content"],
                confidence=t["confidence"],
                timestamp=t["timestamp"],
                reasoning_chain=t.get("reasoning", [])
            )
            for t in state.get("thoughts", [])
        ]
        
        # Restore messages
        self.state.messages = [
            AgentMessage(
                role=m["role"],
                content=m["content"],
                timestamp=m["timestamp"]
            )
            for m in state.get("messages", [])
        ]


class AnalyticalSimpleAgent(SimpleAgent):
    """Base class for analytical agents using simple architecture."""
    
    def __init__(self, *args, analysis_depth: str = "comprehensive", 
                 confidence_threshold: float = 0.7, **kwargs):
        self.analysis_depth = analysis_depth
        self.confidence_threshold = confidence_threshold
        super().__init__(*args, **kwargs)
    
    async def analyze(self, data: Any, analysis_type: str = "general") -> Dict[str, Any]:
        """Perform analysis on data."""
        await self.update_state(status="analyzing", current_task=f"analyzing_{analysis_type}")
        
        # Prepare analysis prompt
        prompt = self._prepare_analysis_prompt(data, analysis_type)
        
        # Get analysis from agent
        response = await self.think(prompt)
        
        # Parse and structure the analysis
        result = self._parse_analysis_response(response)
        
        await self.update_state(status="idle", current_task=None)
        return result
    
    def _prepare_analysis_prompt(self, data: Any, analysis_type: str) -> str:
        """Prepare a prompt for analysis."""
        return f"""Please perform a {self.analysis_depth} {analysis_type} analysis on the following data:

{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}

Provide your analysis with:
1. Key findings
2. Confidence levels for each finding
3. Supporting evidence
4. Potential implications
5. Recommendations

Format your response clearly with sections."""
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the analysis response into structured data."""
        # Simple parsing - can be enhanced with more sophisticated methods
        return {
            "raw_analysis": response,
            "timestamp": time.time(),
            "agent": self.name,
            "confidence_threshold": self.confidence_threshold
        }


class ResearchSimpleAgent(SimpleAgent):
    """Base class for research-oriented agents using simple architecture."""
    
    def __init__(self, *args, research_depth: str = "thorough", 
                 max_sources: int = 10, **kwargs):
        self.research_depth = research_depth
        self.max_sources = max_sources
        super().__init__(*args, **kwargs)
    
    async def research(self, topic: str, focus_areas: List[str] = None) -> Dict[str, Any]:
        """Conduct research on a topic."""
        await self.update_state(status="researching", current_task=f"research_{topic}")
        
        # Prepare research prompt
        prompt = self._prepare_research_prompt(topic, focus_areas)
        
        # Conduct research
        response = await self.think(prompt)
        
        # Parse and structure the research
        result = self._parse_research_response(response)
        
        await self.update_state(status="idle", current_task=None)
        return result
    
    def _prepare_research_prompt(self, topic: str, focus_areas: List[str] = None) -> str:
        """Prepare a prompt for research."""
        focus_str = ""
        if focus_areas:
            focus_str = f"\nFocus particularly on: {', '.join(focus_areas)}"
        
        return f"""Please conduct {self.research_depth} research on: {topic}{focus_str}

Provide:
1. Overview of the topic
2. Key developments and trends
3. Important stakeholders or players
4. Current challenges and opportunities
5. Future outlook
6. Recommended sources for further research

Be specific and cite sources where possible."""
    
    def _parse_research_response(self, response: str) -> Dict[str, Any]:
        """Parse the research response into structured data."""
        return {
            "findings": response,
            "timestamp": time.time(),
            "agent": self.name,
            "research_depth": self.research_depth
        }