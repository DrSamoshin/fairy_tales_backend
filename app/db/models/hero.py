import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, UUID, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base_classes import BaseUser


class Hero(BaseUser):
    __tablename__ = "heroes"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    appearance = Column(String, nullable=True)
    personality = Column(String, nullable=True)
    power = Column(String, nullable=True)
    avatar_image = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="heroes")
    story_heroes = relationship("StoryHero", back_populates="hero", cascade="all, delete-orphan")
    
    # Property to get stories directly
    @property 
    def stories(self):
        return [sh.story for sh in self.story_heroes]

    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_heroes_user_active', 'user_id', 'is_deleted'),
        Index('ix_heroes_user_created', 'user_id', 'created_at'),
        Index('ix_heroes_active_created', 'is_deleted', 'created_at'),
        
        # Single column indexes
        Index('ix_heroes_created_at', 'created_at'),
        Index('ix_heroes_gender', 'gender'),
        Index('ix_heroes_age', 'age'),
        
        # Partial indexes for performance
        Index('ix_heroes_active_only', 'user_id', 'created_at', 
              postgresql_where=Column('is_deleted') == False),
    )

    def __repr__(self):
        return f"Hero(id={self.id}, name={self.name}, user_id={self.user_id}, is_deleted={self.is_deleted})"