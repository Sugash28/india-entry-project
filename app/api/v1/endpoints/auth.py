from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.client import Client
from app.models.service_provider import ServiceProvider
from app.schemas.client import Client as ClientSchema, ClientCreate, ClientLogin
from app.schemas.service_provider import ServiceProvider as ServiceProviderSchema, ServiceProviderCreate, ServiceProviderLogin
from app.schemas.token import Token

router = APIRouter()


@router.post("/login/client", response_model=Token)
def login_client(
    login_in: ClientLogin,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Token login for Clients.
    """
    user = db.query(Client).filter(Client.email == login_in.email).first()
    if not user or not security.verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/service-provider", response_model=Token)
def login_service_provider(
    login_in: ServiceProviderLogin,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Token login for Service Providers.
    """
    user = db.query(ServiceProvider).filter(ServiceProvider.email == login_in.email).first()
    if not user or not security.verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/signup/client", response_model=ClientSchema)
def create_client(
    *,
    db: Session = Depends(deps.get_db),
    user_in: ClientCreate,
) -> Any:
    """
    Create new client.
    """
    user = db.query(Client).filter(Client.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = Client(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/signup/service-provider", response_model=ServiceProviderSchema)
def create_service_provider(
    *,
    db: Session = Depends(deps.get_db),
    user_in: ServiceProviderCreate,
) -> Any:
    """
    Create new service provider.
    """
    user = db.query(ServiceProvider).filter(ServiceProvider.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = ServiceProvider(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
