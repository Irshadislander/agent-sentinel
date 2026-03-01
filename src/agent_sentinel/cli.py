from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent_sentinel.forensics.ledger import FlightRecorder
from agent_sentinel.runtime.demo_planner import DemoPlanner
from agent_sentinel.security.capabilities import CapabilitySet
from agent_sentinel.security.tool_gateway import ToolGateway
from agent_sentinel.tools.fs_tool import read_text, write_text
from agent_sentinel.tools.http_tool import http_get, http_post

DEFAULT_POLICY_PATH = "configs/policies/default.yaml"
ToolFn = Callable[..., Any]


def _parse_scalar(raw_value: str) -> Any:
    value = raw_value.strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() == "null":
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item.strip()) for item in inner.split(",")]
    try:
        return int(value)
    except ValueError:
        return value


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- "):
            if current_list_key is None:
                raise ValueError("invalid yaml: list item without key")
            item_value = _parse_scalar(stripped[2:])
            parsed[current_list_key].append(item_value)
            continue

        if ":" not in stripped:
            raise ValueError(f"invalid yaml line: {line}")

        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value == "":
            parsed[key] = []
            current_list_key = key
        else:
            parsed[key] = _parse_scalar(value)
            current_list_key = None

    return parsed


def load_policy(path: str) -> dict[str, Any]:
    policy_path = Path(path)
    if not policy_path.exists():
        raise FileNotFoundError(f"policy file not found: {policy_path}")

    text = policy_path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        pass

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = _parse_simple_yaml(text)
    if not isinstance(data, dict):
        raise ValueError("policy must parse to an object")
    return data


def _default_run_id() -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return f"run_{timestamp}"


def _prepare_demo_workspace() -> None:
    public_dir = Path("public")
    public_dir.mkdir(parents=True, exist_ok=True)
    demo_input = public_dir / "demo_input.txt"
    if not demo_input.exists():
        demo_input.write_text("agent-sentinel demo input\n", encoding="utf-8")
    Path("workspace").mkdir(parents=True, exist_ok=True)


def run_demo(policy_path: str = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    policy = load_policy(policy_path)
    granted_caps = policy.get("granted_caps", [])
    capabilities_map = policy.get("capabilities")
    if isinstance(capabilities_map, dict):
        granted_caps = [
            str(capability) for capability, enabled in capabilities_map.items() if bool(enabled)
        ]
    if not isinstance(granted_caps, list):
        raise ValueError("policy key granted_caps must be a list or policy.capabilities dict")

    run_id = _default_run_id()
    ledger_path = Path("runs") / run_id / "ledger.jsonl"
    recorder = FlightRecorder(str(ledger_path), run_id=run_id)
    caps = CapabilitySet(set(str(cap) for cap in granted_caps))
    tools: dict[str, ToolFn] = {
        "read_text": read_text,
        "write_text": write_text,
        "http_get": http_get,
        "http_post": http_post,
    }
    gateway = ToolGateway(
        policy=policy,
        recorder=recorder,
        caps=caps,
        tools=tools,
    )

    _prepare_demo_workspace()

    planner = DemoPlanner()
    task = planner.build_task(policy_path=policy_path)
    actions = planner.plan(task)

    allowed = 0
    denied = 0
    failures = 0
    action_results: list[dict[str, Any]] = []

    for tool_name, args in actions:
        try:
            result = gateway.execute(tool_name, args)
            if isinstance(result, dict) and result.get("ok") is False:
                denied += 1
                action_results.append(
                    {
                        "tool_name": tool_name,
                        "status": "denied",
                        "reason": str(result.get("reason", "blocked")),
                    }
                )
            else:
                allowed += 1
                action_results.append(
                    {
                        "tool_name": tool_name,
                        "status": "allowed",
                        "result_keys": sorted(result.keys()),
                    }
                )
        except PermissionError as exc:
            denied += 1
            action_results.append({"tool_name": tool_name, "status": "denied", "reason": str(exc)})
        except Exception as exc:
            failures += 1
            action_results.append(
                {
                    "tool_name": tool_name,
                    "status": "failed",
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )

    verified, verify_reason = recorder.verify()
    summary = {
        "run_id": run_id,
        "ledger_path": str(ledger_path),
        "allowed": allowed,
        "denied": denied,
        "failed": failures,
        "root_hash": recorder.last_hash(),
        "verify_ok": verified,
        "verify_reason": verify_reason,
        "actions": action_results,
    }
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a deterministic Agent Sentinel demo.")
    parser.add_argument("--policy", default=DEFAULT_POLICY_PATH, help="Path to policy file")
    args = parser.parse_args(argv)

    summary = run_demo(policy_path=args.policy)
    print(f"run_id={summary['run_id']}")
    print(
        f"allowed={summary['allowed']} denied={summary['denied']} "
        f"failed={summary['failed']} root_hash={summary['root_hash']}"
    )
    print(f"ledger={summary['ledger_path']} verify={summary['verify_reason']}")
    return 0 if summary["verify_ok"] else 1
