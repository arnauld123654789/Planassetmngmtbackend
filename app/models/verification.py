from datetime import datetime
from typing import List, Optional
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship
from app.models.enums import AssetStatus

class SessionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class VerificationSessionBase(SQLModel):
    name: str
    start_date: datetime
    end_date: datetime
    status: SessionStatus = SessionStatus.OPEN

class VerificationSession(VerificationSessionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_by_id: str = Field(foreign_key="user.user_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    assignments: List["VerificationAssignment"] = Relationship(back_populates="session")
    verifications: List["AssetVerification"] = Relationship(back_populates="session")

class VerificationAssignment(SQLModel, table=True):
    session_id: int = Field(foreign_key="verificationsession.id", primary_key=True)
    user_id: str = Field(foreign_key="user.user_id", primary_key=True)
    
    # Relationships
    session: VerificationSession = Relationship(back_populates="assignments")

class AssetVerificationBase(SQLModel):
    asset_id: str = Field(foreign_key="asset.scom_asset_id")
    verificator_id: str = Field(foreign_key="user.user_id")
    scanned_at: datetime = Field(default_factory=datetime.utcnow)
    status_at_verification: AssetStatus
    notes: Optional[str] = None

class AssetVerification(AssetVerificationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: Optional[int] = Field(default=None, foreign_key="verificationsession.id")
    
    # Relationships
    session: Optional[VerificationSession] = Relationship(back_populates="verifications")
