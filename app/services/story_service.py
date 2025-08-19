import logging
import json
from typing import Dict, Any, AsyncGenerator
from uuid import UUID
from sqlalchemy.orm import Session

from app.schemas.story import StoryGenerateRequest, StoryOut
from app.crud.story import story_crud
from app.core import error_codes


class StoryService:
    """Service for handling story business logic"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def generate_story(
        self, 
        db: Session, 
        story_data: StoryGenerateRequest, 
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate a complete story and save to database.
        
        Args:
            db: Database session
            story_data: Story generation request data
            user_id: ID of the user generating the story
            
        Returns:
            Dict with success status, message, and story data
        """
        self.logger.info(f"Story generation request from user: {user_id}")
        
        try:
            # Use CRUD method for complete story generation
            story = await story_crud.generate_story_complete(db, story_data, user_id)
            
            # Format response data
            story_data = StoryOut.model_validate(story).model_dump(mode='json')
            
            self.logger.info(f"Story generated successfully: {story.id}")
            
            return {
                "success": True,
                "message": "Story generated successfully",
                "data": {"story": story_data}
            }
            
        except Exception as e:
            self.logger.error(f"Story generation failed for user {user_id}: {str(e)}")
            return {
                "success": False,
                "message": "Story generation failed",
                "status_code": 500,
                "errors": ["Failed to generate or save story"],
                "error_code": error_codes.STORY_GENERATION_FAILED
            }
    
    async def generate_story_stream(
        self, 
        db: Session, 
        story_data: StoryGenerateRequest, 
        user_id: UUID
    ) -> AsyncGenerator[str, None]:
        """
        Generate story with streaming response in SSE format.
        
        Args:
            db: Database session
            story_data: Story generation request data
            user_id: ID of the user generating the story
            
        Yields:
            SSE formatted messages
        """
        self.logger.info(f"Streaming story generation request from user: {user_id}")
        
        try:
            # Use CRUD method for streaming generation
            async for message in story_crud.generate_story_stream(db, story_data, user_id):
                # Send message to client in SSE format
                yield f"data: {json.dumps(message)}\n\n"
                
        except Exception as e:
            self.logger.error(f"Error during streaming generation: {str(e)}")
            
            # Send error message
            error_message = {
                "type": "error",
                "message": f"Generation failed: {str(e)}"
            }
            yield f"data: {json.dumps(error_message)}\n\n"
    
    def get_user_stories(
        self, 
        db: Session, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get user's stories with structured response.
        
        Args:
            db: Database session
            user_id: ID of the user
            skip: Number of stories to skip
            limit: Maximum number of stories to return
            
        Returns:
            Dict with success status, message, and stories data
        """
        self.logger.info(f"Getting stories for user: {user_id}")
        
        try:
            stories, total = story_crud.get_user_stories(db, user_id, skip, limit)
            
            # Convert stories to StoryOut format
            stories_data = [StoryOut.model_validate(story).model_dump(mode='json') for story in stories]
            
            self.logger.info(f"Retrieved {len(stories_data)} stories for user: {user_id}")
            
            return {
                "success": True,
                "message": "Stories retrieved successfully",
                "data": {
                    "stories": stories_data,
                    "total": total,
                    "skip": skip,
                    "limit": limit
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting stories for user {user_id}: {str(e)}")
            return {
                "success": False,
                "message": "Failed to retrieve stories",
                "status_code": 500,
                "errors": ["Internal server error"],
                "error_code": error_codes.INTERNAL_ERROR
            }
    
    def delete_story(
        self, 
        db: Session, 
        story_id: UUID, 
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Delete user's story (soft delete).
        
        Args:
            db: Database session
            story_id: ID of the story to delete
            user_id: ID of the user (owner verification)
            
        Returns:
            Dict with success status and message
        """
        self.logger.info(f"Deleting story {story_id} for user: {user_id}")
        
        try:
            success = story_crud.delete(db, story_id, user_id)
            
            if not success:
                self.logger.warning(f"Story not found or access denied: {story_id} for user: {user_id}")
                return {
                    "success": False,
                    "message": "Story not found",
                    "status_code": 404,
                    "errors": ["Story does not exist or you don't have permission to delete it"],
                    "error_code": error_codes.STORY_NOT_FOUND
                }
            
            self.logger.info(f"Story deleted successfully: {story_id}")
            
            return {
                "success": True,
                "message": "Story deleted successfully",
                "data": None
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting story {story_id} for user {user_id}: {str(e)}")
            return {
                "success": False,
                "message": "Failed to delete story",
                "status_code": 500,
                "errors": ["Internal server error"],
                "error_code": error_codes.INTERNAL_ERROR
            }


# Create service instance
story_service = StoryService()
