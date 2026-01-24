from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    budget_range = Column(String, nullable=True)  
    currency = Column(String, nullable=True)  
    project_duration = Column(String, nullable=True)  
    skills_required = Column(String, nullable=True)  
    status = Column(String, default="open")  # open, pending_contract, in_progress, awaiting_review, completed, cancelled
    
    # Work Submission Fields
    submission_pdf_path = Column(String, nullable=True)
    submission_github_link = Column(String, nullable=True)
    
    # Escrow / Funds
    escrow_funded = Column(String, default="no")  # no, yes, released
    
    # Foreign key 
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    
    from sqlalchemy.orm import relationship
    bids = relationship("Bid", back_populates="project", cascade="all, delete-orphan")
