from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


def _import_bench() -> tuple[Any, Any, Any, Any]:
    """Import benchmark helpers with repo-local src on sys.path."""
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from agent_sentinel.benchmark.policy_engine_perf import (
        DEFAULT_JSON_OUTPUT,
        DEFAULT_MARKDOWN_OUTPUT,
        run_policy_engine_benchmark,
        write_policy_engine_benchmark_outputs,
    )

    return (
        DEFAULT_JSON_OUTPUT,
        DEFAULT_MARKDOWN_OUTPUT,
        run_policy_engine_benchmark,
        write_policy_engine_benchmark_outputs,
    )


def _build_parser(
    *, default_json_output: Any, default_markdown_output: Any
) -> argparse.ArgumentParser:
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
        default=str(default_json_output),
        help=f"JSON output path (default: {default_json_output}).",
    )
    parser.add_argument(
        "--markdown-output",
        default=str(default_markdown_output),
        help=f"Markdown output path (default: {default_markdown_output}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    (
        default_json_output,
        default_markdown_output,
        run_policy_engine_benchmark,
        write_policy_engine_benchmark_outputs,
    ) = _import_bench()

    parser = _build_parser(
        default_json_output=default_json_output,
        default_markdown_output=default_markdown_output,
    )
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
