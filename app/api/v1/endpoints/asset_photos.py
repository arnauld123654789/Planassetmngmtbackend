from typing import Any, List
import shutil
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Path
from sqlmodel import select

from app.api.deps import SessionDep, CurrentUser
from app.models.asset import Asset
from app.models.asset_photo import AssetPhoto
from app.schemas.asset_photo import AssetPhotoRead
from app.core.config import settings

from app.services.photo_service import PhotoService

router = APIRouter()

@router.post("/{asset_id}/photos", response_model=AssetPhotoRead)
def upload_asset_photo(
    *,
    session: SessionDep,
    asset_id: str,
    file: UploadFile = File(...),
    current_user: CurrentUser,
) -> Any:
    """
    Upload a photo for an asset. Max 3 photos per asset.
    """
    asset = session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db_photo = PhotoService.save_photo(session, asset_id, file)
    if not db_photo:
        raise HTTPException(status_code=400, detail="Maximum of 3 photos allowed per asset")
        
    session.commit()
    session.refresh(db_photo)
    
    return AssetPhotoRead(
        id=db_photo.id,
        asset_id=db_photo.asset_id,
        filename=db_photo.filename,
        is_profile=db_photo.is_profile,
        created_at=db_photo.created_at,
        url=PhotoService.get_photo_url(db_photo.filename)
    )

@router.delete("/{asset_id}/photos/{photo_id}")
def delete_asset_photo(
    *,
    session: SessionDep,
    asset_id: str,
    photo_id: int,
    current_user: CurrentUser,
) -> Any:
    photo = session.get(AssetPhoto, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    if photo.asset_id != asset_id:
        raise HTTPException(status_code=400, detail="Photo does not belong to this asset")
        
    # delete from file system
    file_path = os.path.join(settings.UPLOAD_DIR, photo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    session.delete(photo)
    session.commit()
    
    return {"ok": True}

@router.put("/{asset_id}/photos/{photo_id}/profile", response_model=AssetPhotoRead)
def set_profile_picture(
    *,
    session: SessionDep,
    asset_id: str,
    photo_id: int,
    current_user: CurrentUser,
) -> Any:
    """
    Set a specific photo as the profile picture for the asset.
    """
    target_photo = session.get(AssetPhoto, photo_id)
    if not target_photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    if target_photo.asset_id != asset_id:
        raise HTTPException(status_code=400, detail="Photo does not belong to this asset")
        
    # Unset is_profile for all other photos of this asset
    statement = select(AssetPhoto).where(AssetPhoto.asset_id == asset_id)
    all_photos = session.exec(statement).all()
    
    for photo in all_photos:
        if photo.id == photo_id:
            photo.is_profile = True
        else:
            photo.is_profile = False
        session.add(photo)
        
    session.commit()
    session.refresh(target_photo)
    
    photo_read = AssetPhotoRead(
        id=target_photo.id,
        asset_id=target_photo.asset_id,
        filename=target_photo.filename,
        is_profile=target_photo.is_profile,
        created_at=target_photo.created_at,
        url=f"/static/{target_photo.filename}"
    )
    return photo_read

@router.get("/{asset_id}/photos", response_model=List[AssetPhotoRead])
def get_asset_photos(
    *,
    session: SessionDep,
    asset_id: str,
    current_user: CurrentUser,
) -> Any:
    statement = select(AssetPhoto).where(AssetPhoto.asset_id == asset_id)
    photos = session.exec(statement).all()
    
    return [
        AssetPhotoRead(
            id=p.id,
            asset_id=p.asset_id,
            filename=p.filename,
            is_profile=p.is_profile,
            created_at=p.created_at,
            url=f"/static/{p.filename}"
        ) for p in photos
    ]
