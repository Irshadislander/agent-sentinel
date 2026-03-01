from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

_REQUIRED_FIELDS: tuple[str, ...] = (
    "ts",
    "run_id",
    "seq",
    "event_type",
    "payload",
    "prev_hash",
    "entry_hash",
)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _compute_entry_hash(entry: dict[str, Any]) -> str:
    hash_input = {
        "ts": entry["ts"],
        "run_id": entry["run_id"],
        "seq": entry["seq"],
        "event_type": entry["event_type"],
        "payload": entry["payload"],
        "prev_hash": entry["prev_hash"],
    }
    encoded = _canonical_json(hash_input).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_log(log_path: str) -> tuple[bool, str]:
    path = Path(log_path)
    if not path.exists():
        return False, "log file does not exist"

    expected_seq = 0
    expected_prev_hash = ""

    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                raw_line = line.rstrip("\n")
                if raw_line == "":
                    return False, f"empty line at line {line_number}"

                try:
                    entry = json.loads(raw_line)
                except json.JSONDecodeError as exc:
                    return False, f"invalid JSON at line {line_number}: {exc.msg}"

                if not isinstance(entry, dict):
                    return False, f"invalid entry object at line {line_number}"

                missing = [field for field in _REQUIRED_FIELDS if field not in entry]
                if missing:
                    return False, f"missing fields at line {line_number}: {','.join(missing)}"

                seq = entry["seq"]
                if not isinstance(seq, int):
                    return False, f"invalid seq at line {line_number}"
                if seq != expected_seq:
                    return (
                        False,
                        f"sequence mismatch at line {line_number}: expected {expected_seq}, got {seq}",
                    )

                prev_hash = entry["prev_hash"]
                if not isinstance(prev_hash, str):
                    return False, f"invalid prev_hash at line {line_number}"
                if prev_hash != expected_prev_hash:
                    return False, f"previous hash mismatch at line {line_number}"

                stored_hash = entry["entry_hash"]
                if not isinstance(stored_hash, str):
                    return False, f"invalid entry_hash at line {line_number}"

                try:
                    computed_hash = _compute_entry_hash(entry)
                except (TypeError, ValueError):
                    return False, f"non-canonical entry data at line {line_number}"

                if computed_hash != stored_hash:
                    return False, f"entry hash mismatch at line {line_number}"

                expected_prev_hash = stored_hash
                expected_seq += 1
    except OSError as exc:
        reason = exc.strerror or str(exc)
        return False, f"unable to read log: {reason}"

    return True, "ok"
