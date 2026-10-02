#!/usr/bin/env python3
"""
SmartDrop Test Data Generator
Safely generates dummy sample files in test_data/sample_downloads for testing.
Never touches real user files.
Usage:
    python tools/create_test_data.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

SAMPLE_DEFINITIONS = [
    # Required test files
    {"name": "photo.jpg", "content": b"\xFF\xD8\xFF\xE0Mock JPG Image Data"},
    {"name": "image.png", "content": b"\x89PNG\r\n\x1a\nMock PNG Image Data"},
    {"name": "document.pdf", "content": b"%PDF-1.4 Mock PDF Document"},
    {"name": "notes.txt", "content": b"Meeting notes and action items."},
    {"name": "video.mp4", "content": b"\x00\x00\x00 ftypisom Mock MP4 Video Data"},
    {"name": "song.mp3", "content": b"ID3 Mock MP3 Audio Data"},
    {"name": "archive.zip", "content": b"PK\x03\x04 Mock Zip Archive"},
    {"name": "script.py", "content": b"print('SmartDrop Test Script')\n"},
    {"name": "app.js", "content": b"console.log('SmartDrop Test JS');\n"},
    {"name": "data.csv", "content": b"id,product,price\n1,Laptop,1200\n2,Mouse,25\n"},
    {"name": "table.xlsx", "content": b"PK\x03\x04 Mock Excel Spreadsheet"},
    {"name": "slides.pptx", "content": b"PK\x03\x04 Mock Presentation Slides"},
    {"name": "program.exe", "content": b"MZ Mock Executable Installer"},
    {"name": "font.ttf", "content": b"\x00\x01\x00\x00 Mock TTF Font"},
    {"name": "unknown.xyz", "content": b"Arbitrary unknown binary format"},

    # Turkish character files
    {"name": "ödev.pdf", "content": b"%PDF-1.4 Odev dosyasi"},
    {"name": "çalışma.docx", "content": b"PK\x03\x04 Calisma dokumani"},
    {"name": "şarkı.mp3", "content": b"ID3 Sarki ses dosyasi"},
    {"name": "görsel.png", "content": b"\x89PNG\r\n\x1a\nGorsel resim dosyasi"},

    # Duplicate / naming edge cases
    {"name": "IMG_20260920_1832.png", "content": b"\x89PNG\r\n\x1a\nCamera Photo"},
    {"name": "report(4).pdf", "content": b"%PDF-1.4 Report Copy 4"},
    {"name": "space separated audio track.wav", "content": b"RIFF Mock Wav Audio"},
]


def create_test_data(target_dir: Path = None) -> Path:
    if target_dir is None:
        target_dir = BASE_DIR / "test_data" / "sample_downloads"

    target_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  SmartDrop Test Verisi Oluşturucu")
    print("=" * 60)
    print(f"Hedef Klasör: {target_dir}")
    print("Örnek test dosyaları oluşturuluyor...\n")

    created = 0
    for item in SAMPLE_DEFINITIONS:
        file_path = target_dir / item["name"]
        file_path.write_bytes(item["content"])
        created += 1
        print(f"  [+] {item['name']}")

    print("\n" + "=" * 60)
    print(f"Başarıyla {created} adet güvenli test dosyası oluşturuldu.")
    print("Gerçek kullanıcı dosyalarına kesinlikle dokunulmamıştır.")
    print("=" * 60)
    return target_dir


if __name__ == "__main__":
    create_test_data()
