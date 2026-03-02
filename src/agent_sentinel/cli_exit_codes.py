from __future__ import annotations

from agent_sentinel.exit_codes import (
    GENERIC_ERROR,
    POLICY_PARSE_ERROR,
    POLICY_VIOLATION,
)

# Backward-compatible aliases used by existing callers/tests.
DENIED = POLICY_VIOLATION
INVALID_POLICY = POLICY_PARSE_ERROR
INTERNAL_ERROR = GENERIC_ERROR
