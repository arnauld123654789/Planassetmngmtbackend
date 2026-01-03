from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel
from app.models.verification import SessionStatus
from app.models.enums import AssetStatus

class VerificationSessionBase(SQLModel):
    name: str
    start_date: datetime
    end_date: datetime
    status: SessionStatus = SessionStatus.OPEN

class VerificationSessionCreate(VerificationSessionBase):
    pass

class VerificationSessionRead(VerificationSessionBase):
    id: int
    created_by_id: str
    created_at: datetime

class AssetVerificationBase(SQLModel):
    asset_id: str
    status_at_verification: AssetStatus
    notes: Optional[str] = None

class AssetVerificationCreate(AssetVerificationBase):
    session_id: Optional[int] = None

class AssetVerificationRead(AssetVerificationBase):
    id: int
    session_id: Optional[int]
    verificator_id: str
    scanned_at: datetime

class VerificatorAssignmentRequest(SQLModel):
    user_ids: List[str]
