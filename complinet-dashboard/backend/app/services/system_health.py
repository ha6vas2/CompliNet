import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

import psutil


class SystemHealthService:
    def __init__(self, docker_binary: str = "docker"):
        self.docker_binary = docker_binary

    def _docker_status(self) -> Dict[str, Any]:
        docker_path = shutil.which(self.docker_binary)
        if not docker_path:
            return {"available": False, "running": None, "containers": None}

        try:
            result = subprocess.run(
                [docker_path, "info", "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return {"available": True, "running": False, "containers": None}

        if result.returncode != 0:
            return {"available": True, "running": False, "containers": None}

        containers = None
        try:
            containers = int(
                subprocess.check_output(
                    [docker_path, "ps", "-q"],
                    text=True,
                    timeout=3,
                ).count("\n")
            )
        except (OSError, subprocess.SubprocessError):
            pass

        return {"available": True, "running": True, "containers": containers}

    def snapshot(self) -> Dict[str, Any]:
        disk_path = Path.cwd().anchor or "/"
        uptime_seconds = max(0.0, time.time() - psutil.boot_time())
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(disk_path)

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": memory.percent,
            "memory_available_bytes": memory.available,
            "disk_percent": disk.percent,
            "disk_free_bytes": disk.free,
            "uptime_seconds": round(uptime_seconds, 1),
            "docker": self._docker_status(),
        }


system_health_service = SystemHealthService()
