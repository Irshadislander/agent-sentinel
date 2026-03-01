from __future__ import annotations

from typing import Any, Iterable

from agent_sentinel.security.tool_gateway import ToolGateway


class AgentRunner:
    def __init__(self, gateway: ToolGateway):
        self._gateway = gateway

    def run(self, scripted_actions: Iterable[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
        outcomes: list[dict[str, Any]] = []
        success_count = 0
        failure_count = 0

        for index, action in enumerate(scripted_actions):
            tool_name, args = action
            try:
                result = self._gateway.execute(tool_name, args)
                outcomes.append(
                    {
                        "index": index,
                        "tool_name": tool_name,
                        "ok": True,
                        "result": result,
                    }
                )
                success_count += 1
            except Exception as exc:
                outcomes.append(
                    {
                        "index": index,
                        "tool_name": tool_name,
                        "ok": False,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
                failure_count += 1

        return {
            "total_actions": success_count + failure_count,
            "success_count": success_count,
            "failure_count": failure_count,
            "actions": outcomes,
        }
