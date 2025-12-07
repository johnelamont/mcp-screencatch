#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test of standalone screencatch functionality
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")

    try:
        from enhanced_capture_standalone import DescriptionDialog, MultiCaptureOverlay, merge_and_save
        print("✓ enhanced_capture_standalone imported")
    except ImportError as e:
        print(f"✗ Failed to import enhanced_capture_standalone: {e}")
        return False

    try:
        from preview_and_confirm_standalone import PreviewWindow
        print("✓ preview_and_confirm_standalone imported")
    except ImportError as e:
        print(f"✗ Failed to import preview_and_confirm_standalone: {e}")
        return False

    try:
        from image_merger import ImageMerger
        print("✓ image_merger imported")
    except ImportError as e:
        print(f"✗ Failed to import image_merger: {e}")
        return False

    try:
        from PIL import Image, ImageGrab
        print("✓ PIL/Pillow imported")
    except ImportError as e:
        print(f"✗ Failed to import PIL: {e}")
        print("  Install with: pip install pillow")
        return False

    return True

def test_description_dialog():
    """Test description dialog"""
    print("\nTesting description dialog...")
    print("A dialog should appear. Enter some text or cancel.")

    from enhanced_capture_standalone import DescriptionDialog

    dialog = DescriptionDialog()
    description = dialog.get_description()

    if description:
        print(f"✓ Got description: '{description}'")
    else:
        print("✓ Dialog cancelled (no description)")

    return True

def test_image_merger():
    """Test image merging with sample images"""
    print("\nTesting image merger...")

    from PIL import Image
    from image_merger import ImageMerger

    # Create sample images
    img1 = Image.new('RGB', (100, 100), 'red')
    img2 = Image.new('RGB', (100, 100), 'blue')
    img3 = Image.new('RGB', (100, 100), 'green')

    try:
        # Test vertical merge
        merged = ImageMerger.merge_vertical([img1, img2, img3])
        assert merged.size == (100, 320), f"Expected (100, 320), got {merged.size}"
        print("✓ Vertical merge works")

        # Test horizontal merge
        merged = ImageMerger.merge_horizontal([img1, img2, img3])
        assert merged.size == (320, 100), f"Expected (320, 100), got {merged.size}"
        print("✓ Horizontal merge works")

        # Test grid merge
        merged = ImageMerger.merge_grid([img1, img2, img3, img1])
        print(f"✓ Grid merge works (size: {merged.size})")

        # Test auto merge
        merged = ImageMerger.merge_auto([img1, img2])
        print(f"✓ Auto merge works (size: {merged.size})")

        return True
    except Exception as e:
        print(f"✗ Image merger test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("ScreenCatch Standalone Test Suite")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # Test imports
    tests_total += 1
    if test_imports():
        tests_passed += 1
    else:
        print("\n✗ Import test failed. Cannot continue.")
        return

    # Test image merger
    tests_total += 1
    if test_image_merger():
        tests_passed += 1

    # Test description dialog (interactive)
    print("\n" + "=" * 60)
    response = input("Test description dialog? (y/n): ").lower()
    if response == 'y':
        tests_total += 1
        if test_description_dialog():
            tests_passed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print("=" * 60)

    if tests_passed == tests_total:
        print("\n✓ All tests passed!")
        print("\nTo test the full capture workflow, run:")
        print("  python screencatch.py")
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
