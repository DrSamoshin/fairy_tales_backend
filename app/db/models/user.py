import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, UUID, DateTime, Index
from sqlalchemy.orm import relationship
from app.db.base_classes import BaseUser


class User(BaseUser):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=True, index=True)
    password_hash = Column(String, nullable=True)
    apple_id = Column(String, unique=True, nullable=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        # Composite indexes for authentication queries
        Index('ix_users_email_active', 'email', 'is_active'),
        Index('ix_users_apple_id_active', 'apple_id', 'is_active'),
        
        # Additional performance indexes
        Index('ix_users_created_at', 'created_at'),
        Index('ix_users_active_created', 'is_active', 'created_at'),
        
        # Partial index for active users only
        Index('ix_users_active_only', 'email', 'created_at',
              postgresql_where=Column('is_active') == True),
    )

    def __repr__(self):
        return f"User(id={self.id}, email={self.email}, name={self.name}, is_active={self.is_active})"
