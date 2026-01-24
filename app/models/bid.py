from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Bid(Base):
    __tablename__ = "bid"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    service_provider_id = Column(Integer, ForeignKey("service_provider.id"), nullable=False)
    bid_amount = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)
    cover_letter = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, accepted, rejected
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    from sqlalchemy.orm import relationship
    project = relationship("Project", back_populates="bids")
    service_provider = relationship("ServiceProvider")
