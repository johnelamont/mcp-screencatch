# ScreenCatch Standalone CLI

A standalone command-line screen capture tool with description input, multi-region capture, and automatic image merging.

## Features

- **Description Input**: Describe what you're capturing before you start
- **Multi-Region Capture**: Capture multiple screen regions in one session
- **Auto-Merge**: Automatically merge multiple captures into a single image
- **Multi-Monitor Support**: Works seamlessly across multiple monitors
- **Preview & Recapture**: Optionally preview results and recapture if needed
- **Metadata**: JSON files with descriptions and capture details
- **JSON Output**: Machine-readable output for integration with other tools

## Installation

### Requirements

- Python 3.7+
- PIL/Pillow for image processing

```bash
pip install pillow
```

## Usage

### Basic Usage

```bash
# Capture with description prompt
python screencatch.py

# Capture without description
python screencatch.py --no-description

# Capture with preview and recapture option
python screencatch.py --preview
```

### Command-Line Options

```bash
python screencatch.py [options]

Options:
  -o, --output-dir DIR    Directory to save captures (default: current directory)
  --no-description        Skip description dialog
  --preview               Show preview and allow recapture
  --merge-method METHOD   How to merge: auto, vertical, horizontal, grid (default: auto)
  --spacing PIXELS        Spacing between merged images (default: 10)
  --json-output           Output result as JSON to stdout
```

### Capture Controls

When the capture overlay appears:

- **Drag** to select a region
- **Enter** - Capture region and continue to next
- **Shift+Enter** - Capture region and finish
- **ESC** - Finish (save all captured regions)
- **Drag instruction box** - Move it out of the way

### Examples

#### Basic Capture with Description

```bash
python screencatch.py
```

1. Enter description (e.g., "Setting up VS Code")
2. Drag to select first region, press Enter
3. Drag to select second region, press Shift+Enter
4. Done! Images merged and saved

#### Capture to Specific Directory

```bash
python screencatch.py --output-dir ./screenshots
```

#### Capture with Preview

```bash
python screencatch.py --preview
```

After capturing, a preview window shows:
- Click "Keep This Capture" to save
- Click "Recapture (Keep Description)" to try again

#### JSON Output for Automation

```bash
python screencatch.py --json-output > result.json
```

Output format:
```json
{
  "success": true,
  "filepath": "capture_2024-01-15_143022.png",
  "description": "Setting up VS Code",
  "capture_count": 3,
  "merged": true,
  "recapture_iterations": 0,
  "metadata_file": "capture_2024-01-15_143022.json"
}
```

## Output Files

### Image File

- **Format**: PNG
- **Naming**: `capture_YYYY-MM-DD_HHMMSS.png`
- **Content**: Single image (merged if multiple regions)

### Metadata File

- **Format**: JSON
- **Naming**: `capture_YYYY-MM-DD_HHMMSS.json`
- **Content**:

```json
{
  "description": "Setting up VS Code",
  "timestamp": "2024-01-15T14:30:22.123456",
  "captures": 3,
  "merged": true,
  "filepath": "capture_2024-01-15_143022.png",
  "regions": [
    {"x": 100, "y": 200, "width": 800, "height": 600},
    {"x": 1000, "y": 300, "width": 600, "height": 400},
    {"x": 150, "y": 850, "width": 900, "height": 500}
  ],
  "recapture_iteration": 0,
  "merge_method": "auto"
}
```

## Merge Methods

### Auto (Recommended)

Intelligently chooses the best layout:
- **2 images**: Vertical or horizontal based on aspect ratio
- **3-4 images**: 2x2 grid
- **5+ images**: Optimized grid

### Vertical

Stack all images top to bottom.

```bash
python screencatch.py --merge-method vertical
```

### Horizontal

Stack all images left to right.

```bash
python screencatch.py --merge-method horizontal
```

### Grid

Arrange images in a grid pattern.

```bash
python screencatch.py --merge-method grid
```

## Multi-Monitor Support

ScreenCatch automatically detects all connected monitors and supports:
- Capturing across multiple screens
- Monitors in any configuration (left, right, above, below)
- Negative coordinates for monitors left of primary
- Dragging instruction box to any monitor

## Web Application Integration

### Using JSON Output

```python
import subprocess
import json

# Run screen capture
result = subprocess.run(
    ['python', 'screencatch.py', '--json-output', '--no-description'],
    capture_output=True,
    text=True
)

# Parse result
data = json.loads(result.stdout)

if data['success']:
    filepath = data['filepath']
    description = data['description']
    # Upload to your web service, etc.
```

### Using Exit Codes

- **0**: Success
- **1**: Cancelled by user
- **130**: Cancelled by Ctrl+C
- **Other**: Error occurred

### Programmatic Control

```bash
# Set output directory via environment
export SCREENCATCH_OUTPUT_DIR=/path/to/output

# Run without user interaction (no description, no preview)
python screencatch.py --no-description --json-output

# Process the JSON output
```

## Troubleshooting

### "Module not found: PIL"

```bash
pip install pillow
```

### Capture overlay doesn't appear

- Check that Python has permission to create windows
- Try running without `--preview` first
- Ensure tkinter is installed (usually included with Python)

### Images not merging correctly

- Try different merge methods: `--merge-method vertical`
- Adjust spacing: `--spacing 20`
- Ensure captured regions have similar sizes

### Multi-monitor issues

- ScreenCatch uses Windows API for monitor detection
- Works on Windows 7+
- For other platforms, multi-monitor support may be limited

## Advanced Usage

### Capture Without Description, Vertical Merge

```bash
python screencatch.py --no-description --merge-method vertical --spacing 5
```

### Custom Output Directory with Preview

```bash
python screencatch.py --output-dir ~/Documents/Screenshots --preview
```

### Automated Workflow

```bash
#!/bin/bash
# capture-and-upload.sh

# Capture with JSON output
RESULT=$(python screencatch.py --no-description --json-output)

# Extract filepath
FILEPATH=$(echo $RESULT | jq -r '.filepath')

# Upload to server
curl -F "file=@$FILEPATH" https://your-server.com/upload

# Clean up
rm "$FILEPATH"
rm "${FILEPATH%.png}.json"
```

## Known Limitations

- Windows only (for full multi-monitor support)
- Requires GUI environment (tkinter)
- Preview mode blocks execution until user responds
- Large images may take time to merge

## License

See main project LICENSE file.

## Contributing

This is part of the mcp-screencatch project. See main README for contribution guidelines.
