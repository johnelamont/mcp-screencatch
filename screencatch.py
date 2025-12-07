#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScreenCatch - Standalone screen capture application
Usage: python screencatch.py [options]
"""

import sys
import json
import argparse
import os
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from enhanced_capture_standalone import DescriptionDialog, MultiCaptureOverlay, merge_and_save
from preview_and_confirm_standalone import PreviewWindow

def main():
    parser = argparse.ArgumentParser(
        description='ScreenCatch - Enhanced screen capture tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic capture with description
  python screencatch.py

  # Capture without description prompt
  python screencatch.py --no-description

  # Specify output directory
  python screencatch.py --output-dir ./screenshots

  # Show preview and allow recapture
  python screencatch.py --preview

Controls during capture:
  Enter           - Capture region and continue to next
  Shift+Enter     - Capture region and finish
  ESC             - Finish (save captured regions)
  Drag inst. box  - Move instruction box out of the way
        '''
    )

    parser.add_argument(
        '--output-dir', '-o',
        default=os.getcwd(),
        help='Directory to save captures (default: current directory)'
    )

    parser.add_argument(
        '--no-description',
        action='store_true',
        help='Skip description dialog'
    )

    parser.add_argument(
        '--preview',
        action='store_true',
        help='Show preview after capture and allow recapture'
    )

    parser.add_argument(
        '--merge-method',
        choices=['auto', 'vertical', 'horizontal', 'grid'],
        default='auto',
        help='How to merge multiple captures (default: auto)'
    )

    parser.add_argument(
        '--spacing',
        type=int,
        default=10,
        help='Spacing between merged images in pixels (default: 10)'
    )

    parser.add_argument(
        '--json-output',
        action='store_true',
        help='Output result as JSON to stdout'
    )

    args = parser.parse_args()

    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        description = None

        # Get description if requested
        if not args.no_description:
            dialog = DescriptionDialog()
            description = dialog.get_description()

            if not description:
                print("No description provided. Continuing without description.", file=sys.stderr)

        # Main capture loop (for recapture support)
        recapture_count = 0
        while True:
            print(f"\nStarting capture session{f' (recapture #{recapture_count + 1})' if recapture_count > 0 else ''}...", file=sys.stderr)

            # Show capture overlay
            temp_output = output_dir / f"temp-capture-{datetime.now().timestamp()}.json"
            overlay = MultiCaptureOverlay(str(temp_output))
            overlay.run()

            # Read results
            if not temp_output.exists():
                print("Capture cancelled - no output file created", file=sys.stderr)
                sys.exit(1)

            with open(temp_output, 'r') as f:
                result = json.load(f)

            temp_output.unlink()

            if result.get('cancelled') or result.get('count', 0) == 0:
                print("Capture cancelled by user", file=sys.stderr)
                sys.exit(1)

            # Merge and save captures
            print(f"\nProcessing {result['count']} captured region(s)...", file=sys.stderr)

            filepath, metadata = merge_and_save(
                regions=result['captures'],
                output_dir=str(output_dir),
                description=description,
                merge_method=args.merge_method,
                spacing=args.spacing,
                recapture_iteration=recapture_count
            )

            print(f"✓ Saved to: {filepath}", file=sys.stderr)
            if result['count'] > 1:
                print(f"✓ Merged {result['count']} captures", file=sys.stderr)

            # Show preview if requested
            if args.preview:
                preview = PreviewWindow(filepath, description or "Untitled", result['count'])
                should_recapture = preview.show()

                if should_recapture:
                    print("\n⟳ User requested recapture...", file=sys.stderr)
                    recapture_count += 1
                    # Delete the file and loop
                    try:
                        os.unlink(filepath)
                        os.unlink(filepath.replace('.png', '.json'))
                    except:
                        pass
                    continue

            # Success - output result
            final_result = {
                'success': True,
                'filepath': filepath,
                'description': description,
                'capture_count': result['count'],
                'merged': result['count'] > 1,
                'recapture_iterations': recapture_count,
                'metadata_file': filepath.replace('.png', '.json')
            }

            if args.json_output:
                print(json.dumps(final_result, indent=2))
            else:
                print("\n" + "=" * 60, file=sys.stderr)
                print("SUCCESS", file=sys.stderr)
                print("=" * 60, file=sys.stderr)
                if description:
                    print(f"Description: {description}", file=sys.stderr)
                print(f"Captures: {result['count']}", file=sys.stderr)
                print(f"Output: {filepath}", file=sys.stderr)
                if recapture_count > 0:
                    print(f"Recaptured: {recapture_count} time(s)", file=sys.stderr)
                print("=" * 60, file=sys.stderr)

            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nCancelled by user (Ctrl+C)", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
