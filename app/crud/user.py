from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.user import User
from app.schemas.user import UserRegister, AppleSignIn, UserUpdate


class UserCRUD:
    def get_by_id(self, db: Session, user_id: UUID) -> Optional[User]:
        return db.query(User).filter(
            User.id == user_id, 
            User.is_active == True
        ).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(
            User.email == email.lower(), 
            User.is_active == True
        ).first()
    
    def get_by_apple_id(self, db: Session, apple_id: str) -> Optional[User]:
        return db.query(User).filter(
            User.apple_id == apple_id, 
            User.is_active == True
        ).first()
    
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
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def get_stories_count(self, db: Session, user_id: UUID) -> int:
        return db.query(func.count()).select_from(User).join(User.stories).filter(
            User.id == user_id,
            User.is_active == True
        ).scalar() or 0


user_crud = UserCRUD()
