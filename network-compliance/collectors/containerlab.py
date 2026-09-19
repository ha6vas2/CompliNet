import subprocess
from pathlib import Path
from typing import Any


class ContainerlabCollector:
    """Collect FRR configuration for lab devices running in Containerlab."""

    def collect_device(self, device: dict[str, Any], collected_root: Path) -> Path:
        name = device["name"]
        container = device["container"]

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

        target_dir = collected_root / name
        target_dir.mkdir(parents=True, exist_ok=True)
        output_path = target_dir / "current.cfg"
        output_path.write_text(result.stdout, encoding="utf-8")
        return output_path
