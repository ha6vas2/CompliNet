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


def get_device_credentials(device: Dict[str, Any] = None) -> Dict[str, str]:
    if device and device.get("username") and device.get("password"):
        credentials = {
            "username": device["username"],
            "password": device["password"],
        }
        if device.get("secret"):
            credentials["secret"] = device["secret"]
        return credentials

    username = os.environ.get("NETMIKO_USERNAME", "admin")
    password = os.environ.get("NETMIKO_PASSWORD", "cisco")
    secret = os.environ.get("NETMIKO_SECRET", "cisco")

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


def get_mock_config(device: Dict[str, Any], base_path: Path) -> str:
    baseline_filename = device.get("baseline")
    if baseline_filename:
        baseline_path = base_path / "baselines" / baseline_filename
        if baseline_path.exists():
            content = baseline_path.read_text(encoding="utf-8")
            # Inject a controlled configuration drift for demonstration/testing
            if device.get("name") == "R1":
                content = content.replace("transport input ssh", "transport input telnet")
            elif device.get("name") == "SW1":
                content = content.replace("vtp mode transparent", "vtp mode server")
            return content
    return "service password-encryption\nno ip http server\n"


def collect_running_config(device: Dict[str, Any], output_dir: Path) -> Path:
    device = validate_device(device)
    device_name = device["name"]

    use_mock = os.environ.get("COMPLINET_MOCK") == "1"
    base_path = output_dir.parent

    if use_mock:
        config = get_mock_config(device, base_path)
    else:
        try:
            credentials = get_device_credentials(device)
            device_params = {
                "device_type": device["device_type"],
                "host": device["host"],
                "username": credentials["username"],
                "password": credentials["password"],
                "global_delay_factor": device.get("global_delay_factor", 2),
            }
            if "secret" in credentials:
                device_params["secret"] = credentials["secret"]
            if device.get("port"):
                device_params["port"] = int(device["port"])

            with ConnectHandler(**device_params) as connection:
                # Enable privilege mode if needed
                if credentials.get("secret") and hasattr(connection, "enable"):
                    try:
                        connection.enable()
                    except Exception:
                        pass
                config = connection.send_command("show running-config")
        except Exception as exc:
            if os.environ.get("COMPLINET_FALLBACK_MOCK") == "1":
                print(f"[WARN] Connection to {device_name} ({device.get('host')}) failed ({exc}). Falling back to mock snapshot.")
                config = get_mock_config(device, base_path)
            else:
                raise

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
