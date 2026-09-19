import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditService:
    def __init__(self, database_path: Optional[Path] = None):
        root = Path(__file__).resolve().parents[3]
        self.database_path = database_path or root / "data" / "audit.db"
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.database_path))
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    device_name TEXT,
                    details_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def record(
        self,
        event_type: str,
        status: str,
        device_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        created_at = datetime.now(timezone.utc).isoformat()
        details_json = json.dumps(details or {}, sort_keys=True, default=str)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO events
                    (event_type, status, device_name, details_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (event_type, status, device_name, details_json, created_at),
            )
            event_id = cursor.lastrowid
        return {
            "id": event_id,
            "event_type": event_type,
            "status": status,
            "device_name": device_name,
            "details": details or {},
            "created_at": created_at,
        }

    def list_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        safe_limit = max(1, min(limit, 500))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM events ORDER BY id DESC LIMIT ?", (safe_limit,)
            ).fetchall()
        return [
            {
                "id": row["id"],
                "event_type": row["event_type"],
                "status": row["status"],
                "device_name": row["device_name"],
                "details": json.loads(row["details_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]


audit_service = AuditService()
