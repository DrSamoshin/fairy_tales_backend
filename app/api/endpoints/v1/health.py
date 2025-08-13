import logging
from fastapi import APIRouter
from app.core.responses import response

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/app/")
async def get_health_check():
    msg = "application is running"
    logging.info(msg)
    return response(msg)
