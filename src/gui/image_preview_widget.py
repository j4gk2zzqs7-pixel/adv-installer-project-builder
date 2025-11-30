"""
Image Preview Widget
Widget for previewing generated image files (PNG, BMP, ICO)
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QScrollArea, QGridLayout, QPushButton, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image
import io
import os
from pathlib import Path


class ImagePreviewWidget(QWidget):
    """Widget for previewing generated images including multi-size ICO files."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget for different preview types
        self.preview_tabs = QTabWidget()

        # BMP Preview tab
        self.bmp_preview_widget = QWidget()
        self.setup_bmp_preview()
        self.preview_tabs.addTab(self.bmp_preview_widget, "BMP Предпросмотр")

        # ICO Preview tab
        self.ico_preview_widget = QWidget()
        self.setup_ico_preview()
        self.preview_tabs.addTab(self.ico_preview_widget, "ICO Предпросмотр (все размеры)")

        layout.addWidget(self.preview_tabs)
        self.setLayout(layout)

    def setup_bmp_preview(self):
        """Setup BMP preview tab."""
        layout = QVBoxLayout()

        # Browse button for BMP
        browse_btn = QPushButton("Загрузить BMP файл для предпросмотра...")
        browse_btn.clicked.connect(self.browse_bmp_file)
        layout.addWidget(browse_btn)

        # Info label
        self.bmp_info_label = QLabel("BMP файл не загружен")
        self.bmp_info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.bmp_info_label)

        # Preview label
        self.bmp_preview_label = QLabel()
        self.bmp_preview_label.setObjectName("bmp_preview")
        self.bmp_preview_label.setFixedSize(256, 256)
        self.bmp_preview_label.setAlignment(Qt.AlignCenter)
        self.bmp_preview_label.setStyleSheet("QLabel { border: 1px solid #555; background: #2a2a2a; }")
        layout.addWidget(self.bmp_preview_label, alignment=Qt.AlignCenter)

        layout.addStretch()
        self.bmp_preview_widget.setLayout(layout)

    def setup_ico_preview(self):
        """Setup ICO preview tab with grid of all sizes."""
        layout = QVBoxLayout()

        # Browse button for ICO
        browse_btn = QPushButton("Загрузить ICO файл для предпросмотра...")
        browse_btn.clicked.connect(self.browse_ico_file)
        layout.addWidget(browse_btn)

        # Info label
        self.ico_info_label = QLabel("ICO файл не загружен")
        self.ico_info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ico_info_label)

        # Scroll area for the grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container widget for the grid
        grid_container = QWidget()
        self.ico_grid_layout = QGridLayout()
        self.ico_grid_layout.setSpacing(15)
        grid_container.setLayout(self.ico_grid_layout)

        scroll_area.setWidget(grid_container)
        layout.addWidget(scroll_area)

        self.ico_preview_widget.setLayout(layout)

    def load_bmp_preview(self, bmp_path: str):
        """
        Load and display BMP file preview.

        Args:
            bmp_path: Path to the BMP file
        """
        if not os.path.exists(bmp_path):
            self.bmp_info_label.setText(f"BMP файл не найден: {Path(bmp_path).name}")
            return

        try:
            # Load BMP using PIL
            img = Image.open(bmp_path)
            width, height = img.size

            # Update info label
            self.bmp_info_label.setText(f"BMP: {Path(bmp_path).name} ({width}x{height})")

            # Convert PIL Image to QPixmap
            pixmap = self.pil_to_qpixmap(img)

            # Scale to fit preview
            scaled_pixmap = pixmap.scaled(
                256, 256,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.bmp_preview_label.setPixmap(scaled_pixmap)

        except Exception as e:
            self.bmp_info_label.setText(f"Ошибка загрузки BMP: {str(e)}")

    def load_ico_preview(self, ico_path: str, ico_images: dict = None):
        """
        Load and display ICO file with all sizes.

        Args:
            ico_path: Path to the ICO file
            ico_images: Dictionary mapping size tuples to PIL Image objects
                       (optional, will be extracted if not provided)
        """
        if not os.path.exists(ico_path):
            self.ico_info_label.setText(f"ICO файл не найден: {Path(ico_path).name}")
            return

        try:
            # Extract ICO sizes if not provided
            if ico_images is None:
                from utils.image_converter import ImageConverter
                converter = ImageConverter()
                ico_images = converter.extract_ico_sizes(ico_path)

            # Update info label
            sizes_str = ", ".join([f"{w}x{h}" for (w, h) in sorted(ico_images.keys())])
            self.ico_info_label.setText(
                f"ICO: {Path(ico_path).name}\n"
                f"Доступные размеры: {sizes_str}"
            )

            # Clear existing grid
            self.clear_ico_grid()

            # Standard ICO sizes we want to display (in order)
            standard_sizes = [(16, 16), (24, 24), (32, 32), (48, 48),
                            (64, 64), (96, 96), (128, 128), (256, 256)]

            # Create grid of previews (4 columns)
            row = 0
            col = 0
            max_cols = 4

            for size in standard_sizes:
                if size in ico_images:
                    # Create group box for this size
                    group = QGroupBox(f"{size[0]}x{size[1]}")
                    group_layout = QVBoxLayout()

                    # Create label for preview
                    preview_label = QLabel()
                    preview_label.setFixedSize(size[0] * 2, size[1] * 2)  # 2x scale for visibility
                    preview_label.setAlignment(Qt.AlignCenter)
                    preview_label.setStyleSheet("QLabel { border: 1px solid #555; background: #2a2a2a; }")

                    # Convert PIL Image to QPixmap
                    img = ico_images[size]
                    pixmap = self.pil_to_qpixmap(img)

                    # Scale up for better visibility
                    scaled_pixmap = pixmap.scaled(
                        size[0] * 2, size[1] * 2,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )

                    preview_label.setPixmap(scaled_pixmap)

                    group_layout.addWidget(preview_label, alignment=Qt.AlignCenter)
                    group.setLayout(group_layout)

                    # Add to grid
                    self.ico_grid_layout.addWidget(group, row, col)

                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1

        except Exception as e:
            self.ico_info_label.setText(f"Ошибка загрузки ICO: {str(e)}")

    def load_previews(self, bmp_path: str = None, ico_path: str = None, ico_images: dict = None):
        """
        Load both BMP and ICO previews.

        Args:
            bmp_path: Path to the BMP file (optional)
            ico_path: Path to the ICO file (optional)
            ico_images: Dictionary mapping size tuples to PIL Image objects (optional)
        """
        if bmp_path:
            self.load_bmp_preview(bmp_path)

        if ico_path:
            self.load_ico_preview(ico_path, ico_images)

    def clear_ico_grid(self):
        """Clear all widgets from the ICO grid."""
        while self.ico_grid_layout.count():
            item = self.ico_grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def pil_to_qpixmap(self, pil_image: Image.Image) -> QPixmap:
        """
        Convert PIL Image to QPixmap.

        Args:
            pil_image: PIL Image object

        Returns:
            QPixmap object
        """
        # Convert PIL Image to bytes
        if pil_image.mode == "RGB":
            r, g, b = pil_image.split()
            pil_image = Image.merge("RGB", (b, g, r))
        elif pil_image.mode == "RGBA":
            r, g, b, a = pil_image.split()
            pil_image = Image.merge("RGBA", (b, g, r, a))
        elif pil_image.mode == "L":
            pil_image = pil_image.convert("RGBA")

        # Convert to bytes
        data = pil_image.tobytes("raw", pil_image.mode)

        # Create QImage
        if pil_image.mode == "RGB":
            qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGB888)
        elif pil_image.mode == "RGBA":
            qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
        else:
            qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format_Grayscale8)

        # Convert to QPixmap
        return QPixmap.fromImage(qimage)

    def clear_previews(self):
        """Clear all previews."""
        self.bmp_preview_label.clear()
        self.bmp_info_label.setText("BMP файл не загружен")

        self.clear_ico_grid()
        self.ico_info_label.setText("ICO файл не загружен")

    def browse_bmp_file(self):
        """Browse for BMP file to preview."""
        from PyQt5.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите BMP файл",
            "",
            "BMP Images (*.bmp);;All Files (*.*)"
        )

        if file_path:
            self.load_bmp_preview(file_path)

    def browse_ico_file(self):
        """Browse for ICO file to preview."""
        from PyQt5.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите ICO файл",
            "",
            "ICO Images (*.ico);;All Files (*.*)"
        )

        if file_path:
            self.load_ico_preview(file_path)
