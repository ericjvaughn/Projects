from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Multi-Agent Chat System"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # Context settings
    CONTEXT_TTL: int = 3600  # 1 hour in seconds
    MAX_CONTEXT_MESSAGES: int = 10
    
    # WebSocket settings
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    # Agent settings
    DEFAULT_AGENTS: List[str] = [
        "sales_agent",
        "strategic_agent"
    ]
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # Backend
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
