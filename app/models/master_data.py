from typing import Optional
from sqlmodel import Field
from app.models.base import CamelModel

class LegalEntity(CamelModel, table=True):
    legal_entity_id: str = Field(primary_key=True, alias="legalEntityId")
    legal_entity_code: str = Field(alias="legalEntityCode")
    legal_entity_name: str = Field(alias="legalEntityName")

class AssetCategory(CamelModel, table=True):
    category_id: str = Field(primary_key=True, alias="categoryId")
    name: str
    description: Optional[str] = None

class AssetSubCategory(CamelModel, table=True):
    sub_category_id: str = Field(primary_key=True, alias="subCategoryId")
    category_id: str = Field(foreign_key="assetcategory.category_id", alias="categoryId")
    name: str
    useful_life_years: int = Field(alias="usefulLifeYears")
    description: Optional[str] = None

class Location(CamelModel, table=True):
    location_id: str = Field(primary_key=True, alias="locationId")
    location_code: str = Field(alias="locationCode")
    location_name: str = Field(alias="locationName")
    site_name: str = Field(alias="siteName")

class Project(CamelModel, table=True):
    project_id: str = Field(primary_key=True, alias="projectId")
    project_code: str = Field(alias="projectCode")
    name: str

class Vendor(CamelModel, table=True):
    vendor_id: str = Field(primary_key=True, alias="vendorId")
    vendor_name: str = Field(alias="vendorName")
    vendor_account: str = Field(alias="vendorAccount")
