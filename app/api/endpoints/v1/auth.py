import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.responses import response
from app.db.db_sessions import get_db
from app.schemas.user import AppleSignIn
from app.schemas.response import AuthResponse
from app.services.authentication import get_current_user
from app.services.apple_signin_service import apple_signin_service

router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/apple-signin/", response_model=AuthResponse)
async def apple_signin(
    apple_data: AppleSignIn,
    db: Session = Depends(get_db)
):
    """Register or login user with Apple Sign In"""
    result = await apple_signin_service.process_apple_signin(db, apple_data)
    
    return response(
        message=result["message"],
        data=result.get("data"),
        status_code=result.get("status_code", 200),
        success=result["success"],
        errors=result.get("errors"),
        error_code=result.get("error_code")
    )



@router.post("/refresh/", response_model=AuthResponse)
async def refresh_token(
    current_user = Depends(get_current_user)
):
    """Refresh access token"""
    result = await apple_signin_service.refresh_user_token(current_user)
    
    return response(
        message=result["message"],
        data=result.get("data"),
        status_code=result.get("status_code", 200),
        success=result["success"],
        errors=result.get("errors"),
        error_code=result.get("error_code")
    )
