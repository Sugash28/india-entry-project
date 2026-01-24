from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.client import Client
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
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Get all projects for the current client.
    """
    return db.query(Project).filter(Project.client_id == current_client.id).order_by(Project.created_at.desc()).all()

@router.get("/{project_id}", response_model=schemas.Project)
def get_project(
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Get a specific project.
    """
    project = db.query(Project).filter(Project.id == project_id, Project.client_id == current_client.id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
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
    
    project.status = "in_progress"
    
    for b in project.bids:
        if b.id == bid_id:
            b.status = "accepted"
        else:
            b.status = "rejected"
            
    db.commit()
    db.refresh(bid)
    return bid
