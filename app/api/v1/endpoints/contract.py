import os
import shutil
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.api import deps
from app.models.client import Client
from app.models.project import Project
from app.models.bid import Bid
from app.models.contract import Contract
from app.models.service_provider import ServiceProvider
from app.schemas import contract as schemas

router = APIRouter()

UPLOAD_DIR = "static/uploads/signatures"

@router.post("/", response_model=schemas.Contract)
async def create_contract(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int = Form(...),
    bid_id: int = Form(...),
    terms_and_conditions: str = Form(...),
    signature_photo: UploadFile = File(...),
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Create a new contract with terms and signature.
    """
    # Verify project ownership
    project = db.query(Project).filter(Project.id == project_id, Project.client_id == current_client.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify bid
    bid = db.query(Bid).filter(Bid.id == bid_id, Bid.project_id == project_id, Bid.status == "accepted").first()
    if not bid:
        raise HTTPException(status_code=400, detail="Bid must be accepted before creating a contract")

    # Check if contract already exists
    existing_contract = db.query(Contract).filter(Contract.bid_id == bid_id).first()
    if existing_contract:
        raise HTTPException(status_code=400, detail="Contract already exists for this bid")

    # Save signature photo
    file_extension = os.path.splitext(signature_photo.filename)[1]
    file_name = f"sig_{project_id}_{bid_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # Ensure directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(signature_photo.file, buffer)

    # Create contract
    contract = Contract(
        project_id=project_id,
        bid_id=bid_id,
        client_id=current_client.id,
        service_provider_id=bid.service_provider_id,
        terms_and_conditions=terms_and_conditions,
        client_signature_path=f"uploads/signatures/{file_name}",
        status="client_signed"
    )
    
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract

@router.get("/", response_model=List[schemas.Contract])
def get_contracts(
    db: Session = Depends(deps.get_db),
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Get all contracts for the current client.
    """
    return db.query(Contract).filter(Contract.client_id == current_client.id).order_by(Contract.created_at.desc()).all()

@router.get("/service-provider", response_model=List[schemas.Contract])
def get_sp_contracts(
    db: Session = Depends(deps.get_db),
    current_sp: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Get all contracts for the current service provider.
    """
    return db.query(Contract).filter(Contract.service_provider_id == current_sp.id).order_by(Contract.created_at.desc()).all()

@router.post("/{contract_id}/sign/service-provider", response_model=schemas.Contract)
async def sign_contract_sp(
    contract_id: int,
    signature_photo: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_sp: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Service provider signs an existing contract.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id, Contract.service_provider_id == current_sp.id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    if contract.status != "client_signed":
        raise HTTPException(status_code=400, detail="Contract is not in a signable state")

    # Save signature photo
    file_extension = os.path.splitext(signature_photo.filename)[1]
    file_name = f"sig_sp_{contract.project_id}_{contract.bid_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(signature_photo.file, buffer)

    contract.service_provider_signature_path = f"uploads/signatures/{file_name}"
    contract.status = "fully_signed"
    
    db.commit()
    db.refresh(contract)
    return contract
