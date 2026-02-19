from typing import Optional
from datetime import date
from pydantic import Field
from app.models.asset import AssetBase
from app.models.enums import AssetStatus
from app.models.base import CamelModel

class AssetCreate(AssetBase):
    pass

class AssetUpdate(AssetBase):
    asset_name: Optional[str] = Field(default=None, alias="assetName")
    physical_asset_tag_number: Optional[str] = Field(default=None, alias="physicalAssetTagNumber")
    brand: Optional[str] = None
    model: Optional[str] = None
    acquisition_price: Optional[float] = Field(default=None, alias="acquisitionPrice")
    currency: Optional[str] = None
    date_of_acquisition: Optional[date] = Field(default=None, alias="dateOfAcquisition")
    type_of_acquisition: Optional[str] = Field(default=None, alias="typeOfAcquisition")
    asset_status: Optional[AssetStatus] = Field(default=None, alias="assetStatus")
    scom_category: Optional[str] = Field(default=None, alias="SCOMCategory")
    useful_life_years: Optional[int] = Field(default=None, alias="usefulLifeYears")
    legal_entity_id: Optional[str] = Field(default=None, alias="legalEntityId")
    business_unit: Optional[str] = Field(default=None, alias="businessUnit")
    project_id: Optional[str] = Field(default=None, alias="projectId")
    funding_source_id: Optional[str] = Field(default=None, alias="fundingSourceId")
    location_id: Optional[str] = Field(default=None, alias="locationId")
    custodian_id: Optional[str] = Field(default=None, alias="custodianId")
    sub_category_id: Optional[str] = Field(default=None, alias="subCategoryId")
    category_id: Optional[str] = Field(default=None, alias="categoryId")
    
    # Optional in Base too, but redeclaring for completeness/clarity
    vendor_name: Optional[str] = Field(default=None, alias="vendorName")
    vendor_account: Optional[str] = Field(default=None, alias="vendorAccount")
    purchase_order_number: Optional[str] = Field(default=None, alias="purchaseOrderNumber")
    rent_price: Optional[float] = Field(default=None, alias="rentPrice")
    vin_number: Optional[str] = Field(default=None, alias="VINNumber")

class AssetRead(AssetBase):
    scom_asset_id: str = Field(alias="SCOMAssetID")
    photo_count: int = 0
    profile_photo_url: Optional[str] = None
    profile_photo_thumb_url: Optional[str] = None

# Nested models for detailed asset response
class SiteInfo(CamelModel):
    site_id: str = Field(alias="siteId")
    site_code: str = Field(alias="siteCode")
    site_name: str = Field(alias="siteName")

class LocationInfo(CamelModel):
    location_id: str = Field(alias="locationId")
    location_code: str = Field(alias="locationCode")
    location_name: str = Field(alias="locationName")
    location_name_code: str = Field(alias="locationNameCode")
    site: Optional[SiteInfo] = None

class AssetDetailedRead(AssetBase):
    """Extended asset response with location and site information"""
    scom_asset_id: str = Field(alias="SCOMAssetID")
    photo_count: int = 0
    profile_photo_url: Optional[str] = None
    profile_photo_thumb_url: Optional[str] = None
    location: Optional[LocationInfo] = None
