#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hotkey-based screen capture - simpler approach
Press a hotkey to capture each region, no persistent overlay
"""

import sys
import json
import argparse
import os
from pathlib import Path
from datetime import datetime
from PIL import ImageGrab
import tkinter as tk
from tkinter import simpledialog
import keyboard  # pip install keyboard

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class HotkeyCapture:
    def __init__(self, output_dir, description=None):
        self.output_dir = output_dir
        self.description = description
        self.captured_images = []  # Store actual images, not just regions
        self.capture_count = 0

    def capture_region(self):
        """Show overlay, capture one region, then hide overlay"""
        print(f"\n>>> Press ESC to cancel, or drag to select region <<<", file=sys.stderr)

        # Create overlay just for this one capture
        overlay = SingleCaptureOverlay()
        region = overlay.run()

        if region:
            # Immediately capture the screen region while it's still there
            bbox = (
                region['x'],
                region['y'],
                region['x'] + region['width'],
                region['y'] + region['height']
            )
            img = ImageGrab.grab(bbox=bbox)
            self.captured_images.append(img)
            self.capture_count += 1
            print(f"✓ Captured region {self.capture_count}: {region['width']}x{region['height']}", file=sys.stderr)
            return True
        else:
            print("Capture cancelled", file=sys.stderr)
            return False

    def finish(self):
        """Merge and save all captures"""
        if not self.captured_images:
            print("No captures to save", file=sys.stderr)
            return None

        print(f"\nProcessing {len(self.captured_images)} capture(s)...", file=sys.stderr)

        # Import image stitcher
        from image_stitcher import ImageStitcher

        # Generate filename
        timestamp = datetime.now()
        year = timestamp.year
        month = str(timestamp.month).zfill(2)
        day = str(timestamp.day).zfill(2)
        hours = str(timestamp.hour).zfill(2)
        minutes = str(timestamp.minute).zfill(2)
        seconds = str(timestamp.second).zfill(2)
        filename = f"capture_{year}-{month}-{day}_{hours}{minutes}{seconds}.png"
        filepath = os.path.join(self.output_dir, filename)

        # Save or stitch
        if len(self.captured_images) == 1:
            self.captured_images[0].save(filepath)
        else:
            print(f"Stitching images together by finding overlapping content...", file=sys.stderr)
            stitched = ImageStitcher.stitch_images(self.captured_images)
            stitched.save(filepath)

        # Save metadata
        metadata = {
            'description': self.description or '',
            'timestamp': timestamp.isoformat(),
            'captures': len(self.captured_images),
            'merged': len(self.captured_images) > 1,
            'filepath': filepath
        }

        metadata_path = filepath.replace('.png', '.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Saved to: {filepath}", file=sys.stderr)
        if len(self.captured_images) > 1:
            print(f"✓ Stitched {len(self.captured_images)} captures into panorama", file=sys.stderr)

        return filepath


class SingleCaptureOverlay:
    """Simple overlay for capturing ONE region"""

    def __init__(self):
        self.region = None
        self.cancelled = False

        # Multi-monitor support
        import ctypes
        user32 = ctypes.windll.user32
        self.virtual_x_min = user32.GetSystemMetrics(76)
        self.virtual_y_min = user32.GetSystemMetrics(77)
        self.virtual_width = user32.GetSystemMetrics(78)
        self.virtual_height = user32.GetSystemMetrics(79)

        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.geometry(f"{self.virtual_width}x{self.virtual_height}+{self.virtual_x_min}+{self.virtual_y_min}")

        self.canvas = tk.Canvas(self.root, cursor='cross', bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None

        # Bind events
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.root.bind('<Escape>', self.on_cancel)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='#4a9eff', width=2
        )

    def on_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if self.rect and self.start_x is not None:
            coords = self.canvas.coords(self.rect)
            x1, y1, x2, y2 = coords
            canvas_x = int(min(x1, x2))
            canvas_y = int(min(y1, y2))
            width = int(abs(x2 - x1))
            height = int(abs(y2 - y1))

            if width > 10 and height > 10:
                self.region = {
                    'x': canvas_x,
                    'y': canvas_y,
                    'width': width,
                    'height': height
                }
                self.root.destroy()

    def on_cancel(self, event):
        self.cancelled = True
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        if self.cancelled or not self.region:
            return None
        return self.region


def main():
    parser = argparse.ArgumentParser(
        description='Hotkey-based screen capture',
        epilog='''
Workflow:
  1. Enter description (optional)
  2. Press F9 to capture each region
  3. Drag to select region, release mouse
  4. Press F9 again for next region
  5. Press F10 when done to merge and save
        '''
    )

    parser.add_argument('--output-dir', '-o', default=os.getcwd())
    parser.add_argument('--no-description', action='store_true')

    args = parser.parse_args()

    # Get description
    description = None
    if not args.no_description:
        root = tk.Tk()
        root.withdraw()
        description = simpledialog.askstring(
            "Capture Description",
            "Enter description (or cancel to skip):",
            parent=root
        )
        root.destroy()

    # Create capture manager
    capture_mgr = HotkeyCapture(args.output_dir, description)

    print("\n" + "="*60, file=sys.stderr)
    print("HOTKEY SCREEN CAPTURE", file=sys.stderr)
    print("="*60, file=sys.stderr)
    if description:
        print(f"Description: {description}", file=sys.stderr)
    print(f"\nPress F9 to capture a region", file=sys.stderr)
    print(f"Press F10 to finish and save", file=sys.stderr)
    print(f"Press ESC during capture to cancel", file=sys.stderr)
    print("="*60, file=sys.stderr)

    def on_capture_hotkey():
        capture_mgr.capture_region()
        print(f"\nReady for next capture (F9) or finish (F10)", file=sys.stderr)

    def on_finish_hotkey():
        print(f"\nFinishing...", file=sys.stderr)
        filepath = capture_mgr.finish()
        if filepath:
            print("\n" + "="*60, file=sys.stderr)
            print("SUCCESS", file=sys.stderr)
            print("="*60, file=sys.stderr)
            print(f"Saved: {filepath}", file=sys.stderr)
            print("="*60 + "\n", file=sys.stderr)
        sys.exit(0)

    # Register hotkeys
    keyboard.add_hotkey('f9', on_capture_hotkey)
    keyboard.add_hotkey('f10', on_finish_hotkey)

    # Wait for hotkeys
    keyboard.wait('f10')


if __name__ == '__main__':
    main()
