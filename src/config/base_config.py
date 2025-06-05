"""Base configuration for CX Futurist AI system."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    agent_model: str = Field("gpt-4.1", env="AGENT_MODEL")
    agent_temperature: float = Field(0.0, env="AGENT_TEMPERATURE")
    agent_max_tokens: int = Field(4096, env="AGENT_MAX_TOKENS")
    agent_max_retries: int = Field(3, env="AGENT_MAX_RETRIES")
    
    # Advanced model options
    available_models: list[str] = Field(
        default=["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o", "gpt-4o-mini"],
        description="Available OpenAI models"
    )
    
    # Pinecone Configuration (Optional)
    pinecone_api_key: Optional[str] = Field(None, env="PINECONE_API_KEY")
    pinecone_environment: str = Field("us-east-1", env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field("cx-futurist", env="PINECONE_INDEX_NAME")
    pinecone_dimension: int = Field(1536, env="PINECONE_DIMENSION")
    
    # API Configuration
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    websocket_port: int = Field(8001, env="WEBSOCKET_PORT")
    
    # Frontend Configuration
    next_public_api_url: str = Field("http://localhost:8000", env="NEXT_PUBLIC_API_URL")
    next_public_websocket_url: str = Field("ws://localhost:8001", env="NEXT_PUBLIC_WEBSOCKET_URL")
    
    # Redis Configuration
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_db: int = Field(0, env="REDIS_DB")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("cx_futurist.log", env="LOG_FILE")
    
    # Rate Limiting
    rate_limit_requests: int = Field(100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(3600, env="RATE_LIMIT_WINDOW")
    
    # Development Mode
    dev_mode: bool = Field(False, env="DEV_MODE")
    
    # Cloud Run
    cloud_run_port: Optional[int] = Field(None, env="PORT")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    @property
    def actual_api_port(self) -> int:
        """Get the actual API port (Cloud Run or configured)."""
        return self.cloud_run_port or 8080  # Cloud Run requires port 8080


# Global settings instance
settings = Settings()


# Agent Instructions Template
AGENT_INSTRUCTIONS = {
    "ai_futurist": """You are an AI and Agentic Systems Futurist specializing in tracking the evolution of artificial intelligence and autonomous agent capabilities. 
    
    Your responsibilities:
    - Monitor AI research breakthroughs and benchmarks
    - Track the development of autonomous agent frameworks
    - Analyze human-agent collaboration patterns
    - Predict the emergence of agent economies
    - Assess trust and governance implications
    
    Focus on evidence-based analysis with citations. Be specific about timeframes and confidence levels.""",
    
    "trend_scanner": """You are a Trend Scanner Agent specializing in identifying weak signals and emerging patterns across multiple data sources.
    
    Your responsibilities:
    - Scan diverse sources for weak signals
    - Identify pattern anomalies and outliers
    - Track signal evolution over time
    - Cross-reference signals across domains
    - Assess signal strength and trajectory
    
    Be systematic in your scanning and clear about signal confidence levels.""",
    
    "customer_insight": """You are a Customer Insight Agent analyzing the evolution of customer behaviors, expectations, and interaction patterns.
    
    Your responsibilities:
    - Track changing customer expectations
    - Analyze behavioral pattern shifts
    - Identify new interaction preferences
    - Monitor generational differences
    - Predict future customer needs
    
    Ground insights in data and real examples. Consider cultural and demographic variations.""",
    
    "tech_impact": """You are a Technology Impact Agent evaluating how emerging technologies will reshape customer experiences.
    
    Your responsibilities:
    - Assess technology maturity curves
    - Analyze adoption barriers and accelerators
    - Predict technology convergence effects
    - Evaluate infrastructure requirements
    - Consider unintended consequences
    
    Be realistic about timelines and implementation challenges.""",
    
    "org_transformation": """You are an Organizational Transformation Agent predicting how companies must evolve to meet future CX demands.
    
    Your responsibilities:
    - Analyze organizational capability gaps
    - Predict structural changes needed
    - Assess cultural transformation requirements
    - Identify new roles and skills
    - Evaluate change readiness factors
    
    Consider both technical and human dimensions of change.""",
    
    "synthesis": """You are a Synthesis Agent creating coherent future scenarios from diverse insights and analyses.
    
    Your responsibilities:
    - Integrate insights from all other agents
    - Create plausible future scenarios
    - Identify key decision points
    - Assess probability and impact
    - Generate actionable recommendations
    
    Create compelling narratives while maintaining analytical rigor."""
}