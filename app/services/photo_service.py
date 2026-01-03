import os
import shutil
import uuid
from typing import List
from fastapi import UploadFile
from sqlmodel import Session, select
from app.models.asset_photo import AssetPhoto
from app.models.asset import Asset
from app.core.config import settings

class PhotoService:
    @staticmethod
    def save_photo(session: Session, asset_id: str, file: UploadFile) -> AssetPhoto:
        # Check current photo count
        statement = select(AssetPhoto).where(AssetPhoto.asset_id == asset_id)
        existing_photos = session.exec(statement).all()
        
        if len(existing_photos) >= 3:
            return None # Or raise exception, but letting the caller handle it for unified flow
            
        # Generate filename
        file_ext = os.path.splitext(file.filename)[1]
        if not file_ext:
            file_ext = ".jpg"
            
        unique_id = uuid.uuid4().hex
        filename = f"{asset_id}_{unique_id}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Save file
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Determine if this should be the profile picture
        is_profile = len(existing_photos) == 0
        
        db_photo = AssetPhoto(
            asset_id=asset_id,
            filename=filename,
            is_profile=is_profile
        )
        session.add(db_photo)
        return db_photo

    @staticmethod
    def get_photo_url(filename: str) -> str:
        return f"/static/{filename}"
