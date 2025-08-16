import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.responses import response
from app.db.db_sessions import get_users_db
from app.schemas.story import StoryGenerateRequest
from app.schemas.response import StoryResponse, StoriesListResponse, BaseResponse
from app.services.authentication import get_current_user
from app.services.story_service import story_service
from app.db.models.user import User

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("/generate/", response_model=StoryResponse)
async def generate_story(
    story_data: StoryGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Generate a new fairy tale story based on detailed parameters"""
    result = await story_service.generate_story(db, story_data, current_user.id)
    
    return response(
        message=result["message"],
        data=result.get("data"),
        status_code=result.get("status_code", 200),
        success=result["success"],
        errors=result.get("errors"),
        error_code=result.get("error_code")
    )


@router.get("/", response_model=StoriesListResponse)
async def get_user_stories(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Get all stories for current user"""
    result = story_service.get_user_stories(db, current_user.id, skip, limit)
    
    return response(
        message=result["message"],
        data=result.get("data"),
        status_code=result.get("status_code", 200),
        success=result["success"],
        errors=result.get("errors"),
        error_code=result.get("error_code")
    )


@router.delete("/{story_id}/", response_model=BaseResponse)
async def delete_story(
    story_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Delete story (soft delete)"""
    result = story_service.delete_story(db, story_id, current_user.id)
    
    return response(
        message=result["message"],
        data=result.get("data"),
        status_code=result.get("status_code", 200),
        success=result["success"],
        errors=result.get("errors"),
        error_code=result.get("error_code")
    )


@router.post("/generate-stream/")
async def generate_story_stream(
    story_data: StoryGenerateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Generate a new fairy tale story with streaming response"""
    async def story_stream_generator():
        # Check if client disconnected
        if await request.is_disconnected():
            logging.info(f"Client disconnected during streaming for user: {current_user.id}")
            return
        
        # Use service for streaming generation with SSE formatting
        async for sse_message in story_service.generate_story_stream(db, story_data, current_user.id):
            yield sse_message
    
    # Return streaming response
    return StreamingResponse(
        story_stream_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
