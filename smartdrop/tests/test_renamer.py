import pytest
from pathlib import Path
from smartdrop.core.renamer import SmartRenamer


def test_sanitize_filename():
    unsafe = 'my<cool>:file*name?"test".png'
    cleaned = SmartRenamer.sanitize_name(unsafe)
    assert "<" not in cleaned
    assert ">" not in cleaned
    assert ":" not in cleaned
    assert "*" not in cleaned
    assert "?" not in cleaned
    assert '"' not in cleaned


def test_suggest_smart_name_camera():
    path = Path("IMG_20260920_1832.png")
    suggested = SmartRenamer.suggest_smart_name(path, "Images")
    assert suggested == "photo_20260920_1832.png"

    vid = Path("VID_20260920_183210.mp4")
    suggested_vid = SmartRenamer.suggest_smart_name(vid, "Videos")
    assert suggested_vid == "video_20260920_183210.mp4"


def test_suggest_smart_name_browser_copy():
    doc = Path("document(4).pdf")
    suggested = SmartRenamer.suggest_smart_name(doc, "Documents")
    assert suggested == "document_4.pdf"

    report = Path("Monthly Report (1).xlsx")
    suggested_rep = SmartRenamer.suggest_smart_name(report, "Spreadsheets")
    assert suggested_rep == "Monthly_Report_1.xlsx"


def test_already_clean_name_returns_none():
    clean = Path("clean_project_summary.pdf")
    assert SmartRenamer.suggest_smart_name(clean, "Documents") is None
