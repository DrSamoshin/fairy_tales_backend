from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.db.db_sessions import get_db
from app.crud import user_onboarding
from app.schemas.user_onboarding import OnboardingStepOut, OnboardingStepUpdate, OnboardingProgressOut
from app.schemas.response import OnboardingProgressResponse, OnboardingStepResponse
from app.core.responses import response
from app.services.authentication import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/progress", response_model=OnboardingProgressResponse)
async def get_user_onboarding_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's onboarding progress"""
    steps = user_onboarding.get_user_onboarding_progress(db, current_user.id)
    
    progress = OnboardingProgressOut(
        user_id=current_user.id,
        steps=[OnboardingStepOut.model_validate(step) for step in steps]
    )
    
    return response(data=progress.model_dump(mode='json'))


@router.post("/step", response_model=OnboardingStepResponse)
async def update_onboarding_step(
    step_data: OnboardingStepUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update or create onboarding step"""
    step = user_onboarding.update_onboarding_step(
        db=db,
        user_id=current_user.id,
        step_name=step_data.step_name,
        completed_at=step_data.completed_at
    )
    
    return response(data=step.model_dump(mode='json'))