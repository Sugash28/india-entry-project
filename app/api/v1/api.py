from fastapi import APIRouter
from app.api.v1.endpoints import auth, service_provider, client, project

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(service_provider.router, prefix="/service-provider", tags=["service-provider"])
api_router.include_router(client.router, prefix="/client", tags=["client"])
api_router.include_router(project.router, prefix="/client/projects", tags=["projects"])

