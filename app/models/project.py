from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    budget_range = Column(String, nullable=True)  # e.g., "$1000-$5000"
    currency = Column(String, nullable=True)  # e.g., "USD", "EUR", "INR"
    project_duration = Column(String, nullable=True)  # e.g., "1-3 months"
    skills_required = Column(String, nullable=True)  # Comma-separated skills
    status = Column(String, default="open")  # open, in_progress, completed, cancelled
    
    # Foreign key to Client
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
