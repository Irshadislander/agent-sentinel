from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter_ns
from typing import Any

from agent_sentinel.benchmark.core import run_benchmark
from agent_sentinel.benchmark.render import render_benchmark
from agent_sentinel.capabilities import registry
from agent_sentinel.capabilities.base import Result
from agent_sentinel.capabilities.plugins import load_capabilities
from agent_sentinel.cli_exit_codes import (
    INTERNAL_ERROR,
    OK,
    USAGE,
    ExitCode,
)
from agent_sentinel.errors import AgentSentinelError, PolicyFileNotFoundError, PolicyParseError
from agent_sentinel.forensics.ledger import FlightRecorder
from agent_sentinel.observability import (
    TraceEvent,
    TraceStore,
    new_run_context,
    validate_payload_against_schema,
)
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


def _build_plugin_options_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--no-plugins",
        action="store_true",
        help="Disable plugin discovery and load only core capabilities.",
    )
    parser.add_argument(
        "--plugins",
        default=None,
        help="Path to allowlist file containing permitted plugin entrypoint names.",
    )
    parser.add_argument(
        "--strict-plugins",
        action="store_true",
        help="Fail fast if any plugin fails to load.",
    )
    return parser


def _load_plugin_allowlist(path: str) -> list[str]:
    allowlist_path = Path(path)
    if not allowlist_path.exists():
        raise FileNotFoundError(f"plugin allowlist file not found: {allowlist_path}")

    entries: list[str] = []
    for raw_line in allowlist_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        entries.append(line)
    return entries


def _print_capabilities_table() -> None:
    entries = registry.entries()
    headers = ("name", "namespace", "version", "description")
    rows = [
        (
            entry.metadata.name,
            entry.metadata.namespace,
            entry.metadata.version,
            entry.metadata.description,
        )
        for entry in entries
    ]

    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def _format_row(values: tuple[str, str, str, str]) -> str:
        return " | ".join(value.ljust(widths[index]) for index, value in enumerate(values))

    print(_format_row(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(_format_row(row))


def _dispatch_command(argv: list[str]) -> int | None:
    if argv and argv[0] == "list":
        _print_capabilities_table()
        return OK
    if len(argv) >= 2 and argv[0] == "capabilities" and argv[1] == "list":
        _print_capabilities_table()
        return OK
    if argv and argv[0] == "run":
        return _dispatch_run_command(argv[1:])
    if len(argv) >= 2 and argv[0] == "trace" and argv[1] == "view":
        return _dispatch_trace_view_command(argv[2:])
    return None


def _dispatch_run_command(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="agent-sentinel run")
    parser.add_argument("capability_id", help="Capability id (spec.id) to execute")
    parser.add_argument("--payload", default="{}", help="JSON payload object")
    parser.add_argument("--run-id", default=None, help="Optional run identifier")
    parser.add_argument("--correlation-id", default=None, help="Optional correlation id")
    parser.add_argument("--trace-path", default="runs/trace.jsonl", help="Trace JSONL output path")
    parser.add_argument(
        "--emit-json", action="store_true", help="Emit machine-readable JSON output"
    )
    args = parser.parse_args(argv)

    trace_store = TraceStore(args.trace_path)
    run_context = new_run_context(run_id=args.run_id, correlation_id=args.correlation_id)
    capability_id = args.capability_id
    schema_version = "unknown"
    validation_outcome = "failed"
    error_kind: str | None = None
    error: str | None = None
    duration_ms = 0.0
    exit_code = int(ExitCode.RUNTIME)
    output_data: dict[str, Any] | None = None

    try:
        payload_raw = json.loads(args.payload)
    except json.JSONDecodeError as exc:
        error_kind = "payload_parse_error"
        error = str(exc)
        exit_code = USAGE
        event = TraceEvent(
            event_type="capability.call",
            run_context=run_context,
            capability_id=capability_id,
            schema_version=schema_version,
            validation_outcome=validation_outcome,
            duration_ms=duration_ms,
            exit_code=exit_code,
            error_kind=error_kind,
            error=error,
        )
        trace_store.append(event)
        if args.emit_json:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "invalid payload json",
                        "details": str(exc),
                    },
                    sort_keys=True,
                )
            )
        else:
            print(f"Error: invalid payload json: {exc}", file=sys.stderr)
        return exit_code

    try:
        capability_cls = registry.get_by_id(capability_id)
        spec = registry.get_spec_by_id(capability_id)
        schema_version = str(spec.schema.get("$schema", spec.version))

        is_valid, validation_error = validate_payload_against_schema(payload_raw, spec.schema)
        if not is_valid:
            validation_outcome = "failed"
            error_kind = "validation_error"
            error = validation_error
            exit_code = USAGE
            result = Result(ok=False, code=ExitCode.USAGE, error=validation_error)
        else:
            validation_outcome = "passed"
            capability = capability_cls()
            start_ns = perf_counter_ns()
            try:
                raw_result = capability.execute(
                    payload_raw if isinstance(payload_raw, dict) else {}
                )
                duration_ms = (perf_counter_ns() - start_ns) / 1_000_000
            except Exception as exc:
                duration_ms = (perf_counter_ns() - start_ns) / 1_000_000
                error_kind = type(exc).__name__
                error = str(exc)
                result = Result(ok=False, code=ExitCode.RUNTIME, error=error)
            else:
                if isinstance(raw_result, Result):
                    result = raw_result
                else:
                    result = Result(ok=True, code=ExitCode.OK, data={"result": raw_result})

        exit_code = int(result.code)
        if result.error and error_kind is None:
            error_kind = "capability_error"
            error = result.error
        output_data = result.data

    except Exception as exc:
        error_kind = type(exc).__name__
        error = str(exc)
        exit_code = INTERNAL_ERROR
        validation_outcome = "failed"

    event = TraceEvent(
        event_type="capability.call",
        run_context=run_context,
        capability_id=capability_id,
        schema_version=schema_version,
        validation_outcome=validation_outcome,
        duration_ms=duration_ms,
        exit_code=exit_code,
        error_kind=error_kind,
        error=error,
    )
    trace_store.append(event)

    if args.emit_json:
        print(
            json.dumps(
                {
                    "ok": exit_code == OK,
                    "run_id": run_context.run_id,
                    "capability_id": capability_id,
                    "exit_code": exit_code,
                    "data": output_data,
                    "error_kind": error_kind,
                    "error": error,
                },
                sort_keys=True,
            )
        )
    elif exit_code == OK:
        print("OK")
    else:
        print(f"Error: {error_kind or 'unknown_error'}: {error}", file=sys.stderr)

    return exit_code


def _dispatch_trace_view_command(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="agent-sentinel trace view")
    parser.add_argument(
        "--last", type=int, default=20, help="Number of recent trace events to show"
    )
    parser.add_argument("--trace-path", default="runs/trace.jsonl", help="Trace JSONL input path")
    parser.add_argument("--emit-json", action="store_true", help="Emit JSON array")
    args = parser.parse_args(argv)

    trace_store = TraceStore(args.trace_path)
    events = trace_store.read_last(args.last)

    if args.emit_json:
        print(json.dumps(events, sort_keys=True))
        return OK

    if not events:
        print("No trace events found.")
        return OK

    headers = (
        "timestamp",
        "run_id",
        "capability_id",
        "validation",
        "duration_ms",
        "exit_code",
        "error_kind",
    )
    rows: list[tuple[str, str, str, str, str, str, str]] = []
    for event in events:
        context = event.get("run_context", {})
        if not isinstance(context, dict):
            context = {}
        rows.append(
            (
                str(context.get("timestamp", "")),
                str(context.get("run_id", "")),
                str(event.get("capability_id", "")),
                str(event.get("validation_outcome", "")),
                f"{float(event.get('duration_ms', 0.0)):.3f}",
                str(event.get("exit_code", "")),
                str(event.get("error_kind", "")),
            )
        )

    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def _format_row(values: tuple[str, ...]) -> str:
        return " | ".join(value.ljust(widths[index]) for index, value in enumerate(values))

    print(_format_row(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(_format_row(row))
    return OK


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
    p.add_argument(
        "--no-plugins",
        action="store_true",
        help="Disable plugin discovery and load only core capabilities.",
    )
    p.add_argument(
        "--plugins",
        default=None,
        help="Path to allowlist file containing permitted plugin entrypoint names.",
    )
    p.add_argument(
        "--strict-plugins",
        action="store_true",
        help="Fail fast if any plugin fails to load.",
    )
    p.add_argument(
        "--capability-name", default=None, help="Registered capability implementation to run"
    )
    p.add_argument("--payload", default=None, help="JSON payload for --capability-name execution")
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
    raw_args = argv if argv is not None else sys.argv[1:]
    plugin_parser = _build_plugin_options_parser()
    plugin_options, command_args = plugin_parser.parse_known_args(raw_args)

    try:
        if not plugin_options.no_plugins:
            allowed_plugins: list[str] | None = None
            if plugin_options.plugins:
                allowed_plugins = _load_plugin_allowlist(plugin_options.plugins)
            load_capabilities(
                allowed=allowed_plugins,
                strict=plugin_options.strict_plugins,
                warn=lambda msg: print(f"Warning: {msg}", file=sys.stderr),
            )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return INTERNAL_ERROR

    command_result = _dispatch_command(command_args)
    if command_result is not None:
        return command_result

    parser = _build_parser()
    args = parser.parse_args(command_args)
    capability_name = args.capability_name
    payload = json.loads(args.payload) if args.payload else None
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
        # Example capability execution wiring
        if capability_name:
            capability_cls = registry.get(capability_name)
            capability = capability_cls()
            result = capability.execute(payload or {})
            print(result)
            return OK

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
