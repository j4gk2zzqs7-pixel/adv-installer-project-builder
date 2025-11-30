"""
Custom Titlebar for Frameless Window
Реализация собственного заголовка окна в плоском стиле
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QMouseEvent


class CustomTitleBar(QWidget):
    """Кастомный заголовок окна с кнопками управления."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.is_maximized = False
        self.drag_position = QPoint()

        self.setup_ui()

    def setup_ui(self):
        """Инициализация UI titlebar."""
        self.setFixedHeight(45)
        self.setObjectName("customTitleBar")

        # Основной layout
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 0, 5, 0)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Иконка и заголовок
        self.title_label = QLabel("⚙️ Advanced Installer Project Builder")
        self.title_label.setObjectName("titleBarLabel")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        layout.addWidget(self.title_label)
        layout.addStretch()

        # Кнопки управления окном
        self.create_window_buttons(layout)

    def create_window_buttons(self, layout):
        """Создание кнопок минимизации, максимизации и закрытия."""

        # Кнопка минимизации
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setObjectName("titleBarButton")
        self.minimize_btn.setToolTip("Свернуть")
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.minimize_btn.setFixedSize(45, 35)

        # Кнопка максимизации/восстановления
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setObjectName("titleBarButton")
        self.maximize_btn.setToolTip("Развернуть")
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.maximize_btn.setFixedSize(45, 35)

        # Кнопка закрытия
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("titleBarCloseButton")
        self.close_btn.setToolTip("Закрыть")
        self.close_btn.clicked.connect(self.parent.close)
        self.close_btn.setFixedSize(45, 35)

        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)

    def toggle_maximize(self):
        """Переключение между максимизированным и обычным состоянием."""
        if self.is_maximized:
            self.parent.showNormal()
            self.maximize_btn.setText("□")
            self.maximize_btn.setToolTip("Развернуть")
            self.is_maximized = False
        else:
            self.parent.showMaximized()
            self.maximize_btn.setText("❐")
            self.maximize_btn.setToolTip("Восстановить")
            self.is_maximized = True

    def mousePressEvent(self, event: QMouseEvent):
        """Обработка нажатия мыши для перетаскивания окна."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Обработка перемещения мыши для перетаскивания окна."""
        if event.buttons() == Qt.LeftButton and not self.is_maximized:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Обработка двойного клика для максимизации/восстановления."""
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()
            event.accept()
