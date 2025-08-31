from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum
from app.schemas.hero import HeroOut


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


class StoryGenerateWithHeroesRequest(BaseModel):
    """Schema for generating stories with multiple heroes"""
    story_name: str = Field(..., description="Name/title of the story")
    story_idea: str = Field(..., description="Main idea or plot of the story")
    story_style: StoryStyle = Field(..., description="Style/genre of the story")
    language: Language = Field(default=Language.ENGLISH, description="Language for the story")
    story_length: StoryLength = Field(default=StoryLength.MEDIUM, description="Length of the story (1-5, where 3 is medium)")
    heroes: List[HeroOut] = Field(..., description="List of heroes to include in the story", min_length=1)


class StoryOut(BaseModel):
    """Complete story output schema"""
    id: UUID
    user_id: UUID
    title: str
    content: str
    story_style: str
    language: str
    story_idea: str
    story_length: int
    hero_names: Optional[List[str]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class StoryListItem(BaseModel):
    """Minimal story info for lists"""
    id: UUID
    user_id: UUID
    title: str
    story_style: str
    language: str
    story_idea: str
    created_at: datetime
    hero_names: Optional[List[str]] = None

    model_config = {"from_attributes": True}