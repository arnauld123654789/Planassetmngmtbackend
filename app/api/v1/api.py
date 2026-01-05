from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, assets, master_data

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(master_data.router, prefix="/master-data", tags=["master-data"])
from app.api.v1.endpoints import asset_photos
api_router.include_router(asset_photos.router, prefix="/assets", tags=["asset-photos"])
from app.api.v1.endpoints import verifications
api_router.include_router(verifications.router, prefix="/verifications", tags=["verifications"])
from app.api.v1.endpoints import operations
api_router.include_router(operations.router, prefix="/operations", tags=["operations"])
from app.api.v1.endpoints import maintenance
api_router.include_router(maintenance.router, prefix="/operations/maintenance", tags=["maintenance"])
from app.api.v1.endpoints import reports
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
