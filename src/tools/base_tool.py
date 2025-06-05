"""Base tool class for CX Futurist AI tools."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, Field
from crewai_tools import BaseTool
from loguru import logger


class ToolResult(BaseModel):
    """Standard result format for tools."""
    success: bool = Field(..., description="Whether the tool execution was successful")
    data: Optional[Any] = Field(None, description="Result data if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseCustomTool(BaseTool, ABC):
    """Base class for all custom tools in the CX Futurist system."""
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(f"Initializing tool: {self.name}")
    
    @abstractmethod
    async def _arun(self, *args, **kwargs) -> ToolResult:
        """Async implementation of the tool logic."""
        pass
    
    def _run(self, *args, **kwargs) -> str:
        """Sync wrapper for the tool - converts to string for CrewAI compatibility."""
        import asyncio
        try:
            # Run the async method
            result = asyncio.run(self._arun(*args, **kwargs))
            
            if result.success:
                # Return data as string for CrewAI
                if isinstance(result.data, str):
                    return result.data
                elif isinstance(result.data, dict):
                    import json
                    return json.dumps(result.data, indent=2)
                else:
                    return str(result.data)
            else:
                return f"Error: {result.error}"
                
        except Exception as e:
            logger.error(f"Error in {self.name}: {str(e)}")
            return f"Error executing {self.name}: {str(e)}"
    
    def log_execution(self, input_data: Any, output_data: Any):
        """Log tool execution for monitoring."""
        logger.debug(f"{self.name} - Input: {input_data}")
        logger.debug(f"{self.name} - Output: {output_data}")


class SearchToolBase(BaseCustomTool):
    """Base class for search-related tools."""
    
    max_results: int = Field(10, description="Maximum number of results to return")
    timeout: int = Field(30, description="Timeout in seconds")
    
    async def format_results(self, results: list) -> str:
        """Format search results for agent consumption."""
        if not results:
            return "No results found."
        
        formatted = []
        for i, result in enumerate(results[:self.max_results], 1):
            formatted.append(f"{i}. {result.get('title', 'Untitled')}")
            formatted.append(f"   Source: {result.get('source', 'Unknown')}")
            formatted.append(f"   Summary: {result.get('summary', 'No summary available')}")
            formatted.append("")
        
        return "\n".join(formatted)


class AnalysisToolBase(BaseCustomTool):
    """Base class for analysis-related tools."""
    
    confidence_threshold: float = Field(0.7, description="Minimum confidence threshold")
    
    def calculate_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate overall confidence score from multiple factors."""
        if not factors:
            return 0.0
        
        total_weight = sum(factors.values())
        if total_weight == 0:
            return 0.0
            
        return total_weight / len(factors)
    
    def format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results for agent consumption."""
        formatted = []
        
        # Add summary
        if "summary" in analysis:
            formatted.append(f"Summary: {analysis['summary']}")
            formatted.append("")
        
        # Add key findings
        if "findings" in analysis:
            formatted.append("Key Findings:")
            for finding in analysis["findings"]:
                formatted.append(f"- {finding}")
            formatted.append("")
        
        # Add confidence
        if "confidence" in analysis:
            formatted.append(f"Confidence Level: {analysis['confidence']:.1%}")
        
        return "\n".join(formatted)