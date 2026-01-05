from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, AliasChoices, model_validator
from app.models.enums import DisposalType, DisposalStatus, TransferStatus

# Disposal Schemas
class DisposalBase(BaseModel):
    reason: str
    type_of_disposal: DisposalType = Field(alias="typeOfDisposal")
    # asset_id removed from base, as creation takes list, read has single

class DisposalCreate(DisposalBase):
    asset_ids: List[str] = Field(validation_alias=AliasChoices("assetIds", "asset_id", "asset_ids"))
    model_config = ConfigDict(populate_by_name=True)

class DisposalUpdate(BaseModel):
    status: DisposalStatus

class DisposalRead(DisposalBase):
    disposal_id: str = Field(alias="disposalId")
    asset_id: str = Field(alias="assetId") # Read model is per-item
    requested_by: str = Field(alias="requestedBy")
    requested_at: datetime = Field(alias="requestedAt")
    status: DisposalStatus
    document_path: str = Field(alias="documentPath")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Transfer Schemas
class TransferBase(BaseModel):
    reason: str
    to_user_id: Optional[str] = Field(default=None, alias="toUserId")
    to_location_id: Optional[str] = Field(default=None, alias="toLocationId")
    from_user_id: Optional[str] = Field(default=None, alias="fromUserId") 
    from_location_id: Optional[str] = Field(default=None, alias="fromLocationId")

    @model_validator(mode='after')
    def check_transfer_type(self) -> 'TransferBase':
        has_users = self.from_user_id and self.to_user_id
        has_locations = self.from_location_id and self.to_location_id
        
        if not has_users and not has_locations:
            raise ValueError("Transfer must be either User-to-User OR Location-to-Location.")
            
        if has_users and has_locations:
            # User didn't strictly say this is forbidden, but "vice versa" implies one or the other.
            # However, usually mixed transfers might exist?
            # User said "if it is person to person then locations id my be empty".
            # Let's enforce that at least one complete pair exists.
            pass
            
        return self

class TransferCreate(TransferBase):
    asset_ids: List[str] = Field(validation_alias=AliasChoices("assetIds", "asset_id", "asset_ids"))
    model_config = ConfigDict(populate_by_name=True)

class TransferUpdate(BaseModel):
    status: TransferStatus

class TransferRead(TransferBase):
    transfer_id: str = Field(alias="transferId")
    asset_id: str = Field(alias="assetId") # Read model is per-item
    status: TransferStatus
    requested_at: datetime = Field(alias="requestedAt")
    initiated_by: str = Field(alias="initiatedBy")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
