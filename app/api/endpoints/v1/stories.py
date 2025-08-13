import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.responses import response
from app.db.db_sessions import get_users_db
from app.schemas.story import (
    StoryGenerate, StoryCreate, StoryUpdate, StoryOut, 
    StoryList, StoriesResponse
)
from app.schemas.response import StoryResponse, StoriesListResponse, BaseResponse
from app.crud.story import story_crud
from app.services.authentication import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("/generate", response_model=StoryResponse)
async def generate_story(
    story_data: StoryGenerate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Generate a new fairy tale story based on prompt"""
    logging.info(f"Generating story for user: {current_user.id}")
    
    # TODO: Implement AI story generation here
    # For now, return a placeholder response
    generated_content = f"Once upon a time, based on your prompt: '{story_data.prompt}', here would be a wonderful fairy tale..."
    
    # Create title if not provided
    title = story_data.title or f"Story from {story_data.prompt[:30]}..."
    
    # Save the story
    story_create = StoryCreate(
        title=title,
        content=generated_content,
        prompt=story_data.prompt
    )
    
    story = story_crud.create(db, story_create, current_user.id)
    
    logging.info(f"Story generated and saved: {story.id}")
    return response(
        message="Story generated successfully",
        data={"story": StoryOut.model_validate(story)}
    )


@router.get("/", response_model=StoriesListResponse)
async def get_user_stories(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Get all stories for current user"""
    logging.info(f"Getting stories for user: {current_user.id}")
    
    stories, total = story_crud.get_user_stories(db, current_user.id, skip, limit)
    
    stories_list = [StoryList.model_validate(story) for story in stories]
    
    return response(
        message="Stories retrieved successfully",
        data=StoriesResponse(stories=stories_list, total=total)
    )


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Get specific story by ID"""
    logging.info(f"Getting story {story_id} for user: {current_user.id}")
    
    story = story_crud.get_by_id(db, story_id, current_user.id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    return response(
        message="Story retrieved successfully",
        data={"story": StoryOut.model_validate(story)}
    )


@router.put("/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: UUID,
    story_update: StoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Update story title"""
    logging.info(f"Updating story {story_id} for user: {current_user.id}")
    
    story = story_crud.update(db, story_id, current_user.id, story_update)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    return response(
        message="Story updated successfully",
        data={"story": StoryOut.model_validate(story)}
    )


@router.delete("/{story_id}", response_model=BaseResponse)
async def delete_story(
    story_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Delete story (soft delete)"""
    logging.info(f"Deleting story {story_id} for user: {current_user.id}")
    
    success = story_crud.delete(db, story_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    return response(message="Story deleted successfully")
