"""
Configuration management for the application.
"""
from functools import lru_cache
from typing import Optional
from pydantic import BaseSettings, AnyHttpUrl, validator

class Settings(BaseSettings):
    # App Config
    app_name: str = "SecuredBanking AI Service"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # Server Config
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Security
    api_key_header: str = "X-API-Key"
    api_keys: list[str] = ["default-secure-key-123"]  # In production, store hashed keys in database
    
    # CORS
    backend_cors_origins: list[AnyHttpUrl] = []
    
    # Database
    database_url: str = "postgresql://postgres:%23nelprox92@localhost:5432/secured_bank_db"
    
    # Rate Limiting
    rate_limit: str = "100/minute"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Get the application settings, cached for performance.
    
    Returns:
        Settings: The application settings
    """
    return Settings()
