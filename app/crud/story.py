import logging
from typing import List, Optional, Tuple, TYPE_CHECKING, AsyncGenerator, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import func, desc, select, and_
from app.db.models.story import Story
from app.schemas.story import StoryGenerateRequest, StoryOut
from app.services.story_generation import story_generation_service

if TYPE_CHECKING:
    from app.schemas.story import StoryGenerate


class StoryCRUD:
    def get_by_id(self, db: Session, story_id: UUID, user_id: UUID, with_user: bool = False) -> Optional[Story]:
        """Get story by ID with optional user eager loading"""
        query = db.query(Story).filter(
            and_(
                Story.id == story_id,
                Story.user_id == user_id,
                Story.is_deleted == False
            )
        )
        
        if with_user:
            query = query.options(joinedload(Story.user))
        
        return query.first()
    
    def get_user_stories(
        self, 
        db: Session, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        with_user: bool = False
    ) -> Tuple[List[Story], int]:
        """Get user stories with optimized counting and optional eager loading"""
        # Optimized count query - uses index
        count_query = select(func.count(Story.id)).where(
            and_(
                Story.user_id == user_id,
                Story.is_deleted == False
            )
        )
        total = db.execute(count_query).scalar()
        
        # Main query with optimization
        query = db.query(Story).filter(
            and_(
                Story.user_id == user_id,
                Story.is_deleted == False
            )
        ).order_by(desc(Story.created_at))
        
        if with_user:
            query = query.options(joinedload(Story.user))
        
        stories = query.offset(skip).limit(limit).all()
        
        return stories, total
    

    
    def create_from_generation(
        self, 
        db: Session, 
        story_data: StoryGenerateRequest, 
        generated_content: str, 
        user_id: UUID
    ) -> Story:
        """Create story from client parameters + AI generated content"""
        # AI только добавляет content, все остальное от клиента
        db_story = Story(
            user_id=user_id,
            title=story_data.story_name,
            content=generated_content,  # ✅ Единственное что добавляет AI
            hero_name=story_data.hero_name,
            age=story_data.age,
            story_style=story_data.story_style.value,
            language=story_data.language.value,
            story_idea=story_data.story_idea,
            story_length=story_data.story_length.value,
            child_gender=story_data.child_gender.value
            # id, created_at, is_deleted - автоматически из модели
        )
        db.add(db_story)
        db.commit()
        db.refresh(db_story)
        return db_story
    
    async def generate_story_complete(
        self, 
        db: Session, 
        story_data: StoryGenerateRequest, 
        user_id: UUID
    ) -> Story:
        """Generate complete story and save to database"""
        logging.info(f"Generating complete story for user: {user_id}")
        logging.info(f"Story details: {story_data.story_name}, Hero: {story_data.hero_name}, Age: {story_data.age}, Style: {story_data.story_style}")
        
        try:
            # Generate story content using service
            generated_content = await story_generation_service.generate_story(story_data)
            
            # Create and save story
            story = self.create_from_generation(db, story_data, generated_content, user_id)
            
            logging.info(f"Story generated and saved: {story.id}")
            return story
            
        except Exception as e:
            logging.error(f"Story generation/save failed for user {user_id}: {str(e)}")
            raise Exception(f"Failed to generate story: {str(e)}")
    
    async def generate_story_stream(
        self, 
        db: Session, 
        story_data: StoryGenerateRequest, 
        user_id: UUID
    ) -> AsyncGenerator[dict, None]:
        """Generate story with streaming and save when complete"""
        logging.info(f"Starting streaming generation for user: {user_id}")
        logging.info(f"Story details: {story_data.story_name}, Hero: {story_data.hero_name}")
        
        full_story_content = ""
        story_saved = False
        
        try:
            # Send initial message
            yield {
                "type": "started",
                "message": f"Starting generation of '{story_data.story_name}'"
            }
            
            # Generate story with streaming
            async for chunk in story_generation_service.generate_story_stream(story_data):
                # Accumulate full story content
                full_story_content += chunk
                
                # Yield chunk to client
                yield {
                    "type": "content",
                    "data": chunk
                }
            
            # Story generation completed - save to database
            if full_story_content:
                logging.info(f"Saving completed story to database for user: {user_id}")
                
                # Save to database
                saved_story = self.create_from_generation(db, story_data, full_story_content, user_id)
                story_saved = True
                
                # Send completion message with story ID
                yield {
                    "type": "completed",
                    "story_id": str(saved_story.id),
                    "message": "Story generated and saved successfully",
                    "story_length": len(full_story_content)
                }
                
                logging.info(f"Story saved successfully with ID: {saved_story.id}")
            
        except Exception as e:
            logging.error(f"Error during streaming generation: {str(e)}")
            
            # Send error message
            yield {
                "type": "error",
                "message": f"Generation failed: {str(e)}"
            }
        
        finally:
            # Log completion status
            if story_saved:
                logging.info(f"Streaming generation completed and saved for user: {user_id}")
            else:
                logging.info(f"Streaming generation completed but not saved for user: {user_id}")
    

    def delete(self, db: Session, story_id: UUID, user_id: UUID) -> bool:
        db_story = self.get_by_id(db, story_id, user_id)
        if not db_story:
            return False
        
        db_story.is_deleted = True
        db.commit()
        return True
    
    def get_user_stories_count(self, db: Session, user_id: UUID) -> int:
        """Optimized count query using index"""
        count_query = select(func.count(Story.id)).where(
            and_(
                Story.user_id == user_id,
                Story.is_deleted == False
            )
        )
        return db.execute(count_query).scalar() or 0
    
    def get_all_stories(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        with_user: bool = True
    ) -> Tuple[List[Story], int]:
        """Get all stories in the system (admin only) with optimized queries"""
        # Optimized count query
        count_query = select(func.count(Story.id)).where(Story.is_deleted == False)
        total = db.execute(count_query).scalar()
        
        # Main query with eager loading for admin view
        query = db.query(Story).filter(Story.is_deleted == False)
        
        if with_user:
            query = query.options(joinedload(Story.user))
        
        stories = query.order_by(desc(Story.created_at)).offset(skip).limit(limit).all()
        
        return stories, total
    
    def get_stories_by_filters(
        self,
        db: Session,
        user_id: Optional[UUID] = None,
        language: Optional[str] = None,
        story_style: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Story], int]:
        """Get stories with advanced filtering"""
        conditions = [Story.is_deleted == False]
        
        if user_id:
            conditions.append(Story.user_id == user_id)
        if language:
            conditions.append(Story.language == language)
        if story_style:
            conditions.append(Story.story_style == story_style)
        if age_min:
            conditions.append(Story.age >= age_min)
        if age_max:
            conditions.append(Story.age <= age_max)
        
        # Count query
        count_query = select(func.count(Story.id)).where(and_(*conditions))
        total = db.execute(count_query).scalar()
        
        # Main query
        query = db.query(Story).filter(and_(*conditions)).order_by(desc(Story.created_at))
        stories = query.offset(skip).limit(limit).all()
        
        return stories, total
    
    def get_stories_for_admin(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get all stories for admin with structured response.
        
        Args:
            db: Database session
            skip: Number of stories to skip
            limit: Maximum number of stories to return
            
        Returns:
            Dict with success status, message, and structured data
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Admin requesting all stories with skip={skip}, limit={limit}")
        
        try:
            # Get stories from database
            stories, total = self.get_all_stories(db, skip=skip, limit=limit)
            
            # Convert stories to StoryOut format
            stories_data = [StoryOut.model_validate(story).model_dump(mode='json') for story in stories]
            
            logger.info(f"Retrieved {len(stories_data)} stories out of {total} total")
            
            return {
                "success": True,
                "message": f"Retrieved {len(stories_data)} stories",
                "data": {
                    "stories": stories_data,
                    "pagination": {
                        "skip": skip,
                        "limit": limit,
                        "count": len(stories_data),
                        "total": total
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting stories for admin: {str(e)}")
            return {
                "success": False,
                "message": "Internal server error",
                "status_code": 500,
                "errors": ["Failed to retrieve stories"],
                "error_code": "INTERNAL_ERROR"
            }


story_crud = StoryCRUD()
