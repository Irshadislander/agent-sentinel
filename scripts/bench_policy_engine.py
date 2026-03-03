from __future__ import annotations

import argparse
from pathlib import Path

from agent_sentinel.benchmark.policy_engine_perf import (
    DEFAULT_JSON_OUTPUT,
    DEFAULT_MARKDOWN_OUTPUT,
    run_policy_engine_benchmark,
    write_policy_engine_benchmark_outputs,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Microbenchmark policy-engine decision resolution."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5000,
        help="Number of measured iterations per case (default: 5000).",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=200,
        help="Number of warmup iterations per case (default: 200).",
    )
    parser.add_argument(
        "--json-output",
        default=str(DEFAULT_JSON_OUTPUT),
        help=f"JSON output path (default: {DEFAULT_JSON_OUTPUT}).",
    )
    parser.add_argument(
        "--markdown-output",
        default=str(DEFAULT_MARKDOWN_OUTPUT),
        help=f"Markdown output path (default: {DEFAULT_MARKDOWN_OUTPUT}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    payload = run_policy_engine_benchmark(iterations=args.iterations, warmup=args.warmup)
    json_path, markdown_path = write_policy_engine_benchmark_outputs(
        payload,
        json_path=Path(args.json_output),
        markdown_path=Path(args.markdown_output),
    )
    print(f"Wrote policy engine benchmark JSON: {json_path}")
    print(f"Wrote policy engine benchmark markdown: {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
