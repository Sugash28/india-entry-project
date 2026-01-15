from typing import Optional
from pydantic import BaseModel

class ServiceProviderProfileBase(BaseModel):
    profile_photo: Optional[str] = None
    full_name: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    language: Optional[str] = None
    experience: Optional[str] = None
    project_completed: Optional[int] = 0
    bio: Optional[str] = None

class ServiceProviderProfileCreate(ServiceProviderProfileBase):
    pass

class ServiceProviderProfileUpdate(ServiceProviderProfileBase):
    pass

class ServiceProviderProfileInDBBase(ServiceProviderProfileBase):
    id: int
    service_provider_id: int

    class Config:
        orm_mode = True

class ServiceProviderProfile(ServiceProviderProfileInDBBase):
    pass
