from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class RequestContext:
    request_id: str
    correlation_id: str | None
    source: str


def new_request_id() -> str:
    return uuid4().hex
