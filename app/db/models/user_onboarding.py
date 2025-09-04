import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, UUID, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base_classes import BaseUser


class UserOnboardingProgress(BaseUser):
    """User onboarding progress tracking"""
    __tablename__ = "user_onboarding_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    step_name = Column(String, nullable=False)
    completed_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="onboarding_progress")

    __table_args__ = (
        # Composite indexes for queries
        Index('ix_onboarding_user_step', 'user_id', 'step_name'),
        Index('ix_onboarding_user_completed', 'user_id', 'completed_at'),
        
        # Single column indexes
        Index('ix_onboarding_step', 'step_name'),
        Index('ix_onboarding_completed_at', 'completed_at'),
    )

    def __repr__(self):
        return f"UserOnboardingProgress(user_id={self.user_id}, step={self.step_name}, completed_at={self.completed_at})"