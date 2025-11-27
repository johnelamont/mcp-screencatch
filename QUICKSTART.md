# Quick Start Guide

## What We Built

MCP ScreenCatch is now fully functional! Here's what was implemented:

✅ **Core Features:**
- Interactive screen region selection with Electron overlay
- Timestamped PNG file output
- Configurable output directory
- List and manage captured screenshots
- MCP server integration for Claude Desktop

✅ **Technologies Used:**
- TypeScript + Node.js
- Electron (for GUI overlay)
- Sharp (for image cropping)
- screenshot-desktop (for screen capture)
- @modelcontextprotocol/sdk (for MCP integration)

## Setup Complete

The following has been configured:

1. ✅ Dependencies installed (`npm install`)
2. ✅ TypeScript compiled (`npm run build`)
3. ✅ MCP server added to Claude Desktop config
4. ✅ Server tested and working

## How to Use

### Step 1: Restart Claude Desktop

**Important:** You must restart Claude Desktop for the MCP server to be loaded.

Close and reopen Claude Desktop completely.

### Step 2: Verify MCP Server is Loaded

In Claude Desktop, you can check if the server is connected by asking:
```
Are there any MCP tools available?
```

You should see `capture_screen`, `set_output_directory`, and `list_captures`.

### Step 3: Capture Your First Screenshot

Simply ask Claude:
```
Can you capture a screenshot for me?
```

**What happens next:**
1. An overlay window appears covering your screen
2. Click and drag to select a region
3. Click "Capture" button (or press Enter) to save
4. Press ESC to cancel

### Step 4: Configure Output Directory (Optional)

By default, screenshots are saved to the current working directory. To change this:

```
Set the screenshot output directory to C:\Users\johne\screenshots
```

Replace the path with your desired location.

### Step 5: View Your Captures

```
List my recent screenshots
```

This shows the 10 most recent captures with timestamps and file sizes.

## Interactive Overlay Features

### Mouse Controls
- **Click + Drag**: Select screen region
- **Release**: Finalize selection

### Keyboard Shortcuts
- **Enter**: Capture the selected region
- **ESC**: Cancel and close overlay

### Visual Feedback
- Semi-transparent overlay dims the screen
- Blue rectangle shows selected region
- Instructions displayed at top
- Capture/Cancel buttons appear after selection

## File Naming Convention

Screenshots are saved with this format:
```
capture_YYYY-MM-DD_HHMMSS.png
```

Examples:
- `capture_2025-11-27_143052.png`
- `capture_2025-11-27_143105.png`

This ensures:
- ✅ Chronological sorting
- ✅ No filename conflicts
- ✅ Easy to identify when screenshot was taken

## Continuous Capture Mode

The MCP tool supports a `prompt_continue` parameter. When enabled, you can capture multiple screenshots in succession:

1. Capture first region
2. Tool asks if you want to capture another
3. Repeat or quit

This is perfect for creating tutorials or documenting multi-step processes.

## Troubleshooting

### "MCP server not found"
- Make sure you restarted Claude Desktop
- Check that the config file exists: `C:\Users\johne\AppData\Roaming\Claude\claude_desktop_config.json`
- Verify the path in the config points to: `C:\Users\johne\mcp-screencatch\build\index.js`

### "Overlay doesn't appear"
- Electron may be initializing for the first time
- Check console output for errors
- Try running `node build/index.js` manually to test

### "Capture failed"
- Ensure you have write permissions to the output directory
- Check that Sharp and screenshot-desktop are installed
- Run `npm install` again if needed

## Example Use Cases

### 1. Bug Reporting
```
Claude, capture screenshots of this error I'm seeing
```

### 2. Documentation
```
Claude, I need to document these 5 steps. Can you help me capture screenshots of each?
```

### 3. Design Review
```
Claude, capture this UI element and analyze the design
```

### 4. Tutorial Creation
```
Claude, let's create a tutorial. Capture screenshots of each step as I go through the process.
```

## Next Steps

Consider these enhancements:

- **Packaging**: Use electron-builder to create a standalone executable
- **Annotations**: Add arrows, text, and highlights to screenshots
- **Multiple Formats**: Support JPG, WebP, etc.
- **Auto-upload**: Upload captures to cloud storage
- **OCR Integration**: Extract text from screenshots automatically

## Project Structure

```
mcp-screencatch/
├── src/
│   ├── index.ts          # MCP server entry point
│   ├── capture.ts        # Screen capture logic
│   ├── overlay.ts        # Electron overlay UI
│   └── screenshot-desktop.d.ts  # Type definitions
├── build/                # Compiled JavaScript
├── node_modules/         # Dependencies
├── package.json          # Project config
├── tsconfig.json         # TypeScript config
├── README.md            # Full documentation
└── QUICKSTART.md        # This file

```

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review the TypeScript source code in `src/`
3. Test the MCP server directly: `node build/index.js`

Enjoy capturing screenshots with Claude! 📸
