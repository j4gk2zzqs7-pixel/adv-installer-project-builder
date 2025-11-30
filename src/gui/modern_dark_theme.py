"""
Modern Dark Theme for Advanced Installer Project Builder
Стильная темная тема с закругленными углами и современными элементами
"""

def get_modern_dark_stylesheet():
    """
    Возвращает CSS стиль для современной темной темы с закругленными элементами
    """
    return """
    /* ========== ОСНОВНЫЕ НАСТРОЙКИ ========== */
    QMainWindow {
        background-color: #1a1a2e;
    }

    QWidget {
        background-color: #1a1a2e;
        color: #eaeaea;
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 10pt;
    }

    /* ========== ГРУППЫ ========== */
    QGroupBox {
        background-color: #16213e;
        border: 2px solid #0f3460;
        border-radius: 12px;
        margin-top: 12px;
        padding-top: 16px;
        font-weight: bold;
        color: #e94560;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 4px 12px;
        background-color: #0f3460;
        border-radius: 6px;
        color: #eaeaea;
        left: 12px;
    }

    /* ========== ВКЛАДКИ ========== */
    QTabWidget::pane {
        border: 2px solid #0f3460;
        border-radius: 12px;
        background-color: #16213e;
        top: -2px;
    }

    QTabBar::tab {
        background-color: #0f3460;
        color: #b0b0b0;
        padding: 10px 20px;
        margin-right: 4px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        min-width: 100px;
        font-weight: 500;
    }

    QTabBar::tab:selected {
        background-color: #16213e;
        color: #e94560;
        font-weight: bold;
        border-bottom: 3px solid #e94560;
    }

    QTabBar::tab:hover:!selected {
        background-color: #1a2942;
        color: #eaeaea;
    }

    /* ========== КНОПКИ ========== */
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #e94560, stop:1 #c23350);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 10pt;
        min-height: 25px;
    }

    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ff5770, stop:1 #e94560);
    }

    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #c23350, stop:1 #a02240);
        padding-top: 12px;
        padding-bottom: 8px;
    }

    QPushButton:disabled {
        background: #2a2a3e;
        color: #666666;
    }

    /* Вторичные кнопки (для действий просмотра/обзора) */
    QPushButton[text="Обзор..."],
    QPushButton[text="..."],
    QPushButton[text="Обновить"] {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #0f3460, stop:1 #0a2747);
        color: #eaeaea;
    }

    QPushButton[text="Обзор..."]:hover,
    QPushButton[text="..."]:hover,
    QPushButton[text="Обновить"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1a4070, stop:1 #0f3460);
    }

    /* ========== ПОЛЯ ВВОДА ========== */
    QLineEdit {
        background-color: #0f3460;
        border: 2px solid #1a4070;
        border-radius: 8px;
        padding: 8px 12px;
        color: #eaeaea;
        selection-background-color: #e94560;
        selection-color: #ffffff;
        font-size: 10pt;
    }

    QLineEdit:focus {
        border: 2px solid #e94560;
        background-color: #16213e;
    }

    QLineEdit:read-only {
        background-color: #1a2942;
        color: #b0b0b0;
    }

    QLineEdit:disabled {
        background-color: #1a1a2e;
        color: #666666;
        border-color: #2a2a3e;
    }

    /* ========== ТЕКСТОВЫЕ ОБЛАСТИ ========== */
    QTextEdit {
        background-color: #0f3460;
        border: 2px solid #1a4070;
        border-radius: 10px;
        padding: 10px;
        color: #eaeaea;
        selection-background-color: #e94560;
        selection-color: #ffffff;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 9pt;
        line-height: 1.4;
    }

    QTextEdit:focus {
        border: 2px solid #e94560;
    }

    /* ========== ТАБЛИЦЫ ========== */
    QTableWidget {
        background-color: #0f3460;
        alternate-background-color: #16213e;
        border: 2px solid #1a4070;
        border-radius: 10px;
        gridline-color: #1a4070;
        color: #eaeaea;
        selection-background-color: #e94560;
        selection-color: #ffffff;
    }

    QTableWidget::item {
        padding: 8px;
        border: none;
    }

    QTableWidget::item:selected {
        background-color: #e94560;
        color: #ffffff;
    }

    QTableWidget::item:hover {
        background-color: #1a4070;
    }

    QHeaderView::section {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #0f3460, stop:1 #0a2747);
        color: #e94560;
        padding: 8px;
        border: none;
        border-right: 1px solid #1a4070;
        border-bottom: 2px solid #e94560;
        font-weight: bold;
        font-size: 10pt;
    }

    QHeaderView::section:first {
        border-top-left-radius: 8px;
    }

    QHeaderView::section:last {
        border-top-right-radius: 8px;
        border-right: none;
    }

    QHeaderView::section:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1a4070, stop:1 #0f3460);
    }

    /* ========== СПИСКИ ========== */
    QListWidget {
        background-color: #0f3460;
        border: 2px solid #1a4070;
        border-radius: 10px;
        padding: 5px;
        color: #eaeaea;
        outline: none;
    }

    QListWidget::item {
        padding: 8px;
        border-radius: 6px;
        margin: 2px;
    }

    QListWidget::item:selected {
        background-color: #e94560;
        color: #ffffff;
    }

    QListWidget::item:hover:!selected {
        background-color: #1a4070;
    }

    /* ========== ЧЕКБОКСЫ ========== */
    QCheckBox {
        spacing: 8px;
        color: #eaeaea;
        font-size: 10pt;
    }

    QCheckBox::indicator {
        width: 20px;
        height: 20px;
        border: 2px solid #1a4070;
        border-radius: 6px;
        background-color: #0f3460;
    }

    QCheckBox::indicator:hover {
        border-color: #e94560;
        background-color: #16213e;
    }

    QCheckBox::indicator:checked {
        background-color: #e94560;
        border-color: #e94560;
        image: url(none);
    }

    QCheckBox::indicator:checked:after {
        content: "✓";
        color: white;
        font-size: 14pt;
        font-weight: bold;
    }

    /* ========== КОМБОБОКСЫ ========== */
    QComboBox {
        background-color: #0f3460;
        border: 2px solid #1a4070;
        border-radius: 8px;
        padding: 8px 12px;
        color: #eaeaea;
        min-height: 25px;
        font-size: 10pt;
    }

    QComboBox:focus {
        border: 2px solid #e94560;
    }

    QComboBox::drop-down {
        border: none;
        width: 30px;
    }

    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #eaeaea;
        margin-right: 8px;
    }

    QComboBox QAbstractItemView {
        background-color: #16213e;
        border: 2px solid #e94560;
        border-radius: 8px;
        selection-background-color: #e94560;
        selection-color: #ffffff;
        outline: none;
        padding: 4px;
    }

    QComboBox QAbstractItemView::item {
        padding: 8px;
        border-radius: 4px;
        min-height: 25px;
    }

    QComboBox QAbstractItemView::item:hover {
        background-color: #1a4070;
    }

    /* ========== ПРОГРЕСС-БАР ========== */
    QProgressBar {
        background-color: #0f3460;
        border: 2px solid #1a4070;
        border-radius: 10px;
        text-align: center;
        color: #ffffff;
        font-weight: bold;
        min-height: 25px;
        font-size: 10pt;
    }

    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #e94560, stop:0.5 #ff5770, stop:1 #e94560);
        border-radius: 8px;
        margin: 2px;
    }

    /* ========== СКРОЛЛБАРЫ ========== */
    QScrollBar:vertical {
        background-color: #0f3460;
        width: 14px;
        border-radius: 7px;
        margin: 0px;
    }

    QScrollBar::handle:vertical {
        background-color: #1a4070;
        border-radius: 7px;
        min-height: 30px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #e94560;
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: none;
    }

    QScrollBar:horizontal {
        background-color: #0f3460;
        height: 14px;
        border-radius: 7px;
        margin: 0px;
    }

    QScrollBar::handle:horizontal {
        background-color: #1a4070;
        border-radius: 7px;
        min-width: 30px;
    }

    QScrollBar::handle:horizontal:hover {
        background-color: #e94560;
    }

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {
        background: none;
    }

    /* ========== СТАТУС-БАР ========== */
    QStatusBar {
        background-color: #0f3460;
        color: #eaeaea;
        border-top: 2px solid #1a4070;
        font-size: 9pt;
    }

    QStatusBar::item {
        border: none;
    }

    /* ========== МЕНЮ ========== */
    QMenuBar {
        background-color: #0f3460;
        color: #eaeaea;
        border-bottom: 2px solid #1a4070;
        padding: 4px;
    }

    QMenuBar::item {
        padding: 6px 12px;
        background-color: transparent;
        border-radius: 6px;
    }

    QMenuBar::item:selected {
        background-color: #1a4070;
        color: #e94560;
    }

    QMenu {
        background-color: #16213e;
        border: 2px solid #e94560;
        border-radius: 8px;
        padding: 6px;
    }

    QMenu::item {
        padding: 8px 24px;
        border-radius: 6px;
        color: #eaeaea;
    }

    QMenu::item:selected {
        background-color: #e94560;
        color: #ffffff;
    }

    /* ========== TOOLTIP ========== */
    QToolTip {
        background-color: #16213e;
        color: #eaeaea;
        border: 2px solid #e94560;
        border-radius: 8px;
        padding: 8px;
        font-size: 9pt;
    }

    /* ========== SPLITTER ========== */
    QSplitter::handle {
        background-color: #1a4070;
        border-radius: 2px;
    }

    QSplitter::handle:hover {
        background-color: #e94560;
    }

    QSplitter::handle:horizontal {
        width: 4px;
    }

    QSplitter::handle:vertical {
        height: 4px;
    }

    /* ========== LABEL ========== */
    QLabel {
        background-color: transparent;
        color: #eaeaea;
        font-size: 10pt;
    }

    QLabel[accessibleName="heading"] {
        color: #e94560;
        font-size: 14pt;
        font-weight: bold;
    }

    /* ========== СПЕЦИАЛЬНЫЕ ЭЛЕМЕНТЫ ========== */
    /* Превью иконки */
    QLabel#icon_preview {
        background-color: #0f3460;
        border: 3px dashed #1a4070;
        border-radius: 12px;
    }

    /* ========== АНИМАЦИИ И ЭФФЕКТЫ ========== */
    * {
        outline: none;
    }
    """


def get_color_palette():
    """
    Возвращает цветовую палитру темы
    """
    return {
        'primary_bg': '#1a1a2e',        # Основной фон
        'secondary_bg': '#16213e',      # Вторичный фон
        'tertiary_bg': '#0f3460',       # Третичный фон (элементы)
        'accent': '#e94560',            # Акцентный цвет (красно-розовый)
        'accent_hover': '#ff5770',      # Акцент при наведении
        'accent_dark': '#c23350',       # Темный акцент
        'text_primary': '#eaeaea',      # Основной текст
        'text_secondary': '#b0b0b0',    # Вторичный текст
        'text_disabled': '#666666',     # Отключенный текст
        'border': '#1a4070',            # Цвет границ
        'border_focus': '#e94560',      # Цвет границ при фокусе
        'success': '#00d9ff',           # Успех
        'warning': '#ffa500',           # Предупреждение
        'error': '#ff4757',             # Ошибка
    }


def apply_modern_dark_theme(app):
    """
    Применяет современную темную тему к приложению

    Args:
        app: QApplication экземпляр
    """
    from PyQt5.QtGui import QPalette, QColor
    from PyQt5.QtCore import Qt

    # Устанавливаем стиль Fusion для лучшей совместимости
    app.setStyle('Fusion')

    # Применяем stylesheet
    app.setStyleSheet(get_modern_dark_stylesheet())

    # Настраиваем палитру для еще лучшей интеграции
    palette = QPalette()
    colors = get_color_palette()

    # Основные цвета
    palette.setColor(QPalette.Window, QColor(colors['primary_bg']))
    palette.setColor(QPalette.WindowText, QColor(colors['text_primary']))
    palette.setColor(QPalette.Base, QColor(colors['tertiary_bg']))
    palette.setColor(QPalette.AlternateBase, QColor(colors['secondary_bg']))
    palette.setColor(QPalette.ToolTipBase, QColor(colors['secondary_bg']))
    palette.setColor(QPalette.ToolTipText, QColor(colors['text_primary']))
    palette.setColor(QPalette.Text, QColor(colors['text_primary']))
    palette.setColor(QPalette.Button, QColor(colors['tertiary_bg']))
    palette.setColor(QPalette.ButtonText, QColor(colors['text_primary']))
    palette.setColor(QPalette.BrightText, QColor('#ffffff'))
    palette.setColor(QPalette.Link, QColor(colors['accent']))
    palette.setColor(QPalette.Highlight, QColor(colors['accent']))
    palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))

    # Отключенные элементы
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(colors['text_disabled']))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(colors['text_disabled']))
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(colors['text_disabled']))

    app.setPalette(palette)
