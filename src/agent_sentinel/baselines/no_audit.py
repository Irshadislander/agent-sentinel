from __future__ import annotations

from typing import Any

from agent_sentinel.security.capabilities import CapabilitySet
from agent_sentinel.security.tool_gateway import ToolGateway

from . import NoopRecorder, ToolFn, granted_capabilities_from_policy


class NoAuditExecutor:
    def __init__(
        self,
        *,
        policy: dict[str, Any],
        tools: dict[str, ToolFn],
        recorder: Any,
    ) -> None:
        del recorder
        caps = CapabilitySet(granted_capabilities_from_policy(policy))
        self._gateway = ToolGateway(
            policy=policy,
            recorder=NoopRecorder(),
            caps=caps,
            tools=tools,
            enable_validation=True,
        )

    def execute(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        return self._gateway.execute(tool_name, args)
