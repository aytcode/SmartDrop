from pathlib import Path
import subprocess
import sys
from typing import List, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog, QMessageBox,
    QProgressBar, QGroupBox, QTextEdit, QFrame, QSplitter, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal

from smartdrop.models.config import SmartDropConfig, LANGUAGE_CATEGORY_NAMES
from smartdrop.models.file_item import FileItem
from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager
from smartdrop.services.logger_service import AppLogger
from smartdrop.ui.preview_table import PreviewTable
from smartdrop.ui.settings_dialog import SettingsDialog
from smartdrop.ui.styles import DARK_THEME_QSS, LIGHT_THEME_QSS
from smartdrop.utils.test_helper import create_sample_test_folder


class ScanWorker(QThread):
    progress = Signal(int, int, str)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, folder_path: Path, config: SmartDropConfig):
        super().__init__()
        self.folder_path = folder_path
        self.config = config

    def run(self):
        try:
            scanner = FolderScanner(self.config)
            items = scanner.scan(
                self.folder_path,
                progress_callback=lambda cur, tot, name: self.progress.emit(cur, tot, name)
            )
            self.finished.emit(items)
        except Exception as e:
            self.error.emit(str(e))


class OrganizeWorker(QThread):
    progress = Signal(int, int, str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, folder_path: Path, items: List[FileItem], undo_manager: UndoManager):
        super().__init__()
        self.folder_path = folder_path
        self.items = items
        self.undo_manager = undo_manager

    def run(self):
        try:
            organizer = FileOrganizer(self.undo_manager)
            result = organizer.organize(
                self.folder_path,
                self.items,
                progress_callback=lambda cur, tot, name: self.progress.emit(cur, tot, name)
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """
    Main application window for SmartDrop Windows Desktop.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartDrop - Akıllı Dosya Düzenleyici")
        self.setMinimumSize(960, 680)

        self.config_path = Path.home() / ".smartdrop_config.json"
        self.config = SmartDropConfig.load(self.config_path)
        self.undo_manager = UndoManager()
        self.logger = AppLogger.get_instance()

        self.selected_folder: Optional[Path] = None
        self.current_items: List[FileItem] = []

        self._init_ui()
        self._apply_theme()
        self.logger.subscribe(self._on_log_entry)
        self.logger.log("SmartDrop başlatıldı. Düzenlenecek bir klasör seçin.")

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        # Header bar
        header_layout = QHBoxLayout()

        title_vbox = QVBoxLayout()
        lbl_title = QLabel("SmartDrop")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: 700; color: #6366f1;")
        lbl_sub = QLabel("Güvenli, Akıllı ve Tam Geri Alınabilir Windows Dosya Düzenleyici")
        lbl_sub.setStyleSheet("font-size: 11px; color: #94a3b8;")
        title_vbox.addWidget(lbl_title)
        title_vbox.addWidget(lbl_sub)
        header_layout.addLayout(title_vbox)

        header_layout.addStretch()

        self.cmb_lang = QComboBox()
        self.cmb_lang.addItem("🇹🇷 Türkçe", "tr")
        self.cmb_lang.addItem("🇬🇧 English", "en")
        self.cmb_lang.addItem("🇩🇪 Deutsch", "de")
        self.cmb_lang.addItem("🇪🇸 Español", "es")
        for i in range(self.cmb_lang.count()):
            if self.cmb_lang.itemData(i) == self.config.language:
                self.cmb_lang.setCurrentIndex(i)
                break
        self.cmb_lang.currentIndexChanged.connect(self._on_language_changed)
        header_layout.addWidget(self.cmb_lang)

        self.btn_theme = QPushButton("☀️ Açık Tema" if self.config.theme == "dark" else "🌙 Koyu Tema")
        self.btn_theme.clicked.connect(self._toggle_theme)
        header_layout.addWidget(self.btn_theme)

        btn_settings = QPushButton("⚙️ Ayarlar")
        btn_settings.clicked.connect(self._open_settings)
        header_layout.addWidget(btn_settings)

        main_layout.addLayout(header_layout)

        # Folder Selection Card
        folder_box = QGroupBox("Klasör Seçimi")
        folder_layout = QHBoxLayout(folder_box)

        self.txt_path = QLineEdit()
        self.txt_path.setPlaceholderText("Lütfen düzenlemek istediğiniz klasörün yolunu seçin...")
        self.txt_path.textChanged.connect(self._on_path_edited)
        folder_layout.addWidget(self.txt_path)

        btn_browse = QPushButton("📁 Klasör Seç")
        btn_browse.setObjectName("primaryBtn")
        btn_browse.clicked.connect(self._browse_folder)
        folder_layout.addWidget(btn_browse)

        btn_create_test = QPushButton("🧪 Test Klasörü Oluştur")
        btn_create_test.clicked.connect(self._create_test_folder)
        folder_layout.addWidget(btn_create_test)

        self.btn_scan = QPushButton("🔍 Tara")
        self.btn_scan.setObjectName("primaryBtn")
        self.btn_scan.clicked.connect(self._start_scan)
        folder_layout.addWidget(self.btn_scan)

        main_layout.addWidget(folder_box)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Statistics summary bar
        self.stats_widget = QFrame()
        self.stats_widget.setStyleSheet("background-color: rgba(30, 41, 59, 0.5); border-radius: 8px; padding: 6px;")
        stats_layout = QHBoxLayout(self.stats_widget)

        self.lbl_stat_total = QLabel("0 Dosya Bulundu")
        self.lbl_stat_move = QLabel("0 Taşınacak")
        self.lbl_stat_move.setStyleSheet("color: #4ade80; font-weight: 600;")
        self.lbl_stat_rename = QLabel("0 Yeniden Adlandırılacak")
        self.lbl_stat_rename.setStyleSheet("color: #38bdf8; font-weight: 600;")
        self.lbl_stat_skipped = QLabel("0 Atlandı")
        self.lbl_stat_skipped.setStyleSheet("color: #94a3b8;")

        stats_layout.addWidget(self.lbl_stat_total)
        stats_layout.addWidget(QLabel("|"))
        stats_layout.addWidget(self.lbl_stat_move)
        stats_layout.addWidget(QLabel("|"))
        stats_layout.addWidget(self.lbl_stat_rename)
        stats_layout.addWidget(QLabel("|"))
        stats_layout.addWidget(self.lbl_stat_skipped)
        stats_layout.addStretch()

        btn_select_all = QPushButton("Tümünü Seç")
        btn_select_all.clicked.connect(lambda: self.preview_table.set_all_selected(True))
        stats_layout.addWidget(btn_select_all)

        btn_deselect_all = QPushButton("Seçimi Kaldır")
        btn_deselect_all.clicked.connect(lambda: self.preview_table.set_all_selected(False))
        stats_layout.addWidget(btn_deselect_all)

        main_layout.addWidget(self.stats_widget)

        # Splitter between Preview Table and Activity Log
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Preview table
        self.preview_table = PreviewTable()
        self.preview_table.selection_changed_signal.connect(self._update_stats)
        splitter.addWidget(self.preview_table)

        # Activity log drawer
        log_widget = QWidget()
        log_vbox = QVBoxLayout(log_widget)
        log_vbox.setContentsMargins(0, 4, 0, 0)
        lbl_log = QLabel("İşlem Günlüğü (Log):")
        lbl_log.setStyleSheet("font-weight: 600; color: #94a3b8; font-size: 11px;")
        log_vbox.addWidget(lbl_log)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(90)
        log_vbox.addWidget(self.log_view)

        splitter.addWidget(log_widget)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        # Bottom Action Bar
        bottom_bar = QHBoxLayout()

        btn_run_tests = QPushButton("🧪 Testleri Çalıştır (pytest)")
        btn_run_tests.clicked.connect(self._run_pytest)
        bottom_bar.addWidget(btn_run_tests)

        bottom_bar.addStretch()

        self.btn_undo = QPushButton("↩️ Son İşlemi Geri Al")
        self.btn_undo.setObjectName("secondaryBtn")
        self.btn_undo.clicked.connect(self._undo_last_operation)
        bottom_bar.addWidget(self.btn_undo)

        self.btn_organize = QPushButton("✨ Düzenlemeyi Başlat")
        self.btn_organize.setObjectName("primaryBtn")
        self.btn_organize.setEnabled(False)
        self.btn_organize.clicked.connect(self._start_organize)
        bottom_bar.addWidget(self.btn_organize)

        main_layout.addLayout(bottom_bar)

    def _apply_theme(self):
        if self.config.theme == "light":
            self.setStyleSheet(LIGHT_THEME_QSS)
            self.btn_theme.setText("🌙 Koyu Tema")
        else:
            self.setStyleSheet(DARK_THEME_QSS)
            self.btn_theme.setText("☀️ Açık Tema")

    def _toggle_theme(self):
        self.config.theme = "light" if self.config.theme == "dark" else "dark"
        self.config.save(self.config_path)
        self._apply_theme()

    def _on_language_changed(self, index: int):
        lang_code = self.cmb_lang.itemData(index)
        self.config.language = lang_code
        lang_defaults = LANGUAGE_CATEGORY_NAMES.get(lang_code, LANGUAGE_CATEGORY_NAMES["en"])
        self.config.category_folders = dict(lang_defaults)
        self.config.save(self.config_path)
        self.logger.log(f"Düzenleme dili '{lang_code}' olarak güncellendi. Hedef klasörler uyarlandı.")
        if self.selected_folder:
            self._start_scan()

    def _open_settings(self):
        dlg = SettingsDialog(self.config, self)
        if dlg.exec():
            self.config.save(self.config_path)
            self.logger.log("Ayarlar kaydedildi.")
            if self.selected_folder:
                self._start_scan()

    def _on_log_entry(self, entry: str):
        self.log_view.append(entry)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Düzenlenecek Klasörü Seçin")
        if folder:
            self.txt_path.setText(folder)
            self.selected_folder = Path(folder)
            self._start_scan()

    def _on_path_edited(self, text: str):
        p = Path(text.strip())
        if p.exists() and p.is_dir():
            self.selected_folder = p
        else:
            self.selected_folder = None
            self.btn_organize.setEnabled(False)

    def _create_test_folder(self):
        test_dir = Path("test_data/sample_downloads").resolve()
        created = create_sample_test_folder(test_dir)
        self.txt_path.setText(str(test_dir))
        self.selected_folder = test_dir
        self.logger.log(f"Test klasörü oluşturuldu: {len(created)} örnek dosya eklendi.")
        QMessageBox.information(
            self,
            "Test Klasörü Hazır",
            f"Test klasörü başarıyla oluşturuldu:\n{test_dir}\n\n{len(created)} adet örnek dosya hazırlandı."
        )
        self._start_scan()

    def _start_scan(self):
        if not self.selected_folder:
            QMessageBox.warning(self, "Klasör Seçilmedi", "Lütfen önce düzenlenecek geçerli bir klasör seçin.")
            return

        self.btn_scan.setEnabled(False)
        self.btn_organize.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.scan_worker = ScanWorker(self.selected_folder, self.config)
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.finished.connect(self._on_scan_finished)
        self.scan_worker.error.connect(self._on_scan_error)
        self.scan_worker.start()

    def _on_scan_progress(self, current: int, total: int, file_name: str):
        pct = int((current / max(total, 1)) * 100)
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"Taranıyor... %p% ({file_name})")

    def _on_scan_finished(self, items: List[FileItem]):
        self.current_items = items
        self.preview_table.load_items(items)
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)

        to_move_count = sum(1 for it in items if it.is_selected and not it.is_skipped)
        self.btn_organize.setEnabled(to_move_count > 0)
        self._update_stats()
        self.logger.log(f"Tarama bitti: {len(items)} dosya incelendi.")

    def _on_scan_error(self, message: str):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.logger.log(f"Tarama hatası: {message}", "ERROR")
        QMessageBox.critical(self, "Tarama Hatası", message)

    def _update_stats(self):
        total = len(self.preview_table.items)
        selected = sum(1 for it in self.preview_table.items if it.is_selected and not it.is_skipped)
        renamed = sum(1 for it in self.preview_table.items if it.is_renamed and it.is_selected)
        skipped = sum(1 for it in self.preview_table.items if it.is_skipped or not it.is_selected)

        self.lbl_stat_total.setText(f"{total} Dosya Bulundu")
        self.lbl_stat_move.setText(f"{selected} Taşınacak")
        self.lbl_stat_rename.setText(f"{renamed} Yeniden Adlandırılacak")
        self.lbl_stat_skipped.setText(f"{skipped} Atlandı")

        self.btn_organize.setEnabled(selected > 0)

    def _start_organize(self):
        selected_count = sum(1 for it in self.preview_table.items if it.is_selected and not it.is_skipped)
        if selected_count == 0:
            QMessageBox.information(self, "Dosya Seçilmedi", "Taşınmak üzere seçilmiş dosya yok.")
            return

        reply = QMessageBox.question(
            self,
            "Düzenlemeyi Onayla",
            f"{selected_count} adet dosya kategorilerine taşınacak.\n"
            "Hiçbir dosya silinmeyecek ve üzerine yazılmayacaktır.\n"
            "İşlem daha sonra 'Geri Al' ile geri alınabilir.\n\n"
            "Devam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.btn_organize.setEnabled(False)
        self.btn_scan.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.org_worker = OrganizeWorker(self.selected_folder, self.preview_table.items, self.undo_manager)
        self.org_worker.progress.connect(self._on_org_progress)
        self.org_worker.finished.connect(self._on_org_finished)
        self.org_worker.error.connect(self._on_org_error)
        self.org_worker.start()

    def _on_org_progress(self, current: int, total: int, file_name: str):
        pct = int((current / max(total, 1)) * 100)
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"Düzenleniyor... %p% ({file_name})")

    def _on_org_finished(self, result: dict):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)

        succ = result.get("successful_moves", 0)
        failed = result.get("failed_moves", 0)

        msg = f"Düzenleme tamamlandı!\nBaşarılı: {succ}\nBaşarısız: {failed}"
        if failed > 0:
            msg += "\n\nHatalar:\n" + "\n".join(result.get("errors", [])[:5])

        QMessageBox.information(self, "İşlem Tamamlandı", msg)

        # Refresh scan to reflect moved files
        self._start_scan()

    def _on_org_error(self, message: str):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.logger.log(f"Düzenleme hatası: {message}", "ERROR")
        QMessageBox.critical(self, "Hata", message)

    def _undo_last_operation(self):
        reply = QMessageBox.question(
            self,
            "Geri Almayı Onayla",
            "Son işlemde taşınan dosyalar eski orijinal konumlarına geri döndürülecektir.\n"
            "Devam edilsin mi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        success, message, restored, failed = self.undo_manager.undo_last_operation(
            str(self.selected_folder) if self.selected_folder else None
        )

        if success:
            QMessageBox.information(self, "Geri Alındı", message)
            if self.selected_folder:
                self._start_scan()
        else:
            QMessageBox.warning(self, "Geri Alma Yapılamadı", message)

    def _run_pytest(self):
        self.logger.log("Pytest testleri başlatılıyor...")
        try:
            res = subprocess.run(
                [sys.executable, "-m", "pytest", "-v"],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = res.stdout or res.stderr
            if res.returncode == 0:
                self.logger.log("Tüm pytest testleri başarıyla GEÇTİ!", "INFO")
                QMessageBox.information(self, "Testler Başarılı", f"Tüm testler geçti:\n\n{output[-500:]}")
            else:
                self.logger.log("Bazı testler başarısız oldu.", "WARNING")
                QMessageBox.warning(self, "Test Sonucu", f"Test çıktısı:\n\n{output[-600:]}")
        except Exception as e:
            self.logger.log(f"Testler çalıştırılırken hata: {e}", "ERROR")
            QMessageBox.critical(self, "Hata", str(e))
