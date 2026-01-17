from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.client import Client
from app.schemas import client as schemas

router = APIRouter()

def calculate_completion_percentage(client: Client) -> int:
    score = 0
    
    # 1. Personal Details - 25%
    personal_fields = [client.profile_photo, client.location_country, client.location_city, client.language, client.bio]
    if any(personal_fields):
        score += 25
    
    # 2. Company Information - 25%
    company_fields = [client.company_name, client.company_size, client.industry, client.website]
    if any(company_fields):
        score += 25
    
    # 3. Contact Preferences - 25%
    contact_fields = [client.preferred_contact_method, client.contact_email, client.contact_phone, client.timezone]
    if any(contact_fields):
        score += 25
    
    # 4. Billing Information - 25%
    billing_fields = [client.billing_name, client.tax_gst_number, client.billing_contact_email, client.billing_contact_phone, client.billing_address]
    if any(billing_fields):
        score += 25
    
    return min(score, 100)

@router.get("/profile", response_model=schemas.Client)
def get_current_client_profile(
    db: Session = Depends(deps.get_db),
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Get current client profile with completion percentage.
    """
    current_client.completion_percentage = calculate_completion_percentage(current_client)
    return current_client

@router.put("/personal-details", response_model=schemas.Client)
def update_personal_details(
    *,
    db: Session = Depends(deps.get_db),
    details_in: schemas.ClientUpdate,
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Update personal details (profile photo, location, language, bio).
    """
    update_data = details_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_client, field, value)
    
    db.add(current_client)
    db.commit()
    db.refresh(current_client)
    current_client.completion_percentage = calculate_completion_percentage(current_client)
    return current_client

@router.put("/company-info", response_model=schemas.Client)
def update_company_info(
    *,
    db: Session = Depends(deps.get_db),
    info_in: schemas.ClientUpdate,
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Update company information (name, size, industry, website).
    """
    update_data = info_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_client, field, value)
    
    db.add(current_client)
    db.commit()
    db.refresh(current_client)
    current_client.completion_percentage = calculate_completion_percentage(current_client)
    return current_client

@router.put("/contact-preferences", response_model=schemas.Client)
def update_contact_preferences(
    *,
    db: Session = Depends(deps.get_db),
    prefs_in: schemas.ClientUpdate,
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Update contact preferences (method, email, phone, timezone, notes).
    """
    update_data = prefs_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_client, field, value)
    
    db.add(current_client)
    db.commit()
    db.refresh(current_client)
    current_client.completion_percentage = calculate_completion_percentage(current_client)
    return current_client

@router.put("/billing-info", response_model=schemas.Client)
def update_billing_info(
    *,
    db: Session = Depends(deps.get_db),
    billing_in: schemas.ClientUpdate,
    current_client: Client = Depends(deps.get_current_client),
) -> Any:
    """
    Update billing information (billing name, tax number, contact details, address).
    """
    update_data = billing_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_client, field, value)
    
    db.add(current_client)
    db.commit()
    db.refresh(current_client)
    current_client.completion_percentage = calculate_completion_percentage(current_client)
    return current_client
