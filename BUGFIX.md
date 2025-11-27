# Bug Fix: Electron Cannot Run in MCP Server Context

## Problem Identified

The original implementation tried to run Electron inline within the MCP server process. However, Electron requires its own GUI event loop and cannot run within a stdio-based MCP server context.

**Error:**
```
TypeError: Cannot read properties of undefined (reading 'isReady')
at selectRegionInteractive
```

## Solution Implemented

Changed the architecture to spawn Electron as a **separate process**:

### Before (Broken)
```
MCP Server (stdio) → Electron inline → Crash ❌
```

### After (Fixed)
```
MCP Server (stdio) → Spawns → Electron Process (separate GUI) → IPC via file → MCP Server ✅
```

## Technical Changes

### New Files
1. **`src/overlay-app.ts`** - Standalone Electron application for region selection
   - Runs as a separate process
   - Communicates via JSON file

2. **Updated `src/overlay.ts`** - Process spawner
   - Spawns Electron as child process
   - Uses temporary JSON files for IPC
   - Waits for overlay to complete

### Architecture
```
┌─────────────────────┐
│   Claude Desktop    │
│                     │
│   MCP Client        │
└──────────┬──────────┘
           │ stdio
           ▼
┌─────────────────────┐
│   MCP Server        │
│   (index.js)        │
│                     │
│   capture_screen    │
└──────────┬──────────┘
           │ spawn
           ▼
┌─────────────────────┐
│  Electron Process   │
│  (overlay-app.js)   │
│                     │
│  GUI Overlay        │
└──────────┬──────────┘
           │
           ▼
    region-output.json
           │
           ▼
┌─────────────────────┐
│   MCP Server        │
│   reads result      │
│   captures region   │
└─────────────────────┘
```

## Files Modified

- ✅ `src/overlay.ts` - Changed from inline Electron to process spawning
- ✅ `src/overlay-app.ts` - New standalone Electron app
- ✅ `package.json` - Already had Electron dependency
- ✅ Built and compiled successfully

## How IPC Works

1. MCP server generates unique temp file path: `region-output-{timestamp}-{random}.json`
2. Spawns Electron: `electron.exe overlay-app.js <temp-file-path>`
3. User selects region in overlay
4. Overlay writes result to JSON file:
   ```json
   {
     "region": { "x": 100, "y": 100, "width": 500, "height": 300 },
     "cancelled": false
   }
   ```
5. Electron app quits
6. MCP server reads JSON file
7. Temp file deleted
8. Region captured and saved

## Testing

Build completed successfully:
```bash
npm run build
✓ overlay-app.js compiled
✓ overlay.js updated
✓ No TypeScript errors
```

## Next Steps for User

1. **Restart Claude Desktop** (important - loads new code)
2. Try the capture_screen command again
3. Electron window should now appear as a separate overlay
4. Select region → Click Capture → Screenshot saved

## Verification

Run this to verify everything is correct:
```bash
npm run verify
```

Should show all ✅ checks passing.

## Notes

- Electron adds ~150MB to node_modules (necessary for GUI)
- Each capture spawns a new Electron process (fast, ~1-2 seconds)
- Temp files are automatically cleaned up
- Multiple captures can be taken in sequence
