from typing import Any, Dict

from fastapi import APIRouter

from app.services.system_health import system_health_service

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health")
def get_system_health() -> Dict[str, Any]:
    return system_health_service.snapshot()
