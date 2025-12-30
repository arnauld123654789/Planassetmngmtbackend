from typing import List, Optional
from sqlmodel import Field, Relationship
from sqlalchemy import Column, String, ARRAY
from app.models.base import CamelModel

class User(CamelModel, table=True):
    user_id: str = Field(primary_key=True, alias="userId")
    full_name: str = Field(alias="fullName")
    email: str = Field(unique=True, index=True)
    role: str
    roles: List[str] = Field(sa_column=Column(ARRAY(String)))
    is_active: bool = Field(default=True, alias="isActive")
    hashed_password: str = Field(exclude=True)  # Not returned in API

    # Relationships can be added here if needed, e.g.
    # assets_custodian: List["Asset"] = Relationship(back_populates="custodian")
