from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class BidBase(BaseModel):
    bid_amount: int
    currency: str
    cover_letter: str
    status: Optional[str] = "pending"

class BidCreate(BidBase):
    pass

class BidUpdate(BaseModel):
    bid_amount: Optional[int] = None
    currency: Optional[str] = None
    cover_letter: Optional[str] = None
    status: Optional[str] = None

class BidInDBBase(BidBase):
    id: int
    project_id: int
    service_provider_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Bid(BidInDBBase):
    pass
