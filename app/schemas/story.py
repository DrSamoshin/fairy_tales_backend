from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum


class StoryStyle(str, Enum):
    ADVENTURE = "Adventure"
    FANTASY = "Fantasy"
    COMEDY = "Comedy"
    EDUCATIONAL = "Educational"
    MYSTERY = "Mystery"


class Language(str, Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"


class StoryBase(BaseModel):
    title: str


class StoryGenerate(BaseModel):
    story_name: str = Field(..., description="Name/title of the story")
    hero_name: str = Field(..., description="Name of the main character")
    age: int = Field(..., ge=3, le=16, description="Age of the target audience (3-16 years)")
    story_style: StoryStyle = Field(..., description="Style/genre of the story")
    language: Language = Field(default=Language.ENGLISH, description="Language for the story")
    story_idea: str = Field(..., description="Main idea or plot of the story")


class StoryCreate(StoryBase):
    content: str
    hero_name: str
    age: int
    story_style: str
    language: str
    story_idea: str


class StoryOut(StoryBase):
    id: UUID
    user_id: UUID
    content: str
    hero_name: str
    age: int
    story_style: str
    language: str
    story_idea: str
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
