from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Multi-Agent Chat System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "multi_agent_chat"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # Agent configuration
    AVAILABLE_AGENTS: List[str] = [
        "sales_agent",
        "strategic_agent",
        "support_agent",
        "technical_agent"
    ]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
