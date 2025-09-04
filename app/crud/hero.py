from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.models.hero import Hero
from app.schemas.hero import HeroCreate, HeroUpdate
from app.crud import user_onboarding
from app.core.consts import OnboardingStep


class HeroCRUD:
    def create(self, db: Session, hero_data: HeroCreate, user_id: UUID) -> Hero:
        """Create a new hero"""
        db_hero = Hero(
            user_id=user_id,
            name=hero_data.name,
            gender=hero_data.gender,
            age=hero_data.age,
            appearance=hero_data.appearance,
            personality=hero_data.personality,
            power=hero_data.power,
            avatar_image=hero_data.avatar_image
        )
        db.add(db_hero)
        db.commit()
        db.refresh(db_hero)
        
        # Check if this is user's first hero and create onboarding step
        existing_step = user_onboarding.get_onboarding_step(
            db, user_id, OnboardingStep.FIRST_HERO_CREATED
        )
        if not existing_step:
            user_onboarding.create_onboarding_step(
                db=db,
                user_id=user_id,
                step_name=OnboardingStep.FIRST_HERO_CREATED
            )
        
        return db_hero
    
    def get_by_id(self, db: Session, hero_id: UUID, user_id: UUID) -> Optional[Hero]:
        """Get hero by ID"""
        return db.query(Hero).filter(
            and_(
                Hero.id == hero_id,
                Hero.user_id == user_id,
                Hero.is_deleted == False
            )
        ).first()
    
    def get_user_heroes(self, db: Session, user_id: UUID) -> List[Hero]:
        """Get all user heroes"""
        return db.query(Hero).filter(
            and_(
                Hero.user_id == user_id,
                Hero.is_deleted == False
            )
        ).order_by(Hero.name).all()
    
    def update(self, db: Session, hero_id: UUID, hero_data: HeroUpdate, user_id: UUID) -> Optional[Hero]:
        """Update hero - rewrite all fields"""
        db_hero = self.get_by_id(db, hero_id, user_id)
        if not db_hero:
            return None
        
        # Simple approach: update all fields directly from the request
        if hero_data.name is not None:
            db_hero.name = hero_data.name
        if hero_data.gender is not None:
            db_hero.gender = hero_data.gender
        if hero_data.age is not None:
            db_hero.age = hero_data.age
        
        # For optional fields, always update them (including None values)
        db_hero.appearance = hero_data.appearance
        db_hero.personality = hero_data.personality
        db_hero.power = hero_data.power
        db_hero.avatar_image = hero_data.avatar_image
        
        db.commit()
        db.refresh(db_hero)
        return db_hero
    
    def delete(self, db: Session, hero_id: UUID, user_id: UUID) -> bool:
        """Soft delete hero (mark as deleted)"""
        db_hero = self.get_by_id(db, hero_id, user_id)
        if not db_hero:
            return False
        
        db_hero.is_deleted = True
        db.commit()
        return True

    def get_heroes_for_admin(self, db: Session) -> dict:
        """Get all heroes for admin"""
        try:
            heroes = db.query(Hero).filter(Hero.is_deleted == False).order_by(Hero.name).all()
            
            from app.schemas.hero import HeroOut
            heroes_data = [HeroOut.model_validate(hero).model_dump() for hero in heroes]
            
            return {
                "success": True,
                "message": f"Retrieved {len(heroes_data)} heroes",
                "data": {"heroes": heroes_data}
            }
        except Exception as e:
            import logging
            logging.error(f"Error getting heroes for admin: {str(e)}")
            return {
                "success": False,
                "message": "Failed to retrieve heroes",
                "status_code": 500,
                "errors": ["Internal server error"]
            }


hero_crud = HeroCRUD()