import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from netmiko import ConnectHandler

try:
    from netmiko.ssh_exception import NetmikoTimeoutException, NetmikoAuthenticationException
except ImportError:
    try:
        from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
    except ImportError:  # type: ignore[assignment]
        NetmikoTimeoutException = Exception  # type: ignore[assignment]
        NetmikoAuthenticationException = Exception  # type: ignore[assignment]


def load_inventory(inventory_path: Path) -> List[Dict[str, Any]]:
    if not inventory_path.exists():
        raise FileNotFoundError(f"Inventory file not found: {inventory_path}")

    with inventory_path.open("r", encoding="utf-8") as inventory_file:
        inventory_data = yaml.safe_load(inventory_file) or {}

    devices = inventory_data.get("devices")
    if not isinstance(devices, list):
        raise ValueError("Inventory file must contain a top-level 'devices' list.")

    return devices


def get_device_credentials() -> Dict[str, str]:
    username = os.environ.get("NETMIKO_USERNAME")
    password = os.environ.get("NETMIKO_PASSWORD")
    secret = os.environ.get("NETMIKO_SECRET")

    if not username or not password:
        raise EnvironmentError(
            "NETMIKO_USERNAME and NETMIKO_PASSWORD must be set in the environment."
        )

    credentials: Dict[str, str] = {"username": username, "password": password}
    if secret:
        credentials["secret"] = secret
    return credentials


def validate_device(device: Dict[str, Any]) -> Dict[str, Any]:
    missing = [field for field in ("name", "host", "device_type") if not device.get(field)]
    if missing:
        raise ValueError(
            f"Device record is missing required fields: {', '.join(missing)}"
        )
    return device


def collect_running_config(device: Dict[str, Any], output_dir: Path) -> Path:
    device = validate_device(device)
    credentials = get_device_credentials()
    device_name = device["name"]
    device_params = {
        "device_type": device["device_type"],
        "host": device["host"],
        "username": credentials["username"],
        "password": credentials["password"],
    }
    if "secret" in credentials:
        device_params["secret"] = credentials["secret"]

    try:
        with ConnectHandler(**device_params) as connection:
            config = connection.send_command("show running-config")
    except NetmikoTimeoutException as exc:
        raise ConnectionError(
            f"Timeout connecting to {device_name} ({device['host']}): {exc}"
        ) from exc
    except NetmikoAuthenticationException as exc:
        raise PermissionError(
            f"Authentication failed for {device_name} ({device['host']}): {exc}"
        ) from exc
    except Exception as exc:
        raise ConnectionError(
            f"Unable to collect configuration from {device_name} ({device['host']}): {exc}"
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
        device_name = device.get("name") or device.get("host") or "unknown"
        print(f"Collecting config for {device_name}...")
        try:
            collected_path = collect_running_config(device, collected_root)
            collected_paths.append(collected_path)
        except Exception as exc:
            print(f"Failed to collect from {device_name}: {exc}")

    return collected_paths


if __name__ == "__main__":
    inventory_file = Path(__file__).resolve().parents[1] / "inventory" / "devices.yaml"
    collected_root = Path(__file__).resolve().parents[1] / "collected"

    try:
        collected_files = collect_all_configs(inventory_file, collected_root)
        if collected_files:
            print("Collection complete. Saved files:")
            for path in collected_files:
                print(f"  - {path}")
        else:
            print("No configurations were collected.")
            exit(1)
    except Exception as exc:
        print(f"Error: {exc}")
        exit(1)
