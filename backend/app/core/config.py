"""
Core Configuration Settings
PowerShare Energy Trading Platform
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "PowerShare"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = "sqlite:///./powershare.db"  # Default to SQLite for development
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None  # Deprecated, use Azure OpenAI below
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None
    AZURE_OPENAI_API_VERSION: Optional[str] = None
    
    # Blockchain
    BLOCKCHAIN_RPC_URL: str = "http://localhost:8545"
    BLOCKCHAIN_NETWORK: str = "development"
    SMART_CONTRACT_ADDRESS: Optional[str] = None
    
    # Beckn Protocol
    BECKN_GATEWAY_URL: str = "https://gateway.beckn.org"
    BECKN_SUBSCRIBER_ID: str = "powershare.energy"
    BECKN_SUBSCRIBER_URL: str = "https://api.powershare.energy"
    
    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_PATH: str = "./uploads"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Energy Trading
    DEFAULT_ENERGY_PRICE_PER_KWH: float = 0.12
    PLATFORM_FEE_PERCENTAGE: float = 2.0
    MAX_TRADING_DISTANCE_KM: float = 50.0
    
    # IoT Integration
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    
    # AI Agents
    AI_AGENT_MAX_RETRIES: int = 3
    AI_AGENT_TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
