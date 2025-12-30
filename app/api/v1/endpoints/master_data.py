from typing import Any, List
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import SessionDep, CurrentUser
from app.models.master_data import AssetCategory, AssetSubCategory, Location, Project, Vendor, LegalEntity
from app.schemas.master_data import (
    AssetCategoryCreate, AssetCategoryUpdate,
    AssetSubCategoryCreate, AssetSubCategoryUpdate,
    LocationCreate, LocationUpdate,
    ProjectCreate, ProjectUpdate,
    VendorCreate, VendorUpdate,
    LegalEntityCreate, LegalEntityUpdate
)

router = APIRouter()

@router.get("/categories", response_model=List[AssetCategory])
def read_categories(session: SessionDep, current_user: CurrentUser) -> Any:
    return session.exec(select(AssetCategory)).all()

@router.get("/sub-categories", response_model=List[AssetSubCategory])
def read_sub_categories(session: SessionDep, current_user: CurrentUser) -> Any:
    return session.exec(select(AssetSubCategory)).all()

@router.get("/locations", response_model=List[Location])
def read_locations(session: SessionDep, current_user: CurrentUser) -> Any:
    return session.exec(select(Location)).all()

@router.get("/projects", response_model=List[Project])
def read_projects(session: SessionDep, current_user: CurrentUser) -> Any:
    return session.exec(select(Project)).all()

@router.get("/vendors", response_model=List[Vendor])
def read_vendors(session: SessionDep, current_user: CurrentUser) -> Any:
    return session.exec(select(Vendor)).all()

@router.post("/categories", response_model=AssetCategory)
def create_category(
    *,
    session: SessionDep,
    category_in: AssetCategoryCreate,
    current_user: CurrentUser,
) -> Any:
    import uuid
    category = AssetCategory.model_validate(
        category_in, update={"category_id": str(uuid.uuid4())}
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.put("/categories/{category_id}", response_model=AssetCategory)
def update_category(
    *,
    session: SessionDep,
    category_id: str,
    category_in: AssetCategoryUpdate,
    current_user: CurrentUser,
) -> Any:
    category = session.get(AssetCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
        
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.delete("/categories/{category_id}", response_model=AssetCategory)
def delete_category(
    session: SessionDep,
    category_id: str,
    current_user: CurrentUser,
) -> Any:
    category = session.get(AssetCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return category

# SubCategories
@router.post("/sub-categories", response_model=AssetSubCategory)
def create_sub_category(
    *,
    session: SessionDep,
    sub_category_in: AssetSubCategoryCreate,
    current_user: CurrentUser,
) -> Any:
    import uuid
    sub_category = AssetSubCategory.model_validate(
        sub_category_in, update={"sub_category_id": str(uuid.uuid4())}
    )
    session.add(sub_category)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Category not found. Please provide a valid categoryId."
        )
    session.refresh(sub_category)
    return sub_category

@router.put("/sub-categories/{sub_category_id}", response_model=AssetSubCategory)
def update_sub_category(
    *,
    session: SessionDep,
    sub_category_id: str,
    sub_category_in: AssetSubCategoryUpdate,
    current_user: CurrentUser,
) -> Any:
    sub_category = session.get(AssetSubCategory, sub_category_id)
    if not sub_category:
        raise HTTPException(status_code=404, detail="SubCategory not found")
    
    update_data = sub_category_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sub_category, key, value)
        
    session.add(sub_category)
    session.commit()
    session.refresh(sub_category)
    return sub_category

@router.delete("/sub-categories/{sub_category_id}", response_model=AssetSubCategory)
def delete_sub_category(
    session: SessionDep,
    sub_category_id: str,
    current_user: CurrentUser,
) -> Any:
    sub_category = session.get(AssetSubCategory, sub_category_id)
    if not sub_category:
        raise HTTPException(status_code=404, detail="SubCategory not found")
    session.delete(sub_category)
    session.commit()
    return sub_category

# Locations
@router.post("/locations", response_model=Location)
def create_location(
    *,
    session: SessionDep,
    location_in: LocationCreate,
    current_user: CurrentUser,
) -> Any:
    import uuid
    location = Location.model_validate(
        location_in, update={"location_id": str(uuid.uuid4())}
    )
    session.add(location)
    session.commit()
    session.refresh(location)
    return location

@router.put("/locations/{location_id}", response_model=Location)
def update_location(
    *,
    session: SessionDep,
    location_id: str,
    location_in: LocationUpdate,
    current_user: CurrentUser,
) -> Any:
    location = session.get(Location, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    update_data = location_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(location, key, value)
        
    session.add(location)
    session.commit()
    session.refresh(location)
    return location

@router.delete("/locations/{location_id}", response_model=Location)
def delete_location(
    session: SessionDep,
    location_id: str,
    current_user: CurrentUser,
) -> Any:
    location = session.get(Location, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    session.delete(location)
    session.commit()
    return location

# Projects
@router.post("/projects", response_model=Project)
def create_project(
    *,
    session: SessionDep,
    project_in: ProjectCreate,
    current_user: CurrentUser,
) -> Any:
    import uuid
    project = Project.model_validate(
        project_in, update={"project_id": str(uuid.uuid4())}
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.put("/projects/{project_id}", response_model=Project)
def update_project(
    *,
    session: SessionDep,
    project_id: str,
    project_in: ProjectUpdate,
    current_user: CurrentUser,
) -> Any:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
        
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.delete("/projects/{project_id}", response_model=Project)
def delete_project(
    session: SessionDep,
    project_id: str,
    current_user: CurrentUser,
) -> Any:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(project)
    session.commit()
    return project

# Vendors
@router.post("/vendors", response_model=Vendor)
def create_vendor(
    *,
    session: SessionDep,
    vendor_in: VendorCreate,
    current_user: CurrentUser,
) -> Any:
    import uuid
    vendor = Vendor.model_validate(
        vendor_in, update={"vendor_id": str(uuid.uuid4())}
    )
    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor

@router.put("/vendors/{vendor_id}", response_model=Vendor)
def update_vendor(
    *,
    session: SessionDep,
    vendor_id: str,
    vendor_in: VendorUpdate,
    current_user: CurrentUser,
) -> Any:
    vendor = session.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    update_data = vendor_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vendor, key, value)
        
    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor

@router.delete("/vendors/{vendor_id}", response_model=Vendor)
def delete_vendor(
    session: SessionDep,
    vendor_id: str,
    current_user: CurrentUser,
) -> Any:
    vendor = session.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    session.delete(vendor)
    session.commit()
    return vendor

# Legal Entities
@router.post("/legal-entities", response_model=LegalEntity)
def create_legal_entity(
    *,
    session: SessionDep,
    legal_entity_in: LegalEntityCreate,
    current_user: CurrentUser,
) -> Any:
    import uuid
    legal_entity = LegalEntity.model_validate(
        legal_entity_in, update={"legal_entity_id": str(uuid.uuid4())}
    )
    session.add(legal_entity)
    session.commit()
    session.refresh(legal_entity)
    return legal_entity

@router.put("/legal-entities/{legal_entity_id}", response_model=LegalEntity)
def update_legal_entity(
    *,
    session: SessionDep,
    legal_entity_id: str,
    legal_entity_in: LegalEntityUpdate,
    current_user: CurrentUser,
) -> Any:
    legal_entity = session.get(LegalEntity, legal_entity_id)
    if not legal_entity:
        raise HTTPException(status_code=404, detail="Legal Entity not found")
    
    update_data = legal_entity_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(legal_entity, key, value)
        
    session.add(legal_entity)
    session.commit()
    session.refresh(legal_entity)
    return legal_entity

@router.delete("/legal-entities/{legal_entity_id}", response_model=LegalEntity)
def delete_legal_entity(
    session: SessionDep,
    legal_entity_id: str,
    current_user: CurrentUser,
) -> Any:
    legal_entity = session.get(LegalEntity, legal_entity_id)
    if not legal_entity:
        raise HTTPException(status_code=404, detail="Legal Entity not found")
    session.delete(legal_entity)
    session.commit()
    return legal_entity
