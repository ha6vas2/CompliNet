import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml


# ---------------------------------------------------------
# Locate the network-compliance engine
# ---------------------------------------------------------

COMPLINET_ROOT = Path(__file__).resolve().parents[4]
NETWORK_COMPLIANCE_ROOT = COMPLINET_ROOT / "network-compliance"

if str(NETWORK_COMPLIANCE_ROOT) not in sys.path:
    sys.path.insert(0, str(NETWORK_COMPLIANCE_ROOT))


from scripts.analyze import analyze_config, generate_diff
from scripts.containerlab_collector import collect_all


class ComplianceService:
    def __init__(self):
        self.base_dir = NETWORK_COMPLIANCE_ROOT

        self.inventory_path = (
            self.base_dir / "inventory" / "devices.yaml"
        )

        self.rules_path = (
            self.base_dir / "compliance" / "rules.yaml"
        )

        self.baselines_root = self.base_dir / "baselines"
        self.collected_root = self.base_dir / "collected"

        self.last_run = None

    # -----------------------------------------------------
    # Inventory
    # -----------------------------------------------------

    def get_inventory(self) -> List[Dict[str, Any]]:
        if not self.inventory_path.exists():
            return []

        with self.inventory_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = yaml.safe_load(file) or {}

        return data.get("devices", [])

    # -----------------------------------------------------
    # Compliance Rules
    # -----------------------------------------------------

    def get_rules(self) -> List[Dict[str, Any]]:
        if not self.rules_path.exists():
            return []

        with self.rules_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = yaml.safe_load(file) or {}

        return data.get("rules", [])

    # -----------------------------------------------------
    # Device Analysis
    # -----------------------------------------------------

    def run_analysis_for_device(
        self,
        device: Dict[str, Any],
    ) -> Dict[str, Any]:

        device_name = device["name"]
        baseline_name = device.get("baseline")

<<<<<<< HEAD
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
=======
        collected_config = (
            self.collected_root
            / device_name
            / "current.cfg"
>>>>>>> 5df13594e4ed23d051ced4a6e074580d23012e62
        )

        if not collected_config.exists():
            return {
                "device_name": device_name,
                "score": 0,
                "compliant": False,
                "results": [],
                "diff": "",
                "role": device.get("role", "router"),
                "host": device.get(
                    "container",
                    "unknown",
                ),
                "device_type": "FRRouting",
                "baseline": baseline_name,
                "error": "No collected configuration available.",
            }

        baseline_path = (
            self.baselines_root
            / baseline_name
        )

        analysis = analyze_config(
            collected_config,
            self.rules_path,
        )

        diff_text = ""

        if baseline_path.exists():
            diff_text = generate_diff(
                baseline_path,
                collected_config,
            )

        analysis["diff"] = diff_text
        analysis["role"] = device.get("role", "router")

        # For Containerlab, display the container name
        # instead of an old Cisco management address.
        analysis["host"] = device.get(
            "container",
            "unknown",
        )

        analysis["device_type"] = "FRRouting"
        analysis["baseline"] = baseline_name

        # Drift and compliance are deliberately separate.
        analysis["drift_detected"] = bool(
            diff_text.strip()
        )

        return analysis

    # -----------------------------------------------------
    # All Devices
    # -----------------------------------------------------

    def get_all_device_compliance(
        self,
    ) -> List[Dict[str, Any]]:

        devices = self.get_inventory()

        return [
            self.run_analysis_for_device(device)
            for device in devices
        ]

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    def get_summary_metrics(
        self,
    ) -> Dict[str, Any]:

        results = self.get_all_device_compliance()

        total_devices = len(results)

        compliant_count = sum(
            1
            for device in results
            if device.get("compliant")
        )

        non_compliant_count = (
            total_devices - compliant_count
        )

        drift_count = sum(
            1
            for device in results
            if device.get("drift_detected")
        )

        if total_devices:
            average_score = round(
                sum(
                    device.get("score", 0)
                    for device in results
                )
                / total_devices,
                1,
            )
        else:
            average_score = 100

        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "warning": 0,
        }

        failed_rules = []

        for device in results:

            device_name = device.get(
                "device_name",
                "unknown",
            )

            for rule in device.get("results", []):

                if rule.get("status") not in (
                    "FAIL",
                    "WARN",
                ):
                    continue

                severity = rule.get(
                    "severity",
                    "medium",
                ).lower()

                severity_counts[severity] = (
                    severity_counts.get(
                        severity,
                        0,
                    )
                    + 1
                )

                failed_rules.append(
                    {
                        "device_name": device_name,
                        "rule_id": rule.get("rule_id"),
                        "name": rule.get("name"),
                        "status": rule.get("status"),
                        "severity": rule.get(
                            "severity"
                        ),
                        "remediation": rule.get(
                            "remediation"
                        ),
                    }
                )

        return {
            "total_devices": total_devices,
            "compliant_devices": compliant_count,
            "non_compliant_devices": non_compliant_count,
            "drift_devices": drift_count,
<<<<<<< HEAD
            "average_score": avg_score,
=======
            "average_score": average_score,
>>>>>>> 5df13594e4ed23d051ced4a6e074580d23012e62
            "severity_counts": severity_counts,
            "failed_rules": failed_rules,
            "devices": results,
            "last_run": self.last_run,
        }

    # -----------------------------------------------------
    # Live Containerlab Collection
    # -----------------------------------------------------

    def trigger_collection(
        self,
    ) -> Dict[str, Any]:

        devices = self.get_inventory()

        collected = collect_all(devices)

        self.last_run = datetime.now(
            timezone.utc
        ).isoformat()

        summary = self.get_summary_metrics()

        summary["collection"] = {
            "status": "success",
            "collected_devices": len(collected),
        }

        return summary
