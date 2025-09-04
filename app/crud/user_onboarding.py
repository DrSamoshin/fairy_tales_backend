from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.models.user_onboarding import UserOnboardingProgress
from datetime import datetime, timezone


def create_onboarding_step(
    db: Session, 
    user_id: UUID, 
    step_name: str,
    completed_at: Optional[datetime] = None
) -> UserOnboardingProgress:
    """Create new onboarding step record"""
    if completed_at is None:
        completed_at = datetime.now(timezone.utc)
    
    db_step = UserOnboardingProgress(
        user_id=user_id,
        step_name=step_name,
        completed_at=completed_at
    )
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    return db_step


def get_user_onboarding_progress(db: Session, user_id: UUID) -> List[UserOnboardingProgress]:
    """Get all onboarding progress for a user"""
    return db.query(UserOnboardingProgress).filter(
        UserOnboardingProgress.user_id == user_id
    ).order_by(UserOnboardingProgress.completed_at).all()


def get_onboarding_step(
    db: Session, 
    user_id: UUID, 
    step_name: str
) -> Optional[UserOnboardingProgress]:
    """Get specific onboarding step for user"""
    return db.query(UserOnboardingProgress).filter(
        UserOnboardingProgress.user_id == user_id,
        UserOnboardingProgress.step_name == step_name
    ).first()


def update_onboarding_step(
    db: Session,
    user_id: UUID,
    step_name: str,
    completed_at: datetime
) -> Optional[UserOnboardingProgress]:
    """Update existing onboarding step or create if doesn't exist"""
    existing = get_onboarding_step(db, user_id, step_name)
    
    if existing:
        existing.completed_at = completed_at
        db.commit()
        db.refresh(existing)
        return existing
    else:
        return create_onboarding_step(db, user_id, step_name, completed_at)


def delete_user_onboarding_progress(db: Session, user_id: UUID) -> bool:
    """Delete all onboarding progress for a user"""
    records_deleted = db.query(UserOnboardingProgress).filter(
        UserOnboardingProgress.user_id == user_id
    ).delete()
    db.commit()
    return records_deleted > 0