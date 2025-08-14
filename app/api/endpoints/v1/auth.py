import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.responses import response
from app.core import error_codes
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
    
    # Check if user already exists (normalize email to lowercase)
    existing_user = user_crud.get_by_email(db, user_data.email.lower())
    if existing_user:
        return response(
            message="User already exists",
            status_code=400,
            success=False,
            errors=["Email is already registered"],
            error_code=error_codes.USER_EXISTS
        )
    
    # Hash password and create user
    password_hash = auth_service.get_password_hash(user_data.password)
    user = user_crud.create_email_user(db, user_data, password_hash)
    
    # Generate token
    token_data = auth_service.create_access_token(user.id)
    
    logging.info(f"User registered successfully: {user.id}")
    return response(
        message="Registration successful",
        data={
            "user": UserOut.model_validate(user).model_dump(mode='json'),
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
    
    # First check if user exists
    normalized_email = login_data.email.lower()
    user_exists = auth_service.check_user_exists(db, normalized_email)
    
    if not user_exists:
        return response(
            message="User not found",
            status_code=401,
            success=False,
            errors=["No account found with this email"],
            error_code=error_codes.USER_NOT_FOUND
        )
    
    # User exists, now check password
    user = auth_service.authenticate_user(db, normalized_email, login_data.password)
    if not user:
        return response(
            message="The password you entered is incorrect",
            status_code=401,
            success=False,
            errors=["Password does not match"],
            error_code=error_codes.INVALID_PASSWORD
        )
    
    # Generate token
    token_data = auth_service.create_access_token(user.id)
    
    logging.info(f"User logged in successfully: {user.id}")
    return response(
        message="Login successful",
        data={
            "user": UserOut.model_validate(user).model_dump(mode='json'),
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
            "user": UserOut.model_validate(user).model_dump(mode='json'),
            "token": token_data
        }
    )


@router.post("/logout", response_model=BaseResponse)
async def logout_user():
    """Logout user (client should remove token)"""
    return response(
        message="Logged out successfully",
        data=None
    )


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
