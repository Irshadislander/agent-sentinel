from __future__ import annotations

from typing import Any

from agent_sentinel.runtime.task_spec import TaskSpec

_FIXED_STEPS: tuple[dict[str, Any], ...] = (
    {"tool_name": "read_text", "args": {"path": "public/demo_input.txt"}},
    {
        "tool_name": "write_text",
        "args": {"path": "workspace/demo_output.txt", "text": "demo run complete"},
    },
    {"tool_name": "http_get", "args": {"url": "https://example.com", "timeout_s": 3}},
)


class DemoPlanner:
    def build_task(self, *, policy_path: str | None = None) -> TaskSpec:
        steps = [
            {"tool_name": step["tool_name"], "args": dict(step["args"])} for step in _FIXED_STEPS
        ]
        return TaskSpec(name="demo_v1", steps=steps, policy_path=policy_path)

    def plan(self, task: TaskSpec) -> list[tuple[str, dict[str, Any]]]:
        actions: list[tuple[str, dict[str, Any]]] = []
        for step in task.steps:
            tool_name = step.get("tool_name")
            args = step.get("args", {})
            if not isinstance(tool_name, str):
                raise ValueError("invalid step: missing tool_name")
            if not isinstance(args, dict):
                raise ValueError(f"invalid step args for tool {tool_name}")
            actions.append((tool_name, dict(args)))
        return actions
