from typing import Optional, List
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
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
