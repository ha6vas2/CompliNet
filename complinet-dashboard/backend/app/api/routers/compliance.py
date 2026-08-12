from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.compliance import ComplianceSchema
from app.services.compliance_service import ComplianceService

router = APIRouter()
compliance_service = ComplianceService()

@router.get("/compliance", response_model=List[ComplianceSchema])
async def get_compliance_data():
    try:
        compliance_data = compliance_service.fetch_compliance_data()
        return compliance_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/{compliance_id}", response_model=ComplianceSchema)
async def get_compliance_result(compliance_id: int):
    try:
        compliance_result = compliance_service.fetch_compliance_result(compliance_id)
        if compliance_result is None:
            raise HTTPException(status_code=404, detail="Compliance result not found")
        return compliance_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))