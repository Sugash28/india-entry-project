from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.client import Client
from app.models.project import Project
from app.schemas import project as schemas

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
