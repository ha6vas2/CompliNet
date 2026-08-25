from pathlib import Path
from typing import Any, Dict, List
import yaml
from fastapi import HTTPException

COMPLINET_ROOT = Path(__file__).resolve().parents[4]
INVENTORY_PATH = COMPLINET_ROOT / "network-compliance" / "inventory" / "devices.yaml"


def get_all_devices() -> List[Dict[str, Any]]:
    if not INVENTORY_PATH.exists():
        return []
    with INVENTORY_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("devices", [])


def add_device(device_data: Dict[str, Any]) -> Dict[str, Any]:
    devices = get_all_devices()
    name = device_data.get("name")
    if any(d.get("name") == name for d in devices):
        raise HTTPException(status_code=400, detail=f"Device '{name}' already exists.")

    new_device = {
        "name": name,
        "host": device_data.get("host"),
        "device_type": device_data.get("device_type", "cisco_ios"),
        "role": device_data.get("role", "router"),
        "baseline": device_data.get("baseline", "cisco_router.cfg"),
    }
    devices.append(new_device)

    INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INVENTORY_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump({"devices": devices}, f)

    return new_device