"""Jupyter server proxy for Hermes Agent dashboard."""

import os
import shutil
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_hermes() -> str:
    """Locate the ``hermes`` executable, respecting HERMES_EXECUTABLE override."""
    executable = os.environ.get("HERMES_EXECUTABLE", "hermes")
    path = shutil.which(executable)
    if not path:
        raise FileNotFoundError(
            f"Cannot find '{executable}' in PATH. "
            "Set HERMES_EXECUTABLE or add Hermes to PATH."
        )
    return path


def _hermes_cmd(port: int, unix_socket: str) -> List[str]:
    """Build the command to launch the Hermes dashboard.

    ``jupyter-server-proxy`` substitutes ``{port}`` with an ephemeral port
    before calling this function, so we use that to tell the dashboard which
    port to listen on.
    """
    hermes_bin = _find_hermes()
    return [
        hermes_bin,
        "dashboard",
        "--port={port}",
        "--host=127.0.0.1",
        "--no-open",
        "--skip-build",
    ]


def setup_hermes() -> Dict[str, Any]:
    """Return a jupyter-server-proxy server spec for the Hermes dashboard.

    See: https://jupyter-server-proxy.readthedocs.io/
    """
    return {
        "command": _hermes_cmd,
        "timeout": 90,
        "new_browser_tab": True,
        "launcher_entry": {
            "title": "Hermes Dashboard",
            "icon_path": os.path.join(HERE, "icons", "hermes.svg"),
        },
    }
