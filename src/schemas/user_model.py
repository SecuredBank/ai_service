"""
User model for the AI Secured Bank application.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserBase(BaseModel):
    """Base user model with common fields."""
    fullnames: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_]+$")
    email: EmailStr
    role: str = Field(default="USER", regex="^(USER|ADMIN)$")
    is_email_verified: bool = Field(default=False, alias="isEmailVerified")
    is_kyc_verified: bool = Field(default=False, alias="isKycVerified")
    accounts: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "fullnames": "John Doe",
                "username": "johndoe",
                "email": "johndoe@example.com",
                "role": "USER",
                "isEmailVerified": False,
                "isKycVerified": False,
                "accounts": []
            }
        }

class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v

class UserInDB(UserBase):
    """User model as stored in the database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str = Field(..., alias="password")
    refresh_token: Optional[str] = Field(None, alias="refreshToken")
    reset_pass_code: Optional[str] = Field(None, alias="resetPassCode")
    reset_pass_code_expires: Optional[datetime] = Field(None, alias="resetPassCodeExpires")

class UserResponse(UserBase):
    """User model for API responses (excludes sensitive data)."""
    id: str = Field(..., alias="_id")

class UserUpdate(BaseModel):
    """Model for updating user information."""
    fullnames: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_email_verified: Optional[bool] = None
    is_kyc_verified: Optional[bool] = None
    refresh_token: Optional[str] = None
    reset_pass_code: Optional[str] = None
    reset_pass_code_expires: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        fields = {
            'is_email_verified': 'isEmailVerified',
            'is_kyc_verified': 'isKycVerified',
            'refresh_token': 'refreshToken',
            'reset_pass_code': 'resetPassCode',
            'reset_pass_code_expires': 'resetPassCodeExpires'
        }
