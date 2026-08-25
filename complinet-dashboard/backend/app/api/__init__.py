# backend/app/api/__init__.py

from fastapi import APIRouter

from .routers import compliance, devices

api_router = APIRouter()

api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])