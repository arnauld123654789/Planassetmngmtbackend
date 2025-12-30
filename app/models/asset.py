from datetime import date
from typing import Optional
from sqlmodel import Field
from app.models.base import CamelModel
from app.models.enums import AssetStatus


class AssetBase(CamelModel):
    asset_name: str = Field(alias="assetName")
    physical_asset_tag_number: str = Field(unique=True, alias="physicalAssetTagNumber")
    brand: str
    model: str
    acquisition_price: float = Field(alias="acquisitionPrice")
    currency: str
    date_of_acquisition: date = Field(alias="dateOfAcquisition")
    type_of_acquisition: str = Field(alias="typeOfAcquisition") # purchase, donation, rental
    
    # Vendor info (can be snapshot or derived from Vendor FK if exists, but keeping fields as requested)
    vendor_name: Optional[str] = Field(default=None, alias="vendorName")
    vendor_account: Optional[str] = Field(default=None, alias="vendorAccount")
    
    purchase_order_number: Optional[str] = Field(default=None, alias="purchaseOrderNumber")
    rent_price: Optional[float] = Field(default=None, alias="rentPrice")
    asset_status: AssetStatus = Field(alias="assetStatus") # Link to Enum
    scom_category: str = Field(alias="SCOMCategory")
    useful_life_years: int = Field(alias="usefulLifeYears")
    
    # Foreign Keys
    legal_entity_id: str = Field(foreign_key="legalentity.legal_entity_id", alias="legalEntityId")
    business_unit: str = Field(alias="businessUnit")
    project_id: str = Field(foreign_key="project.project_id", alias="projectId")
    funding_source_id: str = Field(alias="fundingSourceId") # Keeping as string for now if no model
    location_id: str = Field(foreign_key="location.location_id", alias="locationId")
    custodian_id: str = Field(foreign_key="user.user_id", alias="custodianId")
    category_id: str = Field(foreign_key="assetcategory.category_id", alias="categoryId")
    sub_category_id: str = Field(foreign_key="assetsubcategory.sub_category_id", alias="subCategoryId")
    
    vin_number: Optional[str] = Field(default=None, alias="VINNumber")
    last_physical_verificator: Optional[str] = Field(default=None, alias="lastPhysicalVerificator")
    date_of_last_verification: Optional[date] = Field(default=None, alias="dateOfLastVerification")

class Asset(AssetBase, table=True):
    scom_asset_id: str = Field(primary_key=True, alias="SCOMAssetID")

