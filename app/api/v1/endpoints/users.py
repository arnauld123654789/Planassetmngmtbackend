from typing import Any, List
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.core import security
from app.api.deps import SessionDep, CurrentUser
from app.models.user import User
from app.models.enums import UserRole
from app.core.rbac import RoleChecker
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
    # Note: All authenticated users can view the user list
    # Add role-based filtering here if needed using RoleChecker
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
    
    # Intelligent role handling:
    # If explicit roles list is provided and not empty, use it.
    # Otherwise, fallback to the single 'role' field wrapped in a list.
    if user_in.roles:
        user_data["roles"] = user_in.roles
    else:
        user_data["roles"] = [user_in.role]
    
    user = User.model_validate(user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get a specific user by ID.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=User)
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
        
    # Permission check: Only IT Admin or the user themselves can update
    # Use centralized RoleChecker for multi-role support
    is_admin = RoleChecker.is_admin(current_user.roles)
    is_self = current_user.user_id == user.user_id
    
    if not is_admin and not is_self:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Prevent non-admin from changing roles
    if "role" in update_data and not is_admin:
        raise HTTPException(status_code=403, detail="Only IT Admin can assign roles")
        
    # Handling password
    if "password" in update_data and update_data["password"]:
        hashed_password = security.get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    # Sync roles list if role is updated, BUT only if 'roles' is not also being updated
    # This prevents overwriting a detailed roles list with a single role string
    if "role" in update_data and "roles" not in update_data:
        update_data["roles"] = [update_data["role"]]

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
    # Permission: Only IT Admin
    # Use centralized RoleChecker for multi-role support
    if not RoleChecker.is_admin(current_user.roles):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Prevent self-deletion
    if user.user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
    # Intelligent check: Does user have assets assigned?
    from app.models.asset import Asset
    assigned_assets = session.exec(select(Asset).where(Asset.custodian_id == user_id)).first()
    if assigned_assets:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete user: This user is the custodian of one or more assets. Please reassign assets first."
        )
    
    session.delete(user)
    session.commit()
    return user
