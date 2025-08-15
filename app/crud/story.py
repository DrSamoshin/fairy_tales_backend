from typing import List, Optional, Tuple, TYPE_CHECKING
from uuid import UUID
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import func, desc, select, and_
from app.db.models.story import Story
from app.schemas.story import StoryCreate

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
    
    def create(self, db: Session, story: StoryCreate, user_id: UUID) -> Story:
        db_story = Story(
            user_id=user_id,
            title=story.title,
            content=story.content,
            hero_name=story.hero_name,
            age=story.age,
            story_style=story.story_style,
            language=story.language,
            story_idea=story.story_idea
        )
        db.add(db_story)
        db.commit()
        db.refresh(db_story)
        return db_story
    
    def create_from_generation(
        self, 
        db: Session, 
        story_data: 'StoryGenerate', 
        generated_content: str, 
        user_id: UUID
    ) -> Story:
        """Create story from generation parameters and LLM content"""
        story_create = StoryCreate(
            title=story_data.story_name,
            content=generated_content,
            hero_name=story_data.hero_name,
            age=story_data.age,
            story_style=story_data.story_style.value,
            language=story_data.language.value,
            story_idea=story_data.story_idea
        )
        return self.create(db, story_create, user_id)
    

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


story_crud = StoryCRUD()
