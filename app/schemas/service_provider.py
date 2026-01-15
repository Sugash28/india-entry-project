from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field

class ServiceProviderBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True

class ServiceProviderCreate(ServiceProviderBase):
    email: EmailStr
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
class ServiceProvider(ServiceProviderInDBBase):
    pass
class ServiceProviderInDB(ServiceProviderInDBBase):
    hashed_password: str
