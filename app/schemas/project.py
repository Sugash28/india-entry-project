from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ProjectBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget_range: Optional[str] = None
    currency: Optional[str] = None
    project_duration: Optional[str] = None
    skills_required: Optional[str] = None
    status: Optional[str] = None
    submission_pdf_path: Optional[str] = None
    submission_github_link: Optional[str] = None
    escrow_funded: Optional[str] = None

class ProjectCreate(BaseModel):
    title: str
    description: str
    budget_range: Optional[str] = None
    currency: Optional[str] = None
    project_duration: Optional[str] = None
    skills_required: Optional[str] = None

class ProjectUpdate(ProjectBase):
    pass

class ProjectInDBBase(ProjectBase):
    id: int
    client_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Project(ProjectInDBBase):
    pass
