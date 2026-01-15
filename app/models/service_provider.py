from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class ServiceProvider(Base):
    __tablename__ = "service_provider"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)

    # Professional Summary
    professional_title = Column(String, nullable=True)
    availability = Column(String, nullable=True)  # e.g., "Full-time", "Part-time"
    hourly_rate = Column(Integer, nullable=True)
    skills = Column(String, nullable=True)  # Comma-separated or JSON
    kyc_file = Column(String, nullable=True)  # Path to file

    # Relationships
    portfolio_projects = relationship("PortfolioProject", back_populates="service_provider", cascade="all, delete-orphan")
    work_experiences = relationship("WorkExperience", back_populates="service_provider", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="service_provider", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="service_provider", cascade="all, delete-orphan")


class PortfolioProject(Base):
    __tablename__ = "portfolio_projects"

    id = Column(Integer, primary_key=True, index=True)
    service_provider_id = Column(Integer, ForeignKey("service_provider.id"), nullable=False)
    title = Column(String, nullable=False)
    project_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    service_provider = relationship("ServiceProvider", back_populates="portfolio_projects")


class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id = Column(Integer, primary_key=True, index=True)
    service_provider_id = Column(Integer, ForeignKey("service_provider.id"), nullable=False)
    role = Column(String, nullable=False)
    company = Column(String, nullable=False)
    start_date = Column(String, nullable=True) # Or Date type
    end_date = Column(String, nullable=True)
    currently_working = Column(Boolean, default=False)
    summary = Column(String, nullable=True)

    service_provider = relationship("ServiceProvider", back_populates="work_experiences")


class Education(Base):
    __tablename__ = "educations"

    id = Column(Integer, primary_key=True, index=True)
    service_provider_id = Column(Integer, ForeignKey("service_provider.id"), nullable=False)
    school = Column(String, nullable=False)
    degree = Column(String, nullable=False) # degree/program
    field_of_study = Column(String, nullable=True)
    start_year = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    highlights = Column(String, nullable=True)

    service_provider = relationship("ServiceProvider", back_populates="educations")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    service_provider_id = Column(Integer, ForeignKey("service_provider.id"), nullable=False)
    name = Column(String, nullable=False)
    issuer = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    certificate_link = Column(String, nullable=True)

    service_provider = relationship("ServiceProvider", back_populates="certifications")

   
