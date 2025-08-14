import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.db_sessions import get_users_db
from app.crud.user import user_crud
from app.schemas.user import UserOut
from app.schemas.response import UsersListResponse
from app.core.responses import response
from app.core import error_codes

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/")
async def root():
    logging.info("call method root")
    try:
        logging.info(f"")
        return {"message": "root"}
    except Exception as e:
        logging.info(f"")
        raise HTTPException(status_code=400, detail=f"failed")


@router.get("/users", response_model=UsersListResponse)
async def get_all_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    db: Session = Depends(get_users_db)
):
    """Get all users (no authentication required)"""
    logging.info(f"Requesting users list with skip={skip}, limit={limit}")
    
    try:
        # Get users from database
        users = user_crud.get_all(db, skip=skip, limit=limit)
        
        # Convert users to UserOut format
        users_data = [UserOut.model_validate(user).model_dump(mode='json') for user in users]
        
        logging.info(f"Retrieved {len(users_data)} users")
        
        return response(
            message=f"Retrieved {len(users_data)} users",
            data={
                "users": users_data,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "count": len(users_data)
                }
            }
        )
    except Exception as e:
        logging.error(f"Error getting users: {str(e)}")
        return response(
            message="Internal server error",
            status_code=500,
            success=False,
            errors=["Failed to retrieve users"],
            error_code=error_codes.INTERNAL_ERROR
        )

