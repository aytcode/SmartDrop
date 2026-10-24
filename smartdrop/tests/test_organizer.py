import pytest
from pathlib import Path
from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager
from smartdrop.models.config import SmartDropConfig
from smartdrop.utils.test_helper import create_sample_test_folder


def test_organize_files(tmp_path):
    downloads = tmp_path / "Downloads"
    create_sample_test_folder(downloads)

    history_file = tmp_path / "test_history.json"
    undo_mgr = UndoManager(history_file)
    organizer = FileOrganizer(undo_mgr)

    scanner = FolderScanner()
    items = scanner.scan(downloads)

    result = organizer.organize(downloads, items)

    assert result["successful_moves"] > 0
    assert result["failed_moves"] == 0

    # Verify moved files exist in category folders
    assert (downloads / "Images" / "photo.jpg").exists()
    assert (downloads / "Documents" / "document.pdf").exists()
    assert (downloads / "Code" / "script.py").exists()
    assert (downloads / "Others" / "unknown.xyz").exists()

    # Original files should no longer be at root
    assert not (downloads / "photo.jpg").exists()
    assert not (downloads / "document.pdf").exists()


def test_collision_handling_zero_overwrite(tmp_path):
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    # Put a pre-existing file in the destination folder
    img_dir = downloads / "Images"
    img_dir.mkdir()
    (img_dir / "photo.jpg").write_text("existing target content")

    # Put a new photo in the root downloads to be organized
    (downloads / "photo.jpg").write_text("new incoming content")

    history_file = tmp_path / "test_history.json"
    undo_mgr = UndoManager(history_file)
    organizer = FileOrganizer(undo_mgr)

    scanner = FolderScanner()
    items = scanner.scan(downloads)

    result = organizer.organize(downloads, items)

    assert result["successful_moves"] == 1
    # Check that the existing file was NOT overwritten!
    assert (img_dir / "photo.jpg").read_text() == "existing target content"
    # The new file must be renamed safely to 'photo (1).jpg'
    assert (img_dir / "photo (1).jpg").exists()
    assert (img_dir / "photo (1).jpg").read_text() == "new incoming content"
