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
    QListWidget, QSplitter, QProgressBar
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
        self.setWindowTitle("Advanced Installer Project Builder")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

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

        # Icon selection
        icon_group = QGroupBox("Конвертация иконки")
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

        # Preview
        self.icon_preview = QLabel()
        self.icon_preview.setFixedSize(256, 256)
        self.icon_preview.setAlignment(Qt.AlignCenter)
        self.icon_preview.setStyleSheet("border: 1px solid #ccc; background: #f0f0f0;")
        self.icon_preview.setText("Предпросмотр")

        icon_layout.addWidget(self.icon_preview, alignment=Qt.AlignCenter)

        # Convert button
        convert_btn = QPushButton("Конвертировать и применить к проекту")
        convert_btn.clicked.connect(self.convert_and_apply_icon)

        icon_layout.addWidget(convert_btn)

        icon_group.setLayout(icon_layout)
        layout.addWidget(icon_group)
        layout.addStretch()

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

        # Splitter for editor and versions
        splitter = QSplitter(Qt.Horizontal)

        # Editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout()

        self.ps_editor_text = QTextEdit()
        editor_layout.addWidget(QLabel("Содержимое скрипта:"))
        editor_layout.addWidget(self.ps_editor_text)

        # Editor buttons
        editor_btn_layout = QHBoxLayout()

        save_ps_btn = QPushButton("Сохранить")
        save_ps_btn.clicked.connect(self.save_ps_script)

        create_version_btn = QPushButton("Создать версию")
        create_version_btn.clicked.connect(self.create_ps_version)

        editor_btn_layout.addWidget(save_ps_btn)
        editor_btn_layout.addWidget(create_version_btn)
        editor_btn_layout.addStretch()

        editor_layout.addLayout(editor_btn_layout)
        editor_widget.setLayout(editor_layout)

        # Versions list
        versions_widget = QWidget()
        versions_layout = QVBoxLayout()

        versions_layout.addWidget(QLabel("Версии:"))
        self.ps_versions_list = QListWidget()
        self.ps_versions_list.itemDoubleClicked.connect(self.restore_ps_version)

        versions_layout.addWidget(self.ps_versions_list)

        refresh_versions_btn = QPushButton("Обновить список")
        refresh_versions_btn.clicked.connect(self.refresh_ps_versions)

        versions_layout.addWidget(refresh_versions_btn)
        versions_widget.setLayout(versions_layout)

        splitter.addWidget(editor_widget)
        splitter.addWidget(versions_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Редактор PowerShell")

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

            # Update AIP file
            self.aip_manager.update_icon(result['bmp'])
            self.aip_manager.save()

            self.statusBar().showMessage("Иконка конвертирована и применена")
            QMessageBox.information(
                self,
                "Успех",
                f"Иконка успешно конвертирована:\n"
                f"ICO: {Path(result['ico']).name}\n"
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

            # Load content
            content = self.ps_editor.read_script()
            self.ps_editor_text.setPlainText(content)

            # Refresh versions list
            self.refresh_ps_versions()

            self.statusBar().showMessage(f"Скрипт загружен: {Path(ps_path).name}")

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

    def refresh_ps_versions(self):
        """Refresh the PowerShell versions list."""
        if not self.ps_editor:
            return

        self.ps_versions_list.clear()

        versions = self.ps_editor.list_versions()

        for version in versions:
            item_text = f"{version['name']} ({version['modified'].strftime('%Y-%m-%d %H:%M')})"
            self.ps_versions_list.addItem(item_text)
            # Store the path in item data
            item = self.ps_versions_list.item(self.ps_versions_list.count() - 1)
            item.setData(Qt.UserRole, version['path'])

    def restore_ps_version(self, item):
        """Restore a PowerShell script version."""
        if not self.ps_editor:
            return

        version_path = item.data(Qt.UserRole)

        reply = QMessageBox.question(
            self,
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

                self.statusBar().showMessage("Версия восстановлена")
                QMessageBox.information(self, "Успех", "Версия успешно восстановлена!")

                # Refresh versions
                self.refresh_ps_versions()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось восстановить версию:\n{str(e)}")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
