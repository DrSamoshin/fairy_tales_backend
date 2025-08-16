from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import func, select, and_, desc
from app.db.models.user import User
from app.schemas.user import AppleSignIn, UserOut
from app.schemas.response import UsersListData
import logging


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
    

    def create_apple_user(self, db: Session, user: AppleSignIn, email: Optional[str] = None) -> User:
        """Create new Apple user with minimal required data"""
        db_user = User(
            apple_id=user.apple_id,
            email=email  # From Apple token verification (optional)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update_user_email(self, db: Session, user_id: UUID, email: Optional[str]) -> Optional[User]:
        """Update user email from Apple token verification"""
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.email = email
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
    
    def get_users_for_admin(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get users list for admin with structured response.
        
        Args:
            db: Database session
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            Dict with success status, message, and structured data
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Admin requesting users list with skip={skip}, limit={limit}")
        
        try:
            # Get users from database
            users, total = self.get_all(db, skip=skip, limit=limit)
            
            # Convert users to UserOut format
            users_data = [UserOut.model_validate(user).model_dump(mode='json') for user in users]
            
            logger.info(f"Retrieved {len(users_data)} users out of {total} total")
            
            # Prepare structured response data
            users_list_data = UsersListData(
                users=users_data,
                total=total,
                skip=skip,
                limit=limit
            )
            
            return {
                "success": True,
                "message": f"Retrieved {len(users_data)} users",
                "data": users_list_data.model_dump(mode='json')
            }
            
        except Exception as e:
            logger.error(f"Error getting users for admin: {str(e)}")
            return {
                "success": False,
                "message": "Internal server error",
                "status_code": 500,
                "errors": ["Failed to retrieve users"],
                "error_code": "INTERNAL_ERROR"
            }


user_crud = UserCRUD()
