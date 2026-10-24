import pytest
from pathlib import Path
from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager
from smartdrop.utils.test_helper import create_sample_test_folder


def test_undo_operation(tmp_path):
    downloads = tmp_path / "Downloads"
    create_sample_test_folder(downloads)

    history_file = tmp_path / "test_history.json"
    undo_mgr = UndoManager(history_file)
    organizer = FileOrganizer(undo_mgr)

    scanner = FolderScanner()
    items = scanner.scan(downloads)
    total_scanned = len(items)

    # Step 1: Organize
    result = organizer.organize(downloads, items)
    assert result["successful_moves"] == total_scanned

    # Verify category directories were created
    assert (downloads / "Images").exists()
    assert (downloads / "Documents").exists()

    # Step 2: Undo
    success, msg, restored, failed = undo_mgr.undo_last_operation(downloads)
    assert success is True
    assert restored == total_scanned
    assert failed == 0

    # All files should be back in original root downloads
    assert (downloads / "photo.jpg").exists()
    assert (downloads / "document.pdf").exists()
    assert (downloads / "unknown.xyz").exists()

    # Category directories should have been cleaned up if empty
    assert not (downloads / "Images").exists()


def test_undo_with_source_collision(tmp_path):
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    (downloads / "doc.pdf").write_text("v1")

    history_file = tmp_path / "test_history.json"
    undo_mgr = UndoManager(history_file)
    organizer = FileOrganizer(undo_mgr)

    items = FolderScanner().scan(downloads)
    organizer.organize(downloads, items)
    assert (downloads / "Documents" / "doc.pdf").exists()

    # Suppose a new file with same name "doc.pdf" is created in downloads root before undo
    (downloads / "doc.pdf").write_text("v2 newly created")

    # Undo should NOT overwrite the newly created doc.pdf
    success, msg, restored, failed = undo_mgr.undo_last_operation(downloads)
    assert success is True
    assert (downloads / "doc.pdf").read_text() == "v2 newly created"
    # Restored file will safely be saved as doc (1).pdf
    assert (downloads / "doc (1).pdf").exists()
    assert (downloads / "doc (1).pdf").read_text() == "v1"
