from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select

from app.api.deps import SessionDep, CurrentUser
from app.models.operations import Maintenance
from app.schemas.operations import MaintenanceCreate, MaintenanceRead, MaintenanceUpdate
from app.services.maintenance_service import MaintenanceService

router = APIRouter()

@router.post("/", response_model=MaintenanceRead)
def create_maintenance(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    maintenance_in: MaintenanceCreate,
) -> Any:
    """
    Schedule/record asset maintenance. IT Admin or Logistician only.
    """
    return MaintenanceService.create_maintenance(session, maintenance_in)

@router.get("/", response_model=List[MaintenanceRead])
def list_maintenance(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    asset_id: Optional[str] = None,
) -> Any:
    """
    List maintenance records. Filter by asset_id optional.
    """
    return MaintenanceService.list_maintenance(session, skip, limit, asset_id)

@router.get("/{maintenance_id}", response_model=MaintenanceRead)
def get_maintenance(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    maintenance_id: str,
) -> Any:
    """
    Get single maintenance record.
    """
    return MaintenanceService.get_maintenance(session, maintenance_id)

@router.patch("/{maintenance_id}", response_model=MaintenanceRead)
def update_maintenance(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    maintenance_id: str,
    maintenance_update: MaintenanceUpdate,
) -> Any:
    """
    Update maintenance record (notes, cost, etc).
    """
    return MaintenanceService.update_maintenance(session, maintenance_id, maintenance_update)
