#!/usr/bin/env python3
"""
SmartDrop - Windows Desktop File Organizer
Entry point for launching the PySide6 desktop application.
"""
import sys
import os
from pathlib import Path

# Ensure package root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from smartdrop.ui.main_window import MainWindow


def main():
    # Enable High DPI scaling for modern 4K Windows screens
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("SmartDrop")
    app.setOrganizationName("SmartDropOrg")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
