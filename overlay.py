#!/usr/bin/env python3
"""
Simple screen region selector using tkinter
More reliable than Electron for this use case
"""

import sys
import json
import tkinter as tk
from tkinter import Canvas

class ScreenCapture:
    def __init__(self, output_file):
        self.output_file = output_file
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-topmost', True)
        self.root.configure(background='black', cursor='crosshair')

        self.canvas = Canvas(self.root, cursor='crosshair', bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.region = None

        # Instructions with background box for better visibility
        screen_width = self.root.winfo_screenwidth()

        # Create dark background rectangle for instructions
        self.instructions_bg = self.canvas.create_rectangle(
            screen_width // 2 - 400,
            10,
            screen_width // 2 + 400,
            70,
            fill='#1a1a1a',
            outline='#00a8ff',
            width=3
        )

        self.instructions = self.canvas.create_text(
            screen_width // 2,
            40,
            text="Click and drag to select region. Press Enter to capture, ESC to cancel.",
            fill='#ffffff',
            font=('Arial', 16, 'bold')
        )

        self.canvas.bind('<Button-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.root.bind('<Return>', self.on_capture)
        self.root.bind('<Escape>', self.on_cancel)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='#00a8ff', width=2
        )

    def on_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if self.rect:
            x1, y1, x2, y2 = self.canvas.coords(self.rect)
            self.region = {
                'x': int(min(x1, x2)),
                'y': int(min(y1, y2)),
                'width': int(abs(x2 - x1)),
                'height': int(abs(y2 - y1))
            }

    def on_capture(self, event=None):
        if self.region and self.region['width'] > 5 and self.region['height'] > 5:
            with open(self.output_file, 'w') as f:
                json.dump({'region': self.region, 'cancelled': False}, f)
            self.root.destroy()

    def on_cancel(self, event=None):
        with open(self.output_file, 'w') as f:
            json.dump({'region': None, 'cancelled': True}, f)
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: overlay.py <output_file>", file=sys.stderr)
        sys.exit(1)

    output_file = sys.argv[1]
    app = ScreenCapture(output_file)
    app.run()
