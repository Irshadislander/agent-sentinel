from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    OK = 0
    USAGE = 2
    CONFIG = 78
    RUNTIME = 70
    DENIED = 13


# Backward-compatible constants (tests + older imports expect these)
OK = int(ExitCode.OK)
USAGE = int(ExitCode.USAGE)
CONFIG = int(ExitCode.CONFIG)
RUNTIME = int(ExitCode.RUNTIME)
DENIED = int(ExitCode.DENIED)

# Legacy aliases retained for compatibility with existing CLI code.
INVALID_POLICY = CONFIG
INTERNAL_ERROR = RUNTIME

__all__ = [
    "ExitCode",
    "OK",
    "USAGE",
    "CONFIG",
    "RUNTIME",
    "DENIED",
    "INVALID_POLICY",
    "INTERNAL_ERROR",
]
