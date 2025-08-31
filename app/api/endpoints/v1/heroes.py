import logging
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.responses import response
from app.db.db_sessions import get_users_db
from app.schemas.hero import HeroCreate, HeroUpdate, HeroOut
from app.schemas.response import BaseResponse, DataResponse
from app.services.authentication import get_current_user
from app.crud.hero import hero_crud
from app.db.models.user import User

router = APIRouter(prefix="/heroes", tags=["heroes"])

logger = logging.getLogger(__name__)


@router.post("/", response_model=DataResponse)
async def create_hero(
    hero_data: HeroCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Create a new hero for the current user"""
    logger.info(f"Received hero data: {hero_data}")
    try:
        logger.info(f"Creating hero for user {current_user.id}: {hero_data.name}")
        
        db_hero = hero_crud.create(db, hero_data, current_user.id)
        hero_out = HeroOut.model_validate(db_hero)
        
        logger.info(f"Hero created successfully with ID: {db_hero.id}")
        
        return response(
            message="Hero created successfully",
            data=hero_out.model_dump(mode='json'),
            status_code=201,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error creating hero for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create hero")


@router.get("/", response_model=DataResponse)
async def get_user_heroes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Get all heroes for current user"""
    try:
        logger.info(f"Getting all heroes for user {current_user.id}")
        
        heroes = hero_crud.get_user_heroes(db, current_user.id)
        heroes_data = [HeroOut.model_validate(hero).model_dump(mode='json') for hero in heroes]
        
        logger.info(f"Retrieved {len(heroes_data)} heroes")
        
        return response(
            message=f"Retrieved {len(heroes_data)} heroes",
            data={"heroes": heroes_data},
            status_code=200,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error getting heroes for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve heroes")


@router.put("/{hero_id}/", response_model=DataResponse)
async def update_hero(
    hero_id: UUID,
    hero_data: HeroUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Update a hero"""
    try:
        logger.info(f"Updating hero {hero_id} for user {current_user.id}")
        
        updated_hero = hero_crud.update(db, hero_id, hero_data, current_user.id)
        if not updated_hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        
        hero_out = HeroOut.model_validate(updated_hero)
        
        logger.info(f"Hero {hero_id} updated successfully")
        
        return response(
            message="Hero updated successfully",
            data=hero_out.model_dump(mode='json'),
            status_code=200,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating hero {hero_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update hero")


@router.delete("/{hero_id}/", response_model=BaseResponse)
async def delete_hero(
    hero_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Delete a hero (soft delete)"""
    try:
        logger.info(f"Deleting hero {hero_id} for user {current_user.id}")
        
        deleted = hero_crud.delete(db, hero_id, current_user.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Hero not found")
        
        logger.info(f"Hero {hero_id} deleted successfully")
        
        return response(
            message="Hero deleted successfully",
            status_code=200,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting hero {hero_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete hero")