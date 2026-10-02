# SmartDrop

> A safety-first Windows file organizer that turns cluttered folders into a clean, predictable workflow — with preview, collision protection, and undo built in.

![Platform](https://img.shields.io/badge/platform-Windows-0078D4)
![Python](https://img.shields.io/badge/python-3.12%2B-3776AB)
![GUI](https://img.shields.io/badge/GUI-PySide6-41CD52)
![Tests](https://img.shields.io/badge/tests-39%20passed-success)
![License](https://img.shields.io/badge/license-MIT-green)

## Abstract

SmartDrop is a desktop utility for organizing cluttered folders such as `Downloads` or `Desktop` without turning file management into a risky one-click operation.

The application scans a user-selected folder, classifies files into practical categories, and builds a complete preview before anything is moved. Once the user approves the plan, SmartDrop performs collision-safe moves and records the operation so the last batch can be undone.

The project is built around three principles: **preview before action, never overwrite, and always keep a path back**.

## Core Features

- **Preview-first workflow** — inspect every planned move before applying it.
- **Automatic categorization** — Documents, Images, Videos, Audio, Archives, Code, Spreadsheets, Presentations, Installers, Fonts, and Others.
- **Zero-overwrite policy** — existing files are preserved; collisions become `file (1).ext`, `file (2).ext`, and so on.
- **Undo** — restore the last organization batch to its original locations.
- **Safety guard** — protected Windows/system locations are rejected.
- **Background processing** — scanning and organization run off the main UI thread.
- **Operation history** — actions are recorded in `.smartdrop_history.json`.
- **Optional intelligent naming** — cleaner filenames can be suggested without replacing the original file unless approved.
- **Built-in test mode** — generate safe sample files and run automated checks without touching personal data.

## Supported Categories

| Category | Examples |
|---|---|
| Documents | `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.md` |
| Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`, `.bmp` |
| Videos | `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv` |
| Audio | `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg` |
| Archives | `.zip`, `.rar`, `.7z`, `.tar`, `.gz` |
| Code | `.py`, `.js`, `.ts`, `.html`, `.css`, `.json`, `.cpp`, `.java`, `.sql` |
| Spreadsheets | `.xls`, `.xlsx`, `.csv`, `.tsv` |
| Presentations | `.ppt`, `.pptx`, `.key` |
| Installers | `.exe`, `.msi`, `.dmg`, `.pkg` |
| Fonts | `.ttf`, `.otf`, `.woff`, `.woff2` |
| Others | Unknown or extensionless files |

## System Architecture

SmartDrop separates the desktop UI from the file-management engine so individual parts can be tested independently.

```text
SmartDrop
├── ui/                 Desktop interface and preview
├── core/               Scanning, classification, safety, organization, undo
├── services/           Logging and optional intelligent analysis
├── models/             Configuration, file and operation models
├── utils/              File and Windows path helpers
├── tests/              Automated test suite
└── tools/              Safe test-data generator
```

### Core flow

```text
Select Folder
     ↓
Scan Files
     ↓
Classify
     ↓
Build Preview
     ↓
User Approval
     ↓
Safe Organize
     ↓
Operation Log
     ↓
Undo when needed
```

## Installation

### Requirements

- Windows
- Python 3.12+
- pip

### Setup

Open PowerShell in the project folder and run:

```powershell
python -m pip install -r requirements.txt
```

Then start SmartDrop with:

```powershell
python app.py
```

Or double-click:

```text
setup.bat   # install dependencies
run.bat     # launch the application
```

## Safe Testing

SmartDrop includes a dedicated test-data generator so you can try the organizer without using your personal files.

Create sample data:

```powershell
python tools/create_test_data.py
```

This creates:

```text
test_data/sample_downloads/
```

with representative files such as images, documents, archives, code, installers, and unknown extensions.

### Automated tests

Run the full suite:

```powershell
python -m pytest -v
```

The project includes coverage for:

- file classification
- duplicate names and collision handling
- undo
- Turkish characters and unusual filenames
- unknown extensions
- empty folders
- error isolation
- repeated runs / idempotency
- preview safety
- zero-overwrite behavior

Expected report format:

```text
========================================
SMARTDROP TEST REPORT
========================================
Passed:  39
Failed:  0
Skipped: 0
========================================
```

## Safety Model

SmartDrop is intentionally conservative:

- Files are **not deleted** by the organizer.
- Existing files are **never overwritten**.
- Protected Windows locations are rejected.
- No file movement happens during scanning or preview generation.
- Every completed batch is recorded for undo.
- A single failed file does not have to abort the entire batch.

## Project Structure

```text
smartdrop/
├── app.py
├── core/
│   ├── classifier.py
│   ├── organizer.py
│   ├── renamer.py
│   ├── safety.py
│   ├── scanner.py
│   └── undo_manager.py
├── models/
├── services/
├── utils/
├── tests/
└── ui/

tools/
└── create_test_data.py

app.py
requirements.txt
setup.bat
run.bat
README.md
LICENSE
```

## License

SmartDrop is released under the MIT License. See [LICENSE](LICENSE) for the full text.

## Author

**Ali Yiğit Turan**
