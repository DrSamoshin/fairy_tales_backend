from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import func, select, and_, desc
from app.db.models.user import User
from app.schemas.user import UserRegister, AppleSignIn, UserUpdate


class UserCRUD:
    def get_by_id(self, db: Session, user_id: UUID, with_stories: bool = False) -> Optional[User]:
        """Get user by ID with optional stories eager loading"""
        query = db.query(User).filter(
            and_(
                User.id == user_id, 
                User.is_active == True
            )
        )
        
        if with_stories:
            query = query.options(selectinload(User.stories))
        
        return query.first()
    
    def get_by_email(self, db: Session, email: str, with_stories: bool = False) -> Optional[User]:
        """Get user by email with optional stories eager loading"""
        query = db.query(User).filter(
            and_(
                User.email == email.lower(), 
                User.is_active == True
            )
        )
        
        if with_stories:
            query = query.options(selectinload(User.stories))
        
        return query.first()
    
    def get_by_apple_id(self, db: Session, apple_id: str, with_stories: bool = False) -> Optional[User]:
        """Get user by Apple ID with optional stories eager loading"""
        query = db.query(User).filter(
            and_(
                User.apple_id == apple_id, 
                User.is_active == True
            )
        )
        
        if with_stories:
            query = query.options(selectinload(User.stories))
        
        return query.first()
    
    def create_email_user(self, db: Session, user: UserRegister, password_hash: str) -> User:
        db_user = User(
            email=user.email.lower(),
            password_hash=password_hash,
            name=user.name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def create_apple_user(self, db: Session, user: AppleSignIn) -> User:
        db_user = User(
            apple_id=user.apple_id,
            name=user.name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update(self, db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def deactivate(self, db: Session, user_id: UUID) -> bool:
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return False
        
        db_user.is_active = False
        db.commit()
        return True
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, with_stories: bool = False) -> Tuple[List[User], int]:
        """Get all users with optimized counting and optional eager loading"""
        # Optimized count query
        count_query = select(func.count(User.id)).where(User.is_active == True)
        total = db.execute(count_query).scalar()
        
        # Main query
        query = db.query(User).filter(User.is_active == True)
        
        if with_stories:
            query = query.options(selectinload(User.stories))
        
        users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
        return users, total
    
    def get_stories_count(self, db: Session, user_id: UUID) -> int:
        """Optimized stories count for user"""
        from app.db.models.story import Story
        count_query = select(func.count(Story.id)).where(
            and_(
                Story.user_id == user_id,
                Story.is_deleted == False
            )
        )
        return db.execute(count_query).scalar() or 0
    
    def get_users_with_story_counts(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[dict], int]:
        """Get users with their story counts in a single query"""
        from app.db.models.story import Story
        
        # Count total users
        count_query = select(func.count(User.id)).where(User.is_active == True)
        total = db.execute(count_query).scalar()
        
        # Main query with subquery for story counts
        story_count_subquery = (
            select(func.count(Story.id))
            .where(and_(
                Story.user_id == User.id,
                Story.is_deleted == False
            ))
            .scalar_subquery()
        )
        
        query = db.query(
            User,
            story_count_subquery.label('story_count')
        ).filter(User.is_active == True).order_by(desc(User.created_at))
        
        results = query.offset(skip).limit(limit).all()
        
        # Format results
        users_with_counts = []
        for user, story_count in results:
            users_with_counts.append({
                'user': user,
                'story_count': story_count or 0
            })
        
        return users_with_counts, total


user_crud = UserCRUD()
