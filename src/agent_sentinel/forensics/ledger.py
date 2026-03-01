from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

_SENSITIVE_MARKER = "***"
_SENSITIVE_TOKENS = ("key", "token", "secret", "password")
_REQUIRED_FIELDS = (
    "ts",
    "run_id",
    "seq",
    "event_type",
    "payload",
    "prev_hash",
    "entry_hash",
)


@dataclass
class LedgerEntry:
    ts: str
    run_id: str
    seq: int
    event_type: str
    payload: dict[str, Any]
    prev_hash: str
    entry_hash: str


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _utc_iso8601() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _should_redact(key: str) -> bool:
    lowered = key.lower()
    return any(token in lowered for token in _SENSITIVE_TOKENS)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            key = str(raw_key)
            if _should_redact(key):
                redacted[key] = _SENSITIVE_MARKER
            else:
                redacted[key] = _redact(raw_value)
        return redacted
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, tuple):
        return [_redact(item) for item in value]
    return value


def _entry_hash_input(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "ts": entry["ts"],
        "run_id": entry["run_id"],
        "seq": entry["seq"],
        "event_type": entry["event_type"],
        "payload": entry["payload"],
        "prev_hash": entry["prev_hash"],
    }


def _compute_entry_hash(entry: dict[str, Any]) -> str:
    return _sha256_hex(_canonical_json(_entry_hash_input(entry)))


class FlightRecorder:
    def __init__(self, log_path: str, run_id: str) -> None:
        self._log_path = Path(log_path)
        self._run_id = run_id

        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log_path.touch(exist_ok=True)

        self._seq = 0
        self._last_hash = ""

        ok, reason, next_seq, last_hash = self._scan_chain()
        if not ok:
            raise ValueError(f"invalid ledger: {reason}")
        self._seq = next_seq
        self._last_hash = last_hash

    def append(self, event_type: str, payload: dict[str, Any]) -> LedgerEntry:
        if not isinstance(event_type, str) or not event_type:
            raise ValueError("event_type must be a non-empty string")
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict")

        redacted_payload = _redact(payload)
        entry_data: dict[str, Any] = {
            "ts": _utc_iso8601(),
            "run_id": self._run_id,
            "seq": self._seq,
            "event_type": event_type,
            "payload": redacted_payload,
            "prev_hash": self._last_hash,
        }
        entry_data["entry_hash"] = _compute_entry_hash(entry_data)

        entry = LedgerEntry(**entry_data)

        with self._log_path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical_json(asdict(entry)))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        self._seq += 1
        self._last_hash = entry.entry_hash
        return entry

    def last_hash(self) -> str:
        return self._last_hash

    def verify(self) -> tuple[bool, str]:
        ok, reason, _, _ = self._scan_chain()
        if ok:
            return True, "ok"
        return False, reason

    def _scan_chain(self) -> tuple[bool, str, int, str]:
        expected_seq = 0
        expected_prev_hash = ""

        with self._log_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                raw_line = line.rstrip("\n")
                if raw_line == "":
                    return False, f"empty line at line {line_number}", expected_seq, expected_prev_hash

                try:
                    entry = json.loads(raw_line)
                except json.JSONDecodeError as exc:
                    return (
                        False,
                        f"invalid JSON at line {line_number}: {exc.msg}",
                        expected_seq,
                        expected_prev_hash,
                    )

                if not isinstance(entry, dict):
                    return False, f"invalid entry object at line {line_number}", expected_seq, expected_prev_hash

                missing = [field for field in _REQUIRED_FIELDS if field not in entry]
                if missing:
                    return (
                        False,
                        f"missing fields at line {line_number}: {','.join(missing)}",
                        expected_seq,
                        expected_prev_hash,
                    )

                seq = entry["seq"]
                if not isinstance(seq, int):
                    return False, f"invalid seq at line {line_number}", expected_seq, expected_prev_hash
                if seq != expected_seq:
                    return (
                        False,
                        f"sequence mismatch at line {line_number}: expected {expected_seq}, got {seq}",
                        expected_seq,
                        expected_prev_hash,
                    )

                prev_hash = entry["prev_hash"]
                if not isinstance(prev_hash, str):
                    return False, f"invalid prev_hash at line {line_number}", expected_seq, expected_prev_hash
                if prev_hash != expected_prev_hash:
                    return False, f"previous hash mismatch at line {line_number}", expected_seq, expected_prev_hash

                stored_hash = entry["entry_hash"]
                if not isinstance(stored_hash, str):
                    return False, f"invalid entry_hash at line {line_number}", expected_seq, expected_prev_hash

                try:
                    computed_hash = _compute_entry_hash(entry)
                except (TypeError, ValueError):
                    return (
                        False,
                        f"unable to hash entry at line {line_number}",
                        expected_seq,
                        expected_prev_hash,
                    )

                if computed_hash != stored_hash:
                    return False, f"entry hash mismatch at line {line_number}", expected_seq, expected_prev_hash

                expected_seq += 1
                expected_prev_hash = stored_hash

        return True, "ok", expected_seq, expected_prev_hash
