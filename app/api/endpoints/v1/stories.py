import logging
import json
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.responses import response
from app.core import error_codes
from app.services.story_generation import story_generation_service
from app.db.db_sessions import get_users_db
from app.schemas.story import (
    StoryGenerate, StoryCreate, StoryOut
)
from app.schemas.response import StoryResponse, StoriesListResponse, BaseResponse
from app.crud.story import story_crud
from app.services.authentication import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("/generate/", response_model=StoryResponse)
async def generate_story(
    story_data: StoryGenerate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Generate a new fairy tale story based on detailed parameters"""
    logging.info(f"Generating story for user: {current_user.id}")
    logging.info(f"Story details: {story_data.story_name}, Hero: {story_data.hero_name}, Age: {story_data.age}, Style: {story_data.story_style}")
    
    try:
        # Call LLM service to generate story content
        generated_content = await story_generation_service.generate_story(story_data)
        
        # Create and save story using CRUD
        story = story_crud.create_from_generation(db, story_data, generated_content, current_user.id)
        
        logging.info(f"Story generated and saved: {story.id}")
        return response(
            message="Story generated successfully",
            data={"story": StoryOut.model_validate(story).model_dump(mode='json')}
        )
        
    except Exception as e:
        logging.error(f"Story generation/save failed for user {current_user.id}: {str(e)}")
        return response(
            message="Story generation failed",
            status_code=500,
            success=False,
            errors=["Failed to generate or save story"],
            error_code=error_codes.STORY_GENERATION_FAILED
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
    
    # Return full StoryOut objects instead of StoryList
    stories_full = [StoryOut.model_validate(story).model_dump(mode='json') for story in stories]
    
    return response(
        message="Stories retrieved successfully",
        data={
            "stories": stories_full,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{story_id}/", response_model=StoryResponse)
async def get_story(
    story_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Get specific story by ID"""
    logging.info(f"Getting story {story_id} for user: {current_user.id}")
    
    story = story_crud.get_by_id(db, story_id, current_user.id)
    if not story:
        return response(
            message="Story not found",
            status_code=404,
            success=False,
            errors=["Story does not exist or you don't have permission to view it"],
            error_code=error_codes.STORY_NOT_FOUND
        )
    
    return response(
        message="Story retrieved successfully",
        data={"story": StoryOut.model_validate(story).model_dump(mode='json')}
    )



@router.delete("/{story_id}/", response_model=BaseResponse)
async def delete_story(
    story_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Delete story (soft delete)"""
    logging.info(f"Deleting story {story_id} for user: {current_user.id}")
    
    success = story_crud.delete(db, story_id, current_user.id)
    if not success:
        return response(
            message="Story not found",
            status_code=404,
            success=False,
            errors=["Story does not exist or you don't have permission to delete it"],
            error_code=error_codes.STORY_NOT_FOUND
        )
    
    return response(
        message="Story deleted successfully",
        data=None
    )


@router.post("/generate-stream/")
async def generate_story_stream(
    story_data: StoryGenerate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Generate a new fairy tale story with streaming response"""
    logging.info(f"Starting streaming generation for user: {current_user.id}")
    logging.info(f"Story details: {story_data.story_name}, Hero: {story_data.hero_name}")
    
    async def story_stream_generator():
        full_story_content = ""
        story_saved = False
        
        try:
            # Send initial message
            initial_message = {
                "type": "started",
                "message": f"Starting generation of '{story_data.story_name}'"
            }
            yield f"data: {json.dumps(initial_message)}\n\n"
            
            # Generate story with streaming
            async for chunk in story_generation_service.generate_story_stream(story_data):
                # Check if client disconnected
                if await request.is_disconnected():
                    logging.info(f"Client disconnected during streaming for user: {current_user.id}")
                    return
                
                # Accumulate full story content
                full_story_content += chunk
                
                # Send chunk to client
                chunk_message = {
                    "type": "content",
                    "data": chunk
                }
                yield f"data: {json.dumps(chunk_message)}\n\n"
            
            # Story generation completed - save to database
            if full_story_content and not await request.is_disconnected():
                logging.info(f"Saving completed story to database for user: {current_user.id}")
                
                # Create story object for saving
                story_create = StoryCreate(
                    story_name=story_data.story_name,
                    hero_name=story_data.hero_name,
                    story_idea=story_data.story_idea,
                    story_style=story_data.story_style,
                    language=story_data.language,
                    age=story_data.age,
                    story_content=full_story_content
                )
                
                # Save to database
                saved_story = story_crud.create(db, story_create, current_user.id)
                story_saved = True
                
                # Send completion message with story ID
                completion_message = {
                    "type": "completed",
                    "story_id": str(saved_story.id),
                    "message": "Story generated and saved successfully",
                    "story_length": len(full_story_content)
                }
                yield f"data: {json.dumps(completion_message)}\n\n"
                
                logging.info(f"Story saved successfully with ID: {saved_story.id}")
            
        except Exception as e:
            logging.error(f"Error during streaming generation: {str(e)}")
            
            # Send error message
            error_message = {
                "type": "error",
                "message": f"Generation failed: {str(e)}"
            }
            yield f"data: {json.dumps(error_message)}\n\n"
        
        finally:
            # Log completion status
            if story_saved:
                logging.info(f"Streaming generation completed and saved for user: {current_user.id}")
            else:
                logging.info(f"Streaming generation completed but not saved for user: {current_user.id}")
    
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
