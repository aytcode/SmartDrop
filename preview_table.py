from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QWidget, QHBoxLayout, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
from typing import List, Dict, Callable
from smartdrop.models.file_item import FileItem
from smartdrop.core.classifier import FileClassifier
from smartdrop.utils.file_utils import format_file_size


CATEGORY_COLORS: Dict[str, str] = {
    "Documents": "#3b82f6",
    "Images": "#ec4899",
    "Videos": "#8b5cf6",
    "Audio": "#06b6d4",
    "Archives": "#f59e0b",
    "Code": "#10b981",
    "Spreadsheets": "#14b8a6",
    "Presentations": "#f97316",
    "Installers": "#ef4444",
    "Fonts": "#a855f7",
    "Others": "#64748b"
}


class PreviewTable(QTableWidget):
    """
    Interactive preview table for inspected files before any move operation is committed.
    Allows row-by-row inclusion/exclusion and in-place category/name reassignments.
    """

    selection_changed_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: List[FileItem] = []
        self._init_ui()

    def _init_ui(self):
        headers = ["Seç", "Orijinal Dosya Adı", "Kategori", "Hedef Klasör", "Yeni Dosya Adı", "Boyut", "Durum"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)

    def load_items(self, items: List[FileItem]):
        self.items = items
        self.setRowCount(len(items))

        for row, item in enumerate(items):
            # Column 0: Checkbox
            chk = QCheckBox()
            chk.setChecked(item.is_selected)
            chk.setEnabled(not item.is_skipped)
            chk.stateChanged.connect(lambda state, idx=row: self._on_checkbox_toggled(idx, state))
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.addWidget(chk)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setCellWidget(row, 0, cell_widget)

            # Column 1: Original Name
            item_orig = QTableWidgetItem(item.original_name)
            item_orig.setFlags(item_orig.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, item_orig)

            # Column 2: Category (with dropdown to modify)
            combo = QComboBox()
            categories = FileClassifier.get_all_categories()
            combo.addItems(categories)
            curr_cat_idx = combo.findText(item.category)
            if curr_cat_idx >= 0:
                combo.setCurrentIndex(curr_cat_idx)
            combo.currentTextChanged.connect(lambda new_cat, idx=row: self._on_category_changed(idx, new_cat))
            self.setCellWidget(row, 2, combo)

            # Column 3: Target Folder
            target_str = f"{item.target_folder_name}/"
            item_loc = QTableWidgetItem(target_str)
            item_loc.setFlags(item_loc.flags() & ~Qt.ItemFlag.ItemIsEditable)
            color_hex = CATEGORY_COLORS.get(item.category, "#94a3b8")
            item_loc.setForeground(QBrush(QColor(color_hex)))
            self.setItem(row, 3, item_loc)

            # Column 4: New Name (editable)
            item_new_name = QTableWidgetItem(item.new_name)
            self.setItem(row, 4, item_new_name)

            # Column 5: Size
            size_str = format_file_size(item.size_bytes)
            item_size = QTableWidgetItem(size_str)
            item_size.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_size.setFlags(item_size.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 5, item_size)

            # Column 6: Status
            status_text = "Taşınacak"
            if item.is_skipped:
                status_text = f"Atlandı ({item.skip_reason})"
            elif item.is_renamed:
                status_text = "Adlandırılacak"

            item_status = QTableWidgetItem(status_text)
            item_status.setFlags(item_status.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if item.is_skipped:
                item_status.setForeground(QBrush(QColor("#94a3b8")))
            elif item.is_renamed:
                item_status.setForeground(QBrush(QColor("#38bdf8")))
            else:
                item_status.setForeground(QBrush(QColor("#4ade80")))
            self.setItem(row, 6, item_status)

        self.cellChanged.connect(self._on_cell_changed)
        self.selection_changed_signal.emit()

    def _on_checkbox_toggled(self, row_idx: int, state: int):
        if row_idx < len(self.items):
            self.items[row_idx].is_selected = (state == Qt.CheckState.Checked.value)
            self.selection_changed_signal.emit()

    def _on_category_changed(self, row_idx: int, new_cat: str):
        if row_idx < len(self.items):
            item = self.items[row_idx]
            item.category = new_cat
            item.target_folder_name = new_cat
            item.target_dir = item.original_dir / new_cat
            item.new_path = item.target_dir / item.new_name
            loc_item = self.item(row_idx, 3)
            if loc_item:
                loc_item.setText(f"{new_cat}/")
                color_hex = CATEGORY_COLORS.get(new_cat, "#94a3b8")
                loc_item.setForeground(QBrush(QColor(color_hex)))
            self.selection_changed_signal.emit()

    def _on_cell_changed(self, row: int, column: int):
        if column == 4 and row < len(self.items):
            new_val = self.item(row, column).text().strip()
            if new_val:
                item = self.items[row]
                item.new_name = new_val
                item.new_path = item.target_dir / new_val
                item.is_renamed = (new_val != item.original_name)
                status_item = self.item(row, 6)
                if status_item and not item.is_skipped:
                    if item.is_renamed:
                        status_item.setText("Adlandırılacak")
                        status_item.setForeground(QBrush(QColor("#38bdf8")))
                    else:
                        status_item.setText("Taşınacak")
                        status_item.setForeground(QBrush(QColor("#4ade80")))
                self.selection_changed_signal.emit()

    def set_all_selected(self, selected: bool):
        for row in range(self.rowCount()):
            cell_widget = self.cellWidget(row, 0)
            if cell_widget:
                chk = cell_widget.findChild(QCheckBox)
                if chk and chk.isEnabled():
                    chk.setChecked(selected)
                    if row < len(self.items):
                        self.items[row].is_selected = selected
        self.selection_changed_signal.emit()
