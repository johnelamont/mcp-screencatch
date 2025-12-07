#!/usr/bin/env python3
"""
Enhanced screen capture with description input and multi-capture support
"""

import sys
import json
import tkinter as tk
from tkinter import Canvas, simpledialog, messagebox
from PIL import Image
import io

class DescriptionDialog:
    """Simple dialog to get description from user"""
    def __init__(self):
        self.description = None
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window

    def get_description(self):
        """Show dialog and get description"""
        self.description = simpledialog.askstring(
            "Capture Description",
            "Enter a description for what you're about to capture:",
            parent=self.root
        )
        self.root.destroy()
        return self.description

class MultiCaptureOverlay:
    """Enhanced overlay supporting multiple captures in one session"""
    def __init__(self, output_file):
        self.output_file = output_file
        self.captures = []  # List of captured regions
        self.current_capture = 0

        self.root = tk.Tk()

        # Get the virtual screen dimensions (all monitors combined)
        self.root.update_idletasks()

        # Calculate total screen area covering all monitors
        try:
            import ctypes
            user32 = ctypes.windll.user32

            # Get the virtual screen dimensions
            x_min = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
            y_min = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
            x_max = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
            y_max = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN

            # Set window geometry to cover all monitors
            self.root.geometry(f"{x_max}x{y_max}+{x_min}+{y_min}")
            self.root.overrideredirect(True)

            self.virtual_x_offset = x_min
            self.virtual_y_offset = y_min
        except Exception as e:
            print(f"Warning: Could not detect multi-monitor setup: {e}", file=sys.stderr)
            self.root.attributes('-fullscreen', True)
            self.virtual_x_offset = 0
            self.virtual_y_offset = 0

        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-topmost', True)
        self.root.configure(background='black', cursor='crosshair')

        self.canvas = Canvas(self.root, cursor='crosshair', bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.region = None

        # Dragging state for instruction box
        self.drag_data = {'x': 0, 'y': 0, 'item': None}
        self.is_dragging_instructions = False

        # Instructions with background box
        try:
            primary_screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
            center_x = (primary_screen_width // 2) - self.virtual_x_offset
        except:
            center_x = self.canvas.winfo_screenwidth() // 2

        # Create dark background rectangle for instructions
        self.instructions_bg = self.canvas.create_rectangle(
            center_x - 450,
            10,
            center_x + 450,
            110,
            fill='#1a1a1a',
            outline='#00a8ff',
            width=3,
            tags='instructions'
        )

        self.instructions = self.canvas.create_text(
            center_x,
            60,
            text="Capture #1: Drag to select region.\n** Enter = Capture and CONTINUE **  |  Shift+Enter = Capture and FINISH  |  ESC = Cancel\n(Drag this box to move it)",
            fill='#ffffff',
            font=('Arial', 12, 'bold'),
            tags='instructions'
        )

        # Bind selection events to canvas first (lower priority)
        self.canvas.bind('<Button-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

        # Bind drag events to instruction elements (higher priority)
        self.canvas.tag_bind('instructions', '<Button-1>', self.on_instructions_press)
        self.canvas.tag_bind('instructions', '<B1-Motion>', self.on_instructions_drag)
        self.canvas.tag_bind('instructions', '<ButtonRelease-1>', self.on_instructions_release)

        # Keyboard shortcuts
        self.root.bind('<Return>', self.on_capture_continue)  # Enter = capture and continue
        self.root.bind('<Shift-Return>', self.on_capture)     # Shift+Enter = capture and finish
        self.root.bind('<Escape>', self.on_finish)

    def update_instructions(self):
        """Update instruction text based on current state"""
        count = len(self.captures) + 1
        text = f"Capture #{count}: Drag to select region.\n"
        text += "** Enter = Capture and CONTINUE **  |  Shift+Enter = Capture and FINISH  |  ESC = Cancel\n"
        text += "(Drag this box to move it)"
        self.canvas.itemconfig(self.instructions, text=text)

    def on_instructions_press(self, event):
        self.is_dragging_instructions = True
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y
        self.canvas.config(cursor='fleur')
        return "break"

    def on_instructions_drag(self, event):
        if self.is_dragging_instructions:
            delta_x = event.x - self.drag_data['x']
            delta_y = event.y - self.drag_data['y']
            self.canvas.move('instructions', delta_x, delta_y)
            self.drag_data['x'] = event.x
            self.drag_data['y'] = event.y
        return "break"

    def on_instructions_release(self, event):
        self.is_dragging_instructions = False
        self.canvas.config(cursor='crosshair')
        return "break"

    def on_press(self, event):
        # Check if clicking on instructions
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in items:
            if 'instructions' in self.canvas.gettags(item):
                return

        # Start region selection
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='#00a8ff', width=2
        )

    def on_drag(self, event):
        if self.is_dragging_instructions:
            return
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if self.is_dragging_instructions:
            return

        if self.rect:
            x1, y1, x2, y2 = self.canvas.coords(self.rect)
            canvas_x = int(min(x1, x2))
            canvas_y = int(min(y1, y2))
            width = int(abs(x2 - x1))
            height = int(abs(y2 - y1))

            self.region = {
                'x': canvas_x,
                'y': canvas_y,
                'width': width,
                'height': height
            }

            print(f"Region selected: {width}x{height} at ({canvas_x}, {canvas_y})", file=sys.stderr)

    def on_capture_continue(self, event=None):
        """Capture current region and continue"""
        if self._save_current_region():
            # Clear for next capture
            if self.rect:
                self.canvas.delete(self.rect)
                self.rect = None
            self.region = None
            self.start_x = None
            self.start_y = None
            self.update_instructions()
            print(f"Region {len(self.captures)} captured! Select another region or press ESC when done.", file=sys.stderr)

    def on_capture(self, event=None):
        """Capture current region and finish"""
        if self._save_current_region():
            self.on_finish()

    def show_preview_and_confirm(self):
        """Show preview of merged image and ask to recapture"""
        # This will be called after captures are saved
        # Return True to recapture, False to finish
        pass

    def _save_current_region(self):
        """Save the current region to captures list"""
        if not self.region:
            print("No region selected. Please drag to select a region first.", file=sys.stderr)
            return False

        if self.region['width'] <= 5 or self.region['height'] <= 5:
            print(f"Region too small ({self.region['width']}x{self.region['height']}). Please select a larger area.", file=sys.stderr)
            return False

        print(f"Saving region: {self.region['width']}x{self.region['height']} at ({self.region['x']}, {self.region['y']})", file=sys.stderr)
        self.captures.append(self.region.copy())
        return True

    def on_finish(self, event=None):
        """Finish capturing and save results"""
        print(f"Finishing with {len(self.captures)} capture(s)", file=sys.stderr)

        # Write all captures to output file
        with open(self.output_file, 'w') as f:
            json.dump({
                'captures': self.captures,
                'count': len(self.captures),
                'cancelled': len(self.captures) == 0,
                'show_preview': True  # Flag to show preview after merge
            }, f)

        self.root.destroy()

    def run(self):
        self.root.mainloop()

def main():
    if len(sys.argv) < 2:
        print("Usage: enhanced-capture.py <output_file> [--with-description]", file=sys.stderr)
        sys.exit(1)

    output_file = sys.argv[1]
    with_description = '--with-description' in sys.argv

    description = None
    if with_description:
        # Show description dialog
        dialog = DescriptionDialog()
        description = dialog.get_description()

        if not description:
            print("No description provided, cancelling capture.", file=sys.stderr)
            with open(output_file, 'w') as f:
                json.dump({'cancelled': True, 'reason': 'no_description'}, f)
            sys.exit(0)

        print(f"Description: {description}", file=sys.stderr)

    # Run the multi-capture overlay
    app = MultiCaptureOverlay(output_file)
    app.run()

    # If description was provided, add it to the output
    if with_description and description:
        with open(output_file, 'r') as f:
            data = json.load(f)
        data['description'] = description
        with open(output_file, 'w') as f:
            json.dump(data, f)

if __name__ == '__main__':
    main()
