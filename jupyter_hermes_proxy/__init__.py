"""Jupyter server proxy for Hermes Agent dashboard."""

import os
import shutil
from typing import Any, Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_hermes() -> str:
    """Locate the ``hermes`` executable, respecting HERMES_BIN_PATH override."""
    path = os.environ.get("HERMES_BIN_PATH") or shutil.which("hermes")
    if not path:
        raise FileNotFoundError(
            "Cannot find 'hermes' in PATH. "
            "Install Hermes Agent or set HERMES_BIN_PATH to its full path."
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


def _hermes_url() -> Optional[str]:
    """Return the pre-existing dashboard URL if HERMES_DASHBOARD_URL is set."""
    return os.environ.get("HERMES_DASHBOARD_URL")


def setup_hermes() -> Dict[str, Any]:
    """Return a jupyter-server-proxy server spec for the Hermes dashboard.

    When ``HERMES_DASHBOARD_URL`` is set (e.g. ``http://127.0.0.1:9119``),
    the proxy connects to an existing Hermes dashboard instead of spawning
    a new process. This is the recommended mode in Docker/s6 deployments
    where Hermes is already supervised.

    See: https://jupyter-server-proxy.readthedocs.io/
    """
    existing_url = _hermes_url()

    if existing_url:
        return {
            "url": existing_url,
            "timeout": 90,
            "new_browser_tab": True,
            "launcher_entry": {
                "title": "Hermes Dashboard",
                "icon_path": os.path.join(HERE, "icons", "hermes.svg"),
            },
        }

    return {
        "command": _hermes_cmd,
        "timeout": 90,
        "new_browser_tab": True,
        "launcher_entry": {
            "title": "Hermes Dashboard",
            "icon_path": os.path.join(HERE, "icons", "hermes.svg"),
        },
    }
