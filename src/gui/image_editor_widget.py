"""
Image Editor Widget
Widget for editing images with drawing tools and corner rounding
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QColorDialog, QFileDialog, QMessageBox, QGroupBox,
    QButtonGroup, QRadioButton, QSpinBox
)
from PyQt5.QtCore import Qt, QPoint, QRect, QRectF
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QPainterPath
from PIL import Image, ImageDraw, ImageFilter
import numpy as np


class DrawingCanvas(QLabel):
    """Canvas widget for drawing on images."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.original_image = None
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor(255, 0, 0)  # Red default
        self.pen_width = 3
        self.tool = "pen"  # "pen" or "eraser"

        self.setMinimumSize(400, 400)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QLabel { border: 2px solid #555; background: #2a2a2a; }")

    def load_image(self, image_path: str):
        """Load an image into the canvas."""
        self.original_image = QPixmap(image_path)
        self.image = self.original_image.copy()
        self.update_display()

    def load_from_pixmap(self, pixmap: QPixmap):
        """Load from existing QPixmap."""
        self.original_image = pixmap.copy()
        self.image = self.original_image.copy()
        self.update_display()

    def update_display(self):
        """Update the displayed image."""
        if self.image:
            scaled = self.image.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled)

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        self.update_display()

    def mousePressEvent(self, event):
        """Handle mouse press for drawing."""
        if event.button() == Qt.LeftButton and self.image:
            self.drawing = True
            # Convert widget coordinates to image coordinates
            self.last_point = self.get_image_point(event.pos())

    def mouseMoveEvent(self, event):
        """Handle mouse move for drawing."""
        if event.buttons() & Qt.LeftButton and self.drawing and self.image:
            current_point = self.get_image_point(event.pos())
            self.draw_line(self.last_point, current_point)
            self.last_point = current_point
            self.update_display()

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def get_image_point(self, widget_point):
        """Convert widget coordinates to image coordinates."""
        if not self.pixmap():
            return QPoint()

        pixmap = self.pixmap()
        # Calculate the actual position of the pixmap within the label
        label_rect = self.rect()
        pixmap_rect = pixmap.rect()

        # Calculate offset for centered pixmap
        x_offset = (label_rect.width() - pixmap_rect.width()) / 2
        y_offset = (label_rect.height() - pixmap_rect.height()) / 2

        # Convert to pixmap coordinates
        pixmap_x = widget_point.x() - x_offset
        pixmap_y = widget_point.y() - y_offset

        # Scale to original image coordinates
        scale_x = self.image.width() / pixmap_rect.width()
        scale_y = self.image.height() / pixmap_rect.height()

        image_x = int(pixmap_x * scale_x)
        image_y = int(pixmap_y * scale_y)

        return QPoint(image_x, image_y)

    def draw_line(self, start_point, end_point):
        """Draw a line on the image."""
        painter = QPainter(self.image)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.tool == "pen":
            pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
        elif self.tool == "eraser":
            # Eraser uses transparent color
            pen = QPen(QColor(0, 0, 0, 0), self.pen_width * 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.setPen(pen)

        painter.drawLine(start_point, end_point)
        painter.end()

    def set_pen_color(self, color: QColor):
        """Set the pen color."""
        self.pen_color = color

    def set_pen_width(self, width: int):
        """Set the pen width."""
        self.pen_width = width

    def set_tool(self, tool: str):
        """Set the current tool."""
        self.tool = tool

    def reset_image(self):
        """Reset to original image."""
        if self.original_image:
            self.image = self.original_image.copy()
            self.update_display()

    def get_image(self):
        """Get the current image as QPixmap."""
        return self.image

    def round_corners(self, radius: int):
        """Round the corners of the image."""
        if not self.image:
            return

        # Convert QPixmap to QImage for manipulation
        qimage = self.image.toImage()

        # Convert to RGBA if needed
        if qimage.format() != QImage.Format_RGBA8888:
            qimage = qimage.convertToFormat(QImage.Format_RGBA8888)

        # Create a new image with the same size
        rounded = QImage(qimage.size(), QImage.Format_RGBA8888)
        rounded.fill(Qt.transparent)

        # Create painter for the new image
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create rounded rectangle path
        path = QPainterPath()
        rect = QRectF(0, 0, qimage.width(), qimage.height())
        path.addRoundedRect(rect, radius, radius)

        # Clip to rounded rectangle and draw original image
        painter.setClipPath(path)
        painter.drawImage(0, 0, qimage)
        painter.end()

        # Convert back to pixmap
        self.image = QPixmap.fromImage(rounded)
        self.update_display()


class ImageEditorWidget(QWidget):
    """Widget for editing images with drawing and corner rounding tools."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Canvas
        self.canvas = DrawingCanvas()
        layout.addWidget(self.canvas)

        # Tools group
        tools_group = QGroupBox("Инструменты рисования")
        tools_layout = QVBoxLayout()

        # Tool selection
        tool_buttons_layout = QHBoxLayout()
        self.tool_group = QButtonGroup()

        self.pen_radio = QRadioButton("Карандаш")
        self.pen_radio.setChecked(True)
        self.pen_radio.toggled.connect(lambda: self.canvas.set_tool("pen"))
        self.tool_group.addButton(self.pen_radio)
        tool_buttons_layout.addWidget(self.pen_radio)

        self.eraser_radio = QRadioButton("Ластик")
        self.eraser_radio.toggled.connect(lambda: self.canvas.set_tool("eraser"))
        self.tool_group.addButton(self.eraser_radio)
        tool_buttons_layout.addWidget(self.eraser_radio)

        tools_layout.addLayout(tool_buttons_layout)

        # Color selection
        color_layout = QHBoxLayout()
        color_label = QLabel("Цвет:")
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 30)
        self.color_btn.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        tools_layout.addLayout(color_layout)

        # Pen width
        width_layout = QHBoxLayout()
        width_label = QLabel("Толщина:")
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setMinimum(1)
        self.width_slider.setMaximum(20)
        self.width_slider.setValue(3)
        self.width_slider.valueChanged.connect(self.on_width_changed)
        self.width_value_label = QLabel("3")
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_slider)
        width_layout.addWidget(self.width_value_label)
        tools_layout.addLayout(width_layout)

        tools_group.setLayout(tools_layout)
        layout.addWidget(tools_group)

        # Corner rounding group
        corner_group = QGroupBox("Закругление углов")
        corner_layout = QHBoxLayout()

        corner_label = QLabel("Радиус:")
        self.corner_radius_spin = QSpinBox()
        self.corner_radius_spin.setMinimum(0)
        self.corner_radius_spin.setMaximum(200)
        self.corner_radius_spin.setValue(20)
        self.corner_radius_spin.setSuffix(" px")

        apply_corner_btn = QPushButton("Применить закругление")
        apply_corner_btn.clicked.connect(self.apply_corner_rounding)

        corner_layout.addWidget(corner_label)
        corner_layout.addWidget(self.corner_radius_spin)
        corner_layout.addWidget(apply_corner_btn)
        corner_layout.addStretch()

        corner_group.setLayout(corner_layout)
        layout.addWidget(corner_group)

        # Action buttons
        button_layout = QHBoxLayout()

        reset_btn = QPushButton("Сбросить изменения")
        reset_btn.clicked.connect(self.reset_canvas)

        save_btn = QPushButton("Сохранить изображение")
        save_btn.clicked.connect(self.save_image)

        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_image(self, image_path: str):
        """Load an image for editing."""
        self.canvas.load_image(image_path)

    def load_from_pixmap(self, pixmap: QPixmap):
        """Load image from pixmap."""
        self.canvas.load_from_pixmap(pixmap)

    def choose_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(self.canvas.pen_color, self)
        if color.isValid():
            self.canvas.set_pen_color(color)
            self.color_btn.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")

    def on_width_changed(self, value):
        """Handle pen width change."""
        self.canvas.set_pen_width(value)
        self.width_value_label.setText(str(value))

    def apply_corner_rounding(self):
        """Apply corner rounding to the image."""
        radius = self.corner_radius_spin.value()
        if radius > 0:
            self.canvas.round_corners(radius)
            QMessageBox.information(self, "Успех", f"Углы закруглены с радиусом {radius}px")

    def reset_canvas(self):
        """Reset the canvas to original image."""
        self.canvas.reset_image()

    def save_image(self):
        """Save the edited image."""
        if not self.canvas.image:
            QMessageBox.warning(self, "Ошибка", "Нет изображения для сохранения")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить изображение",
            "",
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*.*)"
        )

        if file_path:
            if self.canvas.image.save(file_path):
                QMessageBox.information(self, "Успех", f"Изображение сохранено:\n{file_path}")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить изображение")

    def get_edited_image(self):
        """Get the edited image as QPixmap."""
        return self.canvas.get_image()
