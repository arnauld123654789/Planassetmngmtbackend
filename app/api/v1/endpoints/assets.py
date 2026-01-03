from typing import Any, List
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
import logging
import json

from app.api.deps import SessionDep, CurrentUser
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate
from app.services.asset_service import AssetService
from app.services.photo_service import PhotoService

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
    asset_data: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    current_user: CurrentUser,
) -> Any:
    # 1. Parse JSON from form data
    try:
        asset_dict = json.loads(asset_data)
        asset_in = AssetCreate.model_validate(asset_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid asset data JSON: {str(e)}")

    # 2. Generate SCOM ID
    try:
        scom_id = AssetService.generate_scom_id(
            session, 
            asset_in.legal_entity_id, 
            asset_in.location_id, 
            asset_in.project_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 3. Create the Asset with automated verification tracking
    from datetime import date
    asset = Asset.model_validate(asset_in, update={
        "scom_asset_id": scom_id,
        "last_physical_verification": current_user.full_name,
        "date_of_last_physical_verification": date.today()
    })
    session.add(asset)
    
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        error_msg = str(e)
        logging.error(f"IntegrityError creating asset: {error_msg}")
        
        if "UNIQUE constraint failed" in error_msg or "duplicate key value violates unique constraint" in error_msg:
            if "physicalAssetTagNumber" in error_msg or "physical_asset_tag_number" in error_msg:
                raise HTTPException(
                    status_code=400,
                    detail="An asset with this Physical Asset Tag Number already exists. Tag numbers must be unique."
                )
        
        raise HTTPException(
            status_code=400, 
            detail="Invalid database operation. Please ensure all IDs (location, project, category, etc.) are valid and unique constraints are not violated."
        )
    
    session.refresh(asset)
    
    # 4. Handle photos if any
    if files:
        for file in files[:3]: # Ensure max 3
            if file.filename: # check if actually a file was uploaded
                PhotoService.save_photo(session, asset.scom_asset_id, file)
        
        session.commit()
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
