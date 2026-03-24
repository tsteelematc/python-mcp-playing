"""Tests for Theme Toggle MCP Server (Windows and macOS)."""

import sys

# winreg is only available on Windows; conftest.py injects a mock on other
# platforms so this import works regardless of the host OS.
try:
    import winreg
except ImportError:
    import sys as _sys
    winreg = _sys.modules["winreg"]  # type: ignore[assignment]
from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch

import pytest

from src.theme_toggle_server import (
    _macos_get_current_theme,
    _macos_set_theme,
    _windows_get_current_theme,
    _windows_set_theme,
    get_current_theme,
    get_theme,
    set_dark_theme,
    set_light_theme,
    set_theme,
    toggle_theme,
)


# ── macOS helpers ──────────────────────────────────────────────────────────────


class TestMacosGetCurrentTheme:
    """Tests for _macos_get_current_theme."""

    @patch("src.theme_toggle_server.subprocess.run")
    def test_dark_mode(self, mock_run):
        """Returns 'dark' when AppleInterfaceStyle is 'Dark'."""
        mock_run.return_value = CompletedProcess(args=[], returncode=0, stdout="Dark\n")

        assert _macos_get_current_theme() == "dark"

        mock_run.assert_called_once_with(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True,
            text=True,
        )

    @patch("src.theme_toggle_server.subprocess.run")
    def test_light_mode_key_absent(self, mock_run):
        """Returns 'light' when the key is absent (exit code 1, light mode default)."""
        mock_run.return_value = CompletedProcess(
            args=[], returncode=1, stdout="", stderr="Does Not Exist\n"
        )

        assert _macos_get_current_theme() == "light"

    @patch("src.theme_toggle_server.subprocess.run")
    def test_light_mode_unexpected_value(self, mock_run):
        """Returns 'light' for any value other than 'Dark'."""
        mock_run.return_value = CompletedProcess(
            args=[], returncode=0, stdout="Light\n"
        )

        assert _macos_get_current_theme() == "light"

    @patch("src.theme_toggle_server.subprocess.run")
    def test_oserror_raises_runtime_error(self, mock_run):
        """Raises RuntimeError when subprocess.run raises OSError."""
        mock_run.side_effect = OSError("defaults not found")

        with pytest.raises(RuntimeError, match="Failed to read macOS theme setting"):
            _macos_get_current_theme()


class TestMacosSetTheme:
    """Tests for _macos_set_theme."""

    @patch("src.theme_toggle_server.subprocess.run")
    def test_set_dark(self, mock_run):
        """Calls osascript with dark mode true."""
        mock_run.return_value = CompletedProcess(args=[], returncode=0, stdout="")

        _macos_set_theme("dark")

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "osascript"
        assert "true" in call_args[2]

    @patch("src.theme_toggle_server.subprocess.run")
    def test_set_light(self, mock_run):
        """Calls osascript with dark mode false."""
        mock_run.return_value = CompletedProcess(args=[], returncode=0, stdout="")

        _macos_set_theme("light")

        call_args = mock_run.call_args[0][0]
        assert "false" in call_args[2]

    @patch("src.theme_toggle_server.subprocess.run")
    def test_nonzero_exit_raises_runtime_error(self, mock_run):
        """Raises RuntimeError when osascript returns a non-zero exit code."""
        mock_run.return_value = CompletedProcess(
            args=[], returncode=1, stdout="", stderr="Not authorized\n"
        )

        with pytest.raises(RuntimeError, match="Failed to set macOS theme"):
            _macos_set_theme("dark")

    @patch("src.theme_toggle_server.subprocess.run")
    def test_oserror_raises_runtime_error(self, mock_run):
        """Raises RuntimeError when subprocess.run raises OSError."""
        mock_run.side_effect = OSError("osascript not found")

        with pytest.raises(RuntimeError, match="Failed to set macOS theme"):
            _macos_set_theme("light")


# ── Windows helpers ────────────────────────────────────────────────────────────


class TestWindowsGetCurrentTheme:
    """Tests for _windows_get_current_theme."""

    @patch("src.theme_toggle_server.winreg.OpenKey")
    @patch("src.theme_toggle_server.winreg.QueryValueEx")
    @patch("src.theme_toggle_server.winreg.CloseKey")
    def test_dark_mode(self, mock_close, mock_query, mock_open):
        """Returns 'dark' when AppsUseLightTheme is 0."""
        mock_key = MagicMock()
        mock_open.return_value = mock_key
        mock_query.return_value = (0, winreg.REG_DWORD)

        assert _windows_get_current_theme() == "dark"

        mock_open.assert_called_once()
        mock_query.assert_called_once_with(mock_key, "AppsUseLightTheme")
        mock_close.assert_called_once_with(mock_key)

    @patch("src.theme_toggle_server.winreg.OpenKey")
    @patch("src.theme_toggle_server.winreg.QueryValueEx")
    @patch("src.theme_toggle_server.winreg.CloseKey")
    def test_light_mode(self, mock_close, mock_query, mock_open):
        """Returns 'light' when AppsUseLightTheme is 1."""
        mock_key = MagicMock()
        mock_open.return_value = mock_key
        mock_query.return_value = (1, winreg.REG_DWORD)

        assert _windows_get_current_theme() == "light"

    @patch("src.theme_toggle_server.winreg.OpenKey")
    @patch("src.theme_toggle_server.winreg.QueryValueEx")
    def test_oserror_raises_runtime_error(self, mock_query, mock_open):
        """Raises RuntimeError when the registry key cannot be opened."""
        mock_open.side_effect = OSError("Registry access denied")

        with pytest.raises(RuntimeError, match="Failed to read theme setting"):
            _windows_get_current_theme()


class TestWindowsSetTheme:
    """Tests for _windows_set_theme."""

    @patch("src.theme_toggle_server.ctypes.windll")
    @patch("src.theme_toggle_server.winreg.OpenKey")
    @patch("src.theme_toggle_server.winreg.SetValueEx")
    @patch("src.theme_toggle_server.winreg.CloseKey")
    def test_set_dark(self, mock_close, mock_set, mock_open, mock_windll):
        """Writes value 0 to both registry keys for dark mode."""
        mock_key = MagicMock()
        mock_open.return_value = mock_key

        _windows_set_theme("dark")

        assert mock_set.call_count == 2
        mock_set.assert_any_call(mock_key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 0)
        mock_set.assert_any_call(
            mock_key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 0
        )
        mock_close.assert_called_once_with(mock_key)

    @patch("src.theme_toggle_server.ctypes.windll")
    @patch("src.theme_toggle_server.winreg.OpenKey")
    @patch("src.theme_toggle_server.winreg.SetValueEx")
    @patch("src.theme_toggle_server.winreg.CloseKey")
    def test_set_light(self, mock_close, mock_set, mock_open, mock_windll):
        """Writes value 1 to both registry keys for light mode."""
        mock_key = MagicMock()
        mock_open.return_value = mock_key

        _windows_set_theme("light")

        assert mock_set.call_count == 2
        mock_set.assert_any_call(mock_key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 1)
        mock_set.assert_any_call(
            mock_key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 1
        )

    @patch("src.theme_toggle_server.winreg.OpenKey")
    def test_oserror_raises_runtime_error(self, mock_open):
        """Raises RuntimeError when the registry key cannot be opened."""
        mock_open.side_effect = OSError("Registry access denied")

        with pytest.raises(RuntimeError, match="Failed to set theme"):
            _windows_set_theme("dark")


# ── Platform dispatch ──────────────────────────────────────────────────────────


class TestGetCurrentThemeDispatch:
    """Tests that get_current_theme dispatches to the correct OS handler."""

    @patch("src.theme_toggle_server._macos_get_current_theme", return_value="dark")
    def test_dispatches_to_macos(self, mock_macos):
        with patch.object(sys, "platform", "darwin"):
            result = get_current_theme()
        assert result == "dark"
        mock_macos.assert_called_once()

    @patch("src.theme_toggle_server._windows_get_current_theme", return_value="light")
    def test_dispatches_to_windows(self, mock_windows):
        with patch.object(sys, "platform", "win32"):
            result = get_current_theme()
        assert result == "light"
        mock_windows.assert_called_once()

    def test_unsupported_platform_raises(self):
        with patch.object(sys, "platform", "linux"):
            with pytest.raises(RuntimeError, match="Unsupported platform"):
                get_current_theme()


class TestSetThemeDispatch:
    """Tests that set_theme dispatches to the correct OS handler."""

    @patch("src.theme_toggle_server._macos_set_theme")
    def test_dispatches_to_macos(self, mock_macos):
        with patch.object(sys, "platform", "darwin"):
            set_theme("dark")
        mock_macos.assert_called_once_with("dark")

    @patch("src.theme_toggle_server._windows_set_theme")
    def test_dispatches_to_windows(self, mock_windows):
        with patch.object(sys, "platform", "win32"):
            set_theme("light")
        mock_windows.assert_called_once_with("light")

    def test_unsupported_platform_raises(self):
        with patch.object(sys, "platform", "linux"):
            with pytest.raises(RuntimeError, match="Unsupported platform"):
                set_theme("dark")


# ── MCP tools ─────────────────────────────────────────────────────────────────


class TestMCPTools:
    """Tests for the MCP tool functions."""

    @patch("src.theme_toggle_server.get_current_theme")
    def test_get_theme_tool(self, mock_get_current):
        mock_get_current.return_value = "dark"

        assert get_theme() == "Current theme is: dark"
        mock_get_current.assert_called_once()

    @patch("src.theme_toggle_server.get_current_theme")
    def test_get_theme_tool_light(self, mock_get_current):
        mock_get_current.return_value = "light"

        assert get_theme() == "Current theme is: light"

    @patch("src.theme_toggle_server.set_theme")
    def test_set_dark_theme_tool(self, mock_set):
        assert set_dark_theme() == "Theme set to dark mode"
        mock_set.assert_called_once_with("dark")

    @patch("src.theme_toggle_server.set_theme")
    def test_set_light_theme_tool(self, mock_set):
        assert set_light_theme() == "Theme set to light mode"
        mock_set.assert_called_once_with("light")

    @patch("src.theme_toggle_server.get_current_theme")
    @patch("src.theme_toggle_server.set_theme")
    def test_toggle_dark_to_light(self, mock_set, mock_get_current):
        mock_get_current.return_value = "dark"

        assert toggle_theme() == "Theme toggled from dark to light"
        mock_set.assert_called_once_with("light")

    @patch("src.theme_toggle_server.get_current_theme")
    @patch("src.theme_toggle_server.set_theme")
    def test_toggle_light_to_dark(self, mock_set, mock_get_current):
        mock_get_current.return_value = "light"

        assert toggle_theme() == "Theme toggled from light to dark"
        mock_set.assert_called_once_with("dark")
