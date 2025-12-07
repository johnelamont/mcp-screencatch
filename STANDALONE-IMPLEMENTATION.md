# Standalone ScreenCatch Implementation

## Overview

The standalone version of ScreenCatch is a command-line application that can be invoked independently of Claude Desktop, making it suitable for web application integration and automation.

## Architecture

```
screencatch.py (CLI entry point)
    |
    |-- enhanced_capture_standalone.py
    |   |-- DescriptionDialog (tkinter)
    |   |-- MultiCaptureOverlay (tkinter)
    |   |-- merge_and_save()
    |       |-- PIL ImageGrab (screen capture)
    |       |-- image_merger.py (merge images)
    |
    |-- preview_and_confirm_standalone.py
    |   |-- PreviewWindow (tkinter)
    |
    |-- image_merger.py
        |-- ImageMerger.merge_vertical()
        |-- ImageMerger.merge_horizontal()
        |-- ImageMerger.merge_grid()
        |-- ImageMerger.merge_auto()
```

## Key Differences from MCP Version

### MCP Version
- Integrated with Claude Desktop via Model Context Protocol
- Uses Node.js screenshot-desktop library
- Uses Sharp for image processing
- Python scripts called from TypeScript
- Result returned to Claude as JSON

### Standalone Version
- Pure Python implementation
- Direct PIL/Pillow ImageGrab for screenshots
- Self-contained, no Node.js dependencies
- Can be invoked from command line or subprocess
- JSON output optional via `--json-output` flag

## Files

### Core Application Files

1. **screencatch.py** (192 lines)
   - CLI entry point
   - Argument parsing
   - Main capture loop with recapture support
   - JSON output formatting

2. **enhanced_capture_standalone.py** (300+ lines)
   - `DescriptionDialog` - tkinter description input
   - `MultiCaptureOverlay` - multi-region capture with draggable instructions
   - `merge_and_save()` - capture regions and merge images

3. **preview_and_confirm_standalone.py** (146 lines)
   - `PreviewWindow` - show merged result
   - Recapture option with same description

4. **image_merger.py** (renamed from image-merger.py)
   - `ImageMerger` class with merge methods
   - Vertical, horizontal, grid, and auto layouts

### Documentation Files

1. **STANDALONE-README.md**
   - Complete usage documentation
   - Command-line options
   - Integration examples
   - Troubleshooting

2. **STANDALONE-QUICKSTART.md**
   - Quick start guide
   - Common use cases
   - Keyboard shortcuts
   - Web integration examples

3. **STANDALONE-IMPLEMENTATION.md** (this file)
   - Architecture overview
   - Technical details
   - Comparison with MCP version

### Test Files

1. **test-standalone.py**
   - Import tests
   - Image merger tests
   - Description dialog test (interactive)

## Technical Details

### Multi-Monitor Support

Uses Windows API via ctypes:

```python
user32 = ctypes.windll.user32
virtual_x_min = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
virtual_y_min = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
virtual_width = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
virtual_height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
```

Overlay window geometry:
```python
self.root.geometry(f"{virtual_width}x{virtual_height}+{virtual_x_min}+{virtual_y_min}")
```

### Screen Capture

Uses PIL ImageGrab for direct screen capture:

```python
from PIL import ImageGrab

bbox = (region['x'], region['y'],
        region['x'] + region['width'],
        region['y'] + region['height'])
img = ImageGrab.grab(bbox=bbox)
```

No intermediate screenshot files needed - captures directly to memory.

### Event Handling

Draggable instruction box using tag bindings:

```python
# Create elements with 'instructions' tag
self.canvas.create_rectangle(..., tags='instructions')
self.canvas.create_text(..., tags='instructions')

# Bind to tag (higher priority than canvas bindings)
self.canvas.tag_bind('instructions', '<ButtonPress-1>', self.on_instructions_press)
self.canvas.tag_bind('instructions', '<B1-Motion>', self.on_instructions_drag)
self.canvas.tag_bind('instructions', '<ButtonRelease-1>', self.on_instructions_release)

# Return "break" to stop propagation
def on_instructions_press(self, event):
    self.is_dragging_instructions = True
    return "break"  # Don't propagate to canvas handlers
```

### Coordinate System

Canvas coordinates are already in virtual screen space:
- Primary monitor at (0, 0)
- Secondary monitor left: negative x coordinates
- Secondary monitor right: positive x beyond primary width
- No offset addition needed when saving regions

### Image Merging

Smart auto-merge logic:

```python
def merge_auto(images, spacing=10):
    if len(images) == 2:
        # Check aspect ratio
        avg_aspect = sum(img.width / img.height for img in images) / 2
        if avg_aspect > 1.5:
            return merge_vertical(images, spacing)  # Wide images
        else:
            return merge_horizontal(images, spacing)  # Tall images
    elif len(images) <= 4:
        return merge_grid(images, cols=2, spacing=spacing)  # 2x2 grid
    else:
        return merge_grid(images, spacing=spacing)  # Auto grid
```

## Command-Line Interface

### Arguments

```python
parser.add_argument('--output-dir', '-o', default=os.getcwd())
parser.add_argument('--no-description', action='store_true')
parser.add_argument('--preview', action='store_true')
parser.add_argument('--merge-method', choices=['auto', 'vertical', 'horizontal', 'grid'], default='auto')
parser.add_argument('--spacing', type=int, default=10)
parser.add_argument('--json-output', action='store_true')
```

### Exit Codes

- `0` - Success
- `1` - Cancelled by user or no regions captured
- `130` - Interrupted with Ctrl+C
- Other - Error occurred

### JSON Output Format

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

## Web Application Integration

### Subprocess Call

```python
import subprocess
import json

result = subprocess.run(
    ['python', 'screencatch.py', '--no-description', '--json-output'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    data = json.loads(result.stdout)
    filepath = data['filepath']
    # Process the captured image
```

### Environment Variables

```python
os.environ['SCREENCATCH_OUTPUT_DIR'] = '/path/to/output'
```

Though command-line `--output-dir` is preferred.

## File Naming

### Image Files
`capture_YYYY-MM-DD_HHMMSS.png`

Example: `capture_2024-01-15_143022.png`

### Metadata Files
`capture_YYYY-MM-DD_HHMMSS.json`

Example: `capture_2024-01-15_143022.json`

### Temporary Files

During capture, creates temporary IPC file:
`temp-capture-{timestamp}.json`

Deleted immediately after reading.

## Dependencies

### Python Standard Library
- `tkinter` - GUI (description dialog, overlay, preview)
- `json` - Data serialization
- `argparse` - CLI argument parsing
- `pathlib` - File path handling
- `datetime` - Timestamps
- `ctypes` - Windows API access

### External Libraries
- `Pillow` (PIL) - Image capture and manipulation
  ```bash
  pip install pillow
  ```

## Platform Support

### Windows
Full support including:
- Multi-monitor detection
- Virtual screen coordinates
- Negative coordinate handling

### macOS / Linux
Basic support:
- Single monitor works
- Multi-monitor may have limitations
- Virtual screen API not available

## Performance

### Typical Workflow (3 captures, auto-merge)
1. Description dialog: ~2s (user input)
2. Capture overlay: ~1s per region
3. Screen capture: <100ms per region
4. Image merge: ~200ms
5. File save: ~100ms

**Total: ~5-7 seconds** (mostly user interaction time)

### Memory Usage
- Each 1920x1080 capture: ~8MB in memory
- Merged images released after save
- Peak memory for 5 full-screen captures: ~50MB

### Disk Usage
- PNG images: typically 100KB - 2MB depending on content
- JSON metadata: ~500 bytes - 2KB

## Testing

### Run Test Suite

```bash
python test-standalone.py
```

Tests:
- Import verification
- Image merger functionality
- Description dialog (optional interactive test)

### Manual Testing

```bash
# Basic capture
python screencatch.py

# Without description
python screencatch.py --no-description

# With preview
python screencatch.py --preview

# JSON output
python screencatch.py --json-output

# Custom output directory
python screencatch.py --output-dir ./screenshots
```

## Known Issues

### Windows Console Encoding
Fixed by setting UTF-8 encoding:
```python
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
```

### Module Import (Hyphens)
Python can't import modules with hyphens in names.

**Solution**: Renamed files:
- `image-merger.py` → `image_merger.py`
- `merge-images-cli.py` → `merge_images_cli.py`

### Preview Blocking
Preview window blocks execution until user responds. This is by design for standalone use, but was problematic for MCP integration.

**Solution**: Made preview optional (default: false)

## Future Enhancements

### Planned
- [ ] Cross-platform multi-monitor support
- [ ] OCR text extraction from captures
- [ ] Annotation tools (arrows, highlights, text)
- [ ] Video recording mode
- [ ] Cloud upload integration
- [ ] Custom merge templates

### Under Consideration
- [ ] GUI mode (not just overlay)
- [ ] Hotkey support for quick capture
- [ ] Tray icon for background operation
- [ ] Plugin system for custom processors
- [ ] Database storage option

## Migration from MCP Version

If you were using the MCP version:

### What Stays the Same
- Multi-region capture workflow
- Description input
- Auto-merge functionality
- Metadata JSON format
- Multi-monitor support

### What Changes
- Invocation: command-line instead of Claude Desktop tool
- Output: files on disk instead of returned to Claude
- Integration: subprocess calls instead of MCP protocol

### Example Migration

**Before (MCP):**
```typescript
// In Claude Desktop
"Please capture screenshots of the installation process"
// Claude calls enhanced_capture tool
// Result returned to conversation
```

**After (Standalone):**
```python
# In your web application
result = subprocess.run(
    ['python', 'screencatch.py', '--json-output'],
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)
filepath = data['filepath']
# Upload filepath to server, save to database, etc.
```

## Support

For issues or questions:
1. Check [STANDALONE-README.md](STANDALONE-README.md) for documentation
2. Run `python screencatch.py --help` for options
3. Run `python test-standalone.py` to verify installation
4. Check logs in stderr for debugging information

## License

See main project LICENSE file.
