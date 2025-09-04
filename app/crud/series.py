from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.db.models.series import Series
from app.crud import user_onboarding
from app.core.consts import OnboardingStep


class SeriesCRUD:
    def create(self, db: Session, title: str, description: Optional[str], user_id: UUID) -> Series:
        """Create a new series"""
        db_series = Series(
            user_id=user_id,
            title=title,
            description=description
        )
        db.add(db_series)
        db.commit()
        db.refresh(db_series)
        
        # Check if this is user's first series and create onboarding step
        existing_step = user_onboarding.get_onboarding_step(
            db, user_id, OnboardingStep.FIRST_SERIES_CREATED
        )
        if not existing_step:
            user_onboarding.create_onboarding_step(
                db=db,
                user_id=user_id,
                step_name=OnboardingStep.FIRST_SERIES_CREATED
            )
        
        return db_series
    
    def get_by_id(self, db: Session, series_id: UUID, user_id: UUID) -> Optional[Series]:
        """Get series by ID"""
        return db.query(Series).filter(
            and_(
                Series.id == series_id,
                Series.user_id == user_id,
                Series.is_deleted == False
            )
        ).first()
    
    def get_user_series(self, db: Session, user_id: UUID) -> List[Series]:
        """Get all user series"""
        return db.query(Series).filter(
            and_(
                Series.user_id == user_id,
                Series.is_deleted == False
            )
        ).order_by(desc(Series.created_at)).all()
    
    def update(self, db: Session, series_id: UUID, title: Optional[str], description: Optional[str], user_id: UUID) -> Optional[Series]:
        """Update series"""
        db_series = self.get_by_id(db, series_id, user_id)
        if not db_series:
            return None
        
        if title is not None:
            db_series.title = title
        if description is not None:
            db_series.description = description
        
        db.commit()
        db.refresh(db_series)
        return db_series
    
    def delete(self, db: Session, series_id: UUID, user_id: UUID) -> bool:
        """Soft delete series"""
        db_series = self.get_by_id(db, series_id, user_id)
        if not db_series:
            return False
        
        db_series.is_deleted = True
        db.commit()
        return True


series_crud = SeriesCRUD()