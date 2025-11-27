#!/usr/bin/env node
/**
 * Standalone Electron app for screen region selection
 * Runs as a separate process from the MCP server
 */

import electron from "electron";
import { writeFileSync } from "fs";

const { app, BrowserWindow, screen, ipcMain } = electron;

interface Region {
  x: number;
  y: number;
  width: number;
  height: number;
}

let overlayWindow: InstanceType<typeof BrowserWindow> | null = null;
const outputFile = process.argv[2] || "region-output.json";

async function createOverlay(): Promise<void> {
  // Create a window that spans all displays
  overlayWindow = new BrowserWindow({
    fullscreen: true,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  // Open DevTools for debugging (comment out in production)
  // overlayWindow.webContents.openDevTools();

  // Load the selection UI
  const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      cursor: crosshair;
      user-select: none;
      overflow: hidden;
    }

    #overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.3);
    }

    #selection {
      position: fixed;
      border: 2px solid #00a8ff;
      background: rgba(0, 168, 255, 0.1);
      box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.3);
      display: none;
    }

    #instructions {
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 12px 24px;
      border-radius: 6px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 14px;
      z-index: 1000;
    }

    #buttons {
      position: fixed;
      bottom: 20px;
      right: 20px;
      display: none;
      gap: 10px;
      z-index: 1000;
    }

    .btn {
      padding: 10px 20px;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .btn-capture {
      background: #00a8ff;
      color: white;
    }

    .btn-capture:hover {
      background: #0077cc;
    }

    .btn-cancel {
      background: #e74c3c;
      color: white;
    }

    .btn-cancel:hover {
      background: #c0392b;
    }
  </style>
</head>
<body>
  <div id="overlay"></div>
  <div id="selection"></div>
  <div id="instructions">Click and drag to select a region. Press ESC to cancel.</div>
  <div id="buttons">
    <button class="btn btn-capture" id="captureBtn">Capture</button>
    <button class="btn btn-cancel" id="cancelBtn">Cancel</button>
  </div>

  <script>
    const { ipcRenderer } = require('electron');

    let startX = 0, startY = 0;
    let isDrawing = false;
    const selection = document.getElementById('selection');
    const buttons = document.getElementById('buttons');
    const instructions = document.getElementById('instructions');
    const captureBtn = document.getElementById('captureBtn');
    const cancelBtn = document.getElementById('cancelBtn');

    document.addEventListener('mousedown', (e) => {
      isDrawing = true;
      startX = e.clientX;
      startY = e.clientY;
      selection.style.left = startX + 'px';
      selection.style.top = startY + 'px';
      selection.style.width = '0px';
      selection.style.height = '0px';
      selection.style.display = 'block';
      buttons.style.display = 'none';
    });

    document.addEventListener('mousemove', (e) => {
      if (!isDrawing) return;

      const currentX = e.clientX;
      const currentY = e.clientY;

      const width = Math.abs(currentX - startX);
      const height = Math.abs(currentY - startY);
      const left = Math.min(startX, currentX);
      const top = Math.min(startY, currentY);

      selection.style.left = left + 'px';
      selection.style.top = top + 'px';
      selection.style.width = width + 'px';
      selection.style.height = height + 'px';
    });

    document.addEventListener('mouseup', (e) => {
      if (!isDrawing) return;
      isDrawing = false;

      const width = parseInt(selection.style.width);
      const height = parseInt(selection.style.height);

      if (width > 5 && height > 5) {
        buttons.style.display = 'flex';
        instructions.textContent = 'Click Capture to save, or press ESC to cancel.';
      } else {
        selection.style.display = 'none';
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        cancelBtn.click();
      } else if (e.key === 'Enter') {
        captureBtn.click();
      }
    });

    // Set up button click handlers
    captureBtn.addEventListener('click', () => {
      try {
        const rect = selection.getBoundingClientRect();
        const region = {
          x: Math.round(rect.left),
          y: Math.round(rect.top),
          width: Math.round(rect.width),
          height: Math.round(rect.height)
        };
        console.log('Sending region:', region);
        ipcRenderer.send('region-selected', region);
      } catch (error) {
        console.error('Error in capture():', error);
        alert('Error capturing region: ' + error.message);
      }
    });

    cancelBtn.addEventListener('click', () => {
      try {
        console.log('Sending cancel');
        ipcRenderer.send('region-cancelled');
      } catch (error) {
        console.error('Error in cancel():', error);
      }
    });
  </script>
</body>
</html>
  `;

  // Set up IPC handlers BEFORE loading the window
  // Handle region selection
  ipcMain.once("region-selected", (event, region: Region) => {
    console.error("IPC: Received region-selected:", region);
    console.error("Writing to file:", outputFile);
    try {
      writeFileSync(outputFile, JSON.stringify({ region, cancelled: false }));
      console.error("File written successfully");
    } catch (error) {
      console.error("Error writing file:", error);
    }
    if (overlayWindow) {
      overlayWindow.close();
    }
    setTimeout(() => app.quit(), 100);
  });

  // Handle cancellation
  ipcMain.once("region-cancelled", () => {
    console.error("IPC: Received region-cancelled");
    console.error("Writing to file:", outputFile);
    try {
      writeFileSync(outputFile, JSON.stringify({ region: null, cancelled: true }));
      console.error("File written successfully");
    } catch (error) {
      console.error("Error writing file:", error);
    }
    if (overlayWindow) {
      overlayWindow.close();
    }
    setTimeout(() => app.quit(), 100);
  });

  // Handle window close
  overlayWindow.on("closed", () => {
    overlayWindow = null;
    setTimeout(() => app.quit(), 100);
  });

  // Now load the window
  await overlayWindow.loadURL(
    `data:text/html;charset=utf-8,${encodeURIComponent(htmlContent)}`
  );
}

// Initialize app
app.whenReady().then(createOverlay);

app.on("window-all-closed", () => {
  app.quit();
});
