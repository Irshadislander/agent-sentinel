from __future__ import annotations

from typing import Any

from agent_sentinel.cli_exit_codes import ExitCode

from . import register_capability
from .base import Capability, Result


@register_capability(
    id="core.example.echo",
    name="example.echo",
    namespace="agent_sentinel.core",
    version="1.0.0",
    description="Built-in example capability for smoke tests and benchmark harness.",
    tags=["core", "example", "benchmark"],
    schema={
        "type": "object",
        "properties": {
            "message": {"type": "string"},
        },
    },
)
class ExampleEchoCapability(Capability):
    name = "example.echo"

    def execute(self, payload: dict[str, Any]) -> Result:
        message = payload.get("message", "")
        if not isinstance(message, str):
            return Result(
                ok=False,
                code=ExitCode.USAGE,
                error="message must be a string",
                metadata={"field": "message"},
            )
        return Result(
            ok=True,
            code=ExitCode.OK,
            data={"echo": message, "payload_size": len(payload)},
        )
