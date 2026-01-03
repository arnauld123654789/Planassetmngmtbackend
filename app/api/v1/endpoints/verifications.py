from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import select, and_

from app.api.deps import SessionDep, CurrentUser
from app.models.verification import (
    VerificationSession, 
    VerificationAssignment, 
    AssetVerification, 
    SessionStatus
)
from app.models.asset import Asset
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.verification import (
    VerificationSessionCreate, 
    VerificationSessionRead,
    AssetVerificationCreate,
    AssetVerificationRead,
    VerificatorAssignmentRequest
)

router = APIRouter()

# --- Sessions ---

@router.post("/sessions", response_model=VerificationSessionRead)
def create_session(
    *,
    session: SessionDep,
    session_in: VerificationSessionCreate,
    current_user: CurrentUser,
) -> Any:
    """
    Create a new physical verification session. (Supply Chain Manager and IT Admin only)
    """
    if current_user.role not in [UserRole.SUPPLY_CHAIN_MANAGER, UserRole.IT_ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    db_session = VerificationSession.model_validate(
        session_in, update={"created_by_id": current_user.user_id}
    )
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session

@router.get("/sessions", response_model=List[VerificationSessionRead])
def read_sessions(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return session.exec(select(VerificationSession).offset(skip).limit(limit)).all()

@router.patch("/sessions/{id}/status", response_model=VerificationSessionRead)
def update_session_status(
    *,
    session: SessionDep,
    id: int,
    status: SessionStatus,
    current_user: CurrentUser,
) -> Any:
    db_session = session.get(VerificationSession, id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    if current_user.role not in [UserRole.SUPPLY_CHAIN_MANAGER, UserRole.IT_ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    db_session.status = status
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session

@router.post("/sessions/{id}/verificators")
def assign_verificators(
    *,
    session: SessionDep,
    id: int,
    assignment_in: VerificatorAssignmentRequest,
    current_user: CurrentUser,
) -> Any:
    """
    Assign users to a verification session.
    """
    db_session = session.get(VerificationSession, id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    if current_user.role not in [UserRole.SUPPLY_CHAIN_MANAGER, UserRole.IT_ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    for user_id in assignment_in.user_ids:
        # Check if user exists
        user = session.get(User, user_id)
        if not user:
            continue
            
        # Check if already assigned
        existing = session.exec(
            select(VerificationAssignment).where(
                and_(
                    VerificationAssignment.session_id == id,
                    VerificationAssignment.user_id == user_id
                )
            )
        ).first()
        
        if not existing:
            assignment = VerificationAssignment(session_id=id, user_id=user_id)
            session.add(assignment)
            
    session.commit()
    return {"ok": True}

# --- Verifications (Scans) ---

@router.post("/verify/{asset_id}", response_model=AssetVerificationRead)
def record_asset_verification(
    *,
    session: SessionDep,
    asset_id: str,
    verification_in: AssetVerificationCreate,
    current_user: CurrentUser,
) -> Any:
    """
    Record an asset verification (scan). 
    If session_id is provided, validates that the session is OPEN and the user is assigned.
    """
    asset = session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    session_id = verification_in.session_id
    
    if session_id:
        db_session = session.get(VerificationSession, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
        if db_session.status != SessionStatus.OPEN:
            raise HTTPException(status_code=400, detail="Session is closed")
            
        # Check if user is assigned to this session
        assignment = session.exec(
            select(VerificationAssignment).where(
                and_(
                    VerificationAssignment.session_id == session_id,
                    VerificationAssignment.user_id == current_user.user_id
                )
            )
        ).first()
        
        if not assignment and current_user.role not in [UserRole.SUPPLY_CHAIN_MANAGER, UserRole.IT_ADMIN]:
            raise HTTPException(status_code=403, detail="User not assigned to this session")
    else:
        # Regular scan check - Logisticians or Verificators can scan anytime
        if current_user.role not in [UserRole.LOGISTICIAN, UserRole.VERIFICATOR, UserRole.SUPPLY_CHAIN_MANAGER, UserRole.IT_ADMIN]:
            raise HTTPException(status_code=403, detail="Regular scans allowed for Logisticians and Verificators only")

    # Create verification record
    db_verification = AssetVerification(
        asset_id=asset_id,
        session_id=session_id,
        verificator_id=current_user.user_id,
        status_at_verification=verification_in.status_at_verification,
        notes=verification_in.notes
    )
    session.add(db_verification)
    
    # Update Asset status and verification metadata
    asset.asset_status = verification_in.status_at_verification
    asset.last_physical_verification = current_user.full_name
    asset.date_of_last_physical_verification = datetime.utcnow().date()
    
    session.add(asset)
    
    session.commit()
    session.refresh(db_verification)
    return db_verification

@router.get("/sessions/{id}/report", response_model=List[AssetVerificationRead])
def get_session_report(
    *,
    session: SessionDep,
    id: int,
    current_user: CurrentUser,
) -> Any:
    """
    Get all verification records for a specific session.
    """
    db_session = session.get(VerificationSession, id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    verifications = session.exec(
        select(AssetVerification).where(AssetVerification.session_id == id)
    ).all()
    return verifications

@router.get("/verifications", response_model=List[AssetVerificationRead])
def get_all_verifications(
    session: SessionDep,
    current_user: CurrentUser,
    asset_id: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all verification records, optionally filtered by asset.
    """
    statement = select(AssetVerification)
    if asset_id:
        statement = statement.where(AssetVerification.asset_id == asset_id)
    verifications = session.exec(statement.offset(skip).limit(limit)).all()
    return verifications
