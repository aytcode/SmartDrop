import pytest
from pathlib import Path
from smartdrop.core.scanner import FolderScanner
from smartdrop.models.config import SmartDropConfig
from smartdrop.utils.test_helper import create_sample_test_folder


def test_scan_default_folder(tmp_path):
    downloads = tmp_path / "Downloads"
    create_sample_test_folder(downloads)

    scanner = FolderScanner()
    items = scanner.scan(downloads)

    assert len(items) > 10
    names = [it.original_name for it in items]
    assert "photo.jpg" in names
    assert "document.pdf" in names
    assert "unknown.xyz" in names

    # Verify categories
    doc_item = next(it for it in items if it.original_name == "document.pdf")
    assert doc_item.category == "Documents"
    assert doc_item.target_folder_name == "Documents"
    assert doc_item.new_path == downloads / "Documents" / "document.pdf"


def test_scan_empty_folder(tmp_path):
    empty = tmp_path / "EmptyDir"
    empty.mkdir()
    scanner = FolderScanner()
    items = scanner.scan(empty)
    assert len(items) == 0


def test_ignore_hidden_files(tmp_path):
    folder = tmp_path / "HiddenTest"
    folder.mkdir()
    (folder / "visible.txt").write_text("hello")
    (folder / ".hidden.txt").write_text("secret")

    config = SmartDropConfig(ignore_hidden_files=True)
    scanner = FolderScanner(config)
    items = scanner.scan(folder)

    names = [it.original_name for it in items]
    assert "visible.txt" in names
    assert ".hidden.txt" not in names


def test_subfolder_scanning(tmp_path):
    folder = tmp_path / "Nested"
    folder.mkdir()
    (folder / "root_file.txt").write_text("root")

    sub = folder / "sub"
    sub.mkdir()
    (sub / "nested_file.pdf").write_text("nested")

    # Without subfolder scanning
    scanner_shallow = FolderScanner(SmartDropConfig(include_subfolders=False))
    items_shallow = scanner_shallow.scan(folder)
    assert len(items_shallow) == 1
    assert items_shallow[0].original_name == "root_file.txt"

    # With subfolder scanning
    scanner_deep = FolderScanner(SmartDropConfig(include_subfolders=True))
    items_deep = scanner_deep.scan(folder)
    names = [it.original_name for it in items_deep]
    assert "root_file.txt" in names
    assert "nested_file.pdf" in names
