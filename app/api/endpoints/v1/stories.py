import logging
import json
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.responses import response
from app.db.db_sessions import get_users_db
from app.schemas.story import StoryGenerateWithHeroesRequest
from app.schemas.response import StoriesListResponse, BaseResponse
from app.services.authentication import get_current_user
from app.crud.story import story_crud
from app.db.models.user import User

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("/", response_model=StoriesListResponse)
async def get_user_stories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Get all stories for current user"""
    try:
        stories = story_crud.get_user_stories(db, current_user.id)
        stories_data = [story_crud.convert_to_list_item(story).model_dump(mode='json') for story in stories]
        
        return response(
            message="Stories retrieved successfully",
            data={"stories": stories_data},
            status_code=200,
            success=True
        )
    except Exception as e:
        logging.error(f"Error getting stories for user {current_user.id}: {str(e)}")
        return response(
            message="Failed to retrieve stories",
            status_code=500,
            success=False
        )


@router.get("/{story_id}/")
async def get_story_by_id(
    story_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Get specific story by ID"""
    
    story = story_crud.get_by_id(db, story_id, current_user.id)
    if not story:
        return response(
            message="Story not found",
            status_code=404,
            success=False
        )
    
    story_schema = story_crud.convert_to_story_out(story)
    
    return response(
        message="Story retrieved successfully",
        data={"story": story_schema.model_dump(mode='json')},
        status_code=200,
        success=True
    )


@router.delete("/{story_id}/", response_model=BaseResponse)
async def delete_story(
    story_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Delete story (soft delete)"""
    try:
        success = story_crud.delete(db, story_id, current_user.id)
        
        if not success:
            return response(
                message="Story not found",
                status_code=404,
                success=False
            )
        
        return response(
            message="Story deleted successfully",
            status_code=200,
            success=True
        )
    except Exception as e:
        logging.error(f"Error deleting story {story_id} for user {current_user.id}: {str(e)}")
        return response(
            message="Failed to delete story",
            status_code=500,
            success=False
        )


@router.post("/generate-with-heroes-stream/")
async def generate_story_with_heroes_stream(
    story_data: StoryGenerateWithHeroesRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """Generate a new fairy tale story with multiple heroes using streaming response"""
    logging.info(f"Starting heroes streaming endpoint for user: {current_user.id}")
    logging.info(f"Raw request type: {type(story_data)}")
    logging.info(f"Request data: {story_data}")
    logging.info(f"Story name: {story_data.story_name}, heroes count: {len(story_data.heroes)}")
    
    # Log each hero
    for i, hero in enumerate(story_data.heroes):
        logging.info(f"Hero {i+1}: {hero.name} (ID: {hero.id})")
    
    async def story_heroes_stream_generator():
        # Check if client disconnected
        if await request.is_disconnected():
            logging.info(f"Client disconnected before starting heroes streaming for user: {current_user.id}")
            return
        
        logging.info(f"Starting stream generator for heroes story...")
        
        try:
            # Use story CRUD for streaming generation
            async for message in story_crud.generate_story_with_heroes_stream(db, story_data, current_user.id):
                if await request.is_disconnected():
                    logging.info(f"Client disconnected during heroes streaming for user: {current_user.id}")
                    return
                yield f"data: {json.dumps(message)}\n\n"
                
        except Exception as e:
            logging.error(f"Error in heroes streaming generation for user {current_user.id}: {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            import traceback
            logging.error(f"Full traceback: {traceback.format_exc()}")
            error_message = {
                "type": "error",
                "message": f"Heroes generation failed: {str(e)}"
            }
            yield f"data: {json.dumps(error_message)}\n\n"
    
    # Return streaming response
    logging.info(f"Returning StreamingResponse for heroes story...")
    return StreamingResponse(
        story_heroes_stream_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
