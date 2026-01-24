from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.api import deps
from app.models.service_provider import (
    ServiceProvider, PortfolioProject, WorkExperience, Education, Certification
)
from app.models.project import Project
from app.models.bid import Bid
from app.schemas import service_provider as schemas
from app.schemas import bid as bid_schemas

router = APIRouter()

@router.get("/my-bids", response_model=List[bid_schemas.Bid])
def get_my_bids(
    db: Session = Depends(deps.get_db),
    current_service_provider: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Get all bids submitted by the current service provider.
    """
    return db.query(Bid).filter(Bid.service_provider_id == current_service_provider.id).all()

def calculate_completion_percentage(sp: ServiceProvider) -> int:
    score = 0
    
    if sp.professional_title and sp.hourly_rate and sp.skills:
        score += 20
    
    
    if sp.kyc_file:
        score += 20
        
    
    if sp.portfolio_projects:
        score += 15
        
    
    if sp.work_experiences:
        score += 15
        
    
    if sp.educations:
        score += 15
        
    
    if sp.certifications:
        score += 15
        
    return min(score, 100)

@router.get("/profile", response_model=schemas.ServiceProvider)
def get_current_service_provider_profile(
    db: Session = Depends(deps.get_db),
    current_service_provider: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Get current service provider profile with completion percentage.
    """
    
    current_service_provider.completion_percentage = calculate_completion_percentage(current_service_provider)
    return current_service_provider

@router.put("/professional-info", response_model=schemas.ServiceProvider)
def update_professional_info(
    *,
    db: Session = Depends(deps.get_db),
    info_in: schemas.ServiceProviderUpdate,
    current_service_provider: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Update professional summary (Title, Rate, Skills, Availability).
    """
    update_data = info_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_service_provider, field, value)
    
    db.add(current_service_provider)
    db.commit()
    db.refresh(current_service_provider)
    current_service_provider.completion_percentage = calculate_completion_percentage(current_service_provider)
    return current_service_provider

@router.post("/portfolio", response_model=schemas.PortfolioProject)
def add_portfolio_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: schemas.PortfolioProjectCreate,
    current_service_provider: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Add a portfolio project.
    """
    project = PortfolioProject(
        **project_in.model_dump(),
        service_provider_id=current_service_provider.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.post("/experience", response_model=schemas.WorkExperience)
def add_work_experience(
    *,
    db: Session = Depends(deps.get_db),
    experience_in: schemas.WorkExperienceCreate,
    current_service_provider: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Add work experience.
    """
    experience = WorkExperience(
        **experience_in.model_dump(),
        service_provider_id=current_service_provider.id
    )
    db.add(experience)
    db.commit()
    db.refresh(experience)
    return experience

@router.post("/education", response_model=schemas.Education)
def add_education(
    *,
    db: Session = Depends(deps.get_db),
    education_in: schemas.EducationCreate,
    current_service_provider: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Add education.
    """
    education = Education(
        **education_in.model_dump(),
        service_provider_id=current_service_provider.id
    )
    db.add(education)
    db.commit()
    db.refresh(education)
    return education

@router.post("/certification", response_model=schemas.Certification)
def add_certification(
    *,
    db: Session = Depends(deps.get_db),
    certification_in: schemas.CertificationCreate,
    current_service_provider: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Add certification.
    """
    certification = Certification(
        **certification_in.model_dump(),
        service_provider_id=current_service_provider.id
    )
    db.add(certification)
    db.commit()
    db.refresh(certification)
    return certification

@router.post("/kyc", response_model=schemas.ServiceProvider)
def upload_kyc_document(
    *,
    db: Session = Depends(deps.get_db),
    file_path: str = Body(..., embed=True), # accepting string path for now
    current_service_provider: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Update KYC file path.
    """
    current_service_provider.kyc_file = file_path
    db.add(current_service_provider)
    db.commit()
    db.refresh(current_service_provider)
    current_service_provider.completion_percentage = calculate_completion_percentage(current_service_provider)
    return current_service_provider

@router.post("/projects/{project_id}/bid", response_model=bid_schemas.Bid)
def create_project_bid(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    bid_in: bid_schemas.BidCreate,
    current_service_provider: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Submit a bid for a project.
    """
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )
    
    bid = Bid(
        **bid_in.model_dump(),
        project_id=project_id,
        service_provider_id=current_service_provider.id
    )
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return bid

@router.put("/bids/{bid_id}", response_model=bid_schemas.Bid)
def update_project_bid(
    *,
    db: Session = Depends(deps.get_db),
    bid_id: int,
    bid_in: bid_schemas.BidUpdate,
    current_service_provider: ServiceProvider = Depends(deps.get_current_service_provider),
) -> Any:
    """
    Update an existing bid.
    """
    bid = db.query(Bid).filter(Bid.id == bid_id, Bid.service_provider_id == current_service_provider.id).first()
    if not bid:
        raise HTTPException(
            status_code=404,
            detail="Bid not found or you don't have permission to update it",
        )
    
    update_data = bid_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bid, field, value)
    
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return bid
