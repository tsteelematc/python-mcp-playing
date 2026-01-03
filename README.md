# Windows Theme Toggle MCP Server

A Python MCP (Model Context Protocol) server that provides tools to toggle Windows theme between light and dark modes using Windows Registry manipulation.

## Features

- **Get Current Theme**: Check whether Windows is currently using light or dark mode
- **Set Dark Theme**: Switch Windows to dark mode
- **Set Light Theme**: Switch Windows to light mode
- **Toggle Theme**: Switch between light and dark modes automatically

## Requirements

- Python 3.10 or higher
- Windows 10/11
- MCP SDK for Python

## Installation

1. Clone this repository:
```powershell
git clone <repository-url>
cd python-mcp-playing
```

2. Install dependencies using uv (recommended):
```powershell
uv sync
```

Or using pip:
```powershell
pip install -e .
```

## Usage

### Running the Server Directly

```powershell
python src/theme_toggle_server.py
```

### Using with Claude Desktop

Add the server to your Claude Desktop configuration file:

**Location**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "windows-theme": {
      "command": "python",
      "args": [
        "C:\\path\\to\\python-mcp-playing\\src\\theme_toggle_server.py"
      ]
    }
  }
}
```

Or using uv:

```json
{
  "mcpServers": {
    "windows-theme": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\path\\to\\python-mcp-playing",
        "python",
        "src/theme_toggle_server.py"
      ]
    }
  }
}
```

### Using with VS Code

1. Install the server in VS Code:
```powershell
uv run mcp install src/theme_toggle_server.py --name "Windows Theme Toggle"
```

2. The server will be available in the MCP panel

### Testing with MCP Inspector

1. Run the server:
```powershell
python src/theme_toggle_server.py
```

2. In a separate terminal, run the inspector:
```powershell
npx @modelcontextprotocol/inspector
```

3. Connect to the server via stdio

## Available Tools

### `get_theme`
Get the current Windows theme setting.

**Returns**: String indicating current theme ("dark" or "light")

### `set_dark_theme`
Set Windows theme to dark mode.

**Returns**: Confirmation message

### `set_light_theme`
Set Windows theme to light mode.

**Returns**: Confirmation message

### `toggle_theme`
Toggle Windows theme between dark and light modes.

**Returns**: Confirmation message with the new theme

## How It Works

The server uses the Windows Registry API (`winreg` module) to read and modify theme settings at:

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize
```

It modifies two registry values:
- `AppsUseLightTheme`: Controls app theme (0 = dark, 1 = light)
- `SystemUsesLightTheme`: Controls system theme (0 = dark, 1 = light)

## Development

### Running Tests

```powershell
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
├── .gitignore
├── pyproject.toml
└── README.md
```

## Security Considerations

- This server requires permission to modify the Windows Registry
- Only modifies theme-related registry keys under HKEY_CURRENT_USER
- Does not require administrator privileges
- All registry operations include proper error handling

## Platform Support

- **Supported**: Windows 10, Windows 11
- **Not Supported**: macOS, Linux

## License

MIT License

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Use type hints for all function parameters and return values
2. Follow PEP 8 style guidelines
3. Include error handling for registry operations
4. Add tests for new functionality

## Troubleshooting

### Theme doesn't change immediately
Windows may take a few seconds to apply the theme change. Some applications may need to be restarted to reflect the new theme.

### Registry access errors
Ensure you have permission to modify the registry. The server should work without administrator privileges as it only modifies HKEY_CURRENT_USER.

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Windows Registry Documentation](https://docs.microsoft.com/en-us/windows/win32/sysinfo/registry)
