#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI-based stitching capture with control panel
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from PIL import ImageGrab
import tkinter as tk
from tkinter import ttk

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


class SimpleCaptureOverlay:
    """Simple overlay for capturing ONE region"""

    def __init__(self, parent=None):
        self.region = None
        self.cancelled = False

        # Multi-monitor support
        import ctypes
        user32 = ctypes.windll.user32
        virtual_x_min = user32.GetSystemMetrics(76)
        virtual_y_min = user32.GetSystemMetrics(77)
        virtual_width = user32.GetSystemMetrics(78)
        virtual_height = user32.GetSystemMetrics(79)

        # Use Toplevel if parent exists, otherwise create new Tk
        if parent:
            self.root = tk.Toplevel(parent)
        else:
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
        # Use wait_window for Toplevel, mainloop for standalone Tk
        if isinstance(self.root, tk.Toplevel):
            self.root.wait_window()
        else:
            self.root.mainloop()

        if self.cancelled or not self.region:
            return None
        return self.region


class ControlPanel:
    """Persistent control panel with buttons"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Capture Control")
        self.root.attributes('-topmost', True)

        # Make window not resizable
        self.root.resizable(False, False)

        # Data
        self.captured_images = []
        self.system = tk.StringVar()
        self.name = tk.StringVar()
        self.description = tk.StringVar()

        # Build UI
        self.build_ui()

    def build_ui(self):
        """Build the control panel UI"""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # System field
        ttk.Label(main_frame, text="System:").grid(row=0, column=0, sticky=tk.W, pady=5)
        system_entry = ttk.Entry(main_frame, textvariable=self.system, width=40)
        system_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # Name field
        ttk.Label(main_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(main_frame, textvariable=self.name, width=40)
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Description field
        ttk.Label(main_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5)
        desc_entry = ttk.Entry(main_frame, textvariable=self.description, width=40)
        desc_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)

        # Capture count label
        self.count_label = ttk.Label(main_frame, text="Captures: 0", font=('Arial', 11, 'bold'))
        self.count_label.grid(row=4, column=0, columnspan=2, pady=10)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        # Capture button (large, green)
        self.capture_btn = tk.Button(
            button_frame,
            text="CAPTURE",
            command=self.capture,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 14, 'bold'),
            width=15,
            height=2
        )
        self.capture_btn.pack(side=tk.LEFT, padx=5)

        # Done button (large, blue)
        self.done_btn = tk.Button(
            button_frame,
            text="DONE",
            command=self.done,
            bg='#2196F3',
            fg='white',
            font=('Arial', 14, 'bold'),
            width=15,
            height=2
        )
        self.done_btn.pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground='green')
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)

    def update_count(self):
        """Update capture count display"""
        self.count_label.config(text=f"Captures: {len(self.captured_images)}")

    def capture(self):
        """Trigger a capture"""
        self.status_label.config(text="Drag to select region...", foreground='blue')
        self.root.update()

        # Hide control panel temporarily
        self.root.withdraw()

        # Show capture overlay (pass parent to create Toplevel)
        overlay = SimpleCaptureOverlay(parent=self.root)
        region = overlay.run()

        # Give time for overlay to fully disappear from screen
        import time
        time.sleep(0.1)

        if region:
            # Capture the screen region after overlay is gone
            bbox = (
                region['x'],
                region['y'],
                region['x'] + region['width'],
                region['y'] + region['height']
            )
            img = ImageGrab.grab(bbox=bbox)
            self.captured_images.append(img)

        # Restore control panel
        self.root.deiconify()

        if region:
            self.update_count()
            self.status_label.config(
                text=f"✓ Captured {region['width']}x{region['height']}",
                foreground='green'
            )
        else:
            self.status_label.config(text="Capture cancelled", foreground='orange')

    def done(self):
        """Finish and save captures"""
        if not self.captured_images:
            self.status_label.config(text="No captures to save!", foreground='red')
            return

        self.status_label.config(text="Processing...", foreground='blue')
        self.root.update()

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
        filepath = os.path.join(os.getcwd(), filename)

        # Save or stitch
        if len(self.captured_images) == 1:
            self.captured_images[0].save(filepath)
        else:
            stitched = ImageStitcher.stitch_images(self.captured_images)
            stitched.save(filepath)

        # Save metadata
        metadata = {
            'system': self.system.get(),
            'name': self.name.get(),
            'description': self.description.get(),
            'timestamp': timestamp.isoformat(),
            'captures': len(self.captured_images),
            'merged': len(self.captured_images) > 1,
            'filepath': filepath
        }

        metadata_path = filepath.replace('.png', '.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        self.status_label.config(
            text=f"✓ Saved to {os.path.basename(filepath)}",
            foreground='green'
        )

        # Close after short delay
        self.root.after(2000, self.root.destroy)

    def run(self):
        """Run the control panel"""
        self.root.mainloop()


def main():
    print("\n" + "="*60)
    print("GUI SCREEN CAPTURE")
    print("="*60)
    print("\nControl panel opening...")
    print("Use the CAPTURE button to capture regions")
    print("Click DONE when finished")
    print("="*60 + "\n")

    panel = ControlPanel()
    panel.run()


if __name__ == '__main__':
    main()
