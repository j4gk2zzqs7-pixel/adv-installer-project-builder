"""
Image Converter Module
Converts PNG/JPG images to ICO and BMP formats for Advanced Installer
"""
from PIL import Image
import os
from pathlib import Path
from typing import Tuple, List

# Compatibility fix for different Pillow versions
# Pillow >= 9.1.0 uses Image.Resampling.LANCZOS
# Older versions use Image.LANCZOS
try:
    LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    LANCZOS = Image.LANCZOS


class ImageConverter:
    """Handles image conversion for Advanced Installer icons."""

    SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg']
    ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (96, 96), (128, 128), (256, 256)]
    BMP_SIZE = (256, 256)

    def __init__(self):
        """Initialize the Image Converter."""
        pass

    def is_supported_format(self, file_path: str) -> bool:
        """
        Check if the file format is supported.

        Args:
            file_path: Path to the image file

        Returns:
            True if format is supported
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_FORMATS

    def convert_to_ico(self, input_path: str, output_path: str,
                       sizes: List[Tuple[int, int]] = None) -> str:
        """
        Convert image to ICO format with multiple sizes.

        Args:
            input_path: Path to the input image (PNG/JPG)
            output_path: Path for the output ICO file
            sizes: List of (width, height) tuples for ICO sizes

        Returns:
            Path to the created ICO file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If input format is not supported
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not self.is_supported_format(input_path):
            raise ValueError(f"Unsupported format: {Path(input_path).suffix}")

        if sizes is None:
            sizes = self.ICO_SIZES

        # Open the image
        img = Image.open(input_path)

        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Create images at different sizes
        icon_images = []
        for size in sizes:
            resized = img.resize(size, LANCZOS)
            icon_images.append(resized)

        # Save as ICO with multiple sizes
        icon_images[0].save(
            output_path,
            format='ICO',
            sizes=[img.size for img in icon_images],
            append_images=icon_images[1:]
        )

        return output_path

    def convert_to_bmp(self, input_path: str, output_path: str,
                      size: Tuple[int, int] = None) -> str:
        """
        Convert image to BMP format.

        Args:
            input_path: Path to the input image (PNG/JPG)
            output_path: Path for the output BMP file
            size: Target size as (width, height) tuple

        Returns:
            Path to the created BMP file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If input format is not supported
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not self.is_supported_format(input_path):
            raise ValueError(f"Unsupported format: {Path(input_path).suffix}")

        if size is None:
            size = self.BMP_SIZE

        # Open the image
        img = Image.open(input_path)

        # Resize to target size
        img_resized = img.resize(size, LANCZOS)

        # Convert to RGB (BMP doesn't support alpha channel well)
        if img_resized.mode == 'RGBA':
            # Create a white background
            background = Image.new('RGB', size, (255, 255, 255))
            background.paste(img_resized, mask=img_resized.split()[3])  # Use alpha as mask
            img_resized = background
        elif img_resized.mode != 'RGB':
            img_resized = img_resized.convert('RGB')

        # Save as BMP
        img_resized.save(output_path, format='BMP')

        return output_path

    def convert_image_for_installer(self, input_path: str,
                                   output_dir: str,
                                   base_name: str = None) -> dict:
        """
        Convert image to both ICO and BMP formats for use in installer.

        Args:
            input_path: Path to the input image
            output_dir: Directory to save output files
            base_name: Base name for output files (without extension)

        Returns:
            Dictionary with paths to created files:
            {'ico': 'path/to/icon.ico', 'bmp': 'path/to/icon.bmp'}

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If input format is not supported
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not self.is_supported_format(input_path):
            raise ValueError(f"Unsupported format: {Path(input_path).suffix}")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Determine base name
        if base_name is None:
            base_name = Path(input_path).stem

        # Generate output paths
        ico_path = os.path.join(output_dir, f"{base_name}.ico")
        bmp_path = os.path.join(output_dir, f"{base_name}.bmp")

        # Convert to both formats
        result = {
            'ico': self.convert_to_ico(input_path, ico_path),
            'bmp': self.convert_to_bmp(input_path, bmp_path)
        }

        return result

    def get_image_info(self, file_path: str) -> dict:
        """
        Get information about an image file.

        Args:
            file_path: Path to the image file

        Returns:
            Dictionary with image information (size, format, mode)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        img = Image.open(file_path)
        return {
            'size': img.size,
            'width': img.width,
            'height': img.height,
            'format': img.format,
            'mode': img.mode
        }

    def extract_ico_sizes(self, ico_path: str) -> dict:
        """
        Extract all available sizes from an ICO file.

        Args:
            ico_path: Path to the ICO file

        Returns:
            Dictionary mapping size tuples to PIL Image objects
        """
        if not os.path.exists(ico_path):
            raise FileNotFoundError(f"ICO file not found: {ico_path}")

        ico_images = {}

        try:
            # Open ICO file
            img = Image.open(ico_path)

            # ICO files can contain multiple sizes
            # We need to iterate through all available sizes
            if hasattr(img, 'n_frames'):
                # Multi-resolution ICO
                for i in range(img.n_frames):
                    img.seek(i)
                    size = img.size
                    # Create a copy of the current frame
                    ico_images[size] = img.copy()
            else:
                # Single resolution ICO
                size = img.size
                ico_images[size] = img.copy()

        except Exception as e:
            raise ValueError(f"Error extracting ICO sizes: {str(e)}")

        return ico_images
