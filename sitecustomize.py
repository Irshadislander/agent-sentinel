"""
Dev-only import helper.

Some environments (notably with newer Python/pip editable installs) may fail to
auto-apply the __editable__.pth path injection consistently.

When running from the repo root, Python always has '' (cwd) on sys.path, so
placing this file here guarantees the src/ layout is discoverable without
requiring manual PYTHONPATH exports.

This does NOT affect normal installed usage (wheel installs). It only helps when
running directly from the repository checkout.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    repo_root = Path(__file__).resolve().parent
    src = repo_root / "src"
    pkg = src / "agent_sentinel"

    if pkg.exists() and src.is_dir():
        src_str = str(src)
        if src_str not in sys.path:
            sys.path.insert(0, src_str)


_ensure_src_on_path()
