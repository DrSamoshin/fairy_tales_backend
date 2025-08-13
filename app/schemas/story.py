from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class StoryBase(BaseModel):
    title: str


class StoryGenerate(BaseModel):
    prompt: str
    title: Optional[str] = None


class StoryCreate(StoryBase):
    content: str
    prompt: str


class StoryUpdate(BaseModel):
    title: Optional[str] = None


class StoryOut(StoryBase):
    id: UUID
    user_id: UUID
    content: str
    prompt: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StoryList(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StoriesResponse(BaseModel):
    stories: List[StoryList]
    total: int
