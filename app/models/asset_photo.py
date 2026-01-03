from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class AssetPhotoBase(SQLModel):
    filename: str
    is_profile: bool = False
    
class AssetPhoto(AssetPhotoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: str = Field(foreign_key="asset.scom_asset_id")
    # Checking Asset model: scom_asset_id: str = Field(primary_key=True, alias="SCOMAssetID")
    # SQLModel uses the field name for relationships usually, but foreign_key argument needs the table name and column name.
    # The table name for Asset is 'asset' (default) or whatever is configured.
    # Let's verify the Asset table name. app/models/asset.py doesn't specify __tablename__, so it defaults to 'asset'.
    # The primary key field is scom_asset_id. 
    # WAIT. The alias in Asset is "SCOMAssetID". SQLModel might use that for serialization but the column name in DB might be different?
    # Usually alias is for Pydantic serialization.
    # Safe bet: `asset.scom_asset_id` if using recent SQLModel, but let's look at other FKs in asset.py.
    # legal_entity_id: str = Field(foreign_key="legalentity.legal_entity_id", alias="legalEntityId")
    # It uses `tablename.columnname`.
    # In Asset class: scom_asset_id: str = Field(primary_key=True, alias="SCOMAssetID")
    # If no sa_column_args, the column name defaults to field name `scom_asset_id`.
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    asset: "Asset" = Relationship(back_populates="photos")
