# MCP ScreenCatch

An MCP (Model Context Protocol) server that provides screen capture functionality for Claude Desktop, emulating Windows Snipping Tool capabilities.

## Overview

MCP ScreenCatch enables Claude Desktop to capture screenshots of user-selected screen regions. The tool allows users to highlight areas of their monitor(s), capture them, and save the images with timestamps for easy retrieval and processing.

## Objectives

- **Seamless Integration**: Provide an MCP command that Claude Desktop can invoke to initiate screen captures
- **Interactive Selection**: Allow users to select specific regions of their screen(s) using a familiar snipping interface
- **Multi-Monitor Support**: Work across multiple monitors for flexible screen capture
- **Sequential Captures**: Enable users to capture multiple screenshots in succession without restarting the tool
- **Timestamped Files**: Automatically timestamp each capture for chronological ordering
- **Configurable Output**: Let users specify the output directory for captured images
- **Pipeline Ready**: Save files in a location accessible to other MCP commands or external applications

## Features

### Core Functionality

- **Region Selection**: Click and drag interface to select screen regions
- **Capture & Save**: Button/icon to finalize and save the selected region
- **Continuous Mode**: After each capture, prompt user to:
  - Capture another screenshot
  - Quit the tool
- **Timestamp Naming**: Files named with ISO 8601 timestamps (e.g., `capture_2025-11-27_064730.png`)
- **Directory Selection**: User-configurable output directory

### Use Cases

- Capture UI elements for debugging
- Document visual workflows
- Create sequential tutorials or guides
- Feed captured images to Claude for analysis
- Build visual documentation pipelines

## Technical Implementation

### MCP Protocol

The tool will be exposed as an MCP server that Claude Desktop can connect to, providing:
- Tool: `capture_screen` - Initiates the screen capture interface
- Tool: `set_output_directory` - Configure where captures are saved
- Tool: `list_captures` - Retrieve timestamped capture files

### Technology Stack

- **Language**: TypeScript/Node.js
- **MCP SDK**: @modelcontextprotocol/sdk
- **Screen Capture**: screenshot-desktop for cross-platform screen capture
- **Image Processing**: Sharp for image cropping and manipulation
- **UI Framework**: Electron for transparent overlay and region selection

### File Format

- Default format: PNG (lossless, good for UI captures)
- Naming convention: `capture_YYYY-MM-DD_HHMMSS.png`
- Metadata: Optional JSON sidecar with capture timestamp and dimensions

## Installation

```bash
npm install
npm run build
```

## Configuration

Add to Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "screencatch": {
      "command": "node",
      "args": ["/path/to/mcp-screencatch/build/index.js"]
    }
  }
}
```

## Usage

### From Claude Desktop

Once configured, you can ask Claude to capture screenshots:

```
Claude, can you capture a screenshot of my screen?
```

### Interactive Overlay

1. An Electron overlay window will appear covering your screen(s)
2. Click and drag to select the region you want to capture
3. Click the **Capture** button or press **Enter** to save
4. Press **ESC** or click **Cancel** to abort
5. The captured image is saved with a timestamp

### Available Commands

**Capture a screenshot:**
```
Claude, capture a screenshot
```

**Set output directory:**
```
Claude, set the screenshot output directory to C:\Users\johne\screenshots
```

**List recent captures:**
```
Claude, list my recent screenshots
```

### File Naming

Screenshots are automatically named with ISO 8601 timestamps:
- `capture_2025-11-27_143052.png`
- `capture_2025-11-27_143105.png`

This ensures chronological ordering and prevents filename conflicts.

## Development Status

✅ **Implemented** - Core functionality complete

- ✅ MCP server with stdio transport
- ✅ Interactive region selection with Electron overlay
- ✅ Timestamped file naming
- ✅ Configurable output directory
- ✅ List and manage captures
- ⚠️ **Note**: Requires Electron, which adds ~150MB to node_modules. For production use, consider electron-builder for packaging.

## Future Enhancements

- Support for full screen and window captures
- Multiple image format options (PNG, JPG, WebP)
- Annotation tools (arrows, text, highlights)
- Clipboard integration
- Automatic cleanup of old captures
- Screenshot comparison tools

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
