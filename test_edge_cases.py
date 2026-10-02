import pytest
from pathlib import Path
import os
import stat
from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager
from smartdrop.models.config import SmartDropConfig


def test_turkish_characters(tmp_path):
    folder = tmp_path / "TurkishTest"
    folder.mkdir()
    turkish_file = folder / "türkçe_şubat_2026_özel_belge_ıığğ.docx"
    turkish_file.write_text("İçerik")

    scanner = FolderScanner()
    items = scanner.scan(folder)
    assert len(items) == 1
    assert items[0].category == "Documents"

    history_file = tmp_path / "hist.json"
    organizer = FileOrganizer(UndoManager(history_file))
    res = organizer.organize(folder, items)
    assert res["successful_moves"] == 1
    assert (folder / "Documents" / "türkçe_şubat_2026_özel_belge_ıığğ.docx").exists()


def test_spaces_in_filename(tmp_path):
    folder = tmp_path / "SpacesTest"
    folder.mkdir()
    space_file = folder / "my awesome song with spaces.mp3"
    space_file.write_text("audio")

    scanner = FolderScanner()
    items = scanner.scan(folder)
    assert len(items) == 1
    assert items[0].category == "Audio"

    organizer = FileOrganizer(UndoManager(tmp_path / "hist.json"))
    res = organizer.organize(folder, items)
    assert res["successful_moves"] == 1
    assert (folder / "Audio" / "my awesome song with spaces.mp3").exists()


def test_very_long_filename(tmp_path):
    folder = tmp_path / "LongNameTest"
    folder.mkdir()
    long_name = "a" * 150 + ".txt"
    (folder / long_name).write_text("long name content")

    scanner = FolderScanner()
    items = scanner.scan(folder)
    assert len(items) == 1

    organizer = FileOrganizer(UndoManager(tmp_path / "hist.json"))
    res = organizer.organize(folder, items)
    assert res["successful_moves"] == 1
    assert (folder / "Documents" / long_name).exists()


def test_idempotent_repeated_runs(tmp_path):
    folder = tmp_path / "RepeatedTest"
    folder.mkdir()
    (folder / "file.txt").write_text("test")

    history_file = tmp_path / "hist.json"
    undo_mgr = UndoManager(history_file)
    organizer = FileOrganizer(undo_mgr)

    # First run
    scanner = FolderScanner()
    items1 = scanner.scan(folder)
    res1 = organizer.organize(folder, items1)
    assert res1["successful_moves"] == 1
    assert (folder / "Documents" / "file.txt").exists()

    # Second scan: file is already in Documents/file.txt
    items2 = scanner.scan(folder)
    # The scanner should not re-organize it or create Documents/Documents/file.txt
    selected_items2 = [it for it in items2 if it.is_selected and not it.is_skipped]
    assert len(selected_items2) == 0


def test_history_persistence_and_recovery(tmp_path):
    folder = tmp_path / "HistoryRecovery"
    folder.mkdir()
    (folder / "data.csv").write_text("1,2,3")

    history_file = tmp_path / "persisted_history.json"

    # Instance 1: organizes and closes
    undo1 = UndoManager(history_file)
    org1 = FileOrganizer(undo1)
    items = FolderScanner().scan(folder)
    org1.organize(folder, items)
    assert (folder / "Spreadsheets" / "data.csv").exists()

    # Instance 2 (simulating program restarted/crash): reloads history file
    undo2 = UndoManager(history_file)
    active_op = undo2.get_last_active_operation(folder)
    assert active_op is not None
    assert active_op.successful_moves == 1

    # Can undo from the new session
    success, msg, restored, failed = undo2.undo_last_operation(folder)
    assert success is True
    assert (folder / "data.csv").exists()
