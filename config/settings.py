from pydantic_settings import BaseSettings
from typing import List
from pydantic import AnyHttpUrl, validator

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
    api_keys: List[str] = ["default-secure-key-123"]  # In production, store hashed keys in database
    
    # CORS
    backend_cors_origins: List[AnyHttpUrl] = []
    
    # Database
    database_url: str = "postgresql://postgres:%23nelprox92@localhost:5432/secured_bank_db"
    
    # Rate Limiting
    rate_limit: str = "100/minute"
    
    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)