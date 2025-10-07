"""
Authentication and Authorization Middleware
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from typing import List
import jwt
from datetime import datetime
from functools import wraps

from core.config import get_settings

settings = get_settings()

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, required_roles: List[str] = None):
        super().__init__(auto_error=auto_error)
        self.required_roles = required_roles or []

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )
            
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication scheme."
            )
            
        payload = self.verify_jwt(credentials.credentials)
        
        # Check if user has required roles
        if self.required_roles:
            user_roles = payload.get("roles", [])
            if not any(role in user_roles for role in self.required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
                
        request.state.user = payload
        return credentials.credentials

    def verify_jwt(self, token: str):
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token"
            )

# Dependency for API key authentication
async def api_key_auth(api_key: str, request: Request):
    """
    Validate API key from header
    """
    if api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )
    return api_key

# Role-based access control middleware
def require_roles(roles: List[str] = None):
    """
    Decorator to require specific roles for a route
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request or not hasattr(request.state, 'user'):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
                
            user_roles = request.state.user.get('roles', [])
            if roles and not any(role in user_roles for role in roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
                
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Rate limiting middleware (basic implementation)
class RateLimiter:
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds
        self.requests = {}

    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = datetime.now()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
            
        # Remove old timestamps
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if (current_time - t).seconds < self.seconds
        ]
        
        if len(self.requests[client_ip]) >= self.times:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests"}
            )
            
        self.requests[client_ip].append(current_time)
        response = await call_next(request)
        return response

# Example usage:
# app.add_middleware(RateLimiter, times=100, seconds=60)  # 100 requests per minute