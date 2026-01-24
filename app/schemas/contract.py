from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Shared properties
class ContractBase(BaseModel):
    project_id: int
    bid_id: int
    terms_and_conditions: str

# Properties to receive on contract creation
class ContractCreate(ContractBase):
    pass

# Properties to return to client
class Contract(ContractBase):
    id: int
    client_id: int
    service_provider_id: int
    client_signature_path: Optional[str] = None
    service_provider_signature_path: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
