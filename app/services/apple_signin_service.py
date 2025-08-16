import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.user import AppleSignIn, UserSummary
from app.schemas.response import AuthData
from app.crud.user import user_crud
from app.services.authentication import auth_service
from app.services.apple_verification import apple_verification_service
from app.core import error_codes


class AppleSignInService:
    """Service for handling Apple Sign In business logic"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def process_apple_signin(
        self, 
        db: Session, 
        apple_data: AppleSignIn
    ) -> Dict[str, Any]:
        """
        Process Apple Sign In request with verification and user management.
        
        Args:
            db: Database session
            apple_data: Apple Sign In request data
            
        Returns:
            Dict with success status, message, data or error details
        """
        self.logger.info(f"Apple Sign In attempt: {apple_data.apple_id}")
        self.logger.debug(f"Apple Sign In data: apple_id={apple_data.apple_id}, name={apple_data.name}")
        self.logger.debug(f"Identity token provided: {bool(apple_data.identity_token)}")
        if apple_data.identity_token:
            self.logger.debug(f"Identity token length: {len(apple_data.identity_token)}")
        
        try:
            # Step 1: Verify Apple identity token and get verified data
            verification_result = await self._verify_apple_token(apple_data)
            if not verification_result["success"]:
                return verification_result
            
            verified_apple_id = verification_result["apple_id"]
            verified_email = verification_result.get("email")
            
            # Step 2: Get or create user
            user = await self._get_or_create_user(
                db, apple_data, verified_apple_id, verified_email
            )
            
            # Step 3: Generate authentication token
            token_data = auth_service.create_access_token(user.id)
            
            # Step 4: Prepare response data
            auth_data = AuthData(
                user=UserSummary.model_validate(user).model_dump(mode='json'),
                token=token_data
            )
            
            self.logger.info(f"Apple Sign In successful for user: {user.id}")
            
            return {
                "success": True,
                "message": "Apple Sign In successful",
                "data": auth_data.model_dump(mode='json')
            }
            
        except Exception as e:
            self.logger.error(f"Apple Sign In processing failed: {str(e)}")
            return {
                "success": False,
                "message": "Apple Sign In failed",
                "status_code": 500,
                "errors": ["Internal server error during Apple Sign In"],
                "error_code": error_codes.INTERNAL_ERROR
            }
    
    async def refresh_user_token(self, current_user) -> Dict[str, Any]:
        """
        Refresh user access token.
        
        Args:
            current_user: Authenticated user object
            
        Returns:
            Dict with success status, message, and new token data
        """
        try:
            # Generate new token
            token_data = auth_service.create_access_token(current_user.id)
            
            # Prepare response data
            auth_data = AuthData(
                user=UserSummary.model_validate(current_user).model_dump(mode='json'),
                token=token_data
            )
            
            self.logger.info(f"Token refreshed for user: {current_user.id}")
            
            return {
                "success": True,
                "message": "Token refreshed successfully",
                "data": auth_data.model_dump(mode='json')
            }
            
        except Exception as e:
            self.logger.error(f"Token refresh failed: {str(e)}")
            return {
                "success": False,
                "message": "Token refresh failed", 
                "status_code": 500,
                "errors": ["Failed to refresh token"],
                "error_code": error_codes.INTERNAL_ERROR
            }
    
    async def _verify_apple_token(self, apple_data: AppleSignIn) -> Dict[str, Any]:
        """
        Verify Apple identity token if provided.
        
        Args:
            apple_data: Apple Sign In request data
            
        Returns:
            Dict with verification result
        """
        verified_apple_id = apple_data.apple_id
        verified_email = None
        
        if apple_data.identity_token:
            verification_result = await apple_verification_service.verify_apple_token(
                identity_token=apple_data.identity_token,
                apple_id=apple_data.apple_id,
                name=apple_data.name
            )
            
            if not verification_result["valid"]:
                self.logger.warning(f"Apple token verification failed for: {apple_data.apple_id}")
                self.logger.debug(f"Verification result: {verification_result}")
                return {
                    "success": False,
                    "message": "Apple Sign In verification failed",
                    "status_code": 401,
                    "errors": ["Invalid Apple identity token"],
                    "error_code": error_codes.INVALID_CREDENTIALS
                }
            
            # Use verified data from token
            verified_apple_id = verification_result["apple_id"]
            verified_email = verification_result.get("email")
            
            self.logger.info(f"Apple token verified for: {verified_apple_id}")
        else:
            # Backward compatibility - no token provided
            self.logger.info(f"Apple Sign In without token verification: {apple_data.apple_id}")
        
        return {
            "success": True,
            "apple_id": verified_apple_id,
            "email": verified_email
        }
    
    async def _get_or_create_user(
        self, 
        db: Session, 
        apple_data: AppleSignIn, 
        verified_apple_id: str, 
        verified_email: Optional[str]
    ):
        """
        Get existing user or create new one with verified Apple data.
        
        Args:
            db: Database session
            apple_data: Original Apple Sign In data
            verified_apple_id: Verified Apple ID from token
            verified_email: Verified email from token (optional)
            
        Returns:
            User object
        """
        # Check if user already exists
        user = user_crud.get_by_apple_id(db, verified_apple_id)
        
        if not user:
            # Create new user with verified data
            user = user_crud.create_apple_user(db, apple_data, email=verified_email)
            self.logger.info(f"New Apple user created: {user.id}")
        else:
            # Update email if we got new verified email
            if verified_email and user.email != verified_email:
                user = user_crud.update_user_email(db, user.id, verified_email)
                self.logger.info(f"Updated email for user: {user.id}")
            
            self.logger.info(f"Existing Apple user found: {user.id}")
        
        return user


# Create service instance
apple_signin_service = AppleSignInService()
