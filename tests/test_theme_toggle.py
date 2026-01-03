"""Tests for Windows Theme Toggle MCP Server."""

import pytest
from unittest.mock import patch, MagicMock
import winreg

from src.theme_toggle_server import (
    get_current_theme,
    set_theme,
    get_theme,
    set_dark_theme,
    set_light_theme,
    toggle_theme,
)


class TestThemeOperations:
    """Test suite for theme operations."""

    @patch("src.theme_toggle_server.winreg.OpenKey")
    @patch("src.theme_toggle_server.winreg.QueryValueEx")
    @patch("src.theme_toggle_server.winreg.CloseKey")
    def test_get_current_theme_dark(self, mock_close, mock_query, mock_open):
        """Test getting current theme when dark mode is active."""
        mock_key = MagicMock()
        mock_open.return_value = mock_key
        mock_query.return_value = (0, winreg.REG_DWORD)  # 0 = dark mode
        
        result = get_current_theme()
        
        assert result == "dark"
        mock_open.assert_called_once()
        mock_query.assert_called_once_with(mock_key, "AppsUseLightTheme")
        mock_close.assert_called_once_with(mock_key)

    @patch("src.theme_toggle_server.winreg.OpenKey")
    @patch("src.theme_toggle_server.winreg.QueryValueEx")
    @patch("src.theme_toggle_server.winreg.CloseKey")
    def test_get_current_theme_light(self, mock_close, mock_query, mock_open):
        """Test getting current theme when light mode is active."""
        mock_key = MagicMock()
        mock_open.return_value = mock_key
        mock_query.return_value = (1, winreg.REG_DWORD)  # 1 = light mode
        
        result = get_current_theme()
        
        assert result == "light"

    @patch("src.theme_toggle_server.winreg.OpenKey")
    @patch("src.theme_toggle_server.winreg.QueryValueEx")
    def test_get_current_theme_error(self, mock_query, mock_open):
        """Test error handling when reading theme fails."""
        mock_open.side_effect = OSError("Registry access denied")
        
        with pytest.raises(RuntimeError, match="Failed to read theme setting"):
            get_current_theme()

    @patch("src.theme_toggle_server.winreg.OpenKey")
    @patch("src.theme_toggle_server.winreg.SetValueEx")
    @patch("src.theme_toggle_server.winreg.CloseKey")
    def test_set_theme_dark(self, mock_close, mock_set, mock_open):
        """Test setting theme to dark mode."""
        mock_key = MagicMock()
        mock_open.return_value = mock_key
        
        set_theme("dark")
        
        assert mock_set.call_count == 2
        mock_set.assert_any_call(mock_key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 0)
        mock_set.assert_any_call(mock_key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 0)
        mock_close.assert_called_once_with(mock_key)

    @patch("src.theme_toggle_server.winreg.OpenKey")
    @patch("src.theme_toggle_server.winreg.SetValueEx")
    @patch("src.theme_toggle_server.winreg.CloseKey")
    def test_set_theme_light(self, mock_close, mock_set, mock_open):
        """Test setting theme to light mode."""
        mock_key = MagicMock()
        mock_open.return_value = mock_key
        
        set_theme("light")
        
        assert mock_set.call_count == 2
        mock_set.assert_any_call(mock_key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 1)
        mock_set.assert_any_call(mock_key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 1)

    @patch("src.theme_toggle_server.winreg.OpenKey")
    def test_set_theme_error(self, mock_open):
        """Test error handling when setting theme fails."""
        mock_open.side_effect = OSError("Registry access denied")
        
        with pytest.raises(RuntimeError, match="Failed to set theme"):
            set_theme("dark")


class TestMCPTools:
    """Test suite for MCP tool functions."""

    @patch("src.theme_toggle_server.get_current_theme")
    def test_get_theme_tool(self, mock_get_current):
        """Test the get_theme MCP tool."""
        mock_get_current.return_value = "dark"
        
        result = get_theme()
        
        assert result == "Current Windows theme is: dark"
        mock_get_current.assert_called_once()

    @patch("src.theme_toggle_server.set_theme")
    def test_set_dark_theme_tool(self, mock_set):
        """Test the set_dark_theme MCP tool."""
        result = set_dark_theme()
        
        assert result == "Windows theme set to dark mode"
        mock_set.assert_called_once_with("dark")

    @patch("src.theme_toggle_server.set_theme")
    def test_set_light_theme_tool(self, mock_set):
        """Test the set_light_theme MCP tool."""
        result = set_light_theme()
        
        assert result == "Windows theme set to light mode"
        mock_set.assert_called_once_with("light")

    @patch("src.theme_toggle_server.get_current_theme")
    @patch("src.theme_toggle_server.set_theme")
    def test_toggle_theme_dark_to_light(self, mock_set, mock_get_current):
        """Test toggling theme from dark to light."""
        mock_get_current.return_value = "dark"
        
        result = toggle_theme()
        
        assert result == "Windows theme toggled from dark to light"
        mock_get_current.assert_called_once()
        mock_set.assert_called_once_with("light")

    @patch("src.theme_toggle_server.get_current_theme")
    @patch("src.theme_toggle_server.set_theme")
    def test_toggle_theme_light_to_dark(self, mock_set, mock_get_current):
        """Test toggling theme from light to dark."""
        mock_get_current.return_value = "light"
        
        result = toggle_theme()
        
        assert result == "Windows theme toggled from light to dark"
        mock_set.assert_called_once_with("dark")
