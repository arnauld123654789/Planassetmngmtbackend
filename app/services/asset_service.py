from sqlmodel import Session, select, col
from app.models.asset import Asset
from app.models.master_data import LegalEntity, Location, Project

class AssetService:
    @staticmethod
    def generate_scom_id(session: Session, legal_entity_id: str, location_id: str, project_id: str) -> str:
        # Fetch codes
        legal_entity = session.get(LegalEntity, legal_entity_id)
        location = session.get(Location, location_id)
        project = session.get(Project, project_id)
        
        if not legal_entity or not location or not project:
            raise ValueError("Invalid Entity, Location, or Project ID")

        prefix = f"{legal_entity.legal_entity_code}-{location.location_code}-{project.project_code}"
        
        # Find max sequence for this prefix
        # We look for Assets starting with prefix
        # SCOM ID format: PREFIX-SEQUENCE (6 digits)
        # e.g. EGYI-2033-EGOO491-000001
        
        query = select(Asset.scom_asset_id).where(col(Asset.scom_asset_id).startswith(prefix))
        ids = session.exec(query).all()
        
        max_seq = 0
        for s_id in ids:
            try:
                # Extract last 6 digits
                parts = s_id.split("-")
                seq = int(parts[-1])
                if seq > max_seq:
                    max_seq = seq
            except (ValueError, IndexError):
                continue
                
        new_seq = max_seq + 1
        return f"{prefix}-{new_seq:06d}"
