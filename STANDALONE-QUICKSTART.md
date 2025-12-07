# ScreenCatch Standalone - Quick Start

## Installation

1. Ensure you have Python 3.7+ installed
2. Install Pillow:

```bash
pip install pillow
```

## Quick Test

Run the test suite to verify everything works:

```bash
python test-standalone.py
```

## Basic Usage

### Simple Capture

```bash
python screencatch.py
```

**What happens:**
1. Description dialog appears - enter "My first capture" (or skip)
2. Capture overlay appears with instructions
3. Drag to select first region
4. Press **Enter** to capture and continue
5. Drag to select second region (optional)
6. Press **Shift+Enter** to capture and finish
7. Done! Check current directory for:
   - `capture_YYYY-MM-DD_HHMMSS.png` - The merged image
   - `capture_YYYY-MM-DD_HHMMSS.json` - Metadata with description

### Capture Without Description

```bash
python screencatch.py --no-description
```

Skips the description dialog and goes straight to capture.

### Capture with Preview

```bash
python screencatch.py --preview
```

After capturing, shows a preview window where you can:
- Click "Keep This Capture" to save
- Click "Recapture (Keep Description)" to try again with the same description

## Keyboard Shortcuts

### During Capture
- **Enter** - Capture current region and continue to next
- **Shift+Enter** - Capture current region and finish
- **ESC** - Finish without capturing current region
- **Drag instruction box** - Move it out of the way

### In Preview Window
- **Enter** or **ESC** - Keep the capture
- **R** - Recapture

## Output

### PNG Image
Single merged image if you captured multiple regions, or single image if one region.

### JSON Metadata
```json
{
  "description": "My first capture",
  "timestamp": "2024-01-15T14:30:22.123456",
  "captures": 2,
  "merged": true,
  "filepath": "capture_2024-01-15_143022.png",
  "regions": [
    {"x": 100, "y": 200, "width": 800, "height": 600},
    {"x": 1000, "y": 300, "width": 600, "height": 400}
  ],
  "recapture_iteration": 0,
  "merge_method": "auto"
}
```

## Common Use Cases

### 1. Tutorial Screenshots

```bash
python screencatch.py
# Description: "Installing Node.js - Step by step"
# Capture each step, merged into single image
```

### 2. Bug Reports

```bash
python screencatch.py --output-dir ./bug-reports
# Description: "Login button not responding"
# Capture error message, console, network tab
```

### 3. Code Review

```bash
python screencatch.py --merge-method vertical
# Description: "Code changes for PR #123"
# Capture before/after code side-by-side
```

### 4. Automation/Web Integration

```bash
python screencatch.py --no-description --json-output > result.json
# Parse result.json to get filepath
# Upload to server, database, etc.
```

## Multi-Monitor Support

Works seamlessly across multiple monitors:
- Drag the instruction box to any monitor
- Capture regions from different monitors
- All regions merged into single image

## Troubleshooting

### "No module named 'PIL'"
```bash
pip install pillow
```

### Capture overlay doesn't show
- Check that tkinter is installed (usually comes with Python)
- Try running as administrator on Windows

### Images merge in wrong order
Regions are merged in capture order (the order you selected them).

## Next Steps

- See [STANDALONE-README.md](STANDALONE-README.md) for full documentation
- Check `--help` for all command-line options:
  ```bash
  python screencatch.py --help
  ```

## Integration with Web Application

For web application integration, use `--json-output`:

```python
import subprocess
import json

result = subprocess.run(
    ['python', 'screencatch.py', '--no-description', '--json-output'],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
filepath = data['filepath']
description = data['description']

# Upload to your web service
# upload_to_server(filepath, description)
```

Exit codes:
- `0` - Success
- `1` - Cancelled by user
- `130` - Interrupted (Ctrl+C)

## Examples

See the examples directory (coming soon) for:
- Web service integration
- Batch processing
- Custom merge layouts
- OCR text extraction
