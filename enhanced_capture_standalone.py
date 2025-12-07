#!/usr/bin/env python3
"""
Enhanced capture functionality for standalone use
Refactored from enhanced-capture.py for standalone CLI
"""

import sys
import json
import tkinter as tk
from tkinter import simpledialog
import ctypes

class DescriptionDialog:
    """Simple dialog to get capture description"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.description = None

    def get_description(self):
        """Show dialog and get description from user"""
        self.description = simpledialog.askstring(
            "Capture Description",
            "Enter a description for what you're about to capture:\n\n(This will be saved with your screenshots)",
            parent=self.root
        )

        self.root.destroy()
        return self.description


class MultiCaptureOverlay:
    """
    Multi-capture overlay with moveable instructions
    Supports multiple monitors and multiple region captures
    """

    def __init__(self, output_file):
        self.output_file = output_file
        self.captures = []
        self.current_rect = None
        self.start_x = None
        self.start_y = None
        self.cancelled = False

        # Draggable instructions state
        self.is_dragging_instructions = False
        self.drag_data = {'x': 0, 'y': 0}

        # Multi-monitor support using Windows API
        user32 = ctypes.windll.user32
        self.virtual_x_min = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
        self.virtual_y_min = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
        self.virtual_width = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
        self.virtual_height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN

        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)

        # Set geometry to cover all monitors
        self.root.geometry(f"{self.virtual_width}x{self.virtual_height}+{self.virtual_x_min}+{self.virtual_y_min}")

        self.canvas = tk.Canvas(
            self.root,
            cursor='cross',
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Create moveable instruction box
        self.create_instructions()

        # Bind events
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

        self.root.bind('<Return>', self.on_capture_continue)
        self.root.bind('<Shift-Return>', self.on_capture)
        self.root.bind('<Escape>', self.on_finish)

    def create_instructions(self):
        """Create moveable instruction box"""
        # Initial position - top right
        x = self.virtual_width - 420
        y = 20

        # Background box with drag tag
        self.inst_bg = self.canvas.create_rectangle(
            x, y, x + 400, y + 180,
            fill='#2d2d2d',
            outline='#4a9eff',
            width=2,
            tags='instructions'
        )

        # Title
        self.inst_title = self.canvas.create_text(
            x + 200, y + 20,
            text='Screen Capture - Multi Region',
            fill='#4a9eff',
            font=('Arial', 14, 'bold'),
            tags='instructions'
        )

        # Instructions text
        instructions = [
            'Drag to select a region',
            '',
            '** Enter = Capture and CONTINUE **',
            'Shift+Enter = Capture and FINISH',
            'ESC = Finish (save all captures)',
            '',
            'Drag this box to move it out of the way'
        ]

        y_offset = y + 50
        self.inst_texts = []
        for i, line in enumerate(instructions):
            text = self.canvas.create_text(
                x + 200, y_offset + (i * 18),
                text=line,
                fill='white' if '**' not in line else '#4a9eff',
                font=('Arial', 10, 'bold' if '**' in line else 'normal'),
                tags='instructions'
            )
            self.inst_texts.append(text)

        # Capture counter
        self.inst_counter = self.canvas.create_text(
            x + 200, y + 160,
            text='Captures: 0',
            fill='#4CAF50',
            font=('Arial', 11, 'bold'),
            tags='instructions'
        )

        # Bind drag events to instructions tag
        self.canvas.tag_bind('instructions', '<ButtonPress-1>', self.on_instructions_press)
        self.canvas.tag_bind('instructions', '<B1-Motion>', self.on_instructions_drag)
        self.canvas.tag_bind('instructions', '<ButtonRelease-1>', self.on_instructions_release)

    def on_instructions_press(self, event):
        """Start dragging instruction box"""
        self.is_dragging_instructions = True
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y
        self.canvas.config(cursor='fleur')
        return "break"  # Stop event propagation

    def on_instructions_drag(self, event):
        """Drag instruction box"""
        if self.is_dragging_instructions:
            dx = event.x - self.drag_data['x']
            dy = event.y - self.drag_data['y']
            self.canvas.move('instructions', dx, dy)
            self.drag_data['x'] = event.x
            self.drag_data['y'] = event.y
            return "break"

    def on_instructions_release(self, event):
        """Stop dragging instruction box"""
        if self.is_dragging_instructions:
            self.is_dragging_instructions = False
            self.canvas.config(cursor='cross')
            return "break"

    def update_counter(self):
        """Update capture counter display"""
        self.canvas.itemconfig(
            self.inst_counter,
            text=f'Captures: {len(self.captures)}'
        )

    def restore_overlay_once(self, event):
        """Restore overlay when any key is pressed after hiding"""
        # Unbind this one-time handler
        self.root.unbind('<KeyPress>')

        # Rebind normal key handlers
        self.root.bind('<Return>', self.on_capture_continue)
        self.root.bind('<Shift-Return>', self.on_capture)
        self.root.bind('<Escape>', self.on_finish)

        # Show overlay again - restore fullscreen and deiconify
        self.root.deiconify()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        print(f"   Overlay restored - drag to select next region", file=sys.stderr)

    def on_press(self, event):
        """Start drawing selection rectangle"""
        if self.is_dragging_instructions:
            return

        # Check if clicking on instructions
        overlapping = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if any('instructions' in self.canvas.gettags(item) for item in overlapping):
            return

        self.start_x = event.x
        self.start_y = event.y

        if self.current_rect:
            self.canvas.delete(self.current_rect)

        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='#4a9eff',
            width=2
        )

    def on_drag(self, event):
        """Update selection rectangle"""
        if self.is_dragging_instructions:
            return

        if self.current_rect and self.start_x is not None:
            self.canvas.coords(
                self.current_rect,
                self.start_x, self.start_y,
                event.x, event.y
            )

    def on_release(self, event):
        """Finish drawing selection rectangle"""
        if self.is_dragging_instructions:
            return

        # Keep the rectangle visible for user feedback
        pass

    def on_capture_continue(self, event):
        """Capture current region and continue (Enter key)"""
        if self.current_rect and self.start_x is not None:
            coords = self.canvas.coords(self.current_rect)

            x1, y1, x2, y2 = coords
            canvas_x = int(min(x1, x2))
            canvas_y = int(min(y1, y2))
            width = int(abs(x2 - x1))
            height = int(abs(y2 - y1))

            if width > 10 and height > 10:
                # Canvas coordinates are already in virtual screen space
                self.captures.append({
                    'x': canvas_x,
                    'y': canvas_y,
                    'width': width,
                    'height': height
                })

                self.update_counter()

                # Change current rectangle to green to show it's been captured
                self.canvas.itemconfig(self.current_rect, outline='#4CAF50', width=2)

                # Reset for next capture
                self.current_rect = None
                self.start_x = None
                self.start_y = None

                print(f"✓ Captured region {len(self.captures)}: {width}x{height} at ({canvas_x}, {canvas_y})", file=sys.stderr)
                print(f"   Drag to select next region, or press Shift+Enter to finish", file=sys.stderr)

    def on_capture(self, event):
        """Capture current region and finish (Shift+Enter)"""
        self.on_capture_continue(event)  # Capture current region
        self.on_finish(event)  # Then finish

    def on_finish(self, event=None):
        """Finish and save all captures"""
        result = {
            'captures': self.captures,
            'count': len(self.captures),
            'cancelled': len(self.captures) == 0
        }

        with open(self.output_file, 'w') as f:
            json.dump(result, f, indent=2)

        self.root.destroy()

    def run(self):
        """Show overlay and wait for captures"""
        self.root.mainloop()


def merge_and_save(regions, output_dir, description=None, merge_method='auto', spacing=10, recapture_iteration=0):
    """
    Capture screen regions and merge/save them

    Args:
        regions: List of region dicts with x, y, width, height
        output_dir: Directory to save output
        description: Optional description text
        merge_method: How to merge multiple captures
        spacing: Spacing between merged images
        recapture_iteration: Recapture attempt number

    Returns:
        (filepath, metadata) tuple
    """
    from PIL import ImageGrab
    import os
    from datetime import datetime
    from pathlib import Path

    # Import image merger
    from image_merger import ImageMerger

    # Capture individual regions
    images = []
    for region in regions:
        # PIL ImageGrab uses screen coordinates directly
        bbox = (
            region['x'],
            region['y'],
            region['x'] + region['width'],
            region['y'] + region['height']
        )
        img = ImageGrab.grab(bbox=bbox)
        images.append(img)

    # Generate filename
    timestamp = datetime.now()
    year = timestamp.year
    month = str(timestamp.month).zfill(2)
    day = str(timestamp.day).zfill(2)
    hours = str(timestamp.hour).zfill(2)
    minutes = str(timestamp.minute).zfill(2)
    seconds = str(timestamp.second).zfill(2)
    filename = f"capture_{year}-{month}-{day}_{hours}{minutes}{seconds}.png"
    filepath = os.path.join(output_dir, filename)

    # Save or merge images
    if len(images) == 1:
        images[0].save(filepath)
    else:
        # Merge multiple images
        merged = None
        if merge_method == 'vertical':
            merged = ImageMerger.merge_vertical(images, spacing)
        elif merge_method == 'horizontal':
            merged = ImageMerger.merge_horizontal(images, spacing)
        elif merge_method == 'grid':
            merged = ImageMerger.merge_grid(images, spacing=spacing)
        else:  # auto
            merged = ImageMerger.merge_auto(images, spacing)

        merged.save(filepath)

    # Save metadata
    metadata = {
        'description': description or '',
        'timestamp': timestamp.isoformat(),
        'captures': len(regions),
        'merged': len(regions) > 1,
        'filepath': filepath,
        'regions': regions,
        'recapture_iteration': recapture_iteration,
        'merge_method': merge_method
    }

    metadata_path = filepath.replace('.png', '.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    return filepath, metadata
