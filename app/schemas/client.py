from typing import Optional, Literal
from pydantic import BaseModel, EmailStr

class ClientBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    
    # Personal Details
    profile_photo: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    language: Optional[str] = None
    bio: Optional[str] = None
    
    # Company Information
    company_name: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    
    # Contact Preferences
    preferred_contact_method: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    timezone: Optional[str] = None
    notes: Optional[str] = None
    
    # Billing Information
    billing_name: Optional[str] = None
    tax_gst_number: Optional[str] = None
    billing_contact_email: Optional[str] = None
    billing_contact_phone: Optional[str] = None
    billing_address: Optional[str] = None

class ClientCreate(ClientBase):
    email: EmailStr
    password: str
    type: Literal["client"] = "client"

class ClientLogin(BaseModel):
    email: EmailStr
    password: str

class ClientUpdate(ClientBase):
    password: Optional[str] = None

class ClientInDBBase(ClientBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class Client(ClientInDBBase):
    # Computed field for API response
    completion_percentage: Optional[int] = None



class ClientInDB(ClientInDBBase):
    hashed_password: str
