from datetime import datetime, date
from typing import Optional
from sqlmodel import Field
from app.models.base import CamelModel
from app.models.enums import TransferStatus, DisposalType, DisposalStatus

class Transfer(CamelModel, table=True):
    transfer_id: str = Field(primary_key=True, alias="transferId")
    status: TransferStatus
    requested_at: datetime = Field(alias="requestedAt")
    from_user_id: str = Field(foreign_key="user.user_id", alias="fromUserId")
    to_user_id: str = Field(foreign_key="user.user_id", alias="toUserId")
    from_location_id: str = Field(foreign_key="location.location_id", alias="fromLocationId")
    to_location_id: str = Field(foreign_key="location.location_id", alias="toLocationId")
    reason: str
    initiated_by: str = Field(foreign_key="user.user_id", alias="initiatedBy")

class Disposal(CamelModel, table=True):
    disposal_id: str = Field(primary_key=True, alias="disposalId")
    asset_id: str = Field(foreign_key="asset.scom_asset_id", alias="assetId")
    type_of_disposal: DisposalType = Field(alias="typeOfDisposal")
    reason: str
    requested_by: str = Field(foreign_key="user.user_id", alias="requestedBy")
    requested_at: datetime = Field(alias="requestedAt")
    status: DisposalStatus

class Maintenance(CamelModel, table=True):
    maintenance_id: str = Field(primary_key=True, alias="maintenanceId")
    asset_id: str = Field(foreign_key="asset.scom_asset_id", alias="assetId")
    date_of_maintenance: date = Field(alias="date") # alias "date"
    type: str # "Preventive" etc
    provider: str
    cost: float
