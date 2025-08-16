from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class AppleSignIn(BaseModel):
    apple_id: str
    name: str  # Display name from Apple/client (not stored in DB)
    identity_token: Optional[str] = None  # JWT token from Apple Sign In


class UserOut(BaseModel):
    """User output schema - only essential data"""
    id: UUID
    apple_id: str
    email: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    """Minimal user summary for responses (without sensitive data)"""
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
