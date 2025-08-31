import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, UUID, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base_classes import BaseUser


class Series(BaseUser):
    """Series of related stories"""
    __tablename__ = "series"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="series")
    stories = relationship("Story", back_populates="series")

    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_series_user_active', 'user_id', 'is_deleted'),
        Index('ix_series_user_created', 'user_id', 'created_at'),
        Index('ix_series_active_created', 'is_deleted', 'created_at'),
        
        # Single column indexes
        Index('ix_series_created_at', 'created_at'),
        
        # Partial indexes for performance
        Index('ix_series_active_only', 'user_id', 'created_at', 
              postgresql_where=Column('is_deleted') == False),
    )

    def __repr__(self):
        return f"Series(id={self.id}, title={self.title}, user_id={self.user_id}, is_deleted={self.is_deleted})"