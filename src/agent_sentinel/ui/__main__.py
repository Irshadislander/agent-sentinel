from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    try:
        from streamlit.web import cli as stcli
    except Exception as exc:
        print(f"Streamlit is required to run the UI: {exc}", file=sys.stderr)
        return 1

    app_path = Path(__file__).with_name("app.py")
    sys.argv = ["streamlit", "run", str(app_path), *sys.argv[1:]]
    stcli.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
