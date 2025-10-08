"""
KYC (Know Your Customer) model for the AI Secured Bank application.
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from bson import ObjectId

from .user_model import PyObjectId

class KYCStatus(str, Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NOT_SUBMITTED = "NOT_SUBMITTED"

class KYCBase(BaseModel):
    """Base KYC model with common fields."""
    user: PyObjectId = Field(..., description="Reference to User")
    national_id: HttpUrl = Field(..., alias="nationalId", description="URL to national ID document")
    selfie: HttpUrl = Field(..., description="URL to user's selfie")
    passport: Optional[HttpUrl] = Field(None, description="URL to passport document (optional)")
    document_number: str = Field(..., alias="documentNumber", min_length=5, max_length=50, description="ID/Passport number")
    status: KYCStatus = Field(default=KYCStatus.PENDING, description="KYC verification status")
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason", description="Reason for rejection if applicable")
    verified_by: Optional[PyObjectId] = Field(None, alias="verifiedBy", description="Admin who verified the KYC")
    verified_at: Optional[datetime] = Field(None, alias="verifiedAt", description="When KYC was verified")
    is_verified: bool = Field(default=False, alias="isVerified", description="Derived from status")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user": "507f1f77bcf86cd799439011",
                "nationalId": "https://example.com/documents/national_id.jpg",
                "selfie": "https://example.com/selfies/selfie.jpg",
                "passport": "https://example.com/documents/passport.jpg",
                "documentNumber": "A12345678",
                "status": "PENDING"
            }
        }

class KYCCreate(KYCBase):
    """Model for creating a new KYC record."""
    pass

class KYCInDB(KYCBase):
    """KYC model as stored in the database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

class KYCResponse(KYCBase):
    """KYC model for API responses."""
    id: str = Field(..., alias="_id")

class KYCUpdate(BaseModel):
    """Model for updating KYC information."""
    status: Optional[KYCStatus] = None
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    verified_by: Optional[PyObjectId] = Field(None, alias="verifiedBy")
    verified_at: Optional[datetime] = Field(None, alias="verifiedAt")
    is_verified: Optional[bool] = Field(None, alias="isVerified")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        fields = {
            'rejection_reason': 'rejectionReason',
            'verified_by': 'verifiedBy',
            'verified_at': 'verifiedAt',
            'is_verified': 'isVerified'
        }

class KYCStatusUpdate(BaseModel):
    """Model for updating KYC status."""
    status: KYCStatus
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")

    class Config:
        allow_population_by_field_name = True
