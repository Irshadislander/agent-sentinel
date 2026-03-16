from __future__ import annotations

import argparse
import csv
import json
import re
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent_sentinel.baselines import (
    ArgumentAllowlistExecutor,
    NoAuditExecutor,
    NoopRecorder,
    NoProtectionExecutor,
    ProgentStyleExecutor,
    StaticAllowlistExecutor,
    ValidatorOnlyExecutor,
    granted_capabilities_from_policy,
)
from agent_sentinel.benchmark.runner import (
    DEFAULT_POLICY_PATH,
    DEFAULT_TASKS_DIR,
    _execute_task,
    _load_tasks,
    _prepare_fixture_data,
    _simulated_http_get,
    _simulated_http_post,
    _unsafe_plugin_write_text,
    _working_directory,
)
from agent_sentinel.cli import load_policy
from agent_sentinel.forensics.ledger import FlightRecorder
from agent_sentinel.security.capabilities import CapabilitySet
from agent_sentinel.security.tool_gateway import ToolGateway
from agent_sentinel.tools.fs_tool import read_text, write_text

DEFAULT_OUTPUT_DIR = Path("artifacts") / "baselines"
DEFAULT_JSON_PATH = DEFAULT_OUTPUT_DIR / "baseline_suite.json"
DEFAULT_CSV_PATH = DEFAULT_OUTPUT_DIR / "baseline_suite.csv"
SAFE_CATEGORIES = {"benign", "trace_stress"}
SECURITY_DENY_CATEGORIES = {"malicious", "policy_blocked"}
ROBUSTNESS_CATEGORIES = {"malformed_payload", "plugin_failure"}
DEFAULT_SYNTH_ROOT = Path("configs/tasks_synth")


@dataclass(frozen=True)
class SystemSpec:
    system_id: str
    label: str
    notes: str
    use_audit: bool


@dataclass(frozen=True)
class WorkloadSelection:
    tasks_dir: Path
    selection_mode: str
    selection_reason: str
    exact_75_found: bool
    scenario_count: int


SYSTEM_SPECS = (
    SystemSpec(
        system_id="no_protection",
        label="No Protection",
        notes="Always allow tool execution; no runtime mediation.",
        use_audit=False,
    ),
    SystemSpec(
        system_id="static_allowlist",
        label="Static Allowlist",
        notes="Allow only by tool name; no argument-aware enforcement.",
        use_audit=False,
    ),
    SystemSpec(
        system_id="argument_allowlist",
        label="Argument Allowlist",
        notes="Allow by tool name plus simple path and destination checks.",
        use_audit=False,
    ),
    SystemSpec(
        system_id="validator_only",
        label="Validator Only",
        notes="Argument validation enabled; capability policy mediation disabled.",
        use_audit=False,
    ),
    SystemSpec(
        system_id="no_audit",
        label="No Audit",
        notes="Full mediation path with audit and trace emission disabled.",
        use_audit=False,
    ),
    SystemSpec(
        system_id="progent_style",
        label="Progent-style",
        notes="Lightweight rule-based DSL-style policy over tools and arguments.",
        use_audit=False,
    ),
    SystemSpec(
        system_id="agent_sentinel",
        label="Agent-Sentinel",
        notes="Full runtime capability mediation with validators and audit trail.",
        use_audit=True,
    ),
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run baseline comparisons for Agent-Sentinel.")
    parser.add_argument("--tasks-dir", default=None)
    parser.add_argument("--policy", default=DEFAULT_POLICY_PATH)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


def _tool_map() -> dict[str, Any]:
    return {
        "read_text": read_text,
        "write_text": write_text,
        "fs_tool.write_text": _unsafe_plugin_write_text,
        "plugin.exec": _unsafe_plugin_write_text,
        "http_get": _simulated_http_get,
        "http_post": _simulated_http_post,
    }


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * percentile
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    weight = index - low
    return ordered[low] + (ordered[high] - ordered[low]) * weight


def _category_bucket(category: str) -> str:
    if category in SAFE_CATEGORIES:
        return "safe"
    if category in SECURITY_DENY_CATEGORIES:
        return "security_deny"
    if category in ROBUSTNESS_CATEGORIES:
        return "robustness"
    return "security_deny"


def _task_count(tasks_dir: Path) -> int:
    try:
        return len(_load_tasks(tasks_dir.resolve()))
    except ValueError:
        return 0


def _select_workload(tasks_dir: str | None) -> WorkloadSelection:
    if tasks_dir:
        resolved = Path(tasks_dir).resolve()
        scenario_count = _task_count(resolved)
        return WorkloadSelection(
            tasks_dir=resolved,
            selection_mode="explicit",
            selection_reason=f"Using explicitly requested workload: {resolved}",
            exact_75_found=(scenario_count == 75),
            scenario_count=scenario_count,
        )

    canonical_dir = Path(DEFAULT_TASKS_DIR).resolve()
    canonical_count = _task_count(canonical_dir)

    synthetic_candidates: list[tuple[int, Path]] = []
    synth_root = DEFAULT_SYNTH_ROOT.resolve()
    if synth_root.exists():
        for candidate in sorted(synth_root.iterdir()):
            if not candidate.is_dir():
                continue
            count = _task_count(candidate)
            if count > 0:
                synthetic_candidates.append((count, candidate.resolve()))

    exact_75 = next((item for item in synthetic_candidates if item[0] == 75), None)
    if exact_75 is not None:
        count, selected = exact_75
        return WorkloadSelection(
            tasks_dir=selected,
            selection_mode="auto",
            selection_reason=(
                "Using exact 75-scenario benchmark workload discovered in configs/tasks_synth."
            ),
            exact_75_found=True,
            scenario_count=count,
        )

    if synthetic_candidates:
        count, selected = max(synthetic_candidates, key=lambda item: item[0])
        match = re.fullmatch(r"scale_n(\d+)", selected.name)
        scale_label = f" ({selected.name})" if match else ""
        return WorkloadSelection(
            tasks_dir=selected,
            selection_mode="auto",
            selection_reason=(
                "No exact 75-scenario benchmark workload was found. "
                f"Using the largest pre-generated benchmark workload available{scale_label}: "
                f"{count} scenarios from {selected}."
            ),
            exact_75_found=False,
            scenario_count=count,
        )

    return WorkloadSelection(
        tasks_dir=canonical_dir,
        selection_mode="auto",
        selection_reason=(
            "No larger pre-generated benchmark workload was found. "
            f"Falling back to canonical task set in {canonical_dir} ({canonical_count} scenarios)."
        ),
        exact_75_found=False,
        scenario_count=canonical_count,
    )


def _summarize_results(results: list[Any]) -> dict[str, float | int]:
    safe_results = [
        result for result in results if _category_bucket(str(result.category)) == "safe"
    ]
    unsafe_results = [
        result for result in results if _category_bucket(str(result.category)) == "security_deny"
    ]
    robustness_results = [
        result for result in results if _category_bucket(str(result.category)) == "robustness"
    ]
    latencies = [float(result.latency_ms) for result in results]

    unsafe_blocked = sum(1 for result in unsafe_results if result.blocked)
    safe_allowed = sum(1 for result in safe_results if result.success)
    robustness_blocked = sum(1 for result in robustness_results if result.blocked)
    robustness_errors = sum(
        1 for result in robustness_results if (not result.success) and (not result.blocked)
    )
    robustness_success = sum(1 for result in robustness_results if result.success)
    execution_error_count = sum(
        1 for result in results if (not result.success) and (not result.blocked)
    )
    category_outcomes: dict[str, dict[str, int]] = {}
    for result in results:
        category = str(result.category)
        bucket = category_outcomes.setdefault(
            category,
            {"total": 0, "blocked": 0, "success": 0, "error": 0},
        )
        bucket["total"] += 1
        if result.blocked:
            bucket["blocked"] += 1
        elif result.success:
            bucket["success"] += 1
        else:
            bucket["error"] += 1

    return {
        "unsafe_actions_blocked_pct": round(
            (unsafe_blocked / len(unsafe_results)) * 100.0 if unsafe_results else 0.0,
            2,
        ),
        "safe_actions_allowed_pct": round(
            (safe_allowed / len(safe_results)) * 100.0 if safe_results else 0.0,
            2,
        ),
        "median_latency_ms": round(_percentile(latencies, 0.5), 6),
        "p95_latency_ms": round(_percentile(latencies, 0.95), 6),
        "unsafe_total": len(unsafe_results),
        "unsafe_blocked_count": unsafe_blocked,
        "safe_total": len(safe_results),
        "safe_allowed_count": safe_allowed,
        "robustness_total": len(robustness_results),
        "robustness_blocked_count": robustness_blocked,
        "robustness_error_count": robustness_errors,
        "robustness_success_count": robustness_success,
        "execution_error_count": execution_error_count,
        "scenario_count": len(results),
        "category_outcomes": category_outcomes,
    }


def _build_executor(
    *,
    spec: SystemSpec,
    policy: dict[str, Any],
    tools: dict[str, Any],
    recorder: Any,
) -> Any:
    if spec.system_id == "no_protection":
        return NoProtectionExecutor(tools=tools, recorder=recorder)
    if spec.system_id == "static_allowlist":
        return StaticAllowlistExecutor(tools=tools, recorder=recorder)
    if spec.system_id == "argument_allowlist":
        return ArgumentAllowlistExecutor(policy=policy, tools=tools, recorder=recorder)
    if spec.system_id == "validator_only":
        return ValidatorOnlyExecutor(policy=policy, tools=tools, recorder=recorder)
    if spec.system_id == "no_audit":
        return NoAuditExecutor(policy=policy, tools=tools, recorder=recorder)
    if spec.system_id == "progent_style":
        return ProgentStyleExecutor(policy=policy, tools=tools, recorder=recorder)
    if spec.system_id == "agent_sentinel":
        caps = CapabilitySet(granted_capabilities_from_policy(policy))
        return ToolGateway(
            policy=policy,
            recorder=recorder,
            caps=caps,
            tools=tools,
            enable_validation=True,
        )
    raise ValueError(f"unsupported system id: {spec.system_id}")


def _recorder_for_task(
    *,
    spec: SystemSpec,
    root: Path,
    system_id: str,
    task_name: str,
) -> Any:
    if not spec.use_audit:
        return NoopRecorder()
    ledger_path = root / "runs" / "baseline_suite" / system_id / f"{task_name}.jsonl"
    return FlightRecorder(str(ledger_path), run_id=f"{system_id}_{task_name}")


def run_suite(
    *,
    tasks_dir: str | None = None,
    policy_path: str = DEFAULT_POLICY_PATH,
    output_dir: str = str(DEFAULT_OUTPUT_DIR),
) -> tuple[Path, Path, dict[str, Any]]:
    workload = _select_workload(tasks_dir)
    tasks = _load_tasks(workload.tasks_dir)
    policy = load_policy(str(Path(policy_path).resolve()))
    systems_payload: list[dict[str, Any]] = []
    category_breakdown = dict(
        sorted(Counter(str(task.get("category", "")) for task in tasks).items())
    )

    for spec in SYSTEM_SPECS:
        with tempfile.TemporaryDirectory(prefix=f"agent-sentinel-{spec.system_id}-") as temp_dir:
            work_root = Path(temp_dir)
            with _working_directory(work_root):
                _prepare_fixture_data(Path("."))
                tools = _tool_map()
                results = []
                for task in tasks:
                    task_name = str(task.get("name", "task"))
                    recorder = _recorder_for_task(
                        spec=spec,
                        root=work_root,
                        system_id=spec.system_id,
                        task_name=task_name,
                    )
                    executor = _build_executor(
                        spec=spec,
                        policy=policy,
                        tools=tools,
                        recorder=recorder,
                    )
                    results.append(
                        _execute_task(
                            task=task,
                            executor=executor,
                            mode=spec.system_id,
                            structured_errors=True,
                            traced=spec.use_audit,
                        )
                    )
        summary = _summarize_results(results)
        systems_payload.append(
            {
                "system_id": spec.system_id,
                "label": spec.label,
                "notes": spec.notes,
                **summary,
            }
        )

    payload = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "tasks_dir": str(workload.tasks_dir),
        "workload_selection_mode": workload.selection_mode,
        "workload_selection_reason": workload.selection_reason,
        "exact_75_scenario_workload_found": workload.exact_75_found,
        "workload_scenario_count": workload.scenario_count,
        "policy_path": str(Path(policy_path)),
        "safe_categories": sorted(SAFE_CATEGORIES),
        "unsafe_categories": sorted(SECURITY_DENY_CATEGORIES),
        "robustness_categories": sorted(ROBUSTNESS_CATEGORIES),
        "category_breakdown": category_breakdown,
        "systems": systems_payload,
        "analytical_baselines": [
            {
                "system_id": "container_sandbox",
                "label": "Container / Sandbox",
                "implemented": False,
                "notes": "Analytical systems baseline only; not executed in this benchmark suite.",
            }
        ],
    }

    output_root = Path(output_dir)
    json_path = output_root / "baseline_suite.json"
    csv_path = output_root / "baseline_suite.csv"
    output_root.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "system_id",
                "label",
                "unsafe_actions_blocked_pct",
                "safe_actions_allowed_pct",
                "median_latency_ms",
                "p95_latency_ms",
                "unsafe_total",
                "unsafe_blocked_count",
                "safe_total",
                "safe_allowed_count",
                "robustness_total",
                "robustness_blocked_count",
                "robustness_error_count",
                "robustness_success_count",
                "execution_error_count",
                "scenario_count",
                "notes",
            ],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(systems_payload)

    return json_path, csv_path, payload


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    json_path, csv_path, _ = run_suite(
        tasks_dir=args.tasks_dir,
        policy_path=args.policy,
        output_dir=args.output_dir,
    )
    print(f"Baseline suite JSON: {json_path}")
    print(f"Baseline suite CSV: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
