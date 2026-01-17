from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class ServiceProviderProfile(Base):
    __tablename__ = "service_provider_profile"
    
    id = Column(Integer, primary_key=True, index=True)
    service_provider_id = Column(Integer, ForeignKey("service_provider.id"), unique=True, nullable=False)
    profile_photo = Column(String(500), nullable=True) 
    full_name = Column(String(255), nullable=True)
    location_country = Column(String(100), nullable=True)
    location_city = Column(String(100), nullable=True)
    language = Column(String(255), nullable=True) 
    experience = Column(String(100), nullable=True) 
    project_completed = Column(Integer, default=0)
    bio = Column(String(1000), nullable=True)

    service_provider = relationship("ServiceProvider", backref="profile")
