from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    name: str


class UserRegister(UserBase):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AppleSignIn(UserBase):
    apple_id: str
    

class UserUpdate(BaseModel):
    name: Optional[str] = None


class UserOut(UserBase):
    id: UUID
    email: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfile(UserOut):
    stories_count: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
