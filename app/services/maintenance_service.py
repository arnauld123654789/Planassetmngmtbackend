import uuid
from datetime import datetime
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.operations import Maintenance
from app.schemas.operations import MaintenanceCreate, MaintenanceUpdate

class MaintenanceService:
    @staticmethod
    def create_maintenance(session: Session, maintenance_in: MaintenanceCreate) -> Maintenance:
        """Create a new maintenance record"""
        from datetime import datetime, date as date_type
        
        maintenance_id = str(uuid.uuid4())
        
        # Parse date string to date object if it's a string
        maintenance_date = maintenance_in.date_of_maintenance
        if isinstance(maintenance_date, str):
            maintenance_date = datetime.strptime(maintenance_date, "%Y-%m-%d").date()
        
        maintenance = Maintenance(
            maintenance_id=maintenance_id,
            asset_id=maintenance_in.asset_id,
            date_of_maintenance=maintenance_date,
            type=maintenance_in.type,
            provider=maintenance_in.provider,
            cost=maintenance_in.cost,
            notes=maintenance_in.notes
        )
        
        session.add(maintenance)
        session.commit()
        session.refresh(maintenance)
        return maintenance
    
    @staticmethod
    def list_maintenance(session: Session, skip: int = 0, limit: int = 100, asset_id: str = None) -> list[Maintenance]:
        """List maintenance records, optionally filtered by asset"""
        query = select(Maintenance)
        
        if asset_id:
            query = query.where(Maintenance.asset_id == asset_id)
        
        query = query.offset(skip).limit(limit).order_by(Maintenance.date_of_maintenance.desc())
        
        return session.exec(query).all()
    
    @staticmethod
    def get_maintenance(session: Session, maintenance_id: str) -> Maintenance:
        """Get single maintenance record"""
        maintenance = session.get(Maintenance, maintenance_id)
        if not maintenance:
            raise HTTPException(status_code=404, detail="Maintenance record not found")
        return maintenance
    
    @staticmethod
    def update_maintenance(session: Session, maintenance_id: str, maintenance_update: MaintenanceUpdate) -> Maintenance:
        """Update maintenance record"""
        maintenance = session.get(Maintenance, maintenance_id)
        if not maintenance:
            raise HTTPException(status_code=404, detail="Maintenance record not found")
        
        update_data = maintenance_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(maintenance, key, value)
        
        session.add(maintenance)
        session.commit()
        session.refresh(maintenance)
        return maintenance
