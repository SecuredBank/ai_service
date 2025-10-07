"""
Authentication controllers for handling user authentication and authorization.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any, Optional
from datetime import timedelta

from core.config import get_settings
from services.auth_services import AuthService
from middleware.auth_middleware import JWTBearer, require_roles
from models.user_models import UserCreate, UserResponse, Token, TokenData

router = APIRouter()
settings = get_settings()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user.
    
    - **username**: Unique username
    - **email**: User's email address
    - **password**: User's password (min 8 characters)
    - **roles**: Optional list of roles (default: ["user"])
    """
    try:
        user = await AuthService.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            roles=user_data.roles
        )
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "roles": user["roles"],
            "is_active": user["is_active"]
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    - **username**: Username or email
    - **password**: User's password
    """
    user = await AuthService.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"sub": user["username"], "roles": user.get("roles", [])},
        expires_delta=access_token_expires
    )
    
    refresh_token = AuthService.create_refresh_token(
        data={"sub": user["username"]}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str):
    """
    Refresh an access token using a refresh token.
    
    - **refresh_token**: A valid refresh token
    """
    try:
        return await AuthService.refresh_tokens(refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(request: Request):
    """
    Get current user information.
    
    Requires authentication.
    """
    if not hasattr(request.state, 'user'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_data = request.state.user
    return {
        "username": user_data["sub"],
        "roles": user_data.get("roles", [])
    }

@router.get("/protected-route")
@require_roles(["admin"])
async def protected_route():
    """
    Example of a protected route that requires admin role.
    
    Requires authentication and admin role.
    """
    return {"message": "This is a protected route that requires admin role"}