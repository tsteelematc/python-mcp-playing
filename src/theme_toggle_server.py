"""Theme Toggle MCP Server.

Cross-platform MCP server that provides tools to toggle system theme between
light and dark modes. Supports Windows (via Registry) and macOS (via osascript).
OS detection is performed at runtime so the same server file works on both platforms.
"""

import ctypes
import subprocess
import sys
from typing import Literal

from mcp.server.fastmcp import FastMCP

try:
    import winreg
except ImportError:
    winreg = None  # type: ignore[assignment]

# Initialize the MCP server
mcp = FastMCP(
    name="Theme Toggle",
    instructions="Provides tools to toggle system theme between light and dark modes",
)


# ── macOS ──────────────────────────────────────────────────────────────────────


def _macos_get_current_theme() -> Literal["dark", "light"]:
    """Get the current macOS theme by reading the global domain preference.

    Returns:
        "dark" if dark mode is enabled, "light" otherwise.
    """
    try:
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True,
            text=True,
        )
        # The key is absent (exit code 1) when light mode is active;
        # it contains "Dark" when dark mode is on.
        if result.returncode == 0 and result.stdout.strip().lower() == "dark":
            return "dark"
        return "light"
    except OSError as e:
        raise RuntimeError(f"Failed to read macOS theme setting: {e}") from e


def _macos_set_theme(theme: Literal["dark", "light"]) -> None:
    """Set the macOS appearance using an AppleScript command.

    Args:
        theme: The theme to set ("dark" or "light").

    Raises:
        RuntimeError: If the osascript command fails.
    """
    dark_mode = "true" if theme == "dark" else "false"
    script = (
        "tell app \"System Events\" to tell appearance preferences "
        f"to set dark mode to {dark_mode}"
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to set macOS theme: {result.stderr.strip()}"
            )
    except OSError as e:
        raise RuntimeError(f"Failed to set macOS theme: {e}") from e


# ── Windows ────────────────────────────────────────────────────────────────────


def _windows_get_current_theme() -> Literal["dark", "light"]:
    """Get the current Windows theme by reading the registry.

    Returns:
        "dark" if dark mode is enabled, "light" otherwise.
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            0,
            winreg.KEY_READ,
        )
        try:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            # Value of 0 means dark mode, 1 means light mode
            return "light" if value == 1 else "dark"
        finally:
            winreg.CloseKey(key)
    except OSError as e:
        raise RuntimeError(f"Failed to read theme setting: {e}")


def _windows_set_theme(theme: Literal["dark", "light"]) -> None:
    """Set the Windows theme by writing to the registry.

    Args:
        theme: The theme to set ("dark" or "light").

    Raises:
        RuntimeError: If the registry cannot be modified.
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            0,
            winreg.KEY_SET_VALUE,
        )
        try:
            # 0 for dark mode, 1 for light mode
            value: int = 1 if theme == "light" else 0

            # App theme
            winreg.SetValueEx(
                key,
                "AppsUseLightTheme",
                0,
                winreg.REG_DWORD,
                value,
            )
            # System (taskbar, Start, etc.) theme
            winreg.SetValueEx(
                key,
                "SystemUsesLightTheme",
                0,
                winreg.REG_DWORD,
                value,
            )
        finally:
            winreg.CloseKey(key)

        # Notify the system that the immersive color set changed
        HWND_BROADCAST: int = 0xFFFF
        WM_SETTINGCHANGE: int = 0x1A
        SMTO_ABORTIFHUNG: int = 0x0002

        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "ImmersiveColorSet",
            SMTO_ABORTIFHUNG,
            5000,
            None,
        )
    except OSError as e:
        raise RuntimeError(f"Failed to set theme: {e}") from e


# ── Platform dispatch ──────────────────────────────────────────────────────────


def get_current_theme() -> Literal["dark", "light"]:
    """Get the current system theme setting.

    Returns:
        "dark" if dark mode is enabled, "light" otherwise.

    Raises:
        RuntimeError: If the theme cannot be read or the platform is unsupported.
    """
    if sys.platform == "darwin":
        return _macos_get_current_theme()
    if sys.platform == "win32":
        return _windows_get_current_theme()
    raise RuntimeError(f"Unsupported platform: {sys.platform}")


def set_theme(theme: Literal["dark", "light"]) -> None:
    """Set the system theme.

    Args:
        theme: The theme to set ("dark" or "light").

    Raises:
        RuntimeError: If the theme cannot be set or the platform is unsupported.
    """
    if sys.platform == "darwin":
        _macos_set_theme(theme)
        return
    if sys.platform == "win32":
        _windows_set_theme(theme)
        return
    raise RuntimeError(f"Unsupported platform: {sys.platform}")


# ── MCP tools ─────────────────────────────────────────────────────────────────


@mcp.tool()
def get_theme() -> str:
    """Get the current system theme setting.

    Returns:
        A string indicating the current theme: "dark" or "light".
    """
    current_theme = get_current_theme()
    return f"Current theme is: {current_theme}"


@mcp.tool()
def set_dark_theme() -> str:
    """Set system theme to dark mode.

    Returns:
        Confirmation message.
    """
    set_theme("dark")
    return "Theme set to dark mode"


@mcp.tool()
def set_light_theme() -> str:
    """Set system theme to light mode.

    Returns:
        Confirmation message.
    """
    set_theme("light")
    return "Theme set to light mode"


@mcp.tool()
def toggle_theme() -> str:
    """Toggle system theme between dark and light modes.

    Returns:
        Confirmation message with the new theme.
    """
    current = get_current_theme()
    new_theme = "light" if current == "dark" else "dark"
    set_theme(new_theme)
    return f"Theme toggled from {current} to {new_theme}"


if __name__ == "__main__":
    # Run the server with stdio transport (default)
    mcp.run()
