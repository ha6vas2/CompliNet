from pathlib import Path

from app.services.audit_service import AuditService
from app.services.remediation_service import RemediationService
from app.services.system_health import SystemHealthService


class FakeCompliance:
    def get_inventory(self):
        return [{"name": "R1"}]

    def trigger_collection(self):
        return {"collection": {"status": "success"}}

    def run_analysis_for_device(self, device):
        return {"compliant": True, "score": 100}


def test_remediation_requires_approval(tmp_path: Path):
    audit = AuditService(tmp_path / "audit.db")
    service = RemediationService(FakeCompliance(), audit, tmp_path / "playbooks")
    request = service.create_request("R1", "hostname", "requester")

    assert request["status"] == "pending"
    try:
        service.execute_request(request["id"])
    except ValueError as exc:
        assert "approved" in str(exc).lower()
    else:
        raise AssertionError("Unapproved remediation was executable")

    events = audit.list_events()
    assert events[0]["event_type"] == "remediation_requested"


def test_health_snapshot_has_required_metrics():
    result = SystemHealthService(docker_binary="missing-docker").snapshot()

    assert result["status"] == "healthy"
    assert "cpu_percent" in result
    assert "memory_percent" in result
    assert "disk_percent" in result
    assert result["docker"]["available"] is False
