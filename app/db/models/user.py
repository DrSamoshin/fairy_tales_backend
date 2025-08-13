import uuid
from sqlalchemy import Column, String, Boolean, UUID
from app.db.base_classes import BaseUser


class User(BaseUser):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    deactivated = Column(Boolean, default=False)

    def __repr__(self):
        return f"id={self.id} name={self.name} deactivated={self.deactivated}"
