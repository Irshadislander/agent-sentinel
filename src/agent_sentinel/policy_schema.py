from __future__ import annotations

from typing import Any

from agent_sentinel.errors import AgentSentinelError


class PolicySchemaError(AgentSentinelError):
    exit_code = 3  # same category as parse error (config issue)

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message,
            code="policy_schema_error",
            details=details,
            hint="Ensure the policy matches the required schema.",
        )


_ALLOWED_TOP_LEVEL_KEYS = {"version", "default", "allow"}
_ALLOWED_DEFAULT_VALUES = {"deny", "allow"}


def validate_policy_schema(policy: dict[str, Any]) -> None:
    if not isinstance(policy, dict):
        raise PolicySchemaError("Policy must be a JSON object.")

    unknown = set(policy.keys()) - _ALLOWED_TOP_LEVEL_KEYS
    if unknown:
        raise PolicySchemaError(
            f"Unknown top-level keys: {sorted(unknown)}",
            details={"unknown_keys": sorted(unknown)},
        )

    if "version" not in policy:
        raise PolicySchemaError("Missing required field: version")
    if not isinstance(policy["version"], int):
        raise PolicySchemaError("Field 'version' must be an integer")

    if "default" not in policy:
        raise PolicySchemaError("Missing required field: default")
    if policy["default"] not in _ALLOWED_DEFAULT_VALUES:
        raise PolicySchemaError(
            "Field 'default' must be 'deny' or 'allow'",
            details={"value": policy["default"]},
        )

    if "allow" not in policy:
        raise PolicySchemaError("Missing required field: allow")
    if not isinstance(policy["allow"], list):
        raise PolicySchemaError("Field 'allow' must be a list")
    for index, item in enumerate(policy["allow"]):
        if not isinstance(item, str):
            raise PolicySchemaError(
                "All items in 'allow' must be strings",
                details={"index": index, "value": item},
            )
