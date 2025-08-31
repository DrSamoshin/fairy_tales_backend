import uuid
from sqlalchemy import Column, UUID, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_classes import BaseUser


class StoryHero(BaseUser):
    """Junction table for many-to-many relationship between stories and heroes"""
    __tablename__ = "story_heroes"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    hero_id = Column(UUID(as_uuid=True), ForeignKey("heroes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    story = relationship("Story", back_populates="story_heroes")
    hero = relationship("Hero", back_populates="story_heroes")

    __table_args__ = (
        # Unique constraint to prevent duplicate story-hero pairs
        Index('ix_story_hero_unique', 'story_id', 'hero_id', unique=True),
        
        # Performance indexes
        Index('ix_story_heroes_story_id', 'story_id'),
        Index('ix_story_heroes_hero_id', 'hero_id'),
    )

    def __repr__(self):
        return f"StoryHero(story_id={self.story_id}, hero_id={self.hero_id})"