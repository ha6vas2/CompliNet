from pydantic import BaseModel
from typing import List, Optional

class ComplianceRule(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool

class ComplianceResult(BaseModel):
    rule_id: int
    device_id: int
    status: str
    timestamp: str

class ComplianceData(BaseModel):
    rules: List[ComplianceRule]
    results: List[ComplianceResult]