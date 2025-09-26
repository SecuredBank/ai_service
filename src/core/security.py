from fastapi import HTTPException, status, Security, Depends
from fastapi.security import APIKeyHeader
from typing import Optional
from config.settings import get_settings

settings = get_settings()

api_key_header = APIKeyHeader(
    name=settings.api_key_header,
    auto_error=True,
    description="API key for authentication"
)

async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validate the API key from the request header.
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If the API key is invalid
    """
    if api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )
    return api_key

# Dependency that can be used in FastAPI route dependencies
api_key_auth = Depends(get_api_key)
