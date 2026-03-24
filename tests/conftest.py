"""Pytest configuration for cross-platform test execution.

On non-Windows platforms, this module injects lightweight mocks for
Windows-only modules (`winreg`) and attributes (`ctypes.windll`) so that
Windows-specific code paths can be exercised via unittest.mock patches
regardless of the host OS.
"""

import ctypes
import sys
from unittest.mock import MagicMock

if sys.platform != "win32":
    # Provide a mock winreg module (only ships with CPython on Windows)
    _winreg_mock = MagicMock()
    _winreg_mock.HKEY_CURRENT_USER = 0x80000001
    _winreg_mock.KEY_READ = 0x20019
    _winreg_mock.KEY_SET_VALUE = 0x0002
    _winreg_mock.REG_DWORD = 4
    sys.modules["winreg"] = _winreg_mock

    # ctypes is a standard library module available on all platforms; only
    # ctypes.windll is Windows-specific.  Patching the attribute here means
    # Windows-specific code paths can be exercised via unittest.mock without
    # replacing the entire ctypes module.
    ctypes.windll = MagicMock()  # type: ignore[attr-defined]
