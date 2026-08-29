import subprocess
from pathlib import Path
from typing import Any


BASE_PATH = Path(__file__).resolve().parents[1]
COLLECTED_ROOT = BASE_PATH / "collected"


def collect_container_config(container: str) -> str:
    """Collect the live FRR configuration from a Containerlab node."""

    result = subprocess.run(
        [
            "docker",
            "exec",
            container,
            "vtysh",
            "-c",
            "show running-config",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Configuration collection failed for {container}: "
            f"{result.stderr.strip()}"
        )

    return result.stdout


def collect_device(device: dict[str, Any]) -> Path:
    """Collect and save one Containerlab device configuration."""

    name = device["name"]
    container = device["container"]

    print(f"Collecting config for {name} ({container})...")

    config = collect_container_config(container)

    device_dir = COLLECTED_ROOT / name
    device_dir.mkdir(parents=True, exist_ok=True)

    output_path = device_dir / "current.cfg"
    output_path.write_text(config, encoding="utf-8")

    print(f"[OK] {name} -> {output_path}")

    return output_path


def collect_all(devices: list[dict[str, Any]]) -> list[Path]:
    """Collect all Containerlab devices."""

    paths = []

    for device in devices:
        if device.get("source") != "containerlab":
            continue

        try:
            paths.append(collect_device(device))
        except Exception as exc:
            print(f"[ERROR] {device.get('name')}: {exc}")

    return paths
