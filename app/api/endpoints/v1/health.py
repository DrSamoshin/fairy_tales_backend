import logging
from fastapi import APIRouter, Depends

from app.core.responses import response
from app.schemas.response import BaseResponse
from app.services.openai_health import openai_health_service
from app.services.authentication import get_user_id_from_token
from uuid import UUID

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/app/", response_model=BaseResponse)
async def get_health_check():
    """Basic application health check"""
    msg = "Application is running"
    logging.info(msg)
    return response(
        message=msg,
        data={"status": "healthy", "service": "fairy_tales_backend"}
    )


@router.get("/openai/quick/", response_model=BaseResponse)
async def openai_quick_check(user_id: UUID = Depends(get_user_id_from_token)):
    """Quick OpenAI API connectivity check (authenticated)"""
    logging.info("Performing quick OpenAI check")
    
    try:
        is_healthy = await openai_health_service.quick_check()
        
        if is_healthy:
            return response(
                message="OpenAI API is responsive",
                data={
                    "service": "openai",
                    "status": "healthy",
                    "check_type": "quick",
                    "timestamp": __import__('time').time()
                }
            )
        else:
            return response(
                message="OpenAI API is not responsive",
                status_code=503,
                success=False,
                data={
                    "service": "openai",
                    "status": "unhealthy",
                    "check_type": "quick",
                    "timestamp": __import__('time').time()
                }
            )
    
    except Exception as e:
        logging.error(f"Quick OpenAI check failed: {e}")
        return response(
            message="Quick OpenAI check failed",
            status_code=503,
            success=False,
            data={
                "service": "openai",
                "status": "error",
                "error": str(e),
                "timestamp": __import__('time').time()
            }
        )
