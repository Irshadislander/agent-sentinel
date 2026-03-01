from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import streamlit as st

from agent_sentinel.forensics.verify import verify_log

RUNS_DIR = Path("runs")


def _discover_ledgers(root: Path) -> list[Path]:
    if not root.exists():
        return []
    files = [path for path in root.rglob("ledger.jsonl") if path.is_file()]
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def _load_events(ledger_path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with ledger_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw_line = line.strip()
            if not raw_line:
                continue
            try:
                parsed = json.loads(raw_line)
            except json.JSONDecodeError:
                parsed = {"event_type": "invalid_json", "raw": raw_line}
            if isinstance(parsed, dict):
                events.append(parsed)
            else:
                events.append({"event_type": "invalid_entry", "raw": parsed})
    return events


def _run_id_from_path(ledger_path: Path) -> str:
    if ledger_path.parent.name:
        return ledger_path.parent.name
    return str(ledger_path)


def _latest_runs_rows(ledger_paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in ledger_paths:
        events = _load_events(path)
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat()
        root_hash = events[-1].get("entry_hash", "") if events else ""
        rows.append(
            {
                "run_id": _run_id_from_path(path),
                "events": len(events),
                "updated_utc": modified,
                "root_hash": root_hash,
                "ledger_path": str(path),
            }
        )
    return rows


def _render_verification(ledger_path: Path) -> None:
    state_key = f"verify:{ledger_path}"
    if st.button("Verify", type="primary"):
        st.session_state[state_key] = verify_log(str(ledger_path))

    result = st.session_state.get(state_key)
    if result is not None:
        ok, reason = result
        if ok:
            st.success("Verification passed: ok")
        else:
            st.error(f"Verification failed: {reason}")


def main() -> None:
    st.set_page_config(page_title="Agent Sentinel Runs", layout="wide")
    st.title("Agent Sentinel Run Browser")

    ledgers = _discover_ledgers(RUNS_DIR)
    if not ledgers:
        st.info("No runs found. Expected ledgers under runs/**/ledger.jsonl")
        return

    st.subheader("Latest Runs")
    rows = _latest_runs_rows(ledgers)
    st.dataframe(rows, width="stretch", hide_index=True)

    selected = st.selectbox(
        "Select run ledger",
        options=ledgers,
        format_func=lambda path: f"{_run_id_from_path(path)} — {path}",
    )

    events = _load_events(selected)
    root_hash = events[-1].get("entry_hash", "") if events else ""

    col1, col2 = st.columns([4, 1])
    with col1:
        st.text_input("Root Hash", value=root_hash or "N/A", disabled=True)
    with col2:
        _render_verification(selected)

    st.subheader("Ledger Events")
    if events:
        st.dataframe(events, width="stretch", hide_index=True)
    else:
        st.info("Selected ledger has no events.")


if __name__ == "__main__":
    main()
