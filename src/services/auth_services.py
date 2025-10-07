"""
Authentication services for user management and JWT token handling.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from core.config import get_settings
from db.mongo import db

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    Service for handling authentication related operations.
    """
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate a password hash."""
        return pwd_context.hash(password)

    @staticmethod
    async def create_user(username: str, email: str, password: str, roles: list = None) -> dict:
        """Create a new user."""
        if roles is None:
            roles = ["user"]
            
        existing_user = await db.db.users.find_one({"$or": [{"username": username}, {"email": email}]})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
            
        hashed_password = AuthService.get_password_hash(password)
        user = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "roles": roles,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.db.users.insert_one(user)
        user["id"] = str(result.inserted_id)
        return user

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[dict]:
        """Authenticate a user."""
        user = await db.db.users.find_one({"$or": [{"username": username}, {"email": username}]})
        if not user:
            return None
        if not AuthService.verify_password(password, user["hashed_password"]):
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
            
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify a JWT token."""
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

    @staticmethod
    async def refresh_token(refresh_token: str) -> Dict[str, str]:
        """Refresh access token using refresh token."""
        try:
            payload = jwt.decode(
                refresh_token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            
            if payload["type"] != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token type"
                )
                
            # Get user from database
            user = await db.db.users.find_one({"username": payload["sub"]})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
                
            # Create new tokens
            access_token = AuthService.create_access_token(
                data={"sub": user["username"], "roles": user["roles"]}
            )
            new_refresh_token = AuthService.create_refresh_token(
                data={"sub": user["username"]}
            )
            
            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid refresh token"
            )