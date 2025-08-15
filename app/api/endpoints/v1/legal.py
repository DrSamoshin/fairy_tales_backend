import logging
from fastapi import APIRouter

from app.core.responses import response
from app.core.consts import IOS_POLICY, TERMS_OF_USE
from app.schemas.response import PolicyResponse

router = APIRouter(prefix="/legal", tags=["legal"])


@router.get("/policy-ios/", response_model=PolicyResponse)
async def get_ios_policy():
    """Get iOS privacy policy"""
    logging.info("iOS policy requested")
    
    return response(
        message="iOS policy retrieved successfully",
        data={"policy": IOS_POLICY}
    )


@router.get("/terms/", response_model=PolicyResponse)
async def get_terms_of_use():
    """Get Terms of Use"""
    logging.info("Terms of Use requested")
    
    return response(
        message="Terms of Use retrieved successfully",
        data={"terms": TERMS_OF_USE}
    )
