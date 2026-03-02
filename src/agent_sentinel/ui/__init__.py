"""
UI package entrypoints.

We export `main` so the console script `agent-sentinel-ui`
(can point to `agent_sentinel.ui:main`) works reliably.
"""

from .app import main  # noqa: F401
