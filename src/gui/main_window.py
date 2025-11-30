"""
Main Window for Advanced Installer Project Builder
PyQt5-based GUI application
"""
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
    QFileDialog, QMessageBox, QGroupBox, QFormLayout, QComboBox,
    QListWidget, QSplitter, QProgressBar, QTableWidget, QTableWidgetItem,
    QCheckBox, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon

# Import core modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.aip_manager import AIPManager
from core.build_manager import BuildManager
from utils.image_converter import ImageConverter
from utils.powershell_editor import PowerShellEditor
from gui.modern_dark_theme import apply_modern_dark_theme
from gui.image_preview_widget import ImagePreviewWidget


class BuildThread(QThread):
    """Thread for running builds without blocking the UI."""

    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, build_manager, aip_file, output_folder=None):
        super().__init__()
        self.build_manager = build_manager
        self.aip_file = aip_file
        self.output_folder = output_folder

    def run(self):
        """Run the build process."""
        success = self.build_manager.build_project(
            self.aip_file,
            self.output_folder,
            callback=self.output_callback
        )
        self.finished_signal.emit(success)

    def output_callback(self, message):
        """Callback for build output."""
        self.output_signal.emit(message)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.aip_manager = None
        self.build_manager = BuildManager()
        self.image_converter = ImageConverter()
        self.ps_editor = None
        self.current_aip_path = None

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Advanced Installer Project Builder - Modern Edition")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        central_widget.setLayout(main_layout)

        # Добавляем стильный заголовок
        title_label = QLabel("⚙️ Advanced Installer Project Builder")
        title_label.setAccessibleName("heading")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Project selection section
        project_group = QGroupBox("Проект Advanced Installer")
        project_layout = QHBoxLayout()

        self.project_path_edit = QLineEdit()
        self.project_path_edit.setPlaceholderText("Выберите .aip файл...")
        self.project_path_edit.setReadOnly(True)

        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_aip_file)

        load_btn = QPushButton("Загрузить")
        load_btn.clicked.connect(self.load_project)

        project_layout.addWidget(self.project_path_edit)
        project_layout.addWidget(browse_btn)
        project_layout.addWidget(load_btn)
        project_group.setLayout(project_layout)

        main_layout.addWidget(project_group)

        # Tab widget for different functionalities
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Create tabs
        self.create_project_info_tab()
        self.create_icon_converter_tab()
        self.create_build_tab()
        self.create_powershell_editor_tab()

        # Status bar
        self.statusBar().showMessage("Готов")

    def create_project_info_tab(self):
        """Create the project information tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Info group
        info_group = QGroupBox("Информация о проекте")
        info_layout = QFormLayout()

        self.product_name_edit = QLineEdit()
        self.manufacturer_edit = QLineEdit()
        self.version_edit = QLineEdit()

        info_layout.addRow("Название продукта:", self.product_name_edit)
        info_layout.addRow("Производитель:", self.manufacturer_edit)
        info_layout.addRow("Версия:", self.version_edit)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Buttons
        btn_layout = QHBoxLayout()

        save_info_btn = QPushButton("Сохранить изменения")
        save_info_btn.clicked.connect(self.save_project_info)

        create_backup_btn = QPushButton("Создать резервную копию")
        create_backup_btn.clicked.connect(self.create_backup)

        btn_layout.addWidget(save_info_btn)
        btn_layout.addWidget(create_backup_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        layout.addStretch()

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Информация о проекте")

    def create_icon_converter_tab(self):
        """Create the icon converter tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create splitter for source and result previews
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Icon selection and source preview
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        icon_group = QGroupBox("Исходное изображение")
        icon_layout = QVBoxLayout()

        # File selection
        file_layout = QHBoxLayout()
        self.icon_path_edit = QLineEdit()
        self.icon_path_edit.setPlaceholderText("Выберите .png/.jpg файл...")

        browse_icon_btn = QPushButton("Обзор...")
        browse_icon_btn.clicked.connect(self.browse_icon_file)

        file_layout.addWidget(self.icon_path_edit)
        file_layout.addWidget(browse_icon_btn)

        icon_layout.addLayout(file_layout)

        # Source preview
        self.icon_preview = QLabel()
        self.icon_preview.setObjectName("icon_preview")
        self.icon_preview.setFixedSize(256, 256)
        self.icon_preview.setAlignment(Qt.AlignCenter)
        self.icon_preview.setText("Предпросмотр исходного файла")
        self.icon_preview.setStyleSheet("QLabel { border: 1px solid #555; background: #2a2a2a; }")

        icon_layout.addWidget(self.icon_preview, alignment=Qt.AlignCenter)

        # Convert button
        convert_btn = QPushButton("Конвертировать и применить к проекту")
        convert_btn.clicked.connect(self.convert_and_apply_icon)

        icon_layout.addWidget(convert_btn)

        icon_group.setLayout(icon_layout)
        left_layout.addWidget(icon_group)
        left_layout.addStretch()
        left_widget.setLayout(left_layout)

        # Right side: Generated files preview
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        preview_group = QGroupBox("Сгенерированные файлы")
        preview_layout = QVBoxLayout()

        # Create image preview widget
        self.generated_preview_widget = ImagePreviewWidget()

        preview_layout.addWidget(self.generated_preview_widget)
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        right_widget.setLayout(right_layout)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])  # Set initial sizes

        layout.addWidget(splitter)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Конвертация иконки")

    def create_build_tab(self):
        """Create the build tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Build settings
        settings_group = QGroupBox("Настройки сборки")
        settings_layout = QFormLayout()

        self.advinst_path_edit = QLineEdit()
        if self.build_manager.advinst_path:
            self.advinst_path_edit.setText(self.build_manager.advinst_path)

        browse_advinst_btn = QPushButton("...")
        browse_advinst_btn.clicked.connect(self.browse_advinst_path)

        advinst_layout = QHBoxLayout()
        advinst_layout.addWidget(self.advinst_path_edit)
        advinst_layout.addWidget(browse_advinst_btn)

        self.output_folder_edit = QLineEdit()
        browse_output_btn = QPushButton("...")
        browse_output_btn.clicked.connect(self.browse_output_folder)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_folder_edit)
        output_layout.addWidget(browse_output_btn)

        settings_layout.addRow("Advanced Installer:", advinst_layout)
        settings_layout.addRow("Папка вывода:", output_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Build button
        self.build_btn = QPushButton("Запустить сборку")
        self.build_btn.clicked.connect(self.start_build)
        layout.addWidget(self.build_btn)

        # Progress bar
        self.build_progress = QProgressBar()
        self.build_progress.setVisible(False)
        layout.addWidget(self.build_progress)

        # Build output
        output_group = QGroupBox("Вывод сборки")
        output_layout = QVBoxLayout()

        self.build_output = QTextEdit()
        self.build_output.setReadOnly(True)

        output_layout.addWidget(self.build_output)
        output_group.setLayout(output_layout)

        layout.addWidget(output_group)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Сборка проекта")

    def create_powershell_editor_tab(self):
        """Create the PowerShell editor tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Script selection
        script_group = QGroupBox("PowerShell скрипт")
        script_layout = QHBoxLayout()

        self.ps_script_path_edit = QLineEdit()
        self.ps_script_path_edit.setPlaceholderText("Выберите .ps1 файл...")

        browse_ps_btn = QPushButton("Обзор...")
        browse_ps_btn.clicked.connect(self.browse_ps_script)

        load_ps_btn = QPushButton("Загрузить")
        load_ps_btn.clicked.connect(self.load_ps_script)

        script_layout.addWidget(self.ps_script_path_edit)
        script_layout.addWidget(browse_ps_btn)
        script_layout.addWidget(load_ps_btn)

        script_group.setLayout(script_layout)
        layout.addWidget(script_group)

        # Sub-tabs for different editing modes
        self.ps_edit_tabs = QTabWidget()

        # Parameters tab
        self.create_ps_parameters_tab()

        # URLs tab
        self.create_ps_urls_tab()

        # Sections tab
        self.create_ps_sections_tab()

        # Raw editor tab
        self.create_ps_raw_editor_tab()

        layout.addWidget(self.ps_edit_tabs)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Редактор PowerShell")

    def create_ps_parameters_tab(self):
        """Create the parameters editing tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel("Редактирование переменных из секции $adtSession:")
        layout.addWidget(info_label)

        # Parameters table
        self.ps_params_table = QTableWidget()
        self.ps_params_table.setColumnCount(3)
        self.ps_params_table.setHorizontalHeaderLabels(["Параметр", "Значение", "Тип"])
        self.ps_params_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ps_params_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ps_params_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        layout.addWidget(self.ps_params_table)

        # Buttons
        btn_layout = QHBoxLayout()

        save_params_btn = QPushButton("Сохранить параметры")
        save_params_btn.clicked.connect(self.save_ps_parameters)

        refresh_params_btn = QPushButton("Обновить")
        refresh_params_btn.clicked.connect(self.refresh_ps_parameters)

        btn_layout.addWidget(save_params_btn)
        btn_layout.addWidget(refresh_params_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        tab.setLayout(layout)
        self.ps_edit_tabs.addTab(tab, "Параметры")

    def create_ps_urls_tab(self):
        """Create the URLs editing tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel("Редактирование URL-ссылок для загрузки файлов:")
        layout.addWidget(info_label)

        # URLs table
        self.ps_urls_table = QTableWidget()
        self.ps_urls_table.setColumnCount(2)
        self.ps_urls_table.setHorizontalHeaderLabels(["Переменная", "URL"])
        self.ps_urls_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ps_urls_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        layout.addWidget(self.ps_urls_table)

        # Buttons
        btn_layout = QHBoxLayout()

        save_urls_btn = QPushButton("Сохранить URL")
        save_urls_btn.clicked.connect(self.save_ps_urls)

        refresh_urls_btn = QPushButton("Обновить")
        refresh_urls_btn.clicked.connect(self.refresh_ps_urls)

        btn_layout.addWidget(save_urls_btn)
        btn_layout.addWidget(refresh_urls_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        tab.setLayout(layout)
        self.ps_edit_tabs.addTab(tab, "URL")

    def create_ps_sections_tab(self):
        """Create the sections toggle tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel("Включение/отключение этапов установки:")
        layout.addWidget(info_label)

        # Sections list
        self.ps_sections_layout = QVBoxLayout()
        self.ps_section_checkboxes = {}

        sections_widget = QWidget()
        sections_widget.setLayout(self.ps_sections_layout)

        layout.addWidget(sections_widget)
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()

        save_sections_btn = QPushButton("Сохранить изменения")
        save_sections_btn.clicked.connect(self.save_ps_sections)

        refresh_sections_btn = QPushButton("Обновить")
        refresh_sections_btn.clicked.connect(self.refresh_ps_sections)

        btn_layout.addWidget(save_sections_btn)
        btn_layout.addWidget(refresh_sections_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        tab.setLayout(layout)
        self.ps_edit_tabs.addTab(tab, "Этапы установки")

    def create_ps_raw_editor_tab(self):
        """Create the raw text editor tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel("Прямое редактирование скрипта (для опытных пользователей):")
        layout.addWidget(info_label)

        # Editor
        self.ps_editor_text = QTextEdit()
        layout.addWidget(self.ps_editor_text)

        # Buttons
        btn_layout = QHBoxLayout()

        save_ps_btn = QPushButton("Сохранить")
        save_ps_btn.clicked.connect(self.save_ps_script)

        create_version_btn = QPushButton("Создать версию")
        create_version_btn.clicked.connect(self.create_ps_version)

        # Versions list button
        show_versions_btn = QPushButton("Показать версии")
        show_versions_btn.clicked.connect(self.show_ps_versions_dialog)

        btn_layout.addWidget(save_ps_btn)
        btn_layout.addWidget(create_version_btn)
        btn_layout.addWidget(show_versions_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        tab.setLayout(layout)
        self.ps_edit_tabs.addTab(tab, "Текстовый редактор")

    # Event handlers
    def browse_aip_file(self):
        """Browse for AIP file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл проекта Advanced Installer",
            "",
            "Advanced Installer Projects (*.aip)"
        )

        if file_path:
            self.project_path_edit.setText(file_path)

    def load_project(self):
        """Load the selected AIP project."""
        aip_path = self.project_path_edit.text()

        if not aip_path:
            QMessageBox.warning(self, "Ошибка", "Выберите файл проекта")
            return

        try:
            self.aip_manager = AIPManager(aip_path)
            self.current_aip_path = aip_path

            # Load project info
            info = self.aip_manager.get_project_info()
            self.product_name_edit.setText(info.get('ProductName', ''))
            self.manufacturer_edit.setText(info.get('Manufacturer', ''))
            self.version_edit.setText(info.get('ProductVersion', ''))

            self.statusBar().showMessage(f"Проект загружен: {Path(aip_path).name}")
            QMessageBox.information(self, "Успех", "Проект успешно загружен!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить проект:\n{str(e)}")

    def save_project_info(self):
        """Save project information changes."""
        if not self.aip_manager:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите проект")
            return

        try:
            results = self.aip_manager.update_project_info(
                product_name=self.product_name_edit.text(),
                manufacturer=self.manufacturer_edit.text(),
                version=self.version_edit.text()
            )

            self.aip_manager.save()

            self.statusBar().showMessage("Изменения сохранены")
            QMessageBox.information(self, "Успех", "Информация о проекте обновлена!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{str(e)}")

    def create_backup(self):
        """Create a backup of the current project."""
        if not self.aip_manager:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите проект")
            return

        try:
            backup_path = self.aip_manager.create_backup()
            QMessageBox.information(self, "Успех", f"Резервная копия создана:\n{backup_path}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать резервную копию:\n{str(e)}")

    def browse_icon_file(self):
        """Browse for icon file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение для иконки",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if file_path:
            self.icon_path_edit.setText(file_path)

            # Show preview
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    256, 256,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.icon_preview.setPixmap(scaled_pixmap)

    def convert_and_apply_icon(self):
        """Convert and apply icon to the project."""
        if not self.aip_manager:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите проект")
            return

        icon_path = self.icon_path_edit.text()

        if not icon_path:
            QMessageBox.warning(self, "Ошибка", "Выберите изображение для конвертации")
            return

        try:
            # Get project directory
            project_dir = Path(self.current_aip_path).parent

            # Convert image
            result = self.image_converter.convert_image_for_installer(
                icon_path,
                str(project_dir),
                base_name=Path(self.current_aip_path).stem + "Icon"
            )

            # Extract ICO sizes for preview
            ico_images = self.image_converter.extract_ico_sizes(result['ico'])

            # Update AIP file
            self.aip_manager.update_icon(result['bmp'])
            self.aip_manager.save()

            # Show preview of generated files
            self.generated_preview_widget.load_previews(
                bmp_path=result['bmp'],
                ico_path=result['ico'],
                ico_images=ico_images
            )

            self.statusBar().showMessage("Иконка конвертирована и применена")
            QMessageBox.information(
                self,
                "Успех",
                f"Иконка успешно конвертирована:\n"
                f"ICO: {Path(result['ico']).name} ({len(ico_images)} размеров)\n"
                f"BMP: {Path(result['bmp']).name}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось конвертировать иконку:\n{str(e)}")

    def browse_advinst_path(self):
        """Browse for Advanced Installer executable."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите AdvancedInstaller.com",
            "",
            "Executable (*.com *.exe)"
        )

        if file_path:
            self.advinst_path_edit.setText(file_path)
            self.build_manager.set_advanced_installer_path(file_path)

    def browse_output_folder(self):
        """Browse for output folder."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для вывода"
        )

        if folder_path:
            self.output_folder_edit.setText(folder_path)

    def start_build(self):
        """Start the build process."""
        if not self.current_aip_path:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите проект")
            return

        if not self.build_manager.is_advanced_installer_available():
            advinst_path = self.advinst_path_edit.text()
            if advinst_path:
                self.build_manager.set_advanced_installer_path(advinst_path)
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Advanced Installer не найден. Укажите путь к AdvancedInstaller.com"
                )
                return

        # Clear output
        self.build_output.clear()

        # Disable build button
        self.build_btn.setEnabled(False)
        self.build_progress.setVisible(True)
        self.build_progress.setRange(0, 0)  # Indeterminate progress

        # Start build thread
        output_folder = self.output_folder_edit.text() if self.output_folder_edit.text() else None

        self.build_thread = BuildThread(
            self.build_manager,
            self.current_aip_path,
            output_folder
        )

        self.build_thread.output_signal.connect(self.on_build_output)
        self.build_thread.finished_signal.connect(self.on_build_finished)

        self.build_thread.start()

        self.statusBar().showMessage("Сборка запущена...")

    def on_build_output(self, message):
        """Handle build output messages."""
        self.build_output.append(message.rstrip())

    def on_build_finished(self, success):
        """Handle build completion."""
        self.build_btn.setEnabled(True)
        self.build_progress.setVisible(False)

        if success:
            self.statusBar().showMessage("Сборка завершена успешно!")
            QMessageBox.information(self, "Успех", "Сборка завершена успешно!")
        else:
            self.statusBar().showMessage("Сборка завершилась с ошибкой")
            QMessageBox.warning(self, "Ошибка", "Сборка завершилась с ошибкой. Проверьте вывод.")

    def browse_ps_script(self):
        """Browse for PowerShell script."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите PowerShell скрипт",
            "",
            "PowerShell Scripts (*.ps1)"
        )

        if file_path:
            self.ps_script_path_edit.setText(file_path)

    def load_ps_script(self):
        """Load PowerShell script."""
        ps_path = self.ps_script_path_edit.text()

        if not ps_path:
            QMessageBox.warning(self, "Ошибка", "Выберите PowerShell скрипт")
            return

        try:
            self.ps_editor = PowerShellEditor(ps_path)

            # Load content into raw editor
            content = self.ps_editor.read_script()
            self.ps_editor_text.setPlainText(content)

            # Refresh all tabs
            self.refresh_ps_parameters()
            self.refresh_ps_urls()
            self.refresh_ps_sections()

            self.statusBar().showMessage(f"Скрипт загружен: {Path(ps_path).name}")
            QMessageBox.information(self, "Успех", "Скрипт успешно загружен и распарсен!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить скрипт:\n{str(e)}")

    def save_ps_script(self):
        """Save PowerShell script."""
        if not self.ps_editor:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите скрипт")
            return

        try:
            content = self.ps_editor_text.toPlainText()
            self.ps_editor.write_script(content, create_backup=True)

            self.statusBar().showMessage("Скрипт сохранен")
            QMessageBox.information(self, "Успех", "Скрипт успешно сохранен!")

            # Refresh versions
            self.refresh_ps_versions()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить скрипт:\n{str(e)}")

    def create_ps_version(self):
        """Create a named version of the PowerShell script."""
        if not self.ps_editor:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите скрипт")
            return

        from PyQt5.QtWidgets import QInputDialog

        version_name, ok = QInputDialog.getText(
            self,
            "Создать версию",
            "Введите имя версии:"
        )

        if ok and version_name:
            try:
                version_path = self.ps_editor.create_version(version_name)
                self.statusBar().showMessage(f"Версия создана: {Path(version_path).name}")
                QMessageBox.information(self, "Успех", f"Версия создана:\n{Path(version_path).name}")

                # Refresh versions
                self.refresh_ps_versions()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать версию:\n{str(e)}")

    def refresh_ps_parameters(self):
        """Refresh the parameters table."""
        if not self.ps_editor:
            return

        self.ps_params_table.setRowCount(0)

        parameters = self.ps_editor.get_parameters()

        # Filter only session variables (not URLs)
        session_params = [p for p in parameters if p.section == 'variables' and p.parameter_type != 'url']

        self.ps_params_table.setRowCount(len(session_params))

        for row, param in enumerate(session_params):
            # Parameter name (read-only)
            name_item = QTableWidgetItem(param.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.ps_params_table.setItem(row, 0, name_item)

            # Parameter value (editable)
            value_item = QTableWidgetItem(param.value)
            self.ps_params_table.setItem(row, 1, value_item)

            # Parameter type (read-only)
            type_item = QTableWidgetItem(param.parameter_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.ps_params_table.setItem(row, 2, type_item)

    def save_ps_parameters(self):
        """Save updated parameters to script."""
        if not self.ps_editor:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите скрипт")
            return

        try:
            updates = {}

            # Collect all updated values from table
            for row in range(self.ps_params_table.rowCount()):
                param_name = self.ps_params_table.item(row, 0).text()
                new_value = self.ps_params_table.item(row, 1).text()
                updates[param_name] = new_value

            # Batch update
            results = self.ps_editor.batch_update_parameters(updates, create_backup=True)

            # Reload content
            content = self.ps_editor.read_script()
            self.ps_editor_text.setPlainText(content)

            self.statusBar().showMessage("Параметры сохранены")
            QMessageBox.information(self, "Успех", f"Обновлено параметров: {sum(results.values())}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить параметры:\n{str(e)}")

    def refresh_ps_urls(self):
        """Refresh the URLs table."""
        if not self.ps_editor:
            return

        self.ps_urls_table.setRowCount(0)

        urls = self.ps_editor.get_urls()

        self.ps_urls_table.setRowCount(len(urls))

        for row, url_param in enumerate(urls):
            # Variable name (read-only)
            name_item = QTableWidgetItem(url_param.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.ps_urls_table.setItem(row, 0, name_item)

            # URL value (editable)
            url_item = QTableWidgetItem(url_param.value)
            self.ps_urls_table.setItem(row, 1, url_item)

    def save_ps_urls(self):
        """Save updated URLs to script."""
        if not self.ps_editor:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите скрипт")
            return

        try:
            updates = {}

            # Collect all updated values from table
            for row in range(self.ps_urls_table.rowCount()):
                var_name = self.ps_urls_table.item(row, 0).text()
                new_url = self.ps_urls_table.item(row, 1).text()
                updates[var_name] = new_url

            # Batch update
            results = self.ps_editor.batch_update_parameters(updates, create_backup=True)

            # Reload content
            content = self.ps_editor.read_script()
            self.ps_editor_text.setPlainText(content)

            self.statusBar().showMessage("URL сохранены")
            QMessageBox.information(self, "Успех", f"Обновлено URL: {sum(results.values())}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить URL:\n{str(e)}")

    def refresh_ps_sections(self):
        """Refresh the sections checkboxes."""
        if not self.ps_editor:
            return

        # Clear existing checkboxes
        for i in reversed(range(self.ps_sections_layout.count())):
            widget = self.ps_sections_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.ps_section_checkboxes.clear()

        sections = self.ps_editor.get_sections()

        for section in sections:
            checkbox = QCheckBox(f"{section.description} ({section.name})")
            checkbox.setChecked(section.enabled)
            checkbox.setProperty('section_name', section.name)

            self.ps_section_checkboxes[section.name] = checkbox
            self.ps_sections_layout.addWidget(checkbox)

    def save_ps_sections(self):
        """Save section enable/disable states."""
        if not self.ps_editor:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите скрипт")
            return

        try:
            modified = False

            for section_name, checkbox in self.ps_section_checkboxes.items():
                enabled = checkbox.isChecked()
                if self.ps_editor.toggle_section(section_name, enabled, create_backup=not modified):
                    modified = True

            if modified:
                # Reload content
                content = self.ps_editor.read_script()
                self.ps_editor_text.setPlainText(content)

                self.statusBar().showMessage("Секции обновлены")
                QMessageBox.information(self, "Успех", "Состояние секций успешно обновлено!")
            else:
                QMessageBox.information(self, "Информация", "Изменений не обнаружено")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить секции:\n{str(e)}")

    def show_ps_versions_dialog(self):
        """Show versions dialog."""
        if not self.ps_editor:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите скрипт")
            return

        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Версии скрипта")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        versions_list = QListWidget()
        versions = self.ps_editor.list_versions()

        for version in versions:
            item_text = f"{version['name']} ({version['modified'].strftime('%Y-%m-%d %H:%M')})"
            versions_list.addItem(item_text)
            item = versions_list.item(versions_list.count() - 1)
            item.setData(Qt.UserRole, version['path'])

        layout.addWidget(QLabel("Двойной клик для восстановления версии:"))
        layout.addWidget(versions_list)

        # Buttons
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        dialog.setLayout(layout)

        def restore_version(item):
            version_path = item.data(Qt.UserRole)
            reply = QMessageBox.question(
                dialog,
                "Восстановить версию",
                f"Восстановить версию:\n{Path(version_path).name}?\n\n"
                "Текущая версия будет сохранена как резервная копия.",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                try:
                    self.ps_editor.restore_version(version_path, create_backup=True)

                    # Reload content
                    content = self.ps_editor.read_script()
                    self.ps_editor_text.setPlainText(content)

                    # Refresh all tabs
                    self.refresh_ps_parameters()
                    self.refresh_ps_urls()
                    self.refresh_ps_sections()

                    self.statusBar().showMessage("Версия восстановлена")
                    QMessageBox.information(dialog, "Успех", "Версия успешно восстановлена!")
                    dialog.close()

                except Exception as e:
                    QMessageBox.critical(dialog, "Ошибка", f"Не удалось восстановить версию:\n{str(e)}")

        versions_list.itemDoubleClicked.connect(restore_version)

        dialog.exec_()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)

    # Применяем современную темную тему
    apply_modern_dark_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
