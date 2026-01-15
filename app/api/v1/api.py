from fastapi import APIRouter
from app.api.v1.endpoints import auth, service_provider

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(service_provider.router, prefix="/service-provider", tags=["service-provider"])
