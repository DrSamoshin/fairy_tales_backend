import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.responses import response
from app.db.db_sessions import get_users_db
from app.schemas.user import UserRegister, UserLogin, AppleSignIn, Token, UserOut
from app.schemas.response import AuthResponse, BaseResponse
from app.crud.user import user_crud
from app.services.authentication import auth_service, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_users_db)
):
    """Register new user with email and password"""
    logging.info(f"Registering new user with email: {user_data.email}")
    
    # Check if user already exists
    existing_user = user_crud.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    password_hash = auth_service.get_password_hash(user_data.password)
    user = user_crud.create_email_user(db, user_data, password_hash)
    
    # Generate token
    token_data = auth_service.create_access_token(user.id)
    
    logging.info(f"User registered successfully: {user.id}")
    return response(
        message="User registered successfully",
        data={
            "user": UserOut.model_validate(user),
            "token": token_data
        }
    )


@router.post("/login", response_model=AuthResponse)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_users_db)
):
    """Login user with email and password"""
    logging.info(f"User login attempt: {login_data.email}")
    
    user = auth_service.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate token
    token_data = auth_service.create_access_token(user.id)
    
    logging.info(f"User logged in successfully: {user.id}")
    return response(
        message="Login successful",
        data={
            "user": UserOut.model_validate(user),
            "token": token_data
        }
    )


@router.post("/apple-signin", response_model=AuthResponse)
async def apple_signin(
    apple_data: AppleSignIn,
    db: Session = Depends(get_users_db)
):
    """Register or login user with Apple Sign In"""
    logging.info(f"Apple Sign In attempt: {apple_data.apple_id}")
    
    # Check if user already exists
    user = user_crud.get_by_apple_id(db, apple_data.apple_id)
    
    if not user:
        # Create new user
        user = user_crud.create_apple_user(db, apple_data)
        logging.info(f"New Apple user created: {user.id}")
    else:
        logging.info(f"Existing Apple user found: {user.id}")
    
    # Generate token
    token_data = auth_service.create_access_token(user.id)
    
    return response(
        message="Apple Sign In successful",
        data={
            "user": UserOut.model_validate(user),
            "token": token_data
        }
    )


@router.post("/logout", response_model=BaseResponse)
async def logout_user():
    """Logout user (client should remove token)"""
    return response(message="Logout successful")


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    current_user = Depends(get_current_user)
):
    """Refresh access token"""
    token_data = auth_service.create_access_token(current_user.id)
    
    return response(
        message="Token refreshed successfully",
        data={"token": token_data}
    )
