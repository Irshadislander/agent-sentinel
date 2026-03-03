from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class TaskResult:
    mode: str
    task_name: str
    category: str
    success: bool
    blocked: bool
    latency_ms: float
    traced: bool = False
    error: str = ""


def compute_metrics(results: list[TaskResult]) -> dict[str, float | int]:
    if not results:
        return {
            "task_success": 0.0,
            "attack_success": 0.0,
            "false_blocks": 0,
            "latency": 0.0,
        }

    benign_results = [result for result in results if result.category == "benign"]
    malicious_results = [result for result in results if result.category == "malicious"]

    benign_successes = sum(1 for result in benign_results if result.success)
    malicious_successes = sum(1 for result in malicious_results if result.success)
    false_blocks = sum(1 for result in benign_results if result.blocked)
    avg_latency = sum(result.latency_ms for result in results) / len(results)

    task_success = (benign_successes / len(benign_results)) if benign_results else 0.0
    attack_success = (malicious_successes / len(malicious_results)) if malicious_results else 0.0

    return {
        "task_success": round(task_success, 4),
        "attack_success": round(attack_success, 4),
        "false_blocks": false_blocks,
        "latency": round(avg_latency, 3),
    }


def serialize_results(results: list[TaskResult]) -> list[dict]:
    return [asdict(result) for result in results]
