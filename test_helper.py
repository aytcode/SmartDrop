from pathlib import Path
from typing import List, Dict, Any


SAMPLE_FILES: List[Dict[str, Any]] = [
    {"name": "photo.jpg", "content": b"Mock JPEG header\xFF\xD8\xFF\xE0"},
    {"name": "document.pdf", "content": b"%PDF-1.4 Mock PDF content"},
    {"name": "video.mp4", "content": b"\x00\x00\x00 ftypisom Mock Video"},
    {"name": "song.mp3", "content": b"ID3 Mock Audio Track"},
    {"name": "archive.zip", "content": b"PK\x03\x04 Mock Zip Content"},
    {"name": "script.py", "content": "print('Hello from SmartDrop test!')\n".encode("utf-8")},
    {"name": "data.csv", "content": "id,name,value\n1,Alpha,100\n2,Beta,200\n".encode("utf-8")},
    {"name": "presentation.pptx", "content": b"PK\x03\x04 Presentation content"},
    {"name": "installer.exe", "content": b"MZ Mock Executable Binary"},
    {"name": "font.ttf", "content": b"\x00\x01\x00\x00 Mock TrueType Font"},
    {"name": "unknown.xyz", "content": b"Arbitrary binary file"},
    # Edge case sample files
    {"name": "türkçe_karakterli_dosya_şubat_2026.docx", "content": b"Turkish file name test"},
    {"name": "dosya ile bosluk iceren muzik.flac", "content": b"fLaC Mock Flac Audio"},
    {"name": "IMG_20260920_1832.png", "content": b"\x89PNG\r\n\x1a\n Mock camera screenshot"},
    {"name": "rapor(4).pdf", "content": b"%PDF-1.4 Mock report copy 4"},
    {"name": "cok_uzun_dosya_adi_test_smartdrop_kategori_denemesi_ve_guvenlik_kontrolu_tam_liste.json", "content": '{"test": true}'.encode("utf-8")},
]


def create_sample_test_folder(target_dir: Path) -> List[Path]:
    """
    Creates the sample downloads directory and populates it with diverse test files.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    created: List[Path] = []

    for item in SAMPLE_FILES:
        file_path = target_dir / item["name"]
        file_path.write_bytes(item["content"])
        created.append(file_path)

    return created
