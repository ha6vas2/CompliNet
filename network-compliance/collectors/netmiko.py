import os
from pathlib import Path
from typing import Any

from netmiko import ConnectHandler


class NetmikoCollector:
    """Collect configuration from real network devices using Netmiko."""

    def get_credentials(self, device: dict[str, Any]) -> dict[str, str]:
        username = device.get("username") or os.environ.get("NETMIKO_USERNAME", "admin")
        password = device.get("password") or os.environ.get("NETMIKO_PASSWORD", "cisco")
        credentials = {"username": username, "password": password}
        if device.get("secret") or os.environ.get("NETMIKO_SECRET"):
            credentials["secret"] = device.get("secret") or os.environ.get("NETMIKO_SECRET", "")
        return credentials

    def collect_device(self, device: dict[str, Any], collected_root: Path) -> Path:
        name = device["name"]
        host = device["host"]
        device_type = device.get("device_type", "cisco_ios")

        credentials = self.get_credentials(device)
        params = {
            "device_type": device_type,
            "host": host,
            "username": credentials["username"],
            "password": credentials["password"],
            "global_delay_factor": device.get("global_delay_factor", 2),
        }
        if "secret" in credentials:
            params["secret"] = credentials["secret"]
        if device.get("port"):
            params["port"] = int(device["port"])

        with ConnectHandler(**params) as connection:
            if credentials.get("secret") and hasattr(connection, "enable"):
                try:
                    connection.enable()
                except Exception:
                    pass
            config = connection.send_command("show running-config")

        target_dir = collected_root / name
        target_dir.mkdir(parents=True, exist_ok=True)
        output_path = target_dir / "current.cfg"
        output_path.write_text(config, encoding="utf-8")
        return output_path
