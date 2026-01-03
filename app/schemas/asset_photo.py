from datetime import datetime
from sqlmodel import SQLModel

class AssetPhotoBase(SQLModel):
    filename: str
    is_profile: bool

class AssetPhotoCreate(AssetPhotoBase):
    pass

class AssetPhotoRead(AssetPhotoBase):
    id: int
    asset_id: str
    created_at: datetime
    url: str  # Computed URL
