from dataclasses import dataclass


@dataclass(slots=True)
class TaskSpec:
    name: str
    steps: list[dict]
    policy_path: str | None = None
