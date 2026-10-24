import pytest
from pathlib import Path
from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager


def test_undo_restores_all_files_to_original_location(tmp_path):
    """
    Organizes multiple files, verifies their migration,
    then executes undo and verifies that all files return to their exact original locations.
    """
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    test_files = [
        "photo.jpg",
        "document.pdf",
        "script.py",
        "song.mp3",
        "notes.txt",
    ]

    for name in test_files:
        (downloads / name).write_text(f"content of {name}")

    history_file = tmp_path / "undo_hist.json"
    undo_mgr = UndoManager(history_file)
    organizer = FileOrganizer(undo_mgr)

    # Step 1: Scan and Organize
    scanner = FolderScanner()
    items = scanner.scan(downloads)
    assert len(items) == len(test_files)

    result = organizer.organize(downloads, items)
    assert result["successful_moves"] == len(test_files)
    assert result["failed_moves"] == 0

    # Ensure none of the files remain in the root downloads
    for name in test_files:
        assert not (downloads / name).exists(), f"File {name} should have moved to category"

    # Step 2: Perform Undo
    success, message, restored, failed = undo_mgr.undo_last_operation(str(downloads))
    assert success is True
    assert restored == len(test_files)
    assert failed == 0

    # Step 3: Verify all files are restored in original root
    for name in test_files:
        restored_file = downloads / name
        assert restored_file.exists(), f"Restored file {name} not found in root"
        assert restored_file.read_text() == f"content of {name}"

    # Step 4: Verify category directories were cleaned up after undo
    assert not (downloads / "Images").exists()
    assert not (downloads / "Documents").exists()
    assert not (downloads / "Code").exists()
    assert not (downloads / "Audio").exists()


def test_undo_when_no_active_operation(tmp_path):
    """Calling undo on empty history returns clean message without error."""
    history_file = tmp_path / "empty_hist.json"
    undo_mgr = UndoManager(history_file)
    success, msg, restored, failed = undo_mgr.undo_last_operation(str(tmp_path))
    assert success is False
    assert "bulunamadı" in msg.lower()
    assert restored == 0
