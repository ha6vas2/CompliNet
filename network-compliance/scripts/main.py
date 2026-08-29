import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analyze import analyze_config, generate_diff
from scripts.collect import collect_all_configs, load_inventory
from scripts.report import save_daily_summary_report, save_report
from scripts.containerlab_collector import collect_all

def main() -> int:
    base_path = Path(__file__).resolve().parents[1]
    inventory_path = base_path / "inventory" / "devices.yaml"
    rules_path = base_path / "compliance" / "rules.yaml"
    collected_root = base_path / "collected"
    reports_root = base_path / "reports"
    baselines_root = base_path / "baselines"

    try:
        devices = load_inventory(inventory_path)
    except Exception as exc:
        print(f"Failed to load inventory: {exc}")
        return 1

    if not devices:
        print("No devices found in inventory.")
        return 1

    try:
        collected_files = collect_all(devices)
    except Exception as exc:
        print(f"Collection failed: {exc}")
        return 1

    all_reports = []

    for config_path in collected_files:
        device_name = config_path.parent.name
        baseline_name = None
        for device in devices:
            if device.get("name") == device_name:
                baseline_name = device.get("baseline")
                break

        if not baseline_name:
            print(f"Baseline not defined for device {device_name}.")
            continue

        baseline_path = baselines_root / baseline_name
        if not baseline_path.exists():
            print(f"Baseline file missing: {baseline_path}")
            continue

        report_data = analyze_config(config_path, rules_path)
        diff_text = generate_diff(baseline_path, config_path)
        report_filename = reports_root / f"{device_name}_report.html"
        save_report(report_data, diff_text, report_filename)
        all_reports.append(report_data)
        print(f"Report generated for {device_name}: {report_filename}")

    if all_reports:
        daily_summary_path = reports_root / "daily_summary_report.html"
        save_daily_summary_report(all_reports, daily_summary_path)
        print(f"Daily summary report generated: {daily_summary_path}")

    return 0



if __name__ == "__main__":
    exit(main())
