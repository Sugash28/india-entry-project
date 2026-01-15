from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.api import deps
from app.models.service_provider import (
    ServiceProvider, PortfolioProject, WorkExperience, Education, Certification
)
from app.schemas import service_provider as schemas

router = APIRouter()

def calculate_completion_percentage(sp: ServiceProvider) -> int:
    score = 0
    # 1. Professional Summary (Title, Rate, Skills, Availability) - 20%
    if sp.professional_title and sp.hourly_rate and sp.skills:
        score += 20
    
    # 2. KYC - 20%
    if sp.kyc_file:
        score += 20
        
    # 3. Portfolio - 15%
    if sp.portfolio_projects:
        score += 15
        
    # 4. Work Experience - 15%
    if sp.work_experiences:
        score += 15
        
    # 5. Education - 15%
    if sp.educations:
        score += 15
        
    # 6. Certification - 15%
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
    # Calculate percentage
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
