import pytest
from pathlib import Path
from smartdrop.core.classifier import FileClassifier


def test_standard_categories():
    classifier = FileClassifier()

    assert classifier.classify(Path("photo.jpg")) == "Images"
    assert classifier.classify(Path("picture.PNG")) == "Images"
    assert classifier.classify(Path("image.webp")) == "Images"

    assert classifier.classify(Path("doc.pdf")) == "Documents"
    assert classifier.classify(Path("text.TXT")) == "Documents"
    assert classifier.classify(Path("paper.docx")) == "Documents"

    assert classifier.classify(Path("clip.mp4")) == "Videos"
    assert classifier.classify(Path("movie.mkv")) == "Videos"

    assert classifier.classify(Path("song.mp3")) == "Audio"
    assert classifier.classify(Path("track.flac")) == "Audio"

    assert classifier.classify(Path("bundle.zip")) == "Archives"
    assert classifier.classify(Path("data.tar.gz")) == "Archives"

    assert classifier.classify(Path("main.py")) == "Code"
    assert classifier.classify(Path("app.tsx")) == "Code"
    assert classifier.classify(Path("style.css")) == "Code"

    assert classifier.classify(Path("sheet.xlsx")) == "Spreadsheets"
    assert classifier.classify(Path("table.csv")) == "Spreadsheets"

    assert classifier.classify(Path("deck.pptx")) == "Presentations"
    assert classifier.classify(Path("setup.exe")) == "Installers"
    assert classifier.classify(Path("package.msi")) == "Installers"
    assert classifier.classify(Path("roboto.ttf")) == "Fonts"


def test_unknown_extension():
    classifier = FileClassifier()
    assert classifier.classify(Path("file.xyz")) == "Others"
    assert classifier.classify(Path("random.foobar123")) == "Others"
    assert classifier.classify(Path("no_extension_file")) == "Others"


def test_custom_folder_mapping():
    custom = {"Images": "Resimler", "Documents": "Belgeler"}
    classifier = FileClassifier(custom)
    assert classifier.get_target_folder_name("Images") == "Resimler"
    assert classifier.get_target_folder_name("Documents") == "Belgeler"
    assert classifier.get_target_folder_name("Videos") == "Videos"
