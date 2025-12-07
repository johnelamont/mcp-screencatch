#!/usr/bin/env python3
"""
Image stitching - combines images by finding overlapping content
"""

import sys
import cv2
import numpy as np
from PIL import Image
from typing import List

class ImageStitcher:
    """Stitch images together by finding overlapping regions"""

    @staticmethod
    def stitch_images(images: List[Image.Image]) -> Image.Image:
        """
        Stitch multiple images together by stacking vertically

        Args:
            images: List of PIL Images in capture order

        Returns:
            Single stitched PIL Image
        """
        if not images:
            raise ValueError("No images to stitch")

        if len(images) == 1:
            return images[0]

        # Just use simple vertical merge - skip OpenCV panorama stitching
        return ImageStitcher._fallback_vertical_merge(images)

    @staticmethod
    def detect_vertical_overlap(img1: Image.Image, img2: Image.Image, max_overlap: int = None) -> int:
        """
        Detect how many pixels of vertical overlap exist between two images.
        Compares bottom of img1 with top of img2.

        Args:
            img1: First image (top)
            img2: Second image (bottom)
            max_overlap: Maximum overlap to check (default: min of heights)

        Returns:
            Number of overlapping pixels (0 = no overlap)
        """
        if max_overlap is None:
            max_overlap = int(min(img1.height, img2.height) * 0.95)  # Check up to 95% overlap

        # Convert to numpy arrays for faster comparison
        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Ensure same width (crop if needed)
        min_width = min(arr1.shape[1], arr2.shape[1])
        arr1 = arr1[:, :min_width]
        arr2 = arr2[:, :min_width]

        best_overlap = 0
        best_score = float('inf')

        # Store scores to find a significant dip
        scores = []

        # Try different overlap amounts
        for overlap in range(10, min(max_overlap, arr1.shape[0], arr2.shape[0])):
            # Get bottom 'overlap' rows from img1
            bottom_section = arr1[-overlap:, :]
            # Get top 'overlap' rows from img2
            top_section = arr2[:overlap, :]

            # Calculate difference (mean squared error)
            diff = np.mean((bottom_section.astype(float) - top_section.astype(float)) ** 2)
            scores.append((overlap, diff))

        # Find the LARGEST overlap with a good score (< 2000)
        # We prefer larger overlaps over slightly better scores at small overlaps
        for overlap, score in reversed(scores):
            if score < 2000:  # Good enough match
                best_overlap = overlap
                best_score = score
                break

        # If no good match found, use the absolute best score
        if best_overlap == 0:
            for overlap, score in scores:
                if score < best_score:
                    best_score = score
                    best_overlap = overlap

        # If best score is too high, probably no real overlap
        # Threshold: 100 = very similar, 1000 = somewhat similar, 10000+ = different
        threshold = 2000
        if best_score > threshold:
            print(f"  No overlap detected (score={best_score:.0f}), stacking without overlap", file=sys.stderr)
            return 0

        # Additional checks to avoid false positives from blank/white space matching
        if len(scores) > 5:
            # Calculate statistics
            score_values = [s[1] for s in scores]
            median_score = sorted(score_values)[len(score_values) // 2]

            # Check: If best score is close to median, no clear overlap pattern
            # This means all overlap amounts match about the same (no distinctive overlap)
            if best_score > median_score * 0.5:
                # But allow it if the match is REALLY good (very low score)
                if best_score > 50:  # If score is not excellent, reject it
                    print(f"  No significant overlap found (best={best_score:.0f} close to median={median_score:.0f}), stacking without overlap", file=sys.stderr)
                    return 0

        # If we have a very good match (low score), accept it even if variance is low
        # This handles cases like text on white background
        if best_score < 50:  # Excellent/good match - likely real overlap
            print(f"  Detected {best_overlap}px overlap (score={best_score:.0f}, excellent match)", file=sys.stderr)
            return best_overlap

        # For moderate scores (50-500), still likely good overlap
        if best_score < 500:
            # Check variance to avoid blank space matching
            bottom_section = arr1[-best_overlap:, :]
            top_section = arr2[:best_overlap, :]

            bottom_variance = np.var(bottom_section)
            top_variance = np.var(top_section)

            # If variance is extremely low (< 10), it's likely solid color/blank
            if bottom_variance < 10 and top_variance < 10:
                print(f"  Blank region detected (variance={bottom_variance:.1f}), stacking without overlap", file=sys.stderr)
                return 0

            print(f"  Detected {best_overlap}px overlap (score={best_score:.0f})", file=sys.stderr)
            return best_overlap

        # Score is moderate (500-2000), be more cautious
        print(f"  Detected {best_overlap}px overlap (score={best_score:.0f})", file=sys.stderr)
        return best_overlap

    @staticmethod
    def _fallback_vertical_merge(images: List[Image.Image]) -> Image.Image:
        """
        Simple vertical merge - stack images one below the other.
        User is responsible for capturing without duplication.
        """
        if len(images) == 1:
            return images[0]

        print("Merging images vertically (simple stack)...", file=sys.stderr)

        # Calculate total height and max width
        total_height = sum(img.height for img in images)
        max_width = max(img.width for img in images)

        # Create merged image
        merged = Image.new('RGB', (max_width, total_height), '#ffffff')

        # Paste each image below the previous
        y_offset = 0
        for i, img in enumerate(images):
            print(f"  Placing image {i+1}/{len(images)} at y={y_offset}", file=sys.stderr)
            merged.paste(img, (0, y_offset))
            y_offset += img.height

        return merged
