from typing import Any, List
import json
from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends
from fastapi.responses import FileResponse
from sqlmodel import select

from app.api.deps import SessionDep, CurrentUser
from app.models.operations import Disposal, Transfer
from app.schemas.operations import DisposalCreate, DisposalRead, DisposalUpdate, TransferCreate, TransferRead, TransferUpdate
from app.services.operation_service import OperationService

router = APIRouter()

# --- Disposals ---

@router.post("/disposals/", response_model=List[DisposalRead])
def create_disposal(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    disposal_data: str = Form(...),
    file: UploadFile = File(...)
) -> Any:
    """
    Create new disposal request(s) with a mandatory justification document.
    Supports bulk creation via `assetIds` list.
    """
    try:
        data = json.loads(disposal_data)
        disposal_in = DisposalCreate.model_validate(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid disposal data JSON: {str(e)}")
        
    return OperationService.create_disposal(session, disposal_in, file, current_user.user_id)

@router.get("/disposals/", response_model=List[DisposalRead])
def read_disposals(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all disposal requests.
    """
    return session.exec(select(Disposal).offset(skip).limit(limit)).all()

@router.patch("/disposals/{disposal_id}/status", response_model=DisposalRead)
def update_disposal_status(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    disposal_id: str,
    status_update: DisposalUpdate,
) -> Any:
    """
    Approve or Reject a disposal request.
    """
    approved = status_update.status == "APPROVED"
    return OperationService.approve_disposal(session, disposal_id, approved)

# --- Transfers ---

@router.post("/transfers/", response_model=List[TransferRead])
def create_transfer(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    transfer_in: TransferCreate,
) -> Any:
    """
    Create new transfer request(s). Only Logisticians can initiate.
    Supports bulk creation via `assetIds` list.
    """
    return OperationService.create_transfer(session, transfer_in, current_user.role, current_user.user_id)

@router.get("/transfers/", response_model=List[TransferRead])
def read_transfers(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all transfer requests.
    """
    return session.exec(select(Transfer).offset(skip).limit(limit)).all()

@router.patch("/transfers/{transfer_id}/status")
def update_transfer_status(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    transfer_id: str,
    status_update: TransferUpdate,
) -> Any:
    """
    Approve or Reject a transfer request. Only SCM or IT Admin.
    When approved, returns the generated PDF document.
    """
    approved = status_update.status == "APPROVED"
    result = OperationService.approve_transfer(session, transfer_id, approved, current_user.role)
    
    # If approved and PDF was generated, return the file
    if approved and isinstance(result, dict) and "pdf_path" in result:
        import os
        pdf_path = result["pdf_path"]
        if os.path.exists(pdf_path):
            filename = f"transfer_{transfer_id}.pdf"
            return FileResponse(
                path=pdf_path,
                media_type="application/pdf",
                filename=filename
            )
    
    # Otherwise return the transfer object
    return result if not isinstance(result, dict) else result.get("transfer")

@router.get("/transfers/{transfer_id}/good-issue-note")
def get_good_issue_note(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    transfer_id: str,
) -> Any:
    """
    Generate and download Good Issue Note PDF for an approved transfer.
    """
    from app.models.user import User
    from app.models.master_data import Location
    from app.models.asset import Asset
    from app.services.pdf_service import PDFService
    import os
    import tempfile
    
    transfer = session.get(Transfer, transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    if transfer.status != "APPROVED":
        raise HTTPException(status_code=400, detail="Can only generate Good Issue Note for approved transfers")
    
    # Fetch related data
    asset = session.get(Asset, transfer.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    initiator = session.get(User, transfer.initiated_by)
    initiator_name = initiator.full_name if initiator else "Unknown"
    
    from_name = ""
    from_loc = ""
    if transfer.from_user_id:
        u = session.get(User, transfer.from_user_id)
        from_name = u.full_name if u else "Unknown User"
    if transfer.from_location_id:
        l = session.get(Location, transfer.from_location_id)
        from_loc = l.location_name if l else "Unknown Loc"
    
    to_name = ""
    to_loc = ""
    if transfer.to_user_id:
        u2 = session.get(User, transfer.to_user_id)
        to_name = u2.full_name if u2 else "Unknown User"
    if transfer.to_location_id:
        l2 = session.get(Location, transfer.to_location_id)
        to_loc = l2.location_name if l2 else "Unknown Loc"
    
    # Generate PDF in temp location
    pdf_path = PDFService.generate_transfer_pdf(
        transfer, asset, initiator_name,
        from_name, to_name, from_loc, to_loc
    )
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
    
    filename = f"good_issue_note_{transfer_id}.pdf"
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename
    )

# --- Asset Holder Forms ---

@router.get("/users/{user_id}/asset-holder-form")
def get_asset_holder_form(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_id: str,
) -> Any:
    """
    Generate and download Asset Holder Form PDF showing all assets assigned to a user.
    """
    from app.models.user import User
    from app.models.asset import Asset
    from app.services.pdf_service import PDFService
    import os
    
    # Fetch user
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fetch all assets where custodian_id = user_id
    assets = session.exec(
        select(Asset).where(Asset.custodian_id == user_id)
    ).all()
    
    # Generate PDF
    pdf_path = PDFService.generate_asset_holder_form(
        user_name=user.full_name,
        user_id=user.user_id,
        assets=list(assets)
    )
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
    
    filename = f"asset_holder_form_{user_id}.pdf"
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename
    )


