from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum


class StoryStyle(str, Enum):
    ADVENTURE = "Adventure"
    FANTASY = "Fantasy"
    EDUCATIONAL = "Educational"
    MYSTERY = "Mystery"


class Language(str, Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"


class StoryLength(int, Enum):
    VERY_SHORT = 1  # ~100-200 words
    SHORT = 2       # ~200-300 words  
    MEDIUM = 3      # ~300-400 words (default)
    LONG = 4        # ~400-500 words
    VERY_LONG = 5   # ~500-600 words


class ChildGender(str, Enum):
    BOY = "boy"
    GIRL = "girl"


class StoryBase(BaseModel):
    title: str


class StoryGenerateRequest(BaseModel):
    """Unified schema for both generate and generate-stream endpoints"""
    story_name: str = Field(..., description="Name/title of the story")
    hero_name: str = Field(..., description="Name of the main character")
    age: int = Field(..., ge=3, le=16, description="Age of the target audience (3-16 years)")
    story_style: StoryStyle = Field(..., description="Style/genre of the story")
    language: Language = Field(default=Language.ENGLISH, description="Language for the story")
    story_idea: str = Field(..., description="Main idea or plot of the story")
    story_length: StoryLength = Field(default=StoryLength.MEDIUM, description="Length of the story (1-5, where 3 is medium)")
    child_gender: ChildGender = Field(..., description="Gender of the target child reader (boy/girl)")


# Legacy alias for backward compatibility
StoryGenerate = StoryGenerateRequest





class StoryOut(StoryBase):
    id: UUID
    user_id: UUID
    content: str
    hero_name: str
    age: int
    story_style: str
    language: str
    story_idea: str
    story_length: int
    child_gender: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StoryListItem(BaseModel):
    """Minimal story info for lists (compact view)"""
    id: UUID
    title: str
    hero_name: str
    story_style: str
    language: str
    age: int
    created_at: datetime

    model_config = {"from_attributes": True}


class StoriesListData(BaseModel):
    """Structured data for stories list response"""
    stories: List[StoryOut]  # Use full StoryOut for complete information
    total: int
    skip: int
    limit: int
