import logging
import jwt
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.configs import settings
from app.crud.user import user_crud

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token settings
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class AuthService:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, user_id: UUID) -> dict:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow()
        }
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_token.JWT_SECRET_KEY, 
            algorithm=settings.jwt_token.ALGORITHM
        )
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def verify_token(self, token: str) -> Optional[UUID]:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_token.JWT_SECRET_KEY,
                algorithms=[settings.jwt_token.ALGORITHM],
            )
            user_id_str = payload.get("sub")
            if user_id_str is None:
                return None
            return UUID(user_id_str)
        except jwt.PyJWTError:
            return None
    
    def authenticate_user(self, db: Session, email: str, password: str):
        user = user_crud.get_by_email(db, email)
        if not user:
            return False
        if not user.password_hash:
            return False
        if not self.verify_password(password, user.password_hash):
            return False
        return user


auth_service = AuthService()


async def get_user_id_from_token(
    credential: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> UUID:
    token = credential.credentials
    user_id = auth_service.verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


def get_current_user_dependency():
    """Factory function to create get_current_user dependency with proper import"""
    from app.db.db_sessions import get_users_db
    
    async def get_current_user(
        user_id: UUID = Depends(get_user_id_from_token),
        db: Session = Depends(get_users_db)
    ):
        user = user_crud.get_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    
    return get_current_user

# Create the dependency
get_current_user = get_current_user_dependency()
