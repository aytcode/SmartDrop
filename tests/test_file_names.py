import pytest
from pathlib import Path
from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager


def test_turkish_character_filenames(tmp_path):
    """
    Tests that Turkish characters (ö, ç, ş, ı, ğ, ü) in filenames:
    'ödev.pdf', 'çalışma.docx', 'şarkı.mp3', 'görsel.png'
    are preserved without corruption and properly categorized.
    """
    folder = tmp_path / "TurkishFiles"
    folder.mkdir()

    turkish_files = {
        "ödev.pdf": "Documents",
        "çalışma.docx": "Documents",
        "şarkı.mp3": "Audio",
        "görsel.png": "Images",
    }

    for name in turkish_files:
        (folder / name).write_text(f"Turkish test content for {name}", encoding="utf-8")

    scanner = FolderScanner()
    items = scanner.scan(folder)
    assert len(items) == 4

    item_names = {it.original_name for it in items}
    for name in turkish_files:
        assert name in item_names, f"Turkish file '{name}' was not detected correctly"

    # Organize
    history_file = tmp_path / "hist.json"
    organizer = FileOrganizer(UndoManager(history_file))
    result = organizer.organize(folder, items)

    assert result["successful_moves"] == 4
    assert result["failed_moves"] == 0

    # Verify preserved names in target categories
    for name, expected_cat in turkish_files.items():
        target_path = folder / expected_cat / name
        assert target_path.exists(), f"Turkish file '{name}' did not arrive in '{expected_cat}/'"
        assert target_path.name == name, f"Filename was corrupted: expected '{name}', got '{target_path.name}'"
        assert target_path.read_text(encoding="utf-8") == f"Turkish test content for {name}"


def test_preview_does_not_modify_or_move_files(tmp_path):
    """
    CRITICAL: Verifies that scanning/previewing NEVER moves or deletes any file.
    Files must strictly remain in their original positions until organization is explicitly executed.
    """
    folder = tmp_path / "PreviewCheck"
    folder.mkdir()

    test_files = ["doc.pdf", "img.jpg", "code.py", "ödev.pdf"]
    for f in test_files:
        (folder / f).write_text("preview integrity check")

    # Run scanner multiple times
    scanner = FolderScanner()
    items = scanner.scan(folder)

    assert len(items) == len(test_files)

    # Check every original file still exists in the exact original directory!
    for f in test_files:
        assert (folder / f).exists(), f"File '{f}' was moved during preview scan!"

    # Ensure no category subdirectories were created by the preview
    assert not (folder / "Documents").exists()
    assert not (folder / "Images").exists()
    assert not (folder / "Code").exists()


def test_spaces_and_parentheses_in_filenames(tmp_path):
    """Tests filenames with spaces and parentheses."""
    folder = tmp_path / "SpecialNames"
    folder.mkdir()

    file_name = "My Favorite Song (Remix 2026).mp3"
    (folder / file_name).write_text("audio content")

    items = FolderScanner().scan(folder)
    assert len(items) == 1
    assert items[0].original_name == file_name

    organizer = FileOrganizer(UndoManager(tmp_path / "hist.json"))
    res = organizer.organize(folder, items)
    assert res["successful_moves"] == 1
    assert (folder / "Audio" / file_name).exists()
