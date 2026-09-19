from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query

from app.schemas.operations import RemediationApproval, RemediationRequestCreate
from app.services.audit_service import audit_service
from app.services.remediation_service import remediation_service

router = APIRouter(prefix="/api", tags=["operations"])


@router.get("/audit/events")
def get_audit_events(limit: int = Query(default=100, ge=1, le=500)) -> List[Dict[str, Any]]:
    return audit_service.list_events(limit)


@router.get("/remediation/requests")
def get_remediation_requests() -> List[Dict[str, Any]]:
    return remediation_service.list_requests()


@router.post("/remediation/requests")
def create_remediation_request(payload: RemediationRequestCreate) -> Dict[str, Any]:
    try:
        return remediation_service.create_request(**payload.dict())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/remediation/requests/{request_id}/approve")
def approve_remediation_request(request_id: int, payload: RemediationApproval) -> Dict[str, Any]:
    try:
        return remediation_service.approve_request(request_id, payload.approved_by)
    except ValueError as exc:
        status_code = 404 if "not found" in str(exc).lower() else 409
        raise HTTPException(status_code=status_code, detail=str(exc))


@router.post("/remediation/requests/{request_id}/execute")
def execute_remediation_request(request_id: int) -> Dict[str, Any]:
    try:
        return remediation_service.execute_request(request_id)
    except ValueError as exc:
        status_code = 404 if "not found" in str(exc).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(exc))
