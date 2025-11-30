#!/usr/bin/env python3
"""
Test script for image preview functionality
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.image_converter import ImageConverter


def test_ico_sizes():
    """Test ICO sizes configuration."""
    converter = ImageConverter()

    print("Testing ICO sizes configuration...")
    print(f"ICO_SIZES: {converter.ICO_SIZES}")

    # Expected sizes
    expected_sizes = [(16, 16), (24, 24), (32, 32), (48, 48),
                     (64, 64), (96, 96), (128, 128), (256, 256)]

    assert converter.ICO_SIZES == expected_sizes, "ICO sizes mismatch!"
    print("✓ ICO sizes configuration is correct")
    print(f"  Total sizes: {len(converter.ICO_SIZES)}")
    print(f"  Sizes: {', '.join([f'{w}x{h}' for w, h in converter.ICO_SIZES])}")


def test_extract_ico_sizes():
    """Test ICO extraction method exists."""
    converter = ImageConverter()

    print("\nTesting ICO extraction method...")
    assert hasattr(converter, 'extract_ico_sizes'), "extract_ico_sizes method not found!"
    print("✓ extract_ico_sizes method exists")


def main():
    """Run tests."""
    print("=" * 60)
    print("Image Preview Functionality Tests")
    print("=" * 60)

    try:
        test_ico_sizes()
        test_extract_ico_sizes()

        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
