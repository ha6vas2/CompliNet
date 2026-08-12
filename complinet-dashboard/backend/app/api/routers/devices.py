from fastapi import APIRouter, HTTPException
from typing import List
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate

router = APIRouter()

# In-memory storage for devices (for demonstration purposes)
devices_db = []

@router.post("/", response_model=Device)
def create_device(device: DeviceCreate):
    new_device = Device(**device.dict())
    devices_db.append(new_device)
    return new_device

@router.get("/", response_model=List[Device])
def get_devices():
    return devices_db

@router.get("/{device_id}", response_model=Device)
def get_device(device_id: int):
    for device in devices_db:
        if device.id == device_id:
            return device
    raise HTTPException(status_code=404, detail="Device not found")

@router.put("/{device_id}", response_model=Device)
def update_device(device_id: int, device_update: DeviceUpdate):
    for index, device in enumerate(devices_db):
        if device.id == device_id:
            updated_device = device.copy(update=device_update.dict())
            devices_db[index] = updated_device
            return updated_device
    raise HTTPException(status_code=404, detail="Device not found")

@router.delete("/{device_id}", response_model=Device)
def delete_device(device_id: int):
    for index, device in enumerate(devices_db):
        if device.id == device_id:
            return devices_db.pop(index)
    raise HTTPException(status_code=404, detail="Device not found")