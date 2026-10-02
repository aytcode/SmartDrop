import pytest
from pathlib import Path
from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager


def test_repeated_runs_idempotency(tmp_path):
    """
    Organizes a folder once, then scans and organizes the same folder again.
    Verifies that already-organized files are not moved or nested unnecessarily.
    """
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    # Initial files
    (downloads / "document.pdf").write_text("pdf content")
    (downloads / "photo.jpg").write_text("photo content")

    history_file = tmp_path / "hist.json"
    undo_mgr = UndoManager(history_file)
    organizer = FileOrganizer(undo_mgr)
    scanner = FolderScanner()

    # --- Run 1 ---
    items_run1 = scanner.scan(downloads)
    assert len(items_run1) == 2
    res_run1 = organizer.organize(downloads, items_run1)
    assert res_run1["successful_moves"] == 2

    assert (downloads / "Documents" / "document.pdf").exists()
    assert (downloads / "Images" / "photo.jpg").exists()

    # --- Run 2 (Immediate re-run without adding new files) ---
    items_run2 = scanner.scan(downloads)

    # In default non-recursive mode, category subdirectories are excluded from re-organizing
    to_move_run2 = [it for it in items_run2 if it.is_selected and not it.is_skipped]
    assert len(to_move_run2) == 0, f"Expected 0 files to move on re-run, but found {len(to_move_run2)}"

    res_run2 = organizer.organize(downloads, items_run2)
    assert res_run2["successful_moves"] == 0
    assert res_run2["failed_moves"] == 0

    # Ensure no nested directories like Documents/Documents/document.pdf were created
    assert not (downloads / "Documents" / "Documents").exists()
    assert not (downloads / "Images" / "Images").exists()


def test_incremental_organization(tmp_path):
    """
    Tests adding a new file after initial organization:
    Only the new incoming file should be organized in the second run.
    """
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    (downloads / "first.pdf").write_text("first")

    history_file = tmp_path / "hist.json"
    undo_mgr = UndoManager(history_file)
    organizer = FileOrganizer(undo_mgr)
    scanner = FolderScanner()

    # First organize
    organizer.organize(downloads, scanner.scan(downloads))
    assert (downloads / "Documents" / "first.pdf").exists()

    # Add a second file
    (downloads / "second.jpg").write_text("second")

    # Second scan & organize
    items_run2 = scanner.scan(downloads)
    to_move = [it for it in items_run2 if it.is_selected and not it.is_skipped]
    assert len(to_move) == 1
    assert to_move[0].original_name == "second.jpg"

    res = organizer.organize(downloads, items_run2)
    assert res["successful_moves"] == 1
    assert (downloads / "Images" / "second.jpg").exists()
    # First file remains intact
    assert (downloads / "Documents" / "first.pdf").exists()
