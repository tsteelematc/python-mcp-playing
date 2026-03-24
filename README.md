# Theme Toggle MCP Server

A Python MCP (Model Context Protocol) server that provides tools to toggle system theme between light and dark modes. Supports both **Windows** (via the Registry) and **macOS** (via `osascript`). OS detection happens automatically at runtime.

## Features

- **Get Current Theme**: Check whether the system is currently using light or dark mode
- **Set Dark Theme**: Switch the system to dark mode
- **Set Light Theme**: Switch the system to light mode
- **Toggle Theme**: Switch between light and dark modes automatically

## Requirements

- Python 3.10 or higher
- MCP SDK for Python
- **Windows 10/11** or **macOS 10.14 Mojave or later**

## Installation

1. Clone this repository:

**Windows (PowerShell)**:
```powershell
git clone <repository-url>
cd python-mcp-playing
```

**macOS/Linux (Terminal)**:
```bash
git clone <repository-url>
cd python-mcp-playing
```

2. Install dependencies using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

## Usage

### Running the Server Directly

**Windows**:
```powershell
python src/theme_toggle_server.py
```

**macOS**:
```bash
python src/theme_toggle_server.py
```

### Using with Claude Desktop

Add the server to your Claude Desktop configuration file.

**Windows** — Location: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "theme-toggle": {
      "command": "python",
      "args": [
        "C:\\path\\to\\python-mcp-playing\\src\\theme_toggle_server.py"
      ]
    }
  }
}
```

**macOS** — Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "theme-toggle": {
      "command": "python",
      "args": [
        "/path/to/python-mcp-playing/src/theme_toggle_server.py"
      ]
    }
  }
}
```

Or using uv (works on both platforms):

```json
{
  "mcpServers": {
    "theme-toggle": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/python-mcp-playing",
        "python",
        "src/theme_toggle_server.py"
      ]
    }
  }
}
```

### Using with VS Code

```bash
uv run mcp install src/theme_toggle_server.py --name "Theme Toggle"
```

### Testing with MCP Inspector

```bash
python src/theme_toggle_server.py
# In a separate terminal:
npx @modelcontextprotocol/inspector
```

## Available Tools

### `get_theme`
Get the current system theme setting.

**Returns**: `"Current theme is: dark"` or `"Current theme is: light"`

### `set_dark_theme`
Set system theme to dark mode.

**Returns**: `"Theme set to dark mode"`

### `set_light_theme`
Set system theme to light mode.

**Returns**: `"Theme set to light mode"`

### `toggle_theme`
Toggle system theme between dark and light modes.

**Returns**: `"Theme toggled from dark to light"` (or vice-versa)

## How It Works

The server detects the current operating system at runtime and calls the appropriate platform API.

### macOS

Reads the current theme using:
```bash
defaults read -g AppleInterfaceStyle
```
Sets the theme using AppleScript via `osascript`:
```applescript
tell app "System Events" to tell appearance preferences to set dark mode to true/false
```

### Windows

Reads and writes to the Windows Registry at:
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize
```
Two values are updated:
- `AppsUseLightTheme`: controls app theme (0 = dark, 1 = light)
- `SystemUsesLightTheme`: controls system theme (0 = dark, 1 = light)

After writing, a `WM_SETTINGCHANGE` message is broadcast so the change takes effect immediately.

## Development

### Running Tests

```bash
pytest
```

### Project Structure

```
python-mcp-playing/
├── .github/
│   └── copilot-instructions.md
├── src/
│   └── theme_toggle_server.py
├── tests/
│   ├── conftest.py
│   └── test_theme_toggle.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Security Considerations

- **macOS**: The server uses `osascript`, which may prompt for Accessibility permissions on first use.
- **Windows**: Only modifies theme-related registry keys under `HKEY_CURRENT_USER`. Does not require administrator privileges.

## Platform Support

| Platform       | Supported | Mechanism                    |
|----------------|-----------|------------------------------|
| Windows 10/11  | ✅        | Windows Registry + ctypes    |
| macOS 10.14+   | ✅        | `defaults` + `osascript`     |
| Linux          | ❌        | Not supported                |

## License

MIT License

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Use type hints for all function parameters and return values
2. Follow PEP 8 style guidelines
3. Include error handling for all OS calls
4. Add tests for new functionality

## Troubleshooting

### macOS: Theme doesn't change / permission error
macOS may require Accessibility permissions for `osascript` to control System Events. Go to **System Settings → Privacy & Security → Accessibility** and allow the terminal app (or whatever application runs the server).

### Windows: Theme doesn't change immediately
Windows may take a few seconds to apply the theme change. Some applications may need to be restarted to reflect the new theme.

### Windows: Registry access errors
Ensure you have permission to modify the registry. The server should work without administrator privileges as it only modifies `HKEY_CURRENT_USER`.

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [macOS defaults command](https://ss64.com/mac/defaults.html)
- [Windows Registry Documentation](https://docs.microsoft.com/en-us/windows/win32/sysinfo/registry)

