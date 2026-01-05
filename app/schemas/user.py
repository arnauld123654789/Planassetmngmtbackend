from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from pydantic.alias_generators import to_camel

class UserBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    role: Optional[str] = None
    roles: List[str] = []

class UserCreate(UserBase):
    full_name: str
    email: EmailStr
    password: str
    role: str

class UserUpdate(UserBase):
    password: Optional[str] = None
