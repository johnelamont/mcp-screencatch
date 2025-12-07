#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple stitching capture - no hotkeys, just console prompts
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from PIL import ImageGrab
import tkinter as tk
from tkinter import simpledialog

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class SimpleCaptureOverlay:
    """Simple overlay for capturing ONE region"""

    def __init__(self):
        self.region = None
        self.cancelled = False

        # Multi-monitor support
        import ctypes
        user32 = ctypes.windll.user32
        virtual_x_min = user32.GetSystemMetrics(76)
        virtual_y_min = user32.GetSystemMetrics(77)
        virtual_width = user32.GetSystemMetrics(78)
        virtual_height = user32.GetSystemMetrics(79)

        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.geometry(f"{virtual_width}x{virtual_height}+{virtual_x_min}+{virtual_y_min}")

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
    print("\n" + "="*60)
    print("SIMPLE STITCHING CAPTURE")
    print("="*60)

    # Get description
    root = tk.Tk()
    root.withdraw()
    description = simpledialog.askstring(
        "Capture Description",
        "Enter description (or cancel to skip):",
        parent=root
    )
    root.destroy()

    output_dir = os.getcwd()
    captured_images = []

    print(f"\nDescription: {description or 'None'}")
    print("="*60)
    print("\nCapture workflow:")
    print("  1. Press Enter to start a capture")
    print("  2. Drag to select region, release mouse")
    print("  3. Repeat for overlapping regions")
    print("  4. Type 'done' when finished")
    print("="*60)

    while True:
        command = input("\nPress Enter to capture (or type 'done' to finish): ").strip().lower()

        if command == 'done':
            if not captured_images:
                print("No captures taken!")
                return
            break

        # Capture region
        print("Drag to select region...")
        overlay = SimpleCaptureOverlay()
        region = overlay.run()

        if region:
            # Immediately capture the screen region
            bbox = (
                region['x'],
                region['y'],
                region['x'] + region['width'],
                region['y'] + region['height']
            )
            img = ImageGrab.grab(bbox=bbox)
            captured_images.append(img)
            print(f"✓ Captured region {len(captured_images)}: {region['width']}x{region['height']}")
        else:
            print("Capture cancelled")

    # Stitch images
    print(f"\nProcessing {len(captured_images)} capture(s)...")

    from image_stitcher import ImageStitcher

    timestamp = datetime.now()
    year = timestamp.year
    month = str(timestamp.month).zfill(2)
    day = str(timestamp.day).zfill(2)
    hours = str(timestamp.hour).zfill(2)
    minutes = str(timestamp.minute).zfill(2)
    seconds = str(timestamp.second).zfill(2)
    filename = f"capture_{year}-{month}-{day}_{hours}{minutes}{seconds}.png"
    filepath = os.path.join(output_dir, filename)

    if len(captured_images) == 1:
        captured_images[0].save(filepath)
    else:
        print("Stitching images together by finding overlapping content...")
        stitched = ImageStitcher.stitch_images(captured_images)
        stitched.save(filepath)

    # Save metadata
    metadata = {
        'description': description or '',
        'timestamp': timestamp.isoformat(),
        'captures': len(captured_images),
        'merged': len(captured_images) > 1,
        'filepath': filepath
    }

    metadata_path = filepath.replace('.png', '.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "="*60)
    print("SUCCESS")
    print("="*60)
    print(f"Saved: {filepath}")
    if len(captured_images) > 1:
        print(f"Stitched {len(captured_images)} captures into panorama")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
