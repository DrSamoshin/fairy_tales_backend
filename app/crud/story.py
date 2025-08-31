import logging
from typing import List, Optional, AsyncGenerator
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_
from app.db.models.story import Story
from app.db.models.story_hero import StoryHero
from app.schemas.story import StoryGenerateWithHeroesRequest, StoryOut, StoryListItem
from app.services.story_generation import story_generation_service


class StoryCRUD:
    def get_by_id(self, db: Session, story_id: UUID, user_id: UUID) -> Optional[Story]:
        """Get story by ID"""
        return db.query(Story).filter(
            and_(
                Story.id == story_id,
                Story.user_id == user_id,
                Story.is_deleted == False
            )
        ).options(
            joinedload(Story.story_heroes).joinedload(StoryHero.hero)
        ).first()
    
    def get_user_stories(self, db: Session, user_id: UUID) -> List[Story]:
        """Get all user stories with heroes eager loading"""
        return db.query(Story).filter(
            and_(
                Story.user_id == user_id,
                Story.is_deleted == False
            )
        ).options(
            joinedload(Story.story_heroes).joinedload(StoryHero.hero)
        ).order_by(desc(Story.created_at)).all()
    
    def convert_to_story_out(self, story: Story) -> StoryOut:
        """Convert Story model to StoryOut schema"""
        hero_names = [sh.hero.name for sh in story.story_heroes if sh.hero and not sh.hero.is_deleted]
        
        return StoryOut(
            id=story.id,
            user_id=story.user_id,
            title=story.title,
            content=story.content,
            story_style=story.story_style,
            language=story.language,
            story_idea=story.story_idea,
            story_length=story.story_length,
            created_at=story.created_at,
            hero_names=hero_names if hero_names else None
        )
    
    def convert_to_list_item(self, story: Story) -> StoryListItem:
        """Convert Story model to StoryListItem schema"""
        hero_names = [sh.hero.name for sh in story.story_heroes if sh.hero and not sh.hero.is_deleted]
        
        return StoryListItem(
            id=story.id,
            user_id=story.user_id,
            title=story.title,
            story_style=story.story_style,
            language=story.language,
            story_idea=story.story_idea,
            created_at=story.created_at,
            hero_names=hero_names if hero_names else None
        )
    
    def create_from_heroes_generation(
        self, 
        db: Session, 
        story_data: StoryGenerateWithHeroesRequest, 
        generated_content: str, 
        user_id: UUID
    ) -> Story:
        """Create story from heroes parameters + AI generated content"""
        # Create story
        db_story = Story(
            user_id=user_id,
            title=story_data.story_name,
            content=generated_content,
            story_style=story_data.story_style.value,
            language=story_data.language.value,
            story_idea=story_data.story_idea,
            story_length=story_data.story_length.value
        )
        db.add(db_story)
        db.commit()
        db.refresh(db_story)
        
        # Create story-hero relationships
        for hero in story_data.heroes:
            story_hero = StoryHero(
                story_id=db_story.id,
                hero_id=hero.id
            )
            db.add(story_hero)
        
        db.commit()
        db.refresh(db_story)
        return db_story

    async def generate_story_with_heroes_stream(
        self, 
        db: Session, 
        story_data: StoryGenerateWithHeroesRequest, 
        user_id: UUID
    ) -> AsyncGenerator[dict, None]:
        """Generate story with heroes using streaming and save when complete"""
        logging.info(f"Starting streaming generation with heroes for user: {user_id}")
        
        full_story_content = ""
        story_saved = False
        
        try:
            yield {
                "type": "started",
                "message": f"Starting generation of '{story_data.story_name}' with heroes"
            }
            
            async for chunk in story_generation_service.generate_story_with_heroes_stream(story_data):
                full_story_content += chunk
                yield {
                    "type": "content",
                    "data": chunk
                }
            
            if full_story_content:
                logging.info(f"Saving completed heroes story to database for user: {user_id}")
                saved_story = self.create_from_heroes_generation(db, story_data, full_story_content, user_id)
                story_saved = True
                
                yield {
                    "type": "completed",
                    "story_id": str(saved_story.id),
                    "message": "Story with heroes generated and saved successfully",
                    "story_length": len(full_story_content)
                }
                
        except Exception as e:
            logging.error(f"Error during heroes streaming generation: {str(e)}")
            yield {
                "type": "error",
                "message": f"Heroes generation failed: {str(e)}"
            }
        
        finally:
            if story_saved:
                logging.info(f"Heroes streaming completed and saved for user: {user_id}")
            else:
                logging.info(f"Heroes streaming completed but not saved for user: {user_id}")

    def delete(self, db: Session, story_id: UUID, user_id: UUID) -> bool:
        """Soft delete story"""
        db_story = self.get_by_id(db, story_id, user_id)
        if not db_story:
            return False
        
        db_story.is_deleted = True
        db.commit()
        return True

    def get_stories_for_admin(self, db: Session) -> dict:
        """Get all stories for admin"""
        try:
            stories = db.query(Story).filter(Story.is_deleted == False).options(
                joinedload(Story.story_heroes).joinedload(StoryHero.hero)
            ).order_by(desc(Story.created_at)).all()
            
            stories_data = [self.convert_to_list_item(story).model_dump() for story in stories]
            
            return {
                "success": True,
                "message": f"Retrieved {len(stories_data)} stories",
                "data": {"stories": stories_data}
            }
        except Exception as e:
            logging.error(f"Error getting stories for admin: {str(e)}")
            return {
                "success": False,
                "message": "Failed to retrieve stories",
                "status_code": 500,
                "errors": ["Internal server error"]
            }


story_crud = StoryCRUD()