import pytest
from pathlib import Path
from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager
from smartdrop.core.classifier import FileClassifier


def test_unknown_extension_goes_to_others(tmp_path):
    """
    Verifies that 'unknown.xyz' is categorized into 'Others' and moved to 'Others/' folder.
    """
    folder = tmp_path / "UnknownExtTest"
    folder.mkdir()

    unknown_files = [
        "unknown.xyz",
        "custom_binary.dat99",
        "no_extension_file",
        "weird_format.foo_bar",
    ]

    for name in unknown_files:
        (folder / name).write_bytes(b"arbitrary format")

    scanner = FolderScanner()
    items = scanner.scan(folder)
    assert len(items) == len(unknown_files)

    for it in items:
        assert it.category == "Others", f"File '{it.original_name}' was categorized as '{it.category}', expected 'Others'"
        assert it.target_folder_name == "Others"

    # Organize
    history_file = tmp_path / "hist.json"
    organizer = FileOrganizer(UndoManager(history_file))
    res = organizer.organize(folder, items)

    assert res["successful_moves"] == len(unknown_files)
    assert res["failed_moves"] == 0

    for name in unknown_files:
        assert (folder / "Others" / name).exists(), f"File '{name}' not found in 'Others/' directory"


def test_empty_directory_scan_and_organize(tmp_path):
    """
    Scanning an empty directory must succeed cleanly without throwing any exception.
    """
    empty_dir = tmp_path / "EmptyDownloads"
    empty_dir.mkdir()

    scanner = FolderScanner()
    items = scanner.scan(empty_dir)

    assert items == []
    assert len(items) == 0

    # Organizing empty items list must complete safely
    history_file = tmp_path / "hist.json"
    organizer = FileOrganizer(UndoManager(history_file))
    res = organizer.organize(empty_dir, items)

    assert res["total_files"] == 0
    assert res["successful_moves"] == 0
    assert res["failed_moves"] == 0
