import pytest
from pathlib import Path
from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager
from smartdrop.utils.file_utils import resolve_collision


def test_duplicate_collision_resolution(tmp_path):
    """
    Tests that when a file with identical name already exists in target folder,
    the incoming file is saved as 'name (1).ext' without overwriting existing file.
    """
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    # Pre-existing file in target Images/ folder
    images_dir = downloads / "Images"
    images_dir.mkdir()
    target_existing_file = images_dir / "photo.jpg"
    target_existing_file.write_text("ORIGINAL_FILE_CONTENT_DO_NOT_OVERWRITE")

    # Incoming new file with the same name in Downloads root
    incoming_file = downloads / "photo.jpg"
    incoming_file.write_text("INCOMING_NEW_PHOTO_CONTENT")

    history_file = tmp_path / "hist.json"
    organizer = FileOrganizer(UndoManager(history_file))

    scanner = FolderScanner()
    items = scanner.scan(downloads)
    assert len(items) == 1
    assert items[0].original_name == "photo.jpg"

    result = organizer.organize(downloads, items)
    assert result["successful_moves"] == 1
    assert result["failed_moves"] == 0

    # Verification:
    # 1. Original target file exists and its content was NEVER modified
    assert target_existing_file.exists()
    assert target_existing_file.read_text() == "ORIGINAL_FILE_CONTENT_DO_NOT_OVERWRITE"

    # 2. Incoming file was safely renamed to 'photo (1).jpg'
    duplicate_result = images_dir / "photo (1).jpg"
    assert duplicate_result.exists(), "Expected 'photo (1).jpg' to be created"
    assert duplicate_result.read_text() == "INCOMING_NEW_PHOTO_CONTENT"


def test_multiple_duplicate_collisions(tmp_path):
    """
    Tests sequential collision handling:
    existing: photo.jpg, photo (1).jpg -> incoming becomes photo (2).jpg
    """
    target_dir = tmp_path / "Images"
    target_dir.mkdir()

    (target_dir / "photo.jpg").write_text("v0")
    (target_dir / "photo (1).jpg").write_text("v1")

    resolved_name = resolve_collision(target_dir, "photo.jpg")
    assert resolved_name == "photo (2).jpg"


def test_no_overwrite_guarantee(tmp_path):
    """
    Verify that existing destination file retains its original size, content and identity.
    """
    folder = tmp_path / "SafeTest"
    folder.mkdir()
    docs = folder / "Documents"
    docs.mkdir()

    important_doc = docs / "notes.txt"
    important_doc.write_text("CRITICAL_USER_DATA_12345")

    (folder / "notes.txt").write_text("TEMP_DATA")

    organizer = FileOrganizer(UndoManager(tmp_path / "hist.json"))
    items = FolderScanner().scan(folder)
    organizer.organize(folder, items)

    assert important_doc.read_text() == "CRITICAL_USER_DATA_12345"
    assert (docs / "notes (1).txt").exists()
    assert (docs / "notes (1).txt").read_text() == "TEMP_DATA"
