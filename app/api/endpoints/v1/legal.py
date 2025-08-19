import logging
import os

import markdown
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.core.responses import response
from app.core.consts import IOS_POLICY, TERMS_OF_USE
from app.schemas.response import PolicyResponse

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
contents = os.listdir(BASE_DIR)

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


@router.get("/privacy-policy/", response_class=HTMLResponse)
async def get_privacy_policy():
    logging.info("get_privacy_policy")
    with open(f"{BASE_DIR}/privacy-policy.md", "r", encoding="utf-8") as f:
        md_text = f.read()
    html = markdown.markdown(md_text)
    return f"<html><body>{html}</body></html>"


@router.get("/terms-of-use/", response_class=HTMLResponse)
async def get_terms_of_use():
    logging.info("get_terms_of_use")
    with open(f"{BASE_DIR}/terms-of-use.md", "r", encoding="utf-8") as f:
        md_text = f.read()
    html = markdown.markdown(md_text)
    return f"<html><body>{html}</body></html>"