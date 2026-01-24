from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.orm import relationship

class Contract(Base):
    __tablename__ = "contract"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    bid_id = Column(Integer, ForeignKey("bid.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    service_provider_id = Column(Integer, ForeignKey("service_provider.id"), nullable=False)
    
    terms_and_conditions = Column(Text, nullable=False)
    client_signature_path = Column(String, nullable=True)  # Path to the client's signature image
    service_provider_signature_path = Column(String, nullable=True)  # Path to the service provider's signature image
    status = Column(String, default="client_signed")  # client_signed, fully_signed, active, completed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project")
    bid = relationship("Bid")
    client = relationship("Client")
    service_provider = relationship("ServiceProvider")
