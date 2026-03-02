from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent_sentinel.benchmark.core import run_benchmark
from agent_sentinel.benchmark.render import render_benchmark
from agent_sentinel.cli_exit_codes import (
    INTERNAL_ERROR,
    OK,
)
from agent_sentinel.errors import AgentSentinelError, PolicyFileNotFoundError, PolicyParseError
from agent_sentinel.forensics.ledger import FlightRecorder
from agent_sentinel.policy_schema import validate_policy_schema
from agent_sentinel.runtime.demo_planner import DemoPlanner
from agent_sentinel.security.audit import AuditEvent, from_exception, make_event, to_json
from agent_sentinel.security.capabilities import CapabilitySet
from agent_sentinel.security.context import RequestContext, new_request_id
from agent_sentinel.security.enforcer import enforce_request
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


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="agent-sentinel")
    p.add_argument("--policy", required=True, help="Path to policy JSON file")
    p.add_argument("--capability", required=True, help="Capability string to request")
    p.add_argument("--json", action="store_true", help="Output errors as JSON")
    p.add_argument(
        "--request-id",
        type=str,
        default=None,
        help="Optional request ID (auto-generated if omitted).",
    )
    p.add_argument(
        "--correlation-id",
        type=str,
        default=None,
        help="Optional correlation ID for tracing.",
    )
    p.add_argument(
        "--source",
        type=str,
        default="cli",
        help="Event source label (default: cli).",
    )
    p.add_argument(
        "--audit-json",
        action="store_true",
        help="Print one JSON audit event line to stderr.",
    )
    p.add_argument(
        "--benchmark",
        action="store_true",
        help="Run a micro-benchmark for enforcement (prints results, exit 0 on success).",
    )
    p.add_argument(
        "--iterations",
        type=int,
        default=10_000,
        help="Benchmark iterations (default: 10000).",
    )
    p.add_argument(
        "--warmup",
        type=int,
        default=200,
        help="Benchmark warmup iterations (default: 200).",
    )
    return p


def _load_policy(path: str) -> Any:
    policy_path = Path(path)
    if not policy_path.exists():
        raise PolicyFileNotFoundError(str(policy_path))
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PolicyParseError(str(policy_path), reason=str(exc)) from exc
    validate_policy_schema(policy)
    return policy


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    ctx = RequestContext(
        request_id=args.request_id or new_request_id(),
        correlation_id=args.correlation_id,
        source=args.source,
    )
    last_audit_event: AuditEvent | None = None

    def _audit_sink(event: AuditEvent) -> None:
        nonlocal last_audit_event
        last_audit_event = event

    try:
        policy = _load_policy(args.policy)

        if args.benchmark:

            def _target() -> None:
                enforce_request(args.capability, policy, ctx=ctx)

            result = run_benchmark(_target, iterations=args.iterations, warmup=args.warmup)
            print(render_benchmark(result, as_json=args.json))
            if args.audit_json:
                print(
                    to_json(
                        make_event(
                            ctx=ctx,
                            capability=args.capability,
                            decision="allow",
                            reason="benchmark completed",
                        )
                    ),
                    file=sys.stderr,
                )
            return OK

        enforce_request(
            args.capability,
            policy,
            ctx=ctx,
            audit_sink=_audit_sink if args.audit_json else None,
        )
        if args.audit_json and last_audit_event is not None:
            print(to_json(last_audit_event), file=sys.stderr)
        print("ALLOWED")
        return OK

    except AgentSentinelError as e:
        if args.audit_json:
            event = last_audit_event or from_exception(e, ctx=ctx, capability=args.capability)
            print(to_json(event), file=sys.stderr)
        if args.json:
            print(json.dumps(e.to_payload().to_dict(), sort_keys=True), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return e.exit_code

    except Exception as e:  # noqa: BLE001
        if args.audit_json:
            event = last_audit_event or from_exception(e, ctx=ctx, capability=args.capability)
            print(to_json(event), file=sys.stderr)
        if args.json:
            print(
                json.dumps(
                    {
                        "code": "internal_error",
                        "message": "Internal error",
                        "details": {"type": type(e).__name__},
                    },
                    sort_keys=True,
                ),
                file=sys.stderr,
            )
        else:
            print(f"Internal error: {e}", file=sys.stderr)
        return INTERNAL_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
