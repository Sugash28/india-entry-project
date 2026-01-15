from typing import Optional, Literal, List
from pydantic import BaseModel, EmailStr, Field

# --- PortfolioProject Schemas ---
class PortfolioProjectBase(BaseModel):
    title: str
    project_url: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class PortfolioProjectCreate(PortfolioProjectBase):
    pass

class PortfolioProjectUpdate(PortfolioProjectBase):
    title: Optional[str] = None

class PortfolioProject(PortfolioProjectBase):
    id: int
    service_provider_id: int

    class Config:
        from_attributes = True

# --- WorkExperience Schemas ---
class WorkExperienceBase(BaseModel):
    role: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    currently_working: bool = False
    summary: Optional[str] = None

class WorkExperienceCreate(WorkExperienceBase):
    pass

class WorkExperienceUpdate(WorkExperienceBase):
    role: Optional[str] = None
    company: Optional[str] = None

class WorkExperience(WorkExperienceBase):
    id: int
    service_provider_id: int

    class Config:
        from_attributes = True

# --- Education Schemas ---
class EducationBase(BaseModel):
    school: str
    degree: str
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    highlights: Optional[str] = None

class EducationCreate(EducationBase):
    pass

class EducationUpdate(EducationBase):
    school: Optional[str] = None
    degree: Optional[str] = None

class Education(EducationBase):
    id: int
    service_provider_id: int

    class Config:
        from_attributes = True

# --- Certification Schemas ---
class CertificationBase(BaseModel):
    name: str
    issuer: Optional[str] = None
    year: Optional[int] = None
    certificate_link: Optional[str] = None

class CertificationCreate(CertificationBase):
    pass

class CertificationUpdate(CertificationBase):
    name: Optional[str] = None

class Certification(CertificationBase):
    id: int
    service_provider_id: int

    class Config:
        from_attributes = True


# --- ServiceProvider Schemas ---
class ServiceProviderBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    
    # Professional Summary
    professional_title: Optional[str] = None
    availability: Optional[str] = None
    hourly_rate: Optional[int] = None
    skills: Optional[str] = None
    kyc_file: Optional[str] = None

class ServiceProviderCreate(ServiceProviderBase):
    email: EmailStr
    password: str = Field(..., alias="pass") 
    type: Literal["service provider"] = "service provider"

class ServiceProviderLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., alias="pass")

class ServiceProviderUpdate(ServiceProviderBase):
    password: Optional[str] = None
    professional_title: Optional[str] = None
    availability: Optional[str] = None
    hourly_rate: Optional[int] = None
    skills: Optional[str] = None


class ServiceProviderInDBBase(ServiceProviderBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True

class ServiceProvider(ServiceProviderInDBBase):
    portfolio_projects: List[PortfolioProject] = []
    work_experiences: List[WorkExperience] = []
    educations: List[Education] = []
    certifications: List[Certification] = []
    
    # Computed field for API response
    completion_percentage: Optional[int] = None

class ServiceProviderInDB(ServiceProviderInDBBase):
    hashed_password: str

