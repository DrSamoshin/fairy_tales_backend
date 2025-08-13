import logging
from fastapi import APIRouter, Depends, HTTPException
from app.services.authentication import get_user_id_from_token

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/")
async def root(user_id: str = Depends(get_user_id_from_token)):
    logging.info("call method root")
    try:
        logging.info(f"")
        return {"message": "root"}
    except Exception as e:
        logging.info(f"")
        raise HTTPException(status_code=400, detail=f"failed")

