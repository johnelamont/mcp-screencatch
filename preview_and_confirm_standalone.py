#!/usr/bin/env python3
"""
Preview window for standalone application
Shows merged image and allows recapture
"""

import sys
import tkinter as tk
from PIL import Image, ImageTk

class PreviewWindow:
    """Show preview of merged image with recapture option"""

    def __init__(self, image_path, description, capture_count):
        self.image_path = image_path
        self.description = description
        self.capture_count = capture_count
        self.recapture = False

        self.root = tk.Tk()
        self.root.title("Capture Preview")

        # Load and display image
        try:
            img = Image.open(image_path)

            # Resize if too large (max 1200x800)
            max_width = 1200
            max_height = 800

            if img.width > max_width or img.height > max_height:
                ratio = min(max_width / img.width, max_height / img.height)
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            self.photo = ImageTk.PhotoImage(img)

            # Create UI
            self.create_ui()

        except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)
            self.root.destroy()

    def create_ui(self):
        """Create the preview UI"""
        # Title frame
        title_frame = tk.Frame(self.root, bg='#f0f0f0', pady=10)
        title_frame.pack(fill=tk.X)

        title_text = f"Preview: {self.description}" if self.description else "Capture Preview"
        title_label = tk.Label(
            title_frame,
            text=title_text,
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack()

        count_label = tk.Label(
            title_frame,
            text=f"({self.capture_count} region{'s' if self.capture_count > 1 else ''} captured)",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#666'
        )
        count_label.pack()

        # Image frame with canvas and scrollbars
        image_frame = tk.Frame(self.root)
        image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas for image
        canvas = tk.Canvas(image_frame, bg='white')
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbars if needed
        v_scrollbar = tk.Scrollbar(image_frame, orient=tk.VERTICAL, command=canvas.yview)
        h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=canvas.xview)

        if self.photo.width() > 1200 or self.photo.height() > 800:
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            h_scrollbar.pack(fill=tk.X)
            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        canvas.configure(scrollregion=canvas.bbox(tk.ALL))

        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0', pady=10)
        button_frame.pack(fill=tk.X)

        # Buttons
        recapture_btn = tk.Button(
            button_frame,
            text="Recapture (Keep Description)",
            command=self.on_recapture,
            bg='#ff9800',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10
        )
        recapture_btn.pack(side=tk.LEFT, padx=10)

        keep_btn = tk.Button(
            button_frame,
            text="✓ Keep This Capture",
            command=self.on_keep,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10
        )
        keep_btn.pack(side=tk.RIGHT, padx=10)

        # Keyboard shortcuts
        self.root.bind('<Return>', lambda e: self.on_keep())
        self.root.bind('<r>', lambda e: self.on_recapture())
        self.root.bind('<Escape>', lambda e: self.on_keep())

        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def on_recapture(self):
        """User wants to recapture"""
        self.recapture = True
        self.root.destroy()

    def on_keep(self):
        """User wants to keep the capture"""
        self.recapture = False
        self.root.destroy()

    def show(self):
        """Show the window and return recapture decision"""
        self.root.mainloop()
        return self.recapture
