import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

import yaml

NETWORK_COMPLIANCE_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = NETWORK_COMPLIANCE_ROOT / "inventory" / "devices.yaml"
GNS3_SERVER = os.environ.get("GNS3_SERVER", "http://127.0.0.1:3080")

# GNS3 built-in node types that are NOT network devices (routers/switches)
BUILTIN_IGNORE_TYPES = {
    "cloud",
    "nat",
    "ethernet_switch",
    "vpcs",
    "frame_relay_switch",
    "atm_switch",
    "docker",
}


def fetch_json(url: str, timeout: int = 5) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "CompliNet-GNS3-Connector"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        if response.status == 200:
            return json.loads(response.read().decode("utf-8"))
    return None


def discover_gns3_devices(gns3_url: str = GNS3_SERVER) -> List[Dict[str, Any]]:
    print(f"Connecting to GNS3 REST API at {gns3_url}...")
    projects_url = f"{gns3_url}/v2/projects"
    try:
        projects = fetch_json(projects_url)
    except Exception as exc:
        print(f"[ERROR] Could not connect to GNS3 API at {gns3_url}: {exc}")
        print("Ensure GNS3 is running and 'Enable local server API' is checked in GNS3 Preferences.")
        return []

    if not isinstance(projects, list) or not projects:
        print("No active projects found in GNS3.")
        return []

    # Find opened/active project or default to first project
    opened_projects = [p for p in projects if p.get("status") == "opened"]
    active_project = opened_projects[0] if opened_projects else projects[0]
    project_id = active_project.get("project_id")
    project_name = active_project.get("name")
    print(f"Connected to GNS3 Project: '{project_name}' (ID: {project_id})")

    nodes_url = f"{gns3_url}/v2/projects/{project_id}/nodes"
    try:
        nodes = fetch_json(nodes_url) or []
    except Exception as exc:
        print(f"[ERROR] Failed to fetch nodes for project '{project_name}': {exc}")
        return []

    discovered = []
    for node in nodes:
        node_name = node.get("name", "Unknown")
        node_type = (node.get("node_type") or "").lower()
        status = node.get("status", "")
        console_port = node.get("console")
        console_type = node.get("console_type", "telnet")

        # Skip built-in GNS3 utility nodes (Cloud, NAT, VPCS, simple switches)
        if node_type in BUILTIN_IGNORE_TYPES or not console_port:
            print(f"  - Skipping non-IOS utility node: {node_name} ({node_type})")
            continue

        # Classify role and baseline based on node name
        is_switch = any(term in node_name.lower() for term in ("sw", "switch", "l2", "cat"))
        role = "switch" if is_switch else "router"
        baseline = "cisco_switch.cfg" if is_switch else "cisco_router.cfg"

        # Determine Netmiko device type
        device_type = "cisco_ios_telnet" if console_type == "telnet" else "cisco_ios"

        device_record = {
            "name": node_name,
            "host": "127.0.0.1",
            "port": int(console_port),
            "device_type": device_type,
            "role": role,
            "baseline": baseline,
            "username": "admin",
            "password": "cisco",
            "secret": "cisco",
            "gns3_status": status,
        }
        discovered.append(device_record)
        print(f"  ✓ Imported GNS3 Node: {node_name} | Port: {console_port} | Driver: {device_type}")

    return discovered


def sync_inventory_from_gns3(gns3_url: str = GNS3_SERVER) -> List[Dict[str, Any]]:
    discovered = discover_gns3_devices(gns3_url)
    if not discovered:
        print("No router or switch devices synced from GNS3.")
        return []

    inventory_data = {"devices": discovered}
    INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INVENTORY_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(inventory_data, f, sort_keys=False)

    print(f"Successfully updated inventory with {len(discovered)} devices -> {INVENTORY_PATH}")
    return discovered


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else GNS3_SERVER
    sync_inventory_from_gns3(url)
