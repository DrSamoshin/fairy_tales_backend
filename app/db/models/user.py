import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, UUID, DateTime, Index
from sqlalchemy.orm import relationship
from app.db.base_classes import BaseUser


class User(BaseUser):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    apple_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=True, index=True)  # Optional from Apple
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        # Primary indexes for Apple authentication
        Index('ix_users_apple_id_active', 'apple_id', 'is_active'),
        
        # Optional email index (for analytics/support)
        Index('ix_users_email_active', 'email', 'is_active'),
        
        # Performance indexes
        Index('ix_users_created_at', 'created_at'),
        Index('ix_users_active_created', 'is_active', 'created_at'),
    )

    def __repr__(self):
        return f"User(id={self.id}, apple_id={self.apple_id}, email={self.email}, is_active={self.is_active})"
