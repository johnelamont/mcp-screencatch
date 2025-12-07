#!/usr/bin/env python3
"""
Image merging utilities for combining multiple screenshots
"""

from PIL import Image, ImageDraw, ImageFont
import sys
from typing import List, Tuple

class ImageMerger:
    """Merge multiple images into a single composite"""

    @staticmethod
    def merge_vertical(images: List[Image.Image], spacing: int = 10, background_color: str = '#ffffff') -> Image.Image:
        """Stack images vertically with spacing"""
        if not images:
            raise ValueError("No images to merge")

        if len(images) == 1:
            return images[0]

        # Calculate total dimensions
        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images) + spacing * (len(images) - 1)

        # Create new image
        merged = Image.new('RGB', (max_width, total_height), background_color)

        # Paste images
        y_offset = 0
        for img in images:
            # Center horizontally
            x_offset = (max_width - img.width) // 2
            merged.paste(img, (x_offset, y_offset))
            y_offset += img.height + spacing

        return merged

    @staticmethod
    def merge_horizontal(images: List[Image.Image], spacing: int = 10, background_color: str = '#ffffff') -> Image.Image:
        """Stack images horizontally with spacing"""
        if not images:
            raise ValueError("No images to merge")

        if len(images) == 1:
            return images[0]

        # Calculate total dimensions
        total_width = sum(img.width for img in images) + spacing * (len(images) - 1)
        max_height = max(img.height for img in images)

        # Create new image
        merged = Image.new('RGB', (total_width, max_height), background_color)

        # Paste images
        x_offset = 0
        for img in images:
            # Center vertically
            y_offset = (max_height - img.height) // 2
            merged.paste(img, (x_offset, y_offset))
            x_offset += img.width + spacing

        return merged

    @staticmethod
    def merge_grid(images: List[Image.Image], cols: int = None, spacing: int = 10, background_color: str = '#ffffff') -> Image.Image:
        """Arrange images in a grid layout"""
        if not images:
            raise ValueError("No images to merge")

        if len(images) == 1:
            return images[0]

        # Auto-calculate grid dimensions
        if cols is None:
            # Try to make roughly square
            cols = int(len(images) ** 0.5) + (1 if len(images) ** 0.5 % 1 > 0 else 0)

        rows = (len(images) + cols - 1) // cols  # Ceiling division

        # Find max dimensions for each cell
        max_cell_width = max(img.width for img in images)
        max_cell_height = max(img.height for img in images)

        # Calculate total dimensions
        total_width = max_cell_width * cols + spacing * (cols - 1)
        total_height = max_cell_height * rows + spacing * (rows - 1)

        # Create new image
        merged = Image.new('RGB', (total_width, total_height), background_color)

        # Paste images
        for idx, img in enumerate(images):
            row = idx // cols
            col = idx % cols

            x_offset = col * (max_cell_width + spacing) + (max_cell_width - img.width) // 2
            y_offset = row * (max_cell_height + spacing) + (max_cell_height - img.height) // 2

            merged.paste(img, (x_offset, y_offset))

        return merged

    @staticmethod
    def merge_auto(images: List[Image.Image], spacing: int = 10, background_color: str = '#ffffff') -> Image.Image:
        """Automatically choose best layout based on image count and aspect ratios"""
        if not images:
            raise ValueError("No images to merge")

        if len(images) == 1:
            return images[0]

        if len(images) == 2:
            # For 2 images, decide based on aspect ratio
            avg_aspect = sum(img.width / img.height for img in images) / len(images)
            if avg_aspect > 1.5:  # Wide images - stack vertically
                return ImageMerger.merge_vertical(images, spacing, background_color)
            else:  # Tall or square - stack horizontally
                return ImageMerger.merge_horizontal(images, spacing, background_color)

        elif len(images) <= 4:
            # For 3-4 images, use grid
            return ImageMerger.merge_grid(images, cols=2, spacing=spacing, background_color=background_color)

        else:
            # For 5+ images, use grid with auto columns
            return ImageMerger.merge_grid(images, spacing=spacing, background_color=background_color)

    @staticmethod
    def add_description_header(image: Image.Image, description: str, padding: int = 20, background_color: str = '#f0f0f0') -> Image.Image:
        """Add a description header to the image"""
        try:
            # Try to use a nice font, fall back to default if not available
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        # Create a temporary image to measure text size
        temp_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(temp_img)

        # Measure text
        bbox = draw.textbbox((0, 0), description, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Create new image with header space
        header_height = text_height + padding * 2
        new_image = Image.new('RGB', (image.width, image.height + header_height), background_color)

        # Draw description
        draw = ImageDraw.Draw(new_image)
        text_x = (image.width - text_width) // 2
        text_y = padding
        draw.text((text_x, text_y), description, fill='#000000', font=font)

        # Paste original image below header
        new_image.paste(image, (0, header_height))

        return new_image

def main():
    """Test the image merger"""
    print("Image merger module loaded successfully")
    print("Available merge methods: vertical, horizontal, grid, auto")

if __name__ == '__main__':
    main()
