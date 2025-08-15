import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, UUID, DateTime, Text, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from app.db.base_classes import BaseUser


class Story(BaseUser):
    __tablename__ = "stories"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    hero_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    story_style = Column(String, nullable=False)
    language = Column(String, nullable=False)
    story_idea = Column(Text, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="stories")

    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_stories_user_active', 'user_id', 'is_deleted'),
        Index('ix_stories_user_created', 'user_id', 'created_at'),
        Index('ix_stories_active_created', 'is_deleted', 'created_at'),
        
        # Single column indexes
        Index('ix_stories_created_at', 'created_at'),
        Index('ix_stories_language', 'language'),
        Index('ix_stories_style', 'story_style'),
        Index('ix_stories_age', 'age'),
        
        # Partial indexes for performance
        Index('ix_stories_active_only', 'user_id', 'created_at', 
              postgresql_where=Column('is_deleted') == False),
    )

    def __repr__(self):
        return f"Story(id={self.id}, title={self.title}, user_id={self.user_id}, is_deleted={self.is_deleted})"
