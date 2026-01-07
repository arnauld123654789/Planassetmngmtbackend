import os
import shutil
import uuid
from typing import List
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlmodel import Session, select
from app.models.operations import Disposal, Transfer
from app.models.asset import Asset
from app.models.enums import DisposalStatus, TransferStatus, UserRole, AssetStatus
from app.services.pdf_service import PDFService
from app.models.user import User
from app.models.master_data import Location
from app.schemas.operations import DisposalCreate, TransferCreate
from app.core.config import settings

class OperationService:
    @staticmethod
    def create_disposal(session: Session, disposal_in: DisposalCreate, file: UploadFile, user_id: str) -> List[Disposal]:
        # Save document ONCE
        file_ext = os.path.splitext(file.filename)[1]
        if not file_ext:
            file_ext = ".pdf"
            
        unique_id = uuid.uuid4().hex
        filename = f"disposal_{unique_id}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        created_disposals = []
        for asset_id in disposal_in.asset_ids:
            disposal = Disposal(
                disposal_id=uuid.uuid4().hex,
                asset_id=asset_id,
                type_of_disposal=disposal_in.type_of_disposal,
                reason=disposal_in.reason,
                requested_by=user_id,
                requested_at=datetime.now(),
                status=DisposalStatus.PENDING,
                document_path=filename
            )
            session.add(disposal)
            created_disposals.append(disposal)
            
        session.commit()
        for d in created_disposals:
            session.refresh(d)
        return created_disposals

    @staticmethod
    def approve_disposal(session: Session, disposal_id: str, approved: bool) -> Disposal:
        disposal = session.get(Disposal, disposal_id)
        if not disposal:
            raise HTTPException(status_code=404, detail="Disposal not found")
            
        if approved:
            disposal.status = DisposalStatus.APPROVED
            # Update Asset Status to DISPOSED
            asset = session.get(Asset, disposal.asset_id)
            if asset:
                asset.asset_status = AssetStatus.DISPOSED
                session.add(asset)
        else:
            disposal.status = DisposalStatus.REJECTED
            
        session.add(disposal)
        session.commit()
        session.refresh(disposal)
        return disposal

    def create_transfer(session: Session, transfer_in: TransferCreate, user_roles: List[str], user_id: str) -> List[Transfer]:
        # Check if user has Logistician role (or IT Admin who can do everything? - user requirement imply cumulate privileges)
        # But strictly, requirement says "Only Logisticians can initiate" in docstring. 
        # However "cumulate privileges" means if I am Logistician AND Manager, I can initiate.
        
        # Check if 'Logistician' is in the list of roles
        is_logistician = any(UserRole.LOGISTICIAN.value == role or UserRole.LOGISTICIAN.value in str(role) for role in user_roles)
        
        if not is_logistician:
            raise HTTPException(status_code=403, detail="Only Logisticians can initiate transfers")
            
        created_transfers = []
        for asset_id in transfer_in.asset_ids:
            transfer = Transfer(
                transfer_id=uuid.uuid4().hex,
                asset_id=asset_id,
                status=TransferStatus.PENDING,
                requested_at=datetime.now(),
                from_user_id=transfer_in.from_user_id,
                to_user_id=transfer_in.to_user_id,
                from_location_id=transfer_in.from_location_id,
                to_location_id=transfer_in.to_location_id,
                reason=transfer_in.reason,
                initiated_by=user_id
            )
            session.add(transfer)
            created_transfers.append(transfer)
            
        session.commit()
        for t in created_transfers:
            session.refresh(t)
        return created_transfers

    @staticmethod
    def approve_transfer(session: Session, transfer_id: str, approved: bool, user_roles: List[str], approver_name: str):
        # Check if user has SCM or IT Admin role
        can_approve = any(
            role in [UserRole.SUPPLY_CHAIN_MANAGER.value, UserRole.IT_ADMIN.value] or 
            any(allowed in str(role) for allowed in [UserRole.SUPPLY_CHAIN_MANAGER.value, UserRole.IT_ADMIN.value])
            for role in user_roles
        )

        if not can_approve:
             raise HTTPException(status_code=403, detail="Only Supply Chain Managers or IT Admins can approve transfers")

        transfer = session.get(Transfer, transfer_id)
        if not transfer:
            raise HTTPException(status_code=404, detail="Transfer not found")
            
        pdf_path = None
        
        if approved:
            transfer.status = TransferStatus.APPROVED
            
            try:
                # === Generate PDF ===
                # 1. Fetch Related Data
                asset = session.get(Asset, transfer.asset_id)
                initiator = session.get(User, transfer.initiated_by)
                initiator_name = initiator.full_name if initiator else "Unknown"
                
                # From
                from_name = ""
                from_loc = ""
                if transfer.from_user_id:
                     u = session.get(User, transfer.from_user_id)
                     from_name = u.full_name if u else "Unknown User"
                if transfer.from_location_id:
                     l = session.get(Location, transfer.from_location_id)
                     from_loc = l.location_name if l else "Unknown Loc"
                     
                # To
                to_name = ""
                to_loc = ""
                if transfer.to_user_id:
                     u2 = session.get(User, transfer.to_user_id)
                     to_name = u2.full_name if u2 else "Unknown User"
                if transfer.to_location_id:
                     l2 = session.get(Location, transfer.to_location_id)
                     to_loc = l2.location_name if l2 else "Unknown Loc"

                if asset:
                    # Use current time as approval date
                    approval_date = datetime.now()
                    
                    # === UPDATE ASSET LOCATION/CUSTODIAN ===
                    if transfer.to_user_id:
                        asset.custodian_id = transfer.to_user_id
                    if transfer.to_location_id:
                        asset.location_id = transfer.to_location_id
                    
                    session.add(asset) # Stage asset update
                    
                    pdf_path = PDFService.generate_transfer_pdf(
                        transfer, asset, initiator_name, 
                        from_name, to_name, from_loc, to_loc,
                        approver_name, approval_date
                    )
                    print(f"Transfer PDF generated at: {pdf_path}")
            except Exception as e:
                print(f"Error updating asset or generating PDF for transfer {transfer_id}: {e}")
                # Note: We continue to commit the transfer status update even if PDF generation fails,
                # but because we added asset to session, it will also be committed below.
                # If PDF fails, we still want the transfer approved and asset moved?
                # Usually yes.
                pass
                
        else:
            transfer.status = TransferStatus.REJECTED
            
        session.add(transfer)
        session.commit()
        session.refresh(transfer)
        
        # Return dict with both transfer and PDF path when approved
        if approved and pdf_path:
            return {"transfer": transfer, "pdf_path": pdf_path}
        
        return transfer
