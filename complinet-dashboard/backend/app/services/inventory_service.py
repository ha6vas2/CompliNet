from typing import List, Dict, Any
from fastapi import HTTPException

# Mock database for devices
mock_device_db: Dict[str, Dict[str, Any]] = {}

def add_device(device_id: str, device_data: Dict[str, Any]) -> None:
    if device_id in mock_device_db:
        raise HTTPException(status_code=400, detail="Device already exists.")
    mock_device_db[device_id] = device_data

def update_device(device_id: str, device_data: Dict[str, Any]) -> None:
    if device_id not in mock_device_db:
        raise HTTPException(status_code=404, detail="Device not found.")
    mock_device_db[device_id].update(device_data)

def get_device(device_id: str) -> Dict[str, Any]:
    device = mock_device_db.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found.")
    return device

def get_all_devices() -> List[Dict[str, Any]]:
    return list(mock_device_db.values())