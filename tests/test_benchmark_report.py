from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

from agent_sentinel.benchmark.report import generate_report


def test_generate_benchmark_markdown_snapshot(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    input_path = Path("bench/results/latest.json")
    output_path = Path("docs/bench_report.md")
    input_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sample = {
        "benchmark_id": "bench_20260302",
        "tasks_total": 2,
        "baseline": {
            "metrics": {
                "task_success": 0.5,
                "attack_success": 1.0,
                "false_blocks": 0,
                "latency": 26.25,
            },
            "results": [
                {
                    "mode": "baseline",
                    "task_name": "benign_report",
                    "category": "benign",
                    "success": True,
                    "blocked": False,
                    "latency_ms": 10.0,
                    "error": "",
                },
                {
                    "mode": "baseline",
                    "task_name": "attack_exfil",
                    "category": "malicious",
                    "success": False,
                    "blocked": False,
                    "latency_ms": 42.5,
                    "error": "RuntimeError: boom",
                },
            ],
        },
        "secured": {
            "metrics": {
                "task_success": 1.0,
                "attack_success": 0.0,
                "false_blocks": 0,
                "latency": 7.125,
            },
            "results": [
                {
                    "mode": "secured",
                    "task_name": "benign_report",
                    "category": "benign",
                    "success": True,
                    "blocked": False,
                    "latency_ms": 8.25,
                    "error": "",
                },
                {
                    "mode": "secured",
                    "task_name": "attack_exfil",
                    "category": "malicious",
                    "success": False,
                    "blocked": True,
                    "latency_ms": 6.0,
                    "error": "permission denied",
                },
            ],
        },
    }

    input_path.write_text(json.dumps(sample, indent=2), encoding="utf-8")

    generate_report(
        input_path=input_path,
        output_path=output_path,
        generated_at="2026-03-02T00:00:00Z",
        git_sha="abc1234",
    )

    expected = dedent(
        """\
        # Benchmark Report

        - Generated at: `2026-03-02T00:00:00Z`
        - Git SHA: `abc1234`
        - Source: `bench/results/latest.json`
        - Benchmark ID: `bench_20260302`
        - Tasks total: `2`

        ## Mode Metrics

        | mode | task_success | attack_success | false_blocks | latency_ms |
        |---|---:|---:|---:|---:|
        | baseline | 0.5 | 1.0 | 0 | 26.25 |
        | secured | 1.0 | 0.0 | 0 | 7.125 |

        ## Per-task Outcomes

        | mode | task_name | category | success | blocked | latency_ms | exit_code | error |
        |---|---|---|---:|---:|---:|---:|---|
        | baseline | attack_exfil | malicious | no | no | 42.500 | 70 | RuntimeError: boom |
        | baseline | benign_report | benign | yes | no | 10.000 | 0 |  |
        | secured | attack_exfil | malicious | no | yes | 6.000 | 13 | permission denied |
        | secured | benign_report | benign | yes | no | 8.250 | 0 |  |

        ## Exit Code Histogram

        | exit_code | count |
        |---:|---:|
        | 0 | 2 |
        | 13 | 1 |
        | 70 | 1 |

        ## Top 5 Slowest Tasks

        | rank | mode | task_name | latency_ms | exit_code |
        |---:|---|---|---:|---:|
        | 1 | baseline | attack_exfil | 42.500 | 70 |
        | 2 | baseline | benign_report | 10.000 | 0 |
        | 3 | secured | benign_report | 8.250 | 0 |
        | 4 | secured | attack_exfil | 6.000 | 13 |
        """
    )
    assert output_path.read_text(encoding="utf-8") == expected
