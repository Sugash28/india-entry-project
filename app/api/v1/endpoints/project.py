import os
import shutil
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.api import deps
from app.models.client import Client
from app.models.service_provider import ServiceProvider
from app.models.project import Project
from app.models.bid import Bid
from app.schemas import project as schemas
from app.schemas import bid as bid_schemas

router = APIRouter()

@router.post("/", response_model=schemas.Project)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: schemas.ProjectCreate,
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Create a new project.
    """
    project = Project(
        **project_in.model_dump(),
        client_id=current_client.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/", response_model=List[schemas.Project])
def get_projects(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all projects relevant to the current user.
    - For Clients: Projects they created.
    - For Service Providers: Projects they have accepted bids on.
    """
    if isinstance(current_user, Client):
        return db.query(Project).filter(Project.client_id == current_user.id).order_by(Project.created_at.desc()).all()
    else:
        # Get projects where SP has an accepted bid
        return db.query(Project).join(Bid).filter(
            Bid.service_provider_id == current_user.id,
            Bid.status == "accepted"
        ).order_by(Project.updated_at.desc()).all()

@router.get("/{project_id}", response_model=schemas.Project)
def get_project(
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific project.
    - Client must be the owner.
    - SP must have an accepted bid.
    """
    if isinstance(current_user, Client):
        project = db.query(Project).filter(Project.id == project_id, Project.client_id == current_user.id).first()
    else:
        project = db.query(Project).join(Bid).filter(
            Project.id == project_id,
            Bid.service_provider_id == current_user.id,
            Bid.status == "accepted"
        ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied",
        )
    return project

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int,
    project_in: schemas.ProjectUpdate,
    db: Session = Depends(deps.get_db),
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Update a project.
    """
    project = db.query(Project).filter(Project.id == project_id, Project.client_id == current_client.id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", response_model=schemas.Project)
def delete_project(
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Delete a project.
    """
    project = db.query(Project).filter(Project.id == project_id, Project.client_id == current_client.id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    db.delete(project)
    db.commit()
    return project

@router.get("/{project_id}/bids", response_model=List[bid_schemas.Bid])
def get_project_bids(
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Get all bids for a specific project owned by the client.
    """
    project = db.query(Project).filter(Project.id == project_id, Project.client_id == current_client.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.bids

@router.put("/{project_id}/bids/{bid_id}/accept", response_model=bid_schemas.Bid)
def accept_project_bid(
    project_id: int,
    bid_id: int,
    db: Session = Depends(deps.get_db),
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Accept a specific bid for a project. 
    This will set the bid status to 'accepted' and project status to 'in_progress'.
    All other bids for this project will be set to 'rejected'.
    """
    project = db.query(Project).filter(Project.id == project_id, Project.client_id == current_client.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    bid = db.query(Bid).filter(Bid.id == bid_id, Bid.project_id == project_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    project.status = "pending_contract"
    
    for b in project.bids:
        if b.id == bid_id:
            b.status = "accepted"
        else:
            b.status = "rejected"
            
    db.commit()
    db.refresh(bid)
    return bid

@router.post("/{project_id}/submit-work", response_model=schemas.Project)
async def submit_project_work(
    project_id: int,
    github_link: str = Form(...),
    work_pdf: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_sp: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Service provider submits their completed work (PDF + GitHub link).
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify this SP has an accepted bid for this project
    bid = db.query(Bid).filter(
        Bid.project_id == project_id, 
        Bid.service_provider_id == current_sp.id,
        Bid.status == "accepted"
    ).first()
    
    if not bid:
        raise HTTPException(status_code=403, detail="You do not have an accepted bid for this project")

    if project.status != "in_progress":
        raise HTTPException(status_code=400, detail="Project is not in a submittable state")

    # Save PDF
    UPLOAD_DIR = "static/uploads/submissions"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    file_extension = os.path.splitext(work_pdf.filename)[1]
    file_name = f"work_{project_id}_{current_sp.id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(work_pdf.file, buffer)

    project.submission_pdf_path = f"uploads/submissions/{file_name}"
    project.submission_github_link = github_link
    project.status = "awaiting_review"
    
    db.commit()
    db.refresh(project)
    return project

@router.put("/{project_id}/release-funds", response_model=schemas.Project)
def release_project_funds(
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Client releases escrowed funds and marks project as completed.
    """
    project = db.query(Project).filter(Project.id == project_id, Project.client_id == current_client.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != "awaiting_review":
        raise HTTPException(status_code=400, detail="Funds can only be released after work submission")

    project.escrow_funded = "released"
    project.status = "completed"
    
    db.commit()
    db.refresh(project)
    return project
