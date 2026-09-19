import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.audit_service import AuditService, audit_service
from app.services.compliance_service import ComplianceService


SUPPORTED_PLAYBOOKS = {
    "syslog": "syslog.yml",
    "ipv6": "ipv6.yml",
    "ospf": "ospf.yml",
    "hostname": "hostname.yml",
}


class RemediationService:
    def __init__(
        self,
        compliance: Optional[ComplianceService] = None,
        audit: Optional[AuditService] = None,
        playbooks_root: Optional[Path] = None,
    ):
        self.compliance = compliance or ComplianceService()
        self.audit = audit or audit_service
        self.ansible_root = Path(__file__).resolve().parents[3] / "ansible"
        self.playbooks_root = playbooks_root or self.ansible_root / "playbooks"
        self.inventory_path = self.ansible_root / "inventory.yml"
        self.requests: Dict[int, Dict[str, Any]] = {}
        self.next_request_id = 1

    def create_request(
        self,
        device_name: str,
        playbook: str,
        requested_by: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        if playbook not in SUPPORTED_PLAYBOOKS:
            raise ValueError("Unsupported playbook. Choose syslog, ipv6, ospf, or hostname.")
        device = next(
            (item for item in self.compliance.get_inventory() if item.get("name") == device_name),
            None,
        )
        if not device:
            raise ValueError("Device '%s' was not found in inventory." % device_name)

        request = {
            "id": self.next_request_id,
            "device_name": device_name,
            "playbook": playbook,
            "requested_by": requested_by,
            "reason": reason,
            "status": "pending",
            "created_at": self.audit.record(
                "remediation_requested",
                "pending",
                device_name,
                {"playbook": playbook, "requested_by": requested_by, "reason": reason},
            )["created_at"],
        }
        self.requests[request["id"]] = request
        self.next_request_id += 1
        return request

    def list_requests(self) -> List[Dict[str, Any]]:
        return list(reversed(list(self.requests.values())))

    def approve_request(self, request_id: int, approved_by: str) -> Dict[str, Any]:
        request = self._get_request(request_id)
        if request["status"] != "pending":
            raise ValueError("Only pending remediation requests can be approved.")
        request["status"] = "approved"
        request["approved_by"] = approved_by
        event = self.audit.record(
            "remediation_approved",
            "approved",
            request["device_name"],
            {"request_id": request_id, "playbook": request["playbook"], "approved_by": approved_by},
        )
        request["approved_at"] = event["created_at"]
        return request

    def execute_request(self, request_id: int) -> Dict[str, Any]:
        request = self._get_request(request_id)
        if request["status"] != "approved":
            raise ValueError("Remediation must be approved before execution.")

        playbook_path = self.playbooks_root / SUPPORTED_PLAYBOOKS[request["playbook"]]
        if not playbook_path.exists():
            raise ValueError("Playbook is missing: %s" % playbook_path)

        command = [
            "ansible-playbook",
            str(playbook_path),
            "-i",
            str(self.inventory_path),
            "-l",
            request["device_name"],
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=300, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            request["status"] = "failed"
            self.audit.record("remediation_executed", "failed", request["device_name"], {"request_id": request_id, "error": str(exc)})
            raise ValueError("Unable to execute Ansible remediation: %s" % exc)

        request["command"] = command
        request["return_code"] = result.returncode
        request["output"] = result.stdout[-4000:]
        request["error_output"] = result.stderr[-4000:]
        request["status"] = "executed" if result.returncode == 0 else "failed"
        self.audit.record(
            "remediation_executed",
            request["status"],
            request["device_name"],
            {"request_id": request_id, "return_code": result.returncode},
        )
        if result.returncode != 0:
            return request

        try:
            collection_summary = self.compliance.trigger_collection()
            verification = self.compliance.run_analysis_for_device(
                next(item for item in self.compliance.get_inventory() if item.get("name") == request["device_name"])
            )
            request["verification"] = {
                "compliant": verification.get("compliant", False),
                "score": verification.get("score", 0),
                "collection_status": collection_summary.get("collection", {}).get("status"),
            }
            request["status"] = "verified" if verification.get("compliant") else "verification_failed"
            self.audit.record(
                "remediation_verified",
                request["status"],
                request["device_name"],
                {"request_id": request_id, "verification": request["verification"]},
            )
        except Exception as exc:
            request["status"] = "verification_failed"
            request["verification_error"] = str(exc)
            self.audit.record("remediation_verified", "failed", request["device_name"], {"request_id": request_id, "error": str(exc)})

        return request

    def _get_request(self, request_id: int) -> Dict[str, Any]:
        request = self.requests.get(request_id)
        if not request:
            raise ValueError("Remediation request '%s' was not found." % request_id)
        return request


remediation_service = RemediationService()
