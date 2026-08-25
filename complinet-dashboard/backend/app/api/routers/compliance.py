from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List
from app.services.compliance_service import ComplianceService

router = APIRouter(prefix="/api/compliance", tags=["compliance"])
compliance_service = ComplianceService()


@router.get("/summary")
async def get_compliance_summary() -> Dict[str, Any]:
    try:
        return compliance_service.get_summary_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices")
async def get_all_devices_compliance() -> List[Dict[str, Any]]:
    try:
        return compliance_service.get_all_device_compliance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_name}")
async def get_device_compliance(device_name: str) -> Dict[str, Any]:
    try:
        devices = compliance_service.get_inventory()
        target = next((d for d in devices if d.get("name") == device_name), None)
        if not target:
            raise HTTPException(status_code=404, detail=f"Device '{device_name}' not found.")
        return compliance_service.run_analysis_for_device(target)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules")
async def get_compliance_rules() -> List[Dict[str, Any]]:
    try:
        return compliance_service.get_rules()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run")
async def trigger_compliance_run() -> Dict[str, Any]:
    try:
        return compliance_service.trigger_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gns3-sync")
async def sync_gns3_topology(gns3_url: str = "http://127.0.0.1:3080") -> Dict[str, Any]:
    try:
        return compliance_service.sync_gns3(gns3_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))