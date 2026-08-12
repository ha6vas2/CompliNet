import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetmikoTimeoutException, NetmikoAuthenticationException


def load_inventory(inventory_path: Path) -> List[Dict[str, Any]]:
    with inventory_path.open("r", encoding="utf-8") as inventory_file:
        inventory_data = yaml.safe_load(inventory_file)
    return inventory_data.get("devices", [])


def get_device_credentials() -> Dict[str, str]:
    username = os.environ.get("NETMIKO_USERNAME")
    password = os.environ.get("NETMIKO_PASSWORD")
    if not username or not password:
        raise EnvironmentError(
            "NETMIKO_USERNAME and NETMIKO_PASSWORD must be set in the environment."
        )
    return {"username": username, "password": password}


def collect_running_config(device: Dict[str, Any], output_dir: Path) -> Path:
    credentials = get_device_credentials()
    device_name = device.get("name")
    device_params = {
        "device_type": device.get("device_type"),
        "host": device.get("host"),
        "username": credentials["username"],
        "password": credentials["password"],
    }

    try:
        with ConnectHandler(**device_params) as connection:
            config = connection.send_command("show running-config")
    except NetmikoTimeoutException as exc:
        raise ConnectionError(
            f"Timeout connecting to {device_name} ({device.get('host')}): {exc}"
        ) from exc
    except NetmikoAuthenticationException as exc:
        raise PermissionError(
            f"Authentication failed for {device_name} ({device.get('host')}): {exc}"
        ) from exc
    except Exception as exc:
        raise ConnectionError(
            f"Unable to collect configuration from {device_name} ({device.get('host')}): {exc}"
        ) from exc

    target_dir = output_dir / device_name
    target_dir.mkdir(parents=True, exist_ok=True)
    config_path = target_dir / "current.cfg"
    config_path.write_text(config, encoding="utf-8")
    return config_path


def collect_all_configs(inventory_path: Path, collected_root: Path) -> List[Path]:
    devices = load_inventory(inventory_path)
    collected_paths: List[Path] = []
    for device in devices:
        print(f"Collecting config for {device.get('name')}...")
        collected_path = collect_running_config(device, collected_root)
        collected_paths.append(collected_path)
    return collected_paths


if __name__ == "__main__":
    inventory_file = Path(__file__).resolve().parents[1] / "inventory" / "devices.yaml"
    collected_root = Path(__file__).resolve().parents[1] / "collected"

    try:
        collected_files = collect_all_configs(inventory_file, collected_root)
        print("Collection complete. Saved files:")
        for path in collected_files:
            print(f"  - {path}")
    except Exception as exc:
        print(f"Error: {exc}")
        exit(1)
