"""
Minimal Configuration for PowerShare Development
Uses SQLite database and basic settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class MinimalSettings(BaseSettings):
    """Minimal application settings for development"""
    
    # Application
    APP_NAME: str = "PowerShare Minimal"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    VERSION: str = "1.0.0-minimal"
    
    # Security
    SECRET_KEY: str = "minimal-dev-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALGORITHM: str = "HS256"
    
    # Database (SQLite for minimal setup)
    DATABASE_URL: str = "sqlite:///./powershare_minimal.db"
    
    # CORS (allow frontend development server)
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Optional External Services (can be None for minimal setup)
    OPENAI_API_KEY: Optional[str] = None  # Deprecated, use Azure OpenAI below
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None
    AZURE_OPENAI_API_VERSION: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # Disable blockchain and other complex features for minimal setup
    BLOCKCHAIN_ENABLED: bool = False
    AI_AGENTS_ENABLED: bool = False
    BECKN_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Use minimal settings for development
settings = MinimalSettings()
