from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List
from pydantic import BaseModel
from app.services import inventory_service

router = APIRouter(prefix="/api/devices", tags=["devices"])


class DeviceCreateSchema(BaseModel):
    name: str
    host: str
    device_type: str = "cisco_ios"
    role: str = "router"
    baseline: str = "cisco_router.cfg"


@router.get("/")
def get_devices() -> List[Dict[str, Any]]:
    return inventory_service.get_all_devices()


@router.post("/")
def create_device(device: DeviceCreateSchema) -> Dict[str, Any]:
    return inventory_service.add_device(device.dict())