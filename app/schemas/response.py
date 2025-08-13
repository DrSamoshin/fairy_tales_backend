from pydantic import BaseModel
from typing import Any, Optional


class BaseResponse(BaseModel):
    success: bool
    message: str


class DataResponse(BaseResponse):
    data: Any


class AuthResponse(BaseResponse):
    data: dict  # Contains user and token


class StoriesListResponse(BaseResponse):
    data: dict  # Contains StoriesResponse


class StoryResponse(BaseResponse):
    data: dict  # Contains story


class UserProfileResponse(BaseResponse):
    data: dict  # Contains profile
