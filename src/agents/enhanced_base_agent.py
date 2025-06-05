"""Enhanced base agent with GPT-4.1 and o3 model support."""

from typing import List, Optional, Dict, Any
from crewai import Agent
from langchain_openai import ChatOpenAI
from loguru import logger
import asyncio
from abc import ABC, abstractmethod

from src.config.base_config import settings


class ModelSelector:
    """Smart model selection based on task requirements."""
    
    # Model capabilities and use cases
    MODEL_PROFILES = {
        "gpt-4.1": {
            "strength": "general_intelligence",
            "best_for": ["complex_reasoning", "synthesis", "strategic_planning"],
            "max_tokens": 8192
        },
        "gpt-4.1-mini": {
            "strength": "fast_analysis",
            "best_for": ["real_time_analysis", "trend_scanning", "quick_insights"],
            "max_tokens": 4096
        },
        "gpt-4.1-nano": {
            "strength": "ultra_efficient",
            "best_for": ["simple_tasks", "data_extraction", "quick_responses"],
            "max_tokens": 2048
        },
        # o3 will be added when available
        # "o3": {
        #     "strength": "deep_reasoning", 
        #     "best_for": ["complex_synthesis", "multi_agent_coordination", "scenario_planning"],
        #     "max_tokens": 16384
        # }
    }
    
    @classmethod
    def select_model(cls, task_type: str, complexity: str = "medium") -> str:
        """Select the best model for a given task."""
        # Task type to model mapping
        task_model_map = {
            "trend_analysis": "gpt-4.1-mini",
            "future_prediction": "gpt-4.1",
            "synthesis": "gpt-4.1",  # Use gpt-4.1 for synthesis until o3 available
            "real_time_monitoring": "gpt-4.1-nano",
            "strategic_planning": "gpt-4.1",
            "innovation_tracking": "gpt-4.1",
            "complex_reasoning": "gpt-4.1"  # Use gpt-4.1 for complex reasoning
        }
        
        # Complexity override
        if complexity == "high":
            return "gpt-4.1"  # Use most capable model for high complexity
        elif complexity == "low":
            return "gpt-4.1-nano"  # Use efficient model for simple tasks
        
        # Return task-specific model or default
        return task_model_map.get(task_type, settings.agent_model)


class EnhancedBaseAgent(ABC):
    """Enhanced base agent with dynamic model selection."""
    
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
        stream_callback: Optional[callable] = None,
        preferred_model: Optional[str] = None,
        task_type: Optional[str] = None
    ):
        """Initialize the enhanced agent."""
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.verbose = verbose
        self.max_iter = max_iter
        self.memory = memory
        self.stream_callback = stream_callback
        self.task_type = task_type
        
        # Model selection
        self.current_model = preferred_model or ModelSelector.select_model(
            task_type or "general",
            complexity="medium"
        )
        
        # Ensure selected model is available
        if self.current_model not in settings.available_models:
            logger.warning(f"Model {self.current_model} not available, falling back to {settings.agent_model}")
            self.current_model = settings.agent_model
        
        # Initialize LLM
        self.llm = self._create_llm()
        
        # Create CrewAI agent
        self.agent = self._create_agent()
        
        # Track agent state
        self.state = {
            "status": "idle",
            "current_task": None,
            "current_model": self.current_model,
            "thoughts": [],
            "collaborations": [],
            "model_switches": []
        }
        
        logger.info(f"Initialized enhanced agent: {self.name} with model: {self.current_model}")
    
    def _create_llm(self, model: Optional[str] = None) -> ChatOpenAI:
        """Create the language model for the agent."""
        model_to_use = model or self.current_model
        model_profile = ModelSelector.MODEL_PROFILES.get(model_to_use, {})
        
        return ChatOpenAI(
            model=model_to_use,
            temperature=settings.agent_temperature,
            max_tokens=model_profile.get("max_tokens", settings.agent_max_tokens),
            openai_api_key=settings.openai_api_key,
            streaming=True,
            callbacks=[self._stream_handler] if self.stream_callback else None
        )
    
    def switch_model(self, new_model: str, reason: str = "task_requirement"):
        """Dynamically switch to a different model."""
        if new_model not in settings.available_models:
            logger.warning(f"Model {new_model} not available")
            return
        
        old_model = self.current_model
        self.current_model = new_model
        self.llm = self._create_llm(new_model)
        
        # Recreate agent with new LLM
        self.agent.llm = self.llm
        
        # Track model switch
        self.state["model_switches"].append({
            "from": old_model,
            "to": new_model,
            "reason": reason,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        logger.info(f"Agent {self.name} switched from {old_model} to {new_model} - Reason: {reason}")
    
    async def adaptive_task_execution(self, task: str, complexity: str = "medium"):
        """Execute task with adaptive model selection."""
        # Select best model for the task
        optimal_model = ModelSelector.select_model(self.task_type or "general", complexity)
        
        if optimal_model != self.current_model:
            self.switch_model(optimal_model, f"optimal_for_{task}")
        
        # Execute the task
        await self.update_state({"status": "thinking", "current_task": task})
        
        try:
            # Add enhanced reasoning prompt
            enhanced_prompt = f"""
            Using advanced {self.current_model} capabilities:
            - Apply deep reasoning and analysis
            - Consider multiple perspectives
            - Identify non-obvious patterns
            - Generate innovative insights
            
            Task: {task}
            """
            
            result = await self._execute_with_model(enhanced_prompt)
            
            await self.update_state({"status": "idle", "current_task": None})
            return result
            
        except Exception as e:
            logger.error(f"Error in adaptive task execution: {e}")
            # Try fallback model
            if self.current_model != "gpt-4.1":
                self.switch_model("gpt-4.1", "error_fallback")
                return await self._execute_with_model(task)
            raise
    
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
                "model": self.current_model,
                "timestamp": asyncio.get_event_loop().time()
            }))
    
    async def update_state(self, update: Dict[str, Any]):
        """Update agent state and notify observers."""
        self.state.update(update)
        self.state["current_model"] = self.current_model
        
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
            "model": self.current_model,
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
            "model": self.current_model,
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
    async def _execute_with_model(self, task: str) -> Any:
        """Execute task with current model - to be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_instructions(self) -> str:
        """Get specific instructions for this agent type."""
        pass
    
    def enhance_backstory(self) -> str:
        """Enhance the backstory with current context and model capabilities."""
        model_profile = ModelSelector.MODEL_PROFILES.get(self.current_model, {})
        model_strength = model_profile.get("strength", "general")
        
        return f"""{self.backstory}

Current Model: {self.current_model}
Model Strength: {model_strength}
Optimized For: {', '.join(model_profile.get("best_for", []))}

Additional Instructions:
{self.get_instructions()}"""


class EnhancedAnalyticalAgent(EnhancedBaseAgent):
    """Enhanced analytical agent with model optimization."""
    
    def __init__(self, *args, **kwargs):
        self.analysis_depth = kwargs.pop("analysis_depth", "comprehensive")
        self.confidence_threshold = kwargs.pop("confidence_threshold", 0.7)
        kwargs["task_type"] = "complex_reasoning"
        super().__init__(*args, **kwargs)
    
    async def analyze(self, data: Any, complexity: str = "medium") -> Dict[str, Any]:
        """Perform analysis with optimal model selection."""
        return await self.adaptive_task_execution(
            f"Analyze the following data: {data}",
            complexity=complexity
        )
    
    async def _execute_with_model(self, task: str) -> Any:
        """Execute analytical task with current model."""
        # Implementation would go here
        return {"analysis": "completed", "model": self.current_model}


class EnhancedResearchAgent(EnhancedBaseAgent):
    """Enhanced research agent with model optimization."""
    
    def __init__(self, *args, **kwargs):
        self.research_depth = kwargs.pop("research_depth", "thorough")
        self.max_sources = kwargs.pop("max_sources", 10)
        kwargs["task_type"] = "innovation_tracking"
        super().__init__(*args, **kwargs)
    
    async def research(self, topic: str, urgency: str = "normal") -> Dict[str, Any]:
        """Conduct research with optimal model selection."""
        complexity = "low" if urgency == "high" else "high"
        return await self.adaptive_task_execution(
            f"Research the following topic: {topic}",
            complexity=complexity
        )
    
    async def _execute_with_model(self, task: str) -> Any:
        """Execute research task with current model."""
        # Implementation would go here
        return {"research": "completed", "model": self.current_model}