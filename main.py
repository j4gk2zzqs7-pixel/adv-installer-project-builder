"""
Advanced Installer Project Builder - Main Entry Point
Запуск GUI приложения для работы с проектами Advanced Installer
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from gui.main_window import main

if __name__ == '__main__':
    main()
