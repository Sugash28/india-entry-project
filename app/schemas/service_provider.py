from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field

# Shared properties
class ServiceProviderBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True

# Properties to receive via API on creation
class ServiceProviderCreate(ServiceProviderBase):
    email: EmailStr
    # Mapping 'pass' from specific JSON payload to 'password'
    password: str = Field(..., alias="pass") 
    type: Literal["service provider"] = "service provider"

class ServiceProviderLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., alias="pass")

class ServiceProviderUpdate(ServiceProviderBase):
    password: Optional[str] = None

class ServiceProviderInDBBase(ServiceProviderBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True

# Additional properties to return via API
class ServiceProvider(ServiceProviderInDBBase):
    pass

# Additional properties stored in DB
class ServiceProviderInDB(ServiceProviderInDBBase):
    hashed_password: str
