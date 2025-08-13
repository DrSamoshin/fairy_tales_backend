from pydantic import BaseModel
from uuid import UUID


class UserBase(BaseModel):
    name: str
    db_name: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserOut(UserBase):
    id: UUID
    deactivated: bool

    model_config = {"from_attributes": True}
