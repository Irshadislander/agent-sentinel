from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    # Run streamlit against our app.py
    # Equivalent to: streamlit run src/agent_sentinel/ui/app.py
    try:
        import streamlit.web.cli as stcli
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "Streamlit is not installed. Install UI deps: pip install -e '.[ui]'"
        ) from exc

    app_path = Path(__file__).with_name("app.py")
    sys.argv = ["streamlit", "run", str(app_path)]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
