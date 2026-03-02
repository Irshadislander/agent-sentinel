from __future__ import annotations

import getpass
import json
import socket
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class RunContext:
    run_id: str
    correlation_id: str | None
    timestamp: str
    git_sha: str
    user: str
    host: str


@dataclass(frozen=True)
class TraceEvent:
    event_type: str
    run_context: RunContext
    capability_id: str
    schema_version: str
    validation_outcome: str
    duration_ms: float
    exit_code: int
    error_kind: str | None
    error: str | None


def new_run_context(
    *,
    run_id: str | None = None,
    correlation_id: str | None = None,
) -> RunContext:
    return RunContext(
        run_id=run_id or uuid4().hex,
        correlation_id=correlation_id,
        timestamp=datetime.now(UTC).isoformat(),
        git_sha=_resolve_git_sha(),
        user=getpass.getuser(),
        host=socket.gethostname(),
    )


def _resolve_git_sha() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            check=True,
            text=True,
        )
    except Exception:
        return "unknown"
    return completed.stdout.strip() or "unknown"


class TraceStore:
    def __init__(self, path: str | Path = Path("runs") / "trace.jsonl") -> None:
        self.path = Path(path)

    def append(self, event: TraceEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(asdict(event), sort_keys=True, separators=(",", ":"))
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    def read_last(self, limit: int) -> list[dict[str, object]]:
        if limit <= 0:
            return []
        if not self.path.exists():
            return []

        events: list[dict[str, object]] = []
        for raw_line in self.path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                events.append(item)
        return events[-limit:]


def validate_payload_against_schema(
    payload: object,
    schema: dict[str, object],
) -> tuple[bool, str | None]:
    expected_type = schema.get("type")
    if expected_type == "object" and not isinstance(payload, dict):
        return False, "payload must be an object"

    if not isinstance(payload, dict):
        return False, "payload must be an object"

    required = schema.get("required", [])
    if isinstance(required, list):
        for key in required:
            if isinstance(key, str) and key not in payload:
                return False, f"missing required field: {key}"

    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for key, value in payload.items():
            if key not in properties:
                continue
            property_schema = properties.get(key)
            if not isinstance(property_schema, dict):
                continue
            property_type = property_schema.get("type")
            if not isinstance(property_type, str):
                continue
            if not _matches_json_type(value, property_type):
                return False, f"field '{key}' must be of type {property_type}"

    return True, None


def _matches_json_type(value: object, expected_type: str) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "null":
        return value is None
    return True
