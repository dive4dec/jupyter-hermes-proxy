"""Tests for jupyter-hermes-proxy hermes executable lookup and proxy modes."""

import os
import sys
from unittest.mock import patch

import pytest


class TestFindHermes:
    """Test _find_hermes() resolves the hermes binary correctly."""

    def test_env_var_overrides_path(self, monkeypatch):
        """HERMES_BIN_PATH takes precedence over PATH lookup."""
        import jupyter_hermes_proxy

        path_bin = "/usr/local/bin/hermes"
        env_bin = "/opt/data/mamba/envs/main/bin/hermes"

        monkeypatch.setenv("HERMES_BIN_PATH", env_bin)
        with patch("shutil.which", return_value=path_bin):
            result = jupyter_hermes_proxy._find_hermes()

        assert result == env_bin
        assert result != path_bin

    def test_falls_back_to_shutil_which(self, monkeypatch):
        """shutil.which is used when HERMES_BIN_PATH is not set."""
        import jupyter_hermes_proxy

        path_bin = "/usr/local/bin/hermes"

        monkeypatch.delenv("HERMES_BIN_PATH", raising=False)
        with patch("shutil.which", return_value=path_bin):
            result = jupyter_hermes_proxy._find_hermes()

        assert result == path_bin

    def test_raises_file_not_found_when_missing(self, monkeypatch):
        """FileNotFoundError is raised when neither env var nor PATH works."""
        import jupyter_hermes_proxy

        monkeypatch.delenv("HERMES_BIN_PATH", raising=False)
        with patch("shutil.which", return_value=None):
            with pytest.raises(FileNotFoundError, match="hermes"):
                jupyter_hermes_proxy._find_hermes()

    def test_env_var_used_even_when_path_exists(self, monkeypatch):
        """HERMES_BIN_PATH must override a binary found in PATH."""
        import jupyter_hermes_proxy

        path_bin = "/usr/local/bin/hermes"
        env_bin = "/opt/custom/bin/hermes"

        monkeypatch.setenv("HERMES_BIN_PATH", env_bin)
        with patch("shutil.which", return_value=path_bin):
            result = jupyter_hermes_proxy._find_hermes()

        assert result == env_bin
        assert result != path_bin


class TestHermesCmd:
    """Test _hermes_cmd() builds the correct command list."""

    def test_basic_command(self, monkeypatch):
        """Command includes dashboard flags."""
        import jupyter_hermes_proxy

        monkeypatch.setattr(jupyter_hermes_proxy, "shutil", __import__("shutil"))
        with patch("shutil.which", return_value="/usr/bin/hermes"):
            cmd = jupyter_hermes_proxy._hermes_cmd(8765, "")

        assert cmd[0] == "/usr/bin/hermes"
        assert "dashboard" in cmd
        assert "--port={port}" in cmd
        assert "--host=127.0.0.1" in cmd
        assert "--no-open" in cmd
        assert "--skip-build" in cmd


class TestSetupHermes:
    """Test setup_hermes() returns a valid server spec in both modes."""

    def _get_module(self):
        import jupyter_hermes_proxy
        return jupyter_hermes_proxy

    # -- Spawn mode (no HERMES_DASHBOARD_URL) --

    def test_spawn_mode_has_command(self, monkeypatch):
        """Spawn mode contains 'command', not 'url'."""
        monkeypatch.delenv("HERMES_DASHBOARD_URL", raising=False)
        with patch("shutil.which", return_value="/usr/bin/hermes"):
            spec = self._get_module().setup_hermes()

        assert "command" in spec
        assert "url" not in spec

    def test_spawn_mode_has_timeout_and_launcher(self, monkeypatch):
        """Spawn spec contains all required keys."""
        monkeypatch.delenv("HERMES_DASHBOARD_URL", raising=False)
        with patch("shutil.which", return_value="/usr/bin/hermes"):
            spec = self._get_module().setup_hermes()

        assert spec["timeout"] == 90
        assert spec["launcher_entry"]["title"] == "Hermes Dashboard"
        assert "hermes.svg" in spec["launcher_entry"]["icon_path"]

    # -- URL mode (HERMES_DASHBOARD_URL set) --

    def test_url_mode_has_url_not_command(self, monkeypatch):
        """URL mode contains 'url', not 'command'."""
        monkeypatch.setenv("HERMES_DASHBOARD_URL", "http://127.0.0.1:9119")
        spec = self._get_module().setup_hermes()

        assert "url" in spec
        assert "command" not in spec

    def test_url_mode_preserves_url_value(self, monkeypatch):
        """URL mode propagates the env var value directly."""
        monkeypatch.setenv("HERMES_DASHBOARD_URL", "http://127.0.0.1:9119")
        spec = self._get_module().setup_hermes()

        assert spec["url"] == "http://127.0.0.1:9119"

    def test_url_mode_has_timeout_and_launcher(self, monkeypatch):
        """URL spec also contains timeout and launcher entry."""
        monkeypatch.setenv("HERMES_DASHBOARD_URL", "http://127.0.0.1:9119")
        spec = self._get_module().setup_hermes()

        assert spec["timeout"] == 90
        assert spec["launcher_entry"]["title"] == "Hermes Dashboard"
        assert "hermes.svg" in spec["launcher_entry"]["icon_path"]

    def test_url_mode_ignores_hermes_bin(self, monkeypatch):
        """URL mode does not need hermes binary on PATH."""
        monkeypatch.setenv("HERMES_DASHBOARD_URL", "http://127.0.0.1:9119")
        # No shutil.which mock — should not be called
        spec = self._get_module().setup_hermes()
        assert spec["url"] == "http://127.0.0.1:9119"
