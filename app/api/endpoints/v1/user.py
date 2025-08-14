import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.responses import response
from app.core import error_codes
from app.db.db_sessions import get_users_db
from app.schemas.user import UserUpdate, UserProfile
from app.schemas.response import UserProfileResponse
from app.crud.user import user_crud
from app.services.authentication import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Get current user profile with stories count"""
    logging.info(f"Getting profile for user: {current_user.id}")
    
    stories_count = user_crud.get_stories_count(db, current_user.id)
    
    profile_data = UserProfile.model_validate(current_user)
    profile_data.stories_count = stories_count
    
    return response(
        message="Profile retrieved successfully", 
        data={"profile": profile_data.model_dump(mode='json')}
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Update current user profile"""
    logging.info(f"Updating profile for user: {current_user.id}")
    
    updated_user = user_crud.update(db, current_user.id, user_update)
    if not updated_user:
        return response(
            message="Failed to update profile",
            status_code=500,
            success=False,
            errors=["Profile update failed"],
            error_code=error_codes.INTERNAL_ERROR
        )
    
    return response(
        message="Profile updated successfully",
        data={"user": UserProfile.model_validate(updated_user).model_dump(mode='json')}
    )
