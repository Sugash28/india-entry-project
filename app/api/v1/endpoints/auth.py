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
        name=user_in.name,
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
        name=user_in.name,
        hashed_password=security.get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


#--> google auth implementation

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
import secrets
import string

def get_random_string(length=12):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(length))

def verify_google_token(token: str):
    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
        return id_info
    except ValueError:
        return None

from app.schemas.token import GoogleToken

@router.post("/login/google/{user_type}", response_model=Token)
def login_google(
    user_type: str,
    token_data: GoogleToken,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Login with Google.
    user_type: "client" or "service_provider"
    """
    if user_type not in ["client", "service_provider"]:
        raise HTTPException(status_code=400, detail="Invalid user type")

    google_data = verify_google_token(token_data.token)
    if not google_data:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    email = google_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Google token")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    if user_type == "client":
        user = db.query(Client).filter(Client.email == email).first()
        if not user:
            password = get_random_string()
            user = Client(
                email=email,
                name=google_data.get("name"),
                hashed_password=security.get_password_hash(password),
                is_active=True,
                is_superuser=False,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        if not user.is_active:
             raise HTTPException(status_code=400, detail="Inactive user")

        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }

    elif user_type == "service_provider":
        user = db.query(ServiceProvider).filter(ServiceProvider.email == email).first()
        if not user:
            password = get_random_string()
            user = ServiceProvider(
                email=email,
                name=google_data.get("name"),
                hashed_password=security.get_password_hash(password),
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        if not user.is_active:
             raise HTTPException(status_code=400, detail="Inactive user")

        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }

#--> Microsoft auth implementation

from app.schemas.token import MicrosoftToken
from jose import jwt

def verify_microsoft_token(token: str):
    try:
        jwks_url = f'https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/discovery/v2.0/keys'
        jwks = requests.get(jwks_url).json()
        
        header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks['keys']:
            if key['kid'] == header['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
        
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=settings.MICROSOFT_CLIENT_ID,
                    issuer=f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/v2.0"
                )
                return payload
            except Exception as e:
                print(f"Token Decode Error: {e}")
                try:
                    debug_payload = jwt.get_unverified_claims(token)
                    print(f"DEBUG: Expected Audience: {settings.MICROSOFT_CLIENT_ID}")
                    print(f"DEBUG: Token Audience: {debug_payload.get('aud')}")
                    print(f"DEBUG: Expected Issuer: https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/v2.0")
                    print(f"DEBUG: Token Issuer: {debug_payload.get('iss')}")
                except:
                    pass
                return None
            
        return None
    except Exception as e:
        print(f'Microsoft Token Error: {e}')
        return None


@router.post('/login/microsoft/{user_type}', response_model=Token)
def login_microsoft(
    user_type: str,
    token_data: MicrosoftToken,
    db: Session = Depends(deps.get_db),
) -> Any:
    '''
    Login with Microsoft.
    user_type: 'client' or 'service_provider'
    '''
    if user_type not in ['client', 'service_provider']:
        raise HTTPException(status_code=400, detail='Invalid user type')

    ms_data = verify_microsoft_token(token_data.token)
    if not ms_data:
        raise HTTPException(status_code=400, detail='Invalid Microsoft token')

    email = ms_data.get('email') or ms_data.get('preferred_username')
    
    if not email:
        raise HTTPException(status_code=400, detail='Email not found in Microsoft token')

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    if user_type == 'client':
        user = db.query(Client).filter(Client.email == email).first()
        if not user:
            password = get_random_string()
            user = Client(
                email=email,
                name=ms_data.get("name"),
                hashed_password=security.get_password_hash(password),
                is_active=True,
                is_superuser=False,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        if not user.is_active:
             raise HTTPException(status_code=400, detail='Inactive user')

        return {
            'access_token': security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            'token_type': 'bearer',
        }

    elif user_type == 'service_provider':
        user = db.query(ServiceProvider).filter(ServiceProvider.email == email).first()
        if not user:
            password = get_random_string()
            user = ServiceProvider(
                email=email,
                name=ms_data.get("name"),
                hashed_password=security.get_password_hash(password),
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        if not user.is_active:
             raise HTTPException(status_code=400, detail='Inactive user')

        return {
            'access_token': security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            'token_type': 'bearer',
        }

