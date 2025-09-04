from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.db_sessions import get_db
from app.crud.user import user_crud
from app.schemas.response import DataResponse
from app.core.responses import response
from app.services.authentication import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.delete("/delete", response_model=DataResponse)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user account permanently with all related content"""
    success = user_crud.delete_user_permanently(db, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return response(
        data={"deleted": True, "user_id": str(current_user.id)},
        message="User account deleted permanently"
    )