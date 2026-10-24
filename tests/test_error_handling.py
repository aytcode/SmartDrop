import pytest
from pathlib import Path
from unittest.mock import patch
import shutil
from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager


def test_single_file_failure_does_not_abort_batch(tmp_path):
    """
    Verifies that if one file fails to move (simulated via mock or missing file),
    the batch operation does NOT crash, and all remaining files are successfully processed.
    """
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    # Create 4 test files
    files = ["file1.txt", "file2_broken.jpg", "file3.pdf", "file4.py"]
    for f in files:
        (downloads / f).write_text(f"content of {f}")

    scanner = FolderScanner()
    items = scanner.scan(downloads)
    assert len(items) == 4

    history_file = tmp_path / "hist.json"
    organizer = FileOrganizer(UndoManager(history_file))

    # Mock shutil.move to fail ONLY for 'file2_broken.jpg'
    real_move = shutil.move

    def mock_move(src, dst):
        if "file2_broken" in str(src):
            raise PermissionError("Access denied: File is locked by another process")
        return real_move(src, dst)

    with patch("shutil.move", side_effect=mock_move):
        result = organizer.organize(downloads, items)

    # Verifications:
    assert result["total_files"] == 4
    assert result["successful_moves"] == 3
    assert result["failed_moves"] == 1
    assert len(result["errors"]) == 1
    assert "file2_broken" in result["errors"][0]

    # Check that successful files were moved properly
    assert (downloads / "Documents" / "file1.txt").exists()
    assert (downloads / "Documents" / "file3.pdf").exists()
    assert (downloads / "Code" / "file4.py").exists()

    # Broken file still remains at source
    assert (downloads / "file2_broken.jpg").exists()


def test_file_disappears_between_scan_and_organize(tmp_path):
    """If a file is deleted by user or another process after scan, handle gracefully."""
    folder = tmp_path / "GhostTest"
    folder.mkdir()
    (folder / "ghost.txt").write_text("will vanish")
    (folder / "real.txt").write_text("will stay")

    items = FolderScanner().scan(folder)
    assert len(items) == 2

    # Delete ghost.txt before organize
    (folder / "ghost.txt").unlink()

    organizer = FileOrganizer(UndoManager(tmp_path / "hist.json"))
    res = organizer.organize(folder, items)

    assert res["successful_moves"] == 1
    assert res["failed_moves"] == 1
    assert (folder / "Documents" / "real.txt").exists()
