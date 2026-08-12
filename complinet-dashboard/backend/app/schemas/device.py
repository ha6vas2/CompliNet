from pydantic import BaseModel
from typing import Optional, List

class DeviceBase(BaseModel):
    name: str
    host: str
    device_type: str
    ip_address: Optional[str] = None
    status: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(DeviceBase):
    pass

class Device(DeviceBase):
    id: int

    class Config:
        orm_mode = True

class DeviceList(BaseModel):
    devices: List[Device]