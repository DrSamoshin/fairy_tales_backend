from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.models.story import Story
from app.schemas.story import StoryCreate, StoryUpdate


class StoryCRUD:
    def get_by_id(self, db: Session, story_id: UUID, user_id: UUID) -> Optional[Story]:
        return db.query(Story).filter(
            Story.id == story_id,
            Story.user_id == user_id,
            Story.is_deleted == False
        ).first()
    
    def get_user_stories(
        self, 
        db: Session, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[Story], int]:
        query = db.query(Story).filter(
            Story.user_id == user_id,
            Story.is_deleted == False
        )
        
        total = query.count()
        stories = query.order_by(desc(Story.created_at)).offset(skip).limit(limit).all()
        
        return stories, total
    
    def create(self, db: Session, story: StoryCreate, user_id: UUID) -> Story:
        db_story = Story(
            user_id=user_id,
            title=story.title,
            content=story.content,
            prompt=story.prompt
        )
        db.add(db_story)
        db.commit()
        db.refresh(db_story)
        return db_story
    
    def update(
        self, 
        db: Session, 
        story_id: UUID, 
        user_id: UUID, 
        story_update: StoryUpdate
    ) -> Optional[Story]:
        db_story = self.get_by_id(db, story_id, user_id)
        if not db_story:
            return None
        
        update_data = story_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_story, field, value)
        
        db.commit()
        db.refresh(db_story)
        return db_story
    
    def delete(self, db: Session, story_id: UUID, user_id: UUID) -> bool:
        db_story = self.get_by_id(db, story_id, user_id)
        if not db_story:
            return False
        
        db_story.is_deleted = True
        db.commit()
        return True
    
    def get_user_stories_count(self, db: Session, user_id: UUID) -> int:
        return db.query(func.count(Story.id)).filter(
            Story.user_id == user_id,
            Story.is_deleted == False
        ).scalar() or 0


story_crud = StoryCRUD()
