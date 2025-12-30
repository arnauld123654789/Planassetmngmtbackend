from typing import Any, List
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.core import security
from app.api.deps import SessionDep, CurrentUser
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()

@router.get("/", response_model=List[User])
def read_users(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users.
    """
    # Simple RBAC check example
    # if current_user.role != "IT Admin": raise HTTPException...
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users

@router.get("/me", response_model=User)
def read_user_me(
    current_user: CurrentUser,
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/", response_model=User)
def create_user(
    *,
    session: SessionDep,
    user_in: UserCreate,
    current_user: CurrentUser,
) -> Any:
    # Check if user with this email already exists
    user = session.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    # Hash password
    import uuid
    user_data = user_in.model_dump()
    user_data["hashed_password"] = security.get_password_hash(user_in.password)
    user_data["user_id"] = str(uuid.uuid4())
    user_data["roles"] = [user_in.role] # Sync single role to roles list
    
    user = User.model_validate(user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    session: SessionDep,
    user_id: str,
    user_in: UserUpdate,
    current_user: CurrentUser,
) -> Any:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        hashed_password = security.get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    for key, value in update_data.items():
        setattr(user, key, value)
        
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.delete("/{user_id}", response_model=User)
def delete_user(
    session: SessionDep,
    user_id: str,
    current_user: CurrentUser,
) -> Any:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(user)
    session.commit()
    return user
