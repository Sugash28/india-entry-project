from sqlalchemy import Boolean, Column, Integer, String
from app.db.base import Base

class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True) # Full Name
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

    # 1. Personal Details
    profile_photo = Column(String, nullable=True)
    location_country = Column(String, nullable=True)
    location_city = Column(String, nullable=True)
    language = Column(String, nullable=True) # Comma separated
    bio = Column(String, nullable=True) # Bio/Company Overview

    # 2. Company Information
    company_name = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    website = Column(String, nullable=True)

    # 3. Contact Preferences
    preferred_contact_method = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    # 4. Billing Information
    billing_name = Column(String, nullable=True) # Legal/Billing Name
    tax_gst_number = Column(String, nullable=True)
    billing_contact_email = Column(String, nullable=True)
    billing_contact_phone = Column(String, nullable=True)
    billing_address = Column(String, nullable=True)

