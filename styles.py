"""
Modern Windows 11 Fluent design QSS stylesheets for SmartDrop.
Enhanced with a sleek obsidian black aesthetic, luminous accents, and high-contrast typography.
"""

DARK_THEME_QSS = """
QMainWindow, QDialog {
    background-color: #090a0f;
    color: #f1f5f9;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #f1f5f9;
}

QGroupBox {
    border: 1px solid #1c2130;
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 16px;
    font-weight: 600;
    color: #94a3b8;
    background-color: #0e1017;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #818cf8;
}

QLineEdit {
    background-color: #0a0b10;
    border: 1px solid #1e2436;
    border-radius: 8px;
    padding: 9px 14px;
    color: #f8fafc;
    selection-background-color: #4f46e5;
}

QLineEdit:focus {
    border: 1px solid #6366f1;
    background-color: #0e1017;
}

QPushButton {
    background-color: #141724;
    border: 1px solid #22293e;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 500;
    color: #f1f5f9;
}

QPushButton:hover {
    background-color: #1e2338;
    border-color: #313a56;
}

QPushButton:pressed {
    background-color: #0f121d;
}

QPushButton:disabled {
    background-color: #0b0c13;
    border-color: #141722;
    color: #475569;
}

QPushButton#primaryButton {
    background-color: #4f46e5;
    border: 1px solid #6366f1;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #4338ca;
    border-color: #818cf8;
}

QPushButton#accentButton {
    background-color: #059669;
    border: 1px solid #10b981;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#accentButton:hover {
    background-color: #047857;
    border-color: #34d399;
}

QPushButton#undoButton {
    background-color: #181926;
    border: 1px solid #373347;
    color: #fbbf24;
    font-weight: 500;
}

QPushButton#undoButton:hover {
    background-color: #262438;
    border-color: #f59e0b;
}

QTableWidget {
    background-color: #0a0b10;
    border: 1px solid #1a1f2e;
    border-radius: 10px;
    gridline-color: #151824;
    color: #e2e8f0;
    selection-background-color: #1e1b4b;
    selection-color: #c7d2fe;
}

QTableWidget::item {
    padding: 7px;
    border-bottom: 1px solid #141724;
}

QHeaderView::section {
    background-color: #0e1017;
    color: #94a3b8;
    padding: 9px;
    border: none;
    border-bottom: 1px solid #1e2436;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QScrollBar:vertical {
    border: none;
    background-color: #0a0b10;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #1f2538;
    min-height: 25px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #313a56;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QProgressBar {
    background-color: #0a0b10;
    border: 1px solid #1a1f2e;
    border-radius: 6px;
    text-align: center;
    color: #e2e8f0;
    font-weight: 600;
    font-size: 11px;
}

QProgressBar::chunk {
    background-color: #4f46e5;
    border-radius: 5px;
}

QComboBox {
    background-color: #0a0b10;
    border: 1px solid #1e2436;
    border-radius: 7px;
    padding: 6px 12px;
    color: #f1f5f9;
}

QComboBox:focus {
    border: 1px solid #6366f1;
}

QComboBox::drop-down {
    border: none;
    width: 22px;
}

QComboBox QAbstractItemView {
    background-color: #0e1017;
    border: 1px solid #22293e;
    selection-background-color: #1e1b4b;
    selection-color: #c7d2fe;
    color: #f1f5f9;
}

QCheckBox {
    color: #e2e8f0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border: 1px solid #2a3147;
    border-radius: 4px;
    background-color: #0a0b10;
}

QCheckBox::indicator:checked {
    background-color: #4f46e5;
    border-color: #6366f1;
}

QTextEdit {
    background-color: #07080b;
    border: 1px solid #161926;
    border-radius: 8px;
    color: #94a3b8;
    font-family: 'Consolas', 'Cascadia Code', monospace;
    font-size: 11px;
    padding: 8px;
}

QLabel {
    color: #cbd5e1;
}

QLabel#statValue {
    font-size: 22px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel#statLabel {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
"""

LIGHT_THEME_QSS = """
QMainWindow, QDialog {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #0f172a;
}

QGroupBox {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 14px;
    font-weight: 600;
    color: #475569;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 4px;
    color: #4f46e5;
}

QLineEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 12px;
    color: #0f172a;
    selection-background-color: #6366f1;
}

QLineEdit:focus {
    border: 1px solid #4f46e5;
}

QPushButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    color: #0f172a;
}

QPushButton:hover {
    background-color: #f1f5f9;
}

QPushButton#primaryButton {
    background-color: #4f46e5;
    border: 1px solid #4338ca;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#accentButton {
    background-color: #10b981;
    border: 1px solid #059669;
    color: #ffffff;
    font-weight: 600;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
    color: #0f172a;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 600;
    font-size: 11px;
}

QProgressBar {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    text-align: center;
    color: #0f172a;
}

QProgressBar::chunk {
    background-color: #4f46e5;
    border-radius: 5px;
}

QTextEdit {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    color: #334155;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}
"""
