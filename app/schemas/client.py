from typing import Optional, Literal
from pydantic import BaseModel, EmailStr

# Shared properties
class ClientBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

# Properties to receive via API on creation
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

# Additional properties to return via API
class Client(ClientInDBBase):
    pass

# Additional properties stored in DB
class ClientInDB(ClientInDBBase):
    hashed_password: str
