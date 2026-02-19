from typing import Optional
from app.models.base import CamelModel

# Site
class SiteBase(CamelModel):
    site_code: str = None
    site_name: str = None

class SiteCreate(SiteBase):
    site_code: str
    site_name: str

class SiteUpdate(SiteBase):
    pass

# Asset Category
class AssetCategoryBase(CamelModel):
    name: str = None
    description: Optional[str] = None

class AssetCategoryCreate(AssetCategoryBase):
    name: str

class AssetCategoryUpdate(AssetCategoryBase):
    pass

# Asset SubCategory
class AssetSubCategoryBase(CamelModel):
    name: str = None
    useful_life_years: int = None
    description: Optional[str] = None
    category_id: str = None

class AssetSubCategoryCreate(AssetSubCategoryBase):
    name: str
    useful_life_years: int
    category_id: str

class AssetSubCategoryUpdate(AssetSubCategoryBase):
    pass

# Location
class LocationBase(CamelModel):
    location_name: str = None
    location_name_code: str = None
    site_id: str = None

class LocationCreate(LocationBase):
    location_name: str
    location_name_code: str
    site_id: str

class LocationUpdate(LocationBase):
    pass

# Project
class ProjectBase(CamelModel):
    project_code: str = None
    name: str = None

class ProjectCreate(ProjectBase):
    project_code: str
    name: str

class ProjectUpdate(ProjectBase):
    pass

# Vendor
class VendorBase(CamelModel):
    vendor_name: str = None
    vendor_account: str = None

class VendorCreate(VendorBase):
    vendor_name: str
    vendor_account: str

class VendorUpdate(VendorBase):
    pass

# Legal Entity
class LegalEntityBase(CamelModel):
    legal_entity_code: str = None
    legal_entity_name: str = None

class LegalEntityCreate(LegalEntityBase):
    legal_entity_code: str
    legal_entity_name: str

class LegalEntityUpdate(LegalEntityBase):
    pass

# Funding Source
class FundingSourceBase(CamelModel):
    name: str = None
    description: Optional[str] = None

class FundingSourceCreate(FundingSourceBase):
    name: str

class FundingSourceUpdate(FundingSourceBase):
    pass
