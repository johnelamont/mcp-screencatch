# Enhanced Capture Feature

## Overview

The enhanced capture feature provides a complete workflow for documenting multi-step processes:

1. **Description Input**: Prompts user to describe what they're capturing
2. **Multi-Capture**: Capture multiple screen regions in one session
3. **Auto-Merge**: Automatically combines multiple captures into a single image
4. **Metadata**: Saves description and capture details alongside the image

## How It Works

### Step 1: Description Dialog

When you request an enhanced capture, a dialog appears asking for a description:

```
Enter a description for what you're about to capture:
┌─────────────────────────────────────┐
│ Setting up a new project in VS Code │
└─────────────────────────────────────┘
        [OK]     [Cancel]
```

- Enter a meaningful description
- Click OK or press Enter
- Click Cancel or close to skip (capture proceeds without description)

### Step 2: Multi-Capture Overlay

After entering the description, the capture overlay appears covering all your monitors:

```
┌──────────────────────────────────────────────────────┐
│ Capture #1: Click and drag to select region.        │
│ Enter = Capture and finish | Ctrl+Enter = Continue  │
│ ESC = Done | (Drag this box to move it)            │
└──────────────────────────────────────────────────────┘
```

**Controls:**
- **Drag to select**: Click and drag to create a blue selection rectangle
- **Enter**: Capture this region and finish
- **Ctrl+Enter**: Capture this region and continue to next
- **ESC**: Finish all captures (saves what you've captured so far)
- **Move instruction box**: Drag the instruction box to keep it out of the way

**Multi-Capture Workflow:**
1. Select first region, press Ctrl+Enter
2. Counter updates: "Capture #2..."
3. Select second region, press Ctrl+Enter
4. Continue as needed
5. Press Enter or ESC when done

### Step 3: Auto-Merge

If you captured multiple regions, they're automatically merged:

**Single Capture:**
- Saves as-is: `capture_2025-12-05_143000.png`

**Multiple Captures:**
- Auto-merged using intelligent layout:
  - 2 images: Vertical or horizontal based on aspect ratio
  - 3-4 images: 2x2 grid
  - 5+ images: Auto grid layout
- Result: `capture_2025-12-05_143000.png` (merged)

**Merge Methods:**
- `auto`: Smart layout selection (default)
- `vertical`: Stack top to bottom
- `horizontal`: Stack left to right
- `grid`: Arrange in grid

### Step 4: Metadata

A JSON file is saved alongside each capture:

```json
{
  "description": "Setting up a new project in VS Code",
  "timestamp": "2025-12-05T14:30:00.000Z",
  "captures": 3,
  "merged": true,
  "filepath": "C:\\Users\\johne\\screenshots\\capture_2025-12-05_143000.png",
  "regions": [
    {"x": 100, "y": 200, "width": 800, "height": 600},
    {"x": 1000, "y": 300, "width": 600, "height": 400},
    {"x": 500, "y": 100, "width": 900, "height": 700}
  ]
}
```

**Filename:** `capture_2025-12-05_143000.json`

## Usage

### From Claude Desktop (MCP)

**Basic Enhanced Capture:**
```
Can you help me capture screenshots with description?
```

Claude will use the `enhanced_capture` tool automatically.

**Without Description:**
```
Capture multiple screenshots without asking for description
```

### From Command Line

**With Description:**
```bash
python enhanced-capture.py output.json --with-description
```

**Without Description:**
```bash
python enhanced-capture.py output.json
```

### Testing

Run the test script:
```bash
python test-enhanced-capture.py
```

## Examples

### Example 1: Tutorial Creation

**Description:** "Installing Node.js on Windows"

**Captures:**
1. Download page
2. Installer welcome screen
3. Installation directory selection
4. Completion screen

**Result:** Single merged image showing all 4 steps vertically

### Example 2: Bug Report

**Description:** "Login button not working on mobile"

**Captures:**
1. Login screen
2. Error message
3. Console log

**Result:** 2x2 grid showing all evidence

### Example 3: Feature Demo

**Description:** "New dashboard layout"

**Captures:**
1. Full dashboard

**Result:** Single image (no merge needed)

## Advanced Features

### Custom Merge Layouts

For programmatic use, you can specify merge method:

```typescript
import { mergeImages } from "./enhanced-capture.js";

// Merge vertically
await mergeImages(imageBuffers, "vertical", "output.png");

// Merge in grid
await mergeImages(imageBuffers, "grid", "output.png");
```

### Python Image Merger CLI

Direct image merging:

```bash
python merge-images-cli.py image1.png image2.png image3.png \
  --output merged.png \
  --method auto \
  --spacing 10 \
  --background "#ffffff" \
  --description "My merged screenshot"
```

**Options:**
- `--method, -m`: vertical, horizontal, grid, auto (default: auto)
- `--spacing, -s`: Pixels between images (default: 10)
- `--background, -b`: Background color (default: #ffffff)
- `--description, -d`: Add description header

## File Structure

```
mcp-screencatch/
├── enhanced-capture.py        # Multi-capture overlay with description
├── image-merger.py            # Image merging utilities
├── merge-images-cli.py        # CLI for merging images
├── src/
│   └── enhanced-capture.ts    # TypeScript integration
└── test-enhanced-capture.py   # Test script
```

## Troubleshooting

### "No description provided"
- Description dialog was cancelled
- Capture proceeds without description
- Metadata will have empty description field

### "No regions captured"
- Pressed ESC without capturing anything
- Check that you pressed Enter or Ctrl+Enter after selecting

### Merged image looks wrong
- Try different merge method: vertical, horizontal, grid
- Adjust spacing parameter
- Captures may have very different sizes

### Multi-monitor issues
- Instruction box works across all monitors
- Can move it to any screen
- Virtual screen coordinates handled automatically

## Future Enhancements

Potential additions:
- ✨ OCR text extraction from captures
- ✨ Annotation tools (arrows, text, highlights)
- ✨ Video recording mode
- ✨ Cloud upload integration
- ✨ AI-powered smart cropping
- ✨ Template-based layouts
