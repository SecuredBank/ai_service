"""
Pydantic models for user authentication and authorization.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime

class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token payload data model."""
    username: Optional[str] = None
    roles: List[str] = []

class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    
    @validator('username')
    def username_must_be_valid(cls, v):
        if ' ' in v:
            raise ValueError('Username must not contain spaces')
        return v.lower()

class UserCreate(UserBase):
    """Model for user creation."""
    password: str = Field(..., min_length=8, max_length=100)
    roles: List[str] = ["user"]
    
    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v

class UserUpdate(BaseModel):
    """Model for updating user information."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None
    
    class Config:
        extra = 'ignore'

class UserInDB(UserBase):
    """User model as stored in the database."""
    id: str
    hashed_password: str
    roles: List[str]
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class UserResponse(UserBase):
    """User response model (excludes sensitive data)."""
    id: str
    roles: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
