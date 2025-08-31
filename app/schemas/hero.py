from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class HeroCreate(BaseModel):
    """Schema for creating a new hero"""
    name: str = Field(..., description="Hero name", min_length=1, max_length=100)
    gender: str = Field(..., description="Hero gender", min_length=1, max_length=20)
    age: int = Field(..., description="Hero age", ge=1, le=100)
    appearance: Optional[str] = Field(None, description="Hero appearance description", max_length=500)
    personality: Optional[str] = Field(None, description="Hero personality description", max_length=500)
    power: Optional[str] = Field(None, description="Hero power description", max_length=500)
    avatar_image: Optional[str] = Field(None, description="Hero avatar image URL", max_length=500)


class HeroUpdate(BaseModel):
    """Schema for updating a hero"""
    name: Optional[str] = Field(None, description="Hero name", min_length=1, max_length=100)
    gender: Optional[str] = Field(None, description="Hero gender", min_length=1, max_length=20)
    age: Optional[int] = Field(None, description="Hero age", ge=1, le=100)
    appearance: Optional[str] = Field(None, description="Hero appearance description", max_length=500)
    personality: Optional[str] = Field(None, description="Hero personality description", max_length=500)
    power: Optional[str] = Field(None, description="Hero power description", max_length=500)
    avatar_image: Optional[str] = Field(None, description="Hero avatar image URL", max_length=500)


class HeroOut(BaseModel):
    """Hero output schema"""
    id: UUID
    user_id: UUID
    name: str
    gender: str
    age: int
    appearance: Optional[str] = None
    personality: Optional[str] = None
    power: Optional[str] = None
    avatar_image: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class HeroSummary(BaseModel):
    """Minimal hero summary for lists"""
    id: UUID
    name: str
    gender: str
    age: int
    avatar_image: Optional[str] = None

    model_config = {"from_attributes": True}