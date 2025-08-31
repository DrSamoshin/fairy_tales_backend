import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.db_sessions import get_users_db
from app.crud.user import user_crud
from app.crud.story import story_crud
from app.crud.hero import hero_crud
from app.schemas.response import UsersListResponse, StoriesListResponse, HeroesListResponse
from app.core.responses import response
from app.services.authentication import get_user_id_from_token
from uuid import UUID

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users/", response_model=UsersListResponse)
async def get_all_users(
    user_id: UUID = Depends(get_user_id_from_token),
    db: Session = Depends(get_users_db)
):
    """Get all users (authenticated admin only)"""
    result = user_crud.get_users_for_admin(db)
    
    return response(
        message=result["message"],
        data=result.get("data"),
        status_code=result.get("status_code", 200),
        success=result["success"],
        errors=result.get("errors"),
        error_code=result.get("error_code")
    )


@router.get("/stories/", response_model=StoriesListResponse)
async def get_all_stories(
    user_id: UUID = Depends(get_user_id_from_token),
    db: Session = Depends(get_users_db)
):
    """Get all stories in the system (authenticated admin only)"""
    result = story_crud.get_stories_for_admin(db)
    
    return response(
        message=result["message"],
        data=result.get("data"),
        status_code=result.get("status_code", 200),
        success=result["success"],
        errors=result.get("errors"),
        error_code=result.get("error_code")
    )


@router.get("/heroes/", response_model=HeroesListResponse)
async def get_all_heroes(
    user_id: UUID = Depends(get_user_id_from_token),
    db: Session = Depends(get_users_db)
):
    """Get all heroes in the system (authenticated admin only)"""
    result = hero_crud.get_heroes_for_admin(db)
    
    return response(
        message=result["message"],
        data=result.get("data"),
        status_code=result.get("status_code", 200),
        success=result["success"],
        errors=result.get("errors"),
        error_code=result.get("error_code")
    )

