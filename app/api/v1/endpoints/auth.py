from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.api.deps import SessionDep
from app.core import security
from app.models.user import User

router = APIRouter()

@router.post("/login")
def login_access_token(
    session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    # Try filtering by email since username field in OAuth2 form is usually used for email
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return {
        "access_token": security.create_access_token(user.user_id),
        "token_type": "bearer",
    }
