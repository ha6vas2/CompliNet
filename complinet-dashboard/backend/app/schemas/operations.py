from typing import Optional

from pydantic import BaseModel, Field


class RemediationRequestCreate(BaseModel):
    device_name: str
    playbook: str
    requested_by: str = Field(min_length=1)
    reason: Optional[str] = None


class RemediationApproval(BaseModel):
    approved_by: str = Field(min_length=1)
