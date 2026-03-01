#!/usr/bin/env bash
set -euo pipefail

VENV="${VENV_PATH:-.venv}"

if [[ ! -d "$VENV" ]]; then
  echo "venv not found at $VENV"
  echo "Run: python -m venv .venv"
  exit 1
fi

PYTHON_BIN="$VENV/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "python executable not found at $PYTHON_BIN"
  echo "Activate the venv or set VENV_PATH correctly."
  exit 1
fi

SP_DIR=$("$PYTHON_BIN" - <<'PY'
import site
print(site.getsitepackages()[0])
PY
)

echo "Fixing macOS hidden flags under: $SP_DIR"
chflags -R nohidden "$SP_DIR" || true

echo "Done."
echo "Now try: python -c \"import agent_sentinel\""
