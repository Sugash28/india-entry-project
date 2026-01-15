from typing import Optional, Literal
from pydantic import BaseModel, EmailStr

class ClientBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

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
    pass


class ClientInDB(ClientInDBBase):
    hashed_password: str
