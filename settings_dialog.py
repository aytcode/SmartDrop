from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QTabWidget, QWidget, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt
from smartdrop.models.config import SmartDropConfig, DEFAULT_CATEGORY_FOLDERS


class SettingsDialog(QDialog):
    """Settings dialog for SmartDrop configuration options."""

    def __init__(self, config: SmartDropConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("SmartDrop - Ayarlar")
        self.setMinimumSize(560, 480)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # Tab 1: General Options
        tab_general = QWidget()
        vbox_gen = QVBoxLayout(tab_general)

        # Checkboxes
        self.chk_subfolders = QCheckBox("Alt klasörleri de tara (Recursive)")
        self.chk_subfolders.setChecked(self.config.include_subfolders)

        self.chk_ai = QCheckBox("Akıllı AI sınıflandırmasını etkinleştir (İçerik & Anlamsal Analiz)")
        self.chk_ai.setChecked(self.config.use_ai_classification)

        self.chk_rename = QCheckBox("Akıllı dosya adlandırmayı etkinleştir (IMG/DSC temizleme)")
        self.chk_rename.setChecked(self.config.use_smart_rename)

        self.chk_open_folder = QCheckBox("İşlem tamamlandığında hedef klasörü Dosya Gezgini'nde aç")
        self.chk_open_folder.setChecked(self.config.open_folder_after_organize)

        self.chk_hidden = QCheckBox("Gizli ve sistem dosyalarını atla (Önerilen)")
        self.chk_hidden.setChecked(self.config.ignore_hidden_files)

        self.chk_safe_overwrite = QCheckBox("Dosya üzerine yazma koruması (Zorunlu Güvenlik - Kapatılamaz)")
        self.chk_safe_overwrite.setChecked(True)
        self.chk_safe_overwrite.setEnabled(False)

        vbox_gen.addWidget(self.chk_subfolders)
        vbox_gen.addWidget(self.chk_ai)
        vbox_gen.addWidget(self.chk_rename)
        vbox_gen.addWidget(self.chk_open_folder)
        vbox_gen.addWidget(self.chk_hidden)
        vbox_gen.addWidget(self.chk_safe_overwrite)

        # Optional Gemini API Key
        ai_box = QGroupBox("İsteğe Bağlı Gemini AI Entegrasyonu")
        ai_layout = QVBoxLayout(ai_box)
        ai_layout.addWidget(QLabel("Gemini API Anahtarı (Opsiyonel - Boş bırakılırsa yerel kural motoru çalışır):"))
        self.txt_api_key = QLineEdit(self.config.gemini_api_key)
        self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_api_key.setPlaceholderText("AI Studio API Key...")
        ai_layout.addWidget(self.txt_api_key)
        vbox_gen.addWidget(ai_box)
        vbox_gen.addStretch()

        tabs.addTab(tab_general, "Genel Ayarlar")

        # Tab 2: Category Folder Names Customization
        tab_categories = QWidget()
        vbox_cat = QVBoxLayout(tab_categories)
        vbox_cat.addWidget(QLabel("Her kategori için oluşturulacak klasör adını özelleştirin:"))

        self.cat_table = QTableWidget()
        self.cat_table.setColumnCount(2)
        self.cat_table.setHorizontalHeaderLabels(["Kategori", "Özel Klasör Adı"])
        self.cat_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        categories = list(DEFAULT_CATEGORY_FOLDERS.keys())
        self.cat_table.setRowCount(len(categories))

        for idx, cat in enumerate(categories):
            item_cat = QTableWidgetItem(cat)
            item_cat.setFlags(item_cat.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cat_table.setItem(idx, 0, item_cat)

            custom_name = self.config.category_folders.get(cat, cat)
            item_val = QTableWidgetItem(custom_name)
            self.cat_table.setItem(idx, 1, item_val)

        vbox_cat.addWidget(self.cat_table)
        tabs.addTab(tab_categories, "Kategori İsimleri")

        main_layout.addWidget(tabs)

        # Bottom Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("Kaydet")
        btn_save.setObjectName("primaryBtn")
        btn_save.clicked.connect(self._save_and_accept)
        btn_box.addWidget(btn_save)

        main_layout.addLayout(btn_box)

    def _save_and_accept(self):
        self.config.include_subfolders = self.chk_subfolders.isChecked()
        self.config.use_ai_classification = self.chk_ai.isChecked()
        self.config.use_smart_rename = self.chk_rename.isChecked()
        self.config.open_folder_after_organize = self.chk_open_folder.isChecked()
        self.config.ignore_hidden_files = self.chk_hidden.isChecked()
        self.config.gemini_api_key = self.txt_api_key.text().strip()

        # Update category folders
        for row in range(self.cat_table.rowCount()):
            cat = self.cat_table.item(row, 0).text()
            val_item = self.cat_table.item(row, 1)
            val = val_item.text().strip() if val_item else cat
            self.config.category_folders[cat] = val or cat

        self.accept()
