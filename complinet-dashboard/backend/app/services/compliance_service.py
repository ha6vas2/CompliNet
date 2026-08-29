import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Add network-compliance path to sys.path to reuse analyze & collect functions
COMPLINET_ROOT = Path(__file__).resolve().parents[4]
NETWORK_COMPLIANCE_ROOT = COMPLINET_ROOT / "network-compliance"

if str(NETWORK_COMPLIANCE_ROOT) not in sys.path:
    sys.path.insert(0, str(NETWORK_COMPLIANCE_ROOT))

try:
    from scripts.analyze import analyze_config, generate_diff, load_rules
    from scripts.collect import collect_all_configs, load_inventory
except ImportError:
    # Fallback if path setup differs
    analyze_config = None
    generate_diff = None
    load_rules = None
    collect_all_configs = None
    load_inventory = None


class ComplianceService:
    def __init__(self):
        self.base_dir = NETWORK_COMPLIANCE_ROOT
        self.inventory_path = self.base_dir / "inventory" / "devices.yaml"
        self.rules_path = self.base_dir / "compliance" / "rules.yaml"
        self.baselines_root = self.base_dir / "baselines"
        self.collected_root = self.base_dir / "collected"
        self.reports_root = self.base_dir / "reports"

    def get_rules(self) -> List[Dict[str, Any]]:
        if not self.rules_path.exists():
            return []
        with self.rules_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("rules", [])

    def get_inventory(self) -> List[Dict[str, Any]]:
        if not self.inventory_path.exists():
            return []
        with self.inventory_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("devices", [])

    def run_analysis_for_device(self, device: Dict[str, Any]) -> Dict[str, Any]:
        device_name = device.get("name")
        baseline_name = device.get("baseline")
        collected_config = self.collected_root / device_name / "current.cfg"

        # If collected config doesn't exist yet, try creating from mock/baseline
        if not collected_config.exists():
            collected_config.parent.mkdir(parents=True, exist_ok=True)
            baseline_file = self.baselines_root / baseline_name if baseline_name else None
            sample_content = (
                baseline_file.read_text(encoding="utf-8")
                if (baseline_file and baseline_file.exists())
                else "service password-encryption\n"
            )
            # Inject minor drift for R1 / SW1 demonstration if creating initial snapshot
            if device_name == "R1":
                sample_content = sample_content.replace("transport input ssh", "transport input telnet")
            elif device_name == "SW1":
                sample_content = sample_content.replace("vtp mode transparent", "vtp mode server")
            collected_config.write_text(sample_content, encoding="utf-8")

        baseline_path = self.baselines_root / (baseline_name or "")
        analysis = analyze_config(collected_config, self.rules_path) if analyze_config else {}

        diff_text = ""
        if baseline_path.exists() and generate_diff:
            diff_text = generate_diff(baseline_path, collected_config)

        analysis["diff"] = diff_text
        analysis["role"] = device.get("role", "device")
        analysis["host"] = device.get("host", "127.0.0.1")
        analysis["device_type"] = device.get("device_type", "cisco_ios")
        analysis["baseline"] = baseline_name
        return analysis

    def get_all_device_compliance(self) -> List[Dict[str, Any]]:
        devices = self.get_inventory()
        results = []
        for device in devices:
            results.append(self.run_analysis_for_device(device))
        return results

    def get_summary_metrics(self) -> Dict[str, Any]:
        all_device_results = self.get_all_device_compliance()
        total_devices = len(all_device_results)
        compliant_count = sum(1 for d in all_device_results if d.get("compliant"))
        non_compliant_count = total_devices - compliant_count
        drift_count = sum(1 for d in all_device_results if not d.get("compliant"))
        avg_score = (
            round(sum(d.get("score", 0) for d in all_device_results) / max(total_devices, 1), 1)
            if total_devices
            else 100
        )

        all_failed_rules = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "warning": 0}

        for d in all_device_results:
            device_name = d.get("device_name")
            for res in d.get("results", []):
                if res.get("status") in ("FAIL", "WARN"):
                    sev = res.get("severity", "medium").lower()
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1
                    all_failed_rules.append(
                        {
                            "device_name": device_name,
                            "rule_id": res.get("rule_id"),
                            "name": res.get("name"),
                            "status": res.get("status"),
                            "severity": res.get("severity"),
                            "remediation": res.get("remediation"),
                        }
                    )

        return {
            "total_devices": total_devices,
            "compliant_devices": compliant_count,
            "non_compliant_devices": non_compliant_count,
            "drift_devices": drift_count,
            "average_score": avg_score,
            "severity_counts": severity_counts,
            "failed_rules": all_failed_rules,
            "devices": all_device_results,
        }

    def trigger_collection(self) -> Dict[str, Any]:
        os.environ["COMPLINET_FALLBACK_MOCK"] = "1"
        if collect_all_configs:
            collect_all_configs(self.inventory_path, self.collected_root)
        return self.get_summary_metrics()

    def sync_gns3(self, gns3_url: str = "http://127.0.0.1:3080") -> Dict[str, Any]:
        try:
            from scripts.gns3_sync import sync_inventory_from_gns3
            discovered = sync_inventory_from_gns3(gns3_url)
            return {"status": "success", "count": len(discovered), "devices": discovered}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}