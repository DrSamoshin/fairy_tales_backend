from pydantic import BaseModel
from typing import Any, Optional, List
from uuid import UUID
from datetime import datetime


class BaseResponse(BaseModel):
    success: bool
    message: str


class DataResponse(BaseResponse):
    data: Any


# Auth-related responses
class AuthData(BaseModel):
    """Structured auth response data"""
    user: dict  # UserOut or UserSummary
    token: dict  # Token


class AuthResponse(BaseResponse):
    data: AuthData


class StoriesListResponse(BaseResponse):
    data: dict  # Contains StoriesResponse


class StoryResponse(BaseResponse):
    data: dict  # Contains story


# Hero-related responses
class HeroesListData(BaseModel):
    """Structured heroes list response data"""
    heroes: List[dict]  # List of HeroOut or HeroSummary
    pagination: dict  # Contains skip, limit, count, total


class HeroesListResponse(BaseResponse):
    data: HeroesListData


class HeroResponse(BaseResponse):
    data: dict  # Contains hero




# User-related responses  
class UsersListData(BaseModel):
    """Structured users list response data"""
    users: List[dict]  # List of UserOut
    total: int
    skip: int
    limit: int


class UsersListResponse(BaseResponse):
    data: UsersListData


class PolicyResponse(BaseResponse):
    data: dict  # Contains policy content
