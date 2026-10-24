import pytest
from pathlib import Path
from smartdrop.core.classifier import FileClassifier
from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager


def test_classification_of_all_specified_types(tmp_path):
    """
    Creates the required 15 test files in a temporary pytest folder
    and automatically verifies each file is routed to the exact expected category.
    """
    expected_categories = {
        "photo.jpg": "Images",
        "image.png": "Images",
        "document.pdf": "Documents",
        "notes.txt": "Documents",
        "video.mp4": "Videos",
        "song.mp3": "Audio",
        "archive.zip": "Archives",
        "script.py": "Code",
        "app.js": "Code",
        "data.csv": "Spreadsheets",
        "table.xlsx": "Spreadsheets",
        "slides.pptx": "Presentations",
        "program.exe": "Installers",
        "font.ttf": "Fonts",
        "unknown.xyz": "Others",
    }

    # Create dummy files
    for filename in expected_categories:
        (tmp_path / filename).write_bytes(b"dummy test content for " + filename.encode())

    # Step 1: Scan
    scanner = FolderScanner()
    items = scanner.scan(tmp_path)
    assert len(items) == len(expected_categories), f"Expected {len(expected_categories)} items, got {len(items)}"

    item_map = {it.original_name: it for it in items}
    for filename, expected_cat in expected_categories.items():
        assert filename in item_map, f"Missing scanned file: {filename}"
        assert item_map[filename].category == expected_cat, (
            f"File '{filename}' categorized as '{item_map[filename].category}', expected '{expected_cat}'"
        )

    # Step 2: Organize and verify on filesystem
    history_file = tmp_path / "test_hist.json"
    organizer = FileOrganizer(UndoManager(history_file))
    result = organizer.organize(tmp_path, items)

    assert result["successful_moves"] == len(expected_categories)
    assert result["failed_moves"] == 0

    # Step 3: Check each file exists in its category folder
    for filename, expected_cat in expected_categories.items():
        expected_path = tmp_path / expected_cat / filename
        assert expected_path.exists(), f"File '{filename}' not found in category directory '{expected_cat}/'"


def test_classifier_unit_rules():
    """Unit test for FileClassifier mappings and fallback to Others."""
    classifier = FileClassifier()
    assert classifier.classify(Path("sample.jpg")) == "Images"
    assert classifier.classify(Path("sample.png")) == "Images"
    assert classifier.classify(Path("sample.pdf")) == "Documents"
    assert classifier.classify(Path("sample.txt")) == "Documents"
    assert classifier.classify(Path("sample.mp4")) == "Videos"
    assert classifier.classify(Path("sample.mp3")) == "Audio"
    assert classifier.classify(Path("sample.zip")) == "Archives"
    assert classifier.classify(Path("sample.py")) == "Code"
    assert classifier.classify(Path("sample.js")) == "Code"
    assert classifier.classify(Path("sample.csv")) == "Spreadsheets"
    assert classifier.classify(Path("sample.xlsx")) == "Spreadsheets"
    assert classifier.classify(Path("sample.pptx")) == "Presentations"
    assert classifier.classify(Path("sample.exe")) == "Installers"
    assert classifier.classify(Path("sample.ttf")) == "Fonts"
    assert classifier.classify(Path("sample.xyz")) == "Others"


def test_language_specific_turkish_organization(tmp_path):
    """
    Tests organizing files into Turkish category folder names:
    Belgeler, Resimler, Videolar, Müzikler, Arşivler, Kodlar, Tablolar, Sunumlar, Kurulumlar, Yazı Tipleri, Diğerleri
    """
    from smartdrop.models.config import SmartDropConfig

    folder = tmp_path / "TurkishDownloads"
    folder.mkdir()

    (folder / "evrak.pdf").write_text("evrak")
    (folder / "manzara.jpg").write_text("resim")
    (folder / "melodi.mp3").write_text("muzik")
    (folder / "program.exe").write_text("kurulum")
    (folder / "bilinmeyen.xyz").write_text("diger")

    config = SmartDropConfig(language="tr")
    scanner = FolderScanner(config)
    items = scanner.scan(folder)

    item_map = {it.original_name: it.target_folder_name for it in items}
    assert item_map["evrak.pdf"] == "Belgeler"
    assert item_map["manzara.jpg"] == "Resimler"
    assert item_map["melodi.mp3"] == "Müzikler"
    assert item_map["program.exe"] == "Kurulumlar"
    assert item_map["bilinmeyen.xyz"] == "Diğerleri"

    organizer = FileOrganizer(UndoManager(tmp_path / "tr_hist.json"))
    res = organizer.organize(folder, items)
    assert res["successful_moves"] == 5

    assert (folder / "Belgeler" / "evrak.pdf").exists()
    assert (folder / "Resimler" / "manzara.jpg").exists()
    assert (folder / "Müzikler" / "melodi.mp3").exists()
    assert (folder / "Kurulumlar" / "program.exe").exists()
    assert (folder / "Diğerleri" / "bilinmeyen.xyz").exists()


def test_language_specific_german_organization(tmp_path):
    """
    Tests organizing files into German category folder names:
    Dokumente, Bilder, etc.
    """
    from smartdrop.models.config import SmartDropConfig

    folder = tmp_path / "GermanDownloads"
    folder.mkdir()

    (folder / "brief.pdf").write_text("brief")
    (folder / "foto.png").write_text("foto")

    config = SmartDropConfig(language="de")
    scanner = FolderScanner(config)
    items = scanner.scan(folder)

    item_map = {it.original_name: it.target_folder_name for it in items}
    assert item_map["brief.pdf"] == "Dokumente"
    assert item_map["foto.png"] == "Bilder"

    organizer = FileOrganizer(UndoManager(tmp_path / "de_hist.json"))
    res = organizer.organize(folder, items)
    assert res["successful_moves"] == 2
    assert (folder / "Dokumente" / "brief.pdf").exists()
    assert (folder / "Bilder" / "foto.png").exists()
