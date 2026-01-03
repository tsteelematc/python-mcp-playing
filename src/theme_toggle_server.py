"""Windows Theme Toggle MCP Server.

This MCP server provides tools to toggle Windows theme between light and dark modes
using Windows Registry manipulation.
"""

import ctypes
import winreg
from typing import Literal

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP(
    name="Windows Theme Toggle",
    instructions="Provides tools to toggle Windows theme between light and dark modes",
)


def get_current_theme() -> Literal["dark", "light"]:
    """Get the current Windows theme setting.

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


def set_theme(theme: Literal["dark", "light"]) -> None:
    """Set the Windows theme.

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


@mcp.tool()
def get_theme() -> str:
    """Get the current Windows theme setting.

    Returns:
        A string indicating the current theme: "dark" or "light".
    """
    current_theme = get_current_theme()
    return f"Current Windows theme is: {current_theme}"


@mcp.tool()
def set_dark_theme() -> str:
    """Set Windows theme to dark mode.

    Returns:
        Confirmation message.
    """
    set_theme("dark")
    return "Windows theme set to dark mode"


@mcp.tool()
def set_light_theme() -> str:
    """Set Windows theme to light mode.

    Returns:
        Confirmation message.
    """
    set_theme("light")
    return "Windows theme set to light mode"


@mcp.tool()
def toggle_theme() -> str:
    """Toggle Windows theme between dark and light modes.

    Returns:
        Confirmation message with the new theme.
    """
    current = get_current_theme()
    new_theme = "light" if current == "dark" else "dark"
    set_theme(new_theme)
    return f"Windows theme toggled from {current} to {new_theme}"


if __name__ == "__main__":
    # Run the server with stdio transport (default)
    mcp.run()
