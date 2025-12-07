#!/usr/bin/env python3
"""
CLI tool for merging images
"""

import sys
import argparse
from PIL import Image
from pathlib import Path
from os.path import dirname, join, abspath

# Add current directory to path for imports
sys.path.insert(0, dirname(abspath(__file__)))

# Now we can import the ImageMerger class
# We'll import it inline since the file is named with hyphens
import importlib.util
spec = importlib.util.spec_from_file_location("image_merger", join(dirname(abspath(__file__)), "image-merger.py"))
image_merger_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(image_merger_module)
ImageMerger = image_merger_module.ImageMerger

def main():
    parser = argparse.ArgumentParser(description='Merge multiple images into one')
    parser.add_argument('images', nargs='+', help='Input image paths')
    parser.add_argument('--output', '-o', required=True, help='Output image path')
    parser.add_argument('--method', '-m', choices=['vertical', 'horizontal', 'grid', 'auto'],
                        default='auto', help='Merge method (default: auto)')
    parser.add_argument('--spacing', '-s', type=int, default=10, help='Spacing between images (default: 10)')
    parser.add_argument('--background', '-b', default='#ffffff', help='Background color (default: white)')
    parser.add_argument('--description', '-d', help='Optional description to add as header')

    args = parser.parse_args()

    try:
        # Load images
        print(f"Loading {len(args.images)} images...", file=sys.stderr)
        images = []
        for img_path in args.images:
            if not Path(img_path).exists():
                print(f"Error: Image not found: {img_path}", file=sys.stderr)
                sys.exit(1)
            images.append(Image.open(img_path))

        # Merge images
        print(f"Merging using method: {args.method}", file=sys.stderr)
        merger = ImageMerger()

        if args.method == 'vertical':
            merged = merger.merge_vertical(images, args.spacing, args.background)
        elif args.method == 'horizontal':
            merged = merger.merge_horizontal(images, args.spacing, args.background)
        elif args.method == 'grid':
            merged = merger.merge_grid(images, spacing=args.spacing, background_color=args.background)
        else:  # auto
            merged = merger.merge_auto(images, args.spacing, args.background)

        # Add description if provided
        if args.description:
            print(f"Adding description header", file=sys.stderr)
            merged = merger.add_description_header(merged, args.description)

        # Save result
        print(f"Saving to: {args.output}", file=sys.stderr)
        merged.save(args.output, 'PNG')

        print(f"Successfully merged {len(images)} images", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
