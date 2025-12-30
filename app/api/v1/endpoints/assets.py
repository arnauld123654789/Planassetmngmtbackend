from typing import Any, List
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import SessionDep, CurrentUser
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate
from app.services.asset_service import AssetService

router = APIRouter()

@router.get("/", response_model=List[Asset])
def read_assets(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return session.exec(select(Asset).offset(skip).limit(limit)).all()

@router.get("/{asset_id}", response_model=Asset)
def read_asset(
    asset_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    asset = session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.post("/", response_model=Asset)
def create_asset(
    *,
    session: SessionDep,
    asset_in: AssetCreate,
    current_user: CurrentUser,
) -> Any:
    # Generate SCOM ID
    try:
        scom_id = AssetService.generate_scom_id(
            session, 
            asset_in.legal_entity_id, 
            asset_in.location_id, 
            asset_in.project_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    asset = Asset.model_validate(asset_in, update={"scom_asset_id": scom_id})
    session.add(asset)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        # Log the actual error for debugging
        logging.error(f"IntegrityError creating asset: {e}")
        raise HTTPException(
            status_code=400, 
            detail="Invalid Foreign Key ID provided (e.g., locationId, projectId, categoryId). Please ensure all IDs exist."
        )
    session.refresh(asset)
    return asset

@router.put("/{asset_id}", response_model=Asset)
def update_asset(
    *,
    session: SessionDep,
    asset_id: str,
    asset_in: AssetUpdate,
    current_user: CurrentUser,
) -> Any:
    asset = session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    update_data = asset_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(asset, key, value)
        
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset

@router.delete("/{asset_id}", response_model=Asset)
def delete_asset(
    session: SessionDep,
    asset_id: str,
    current_user: CurrentUser,
) -> Any:
    asset = session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    session.delete(asset)
    session.commit()
    return asset
