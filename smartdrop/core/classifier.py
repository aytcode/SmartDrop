from typing import Dict, List, Set, Optional
from pathlib import Path
from smartdrop.models.config import LANGUAGE_CATEGORY_NAMES


class FileClassifier:
    """
    Classifies files based on their extensions and custom mapping.
    Also handles unknown extensions cleanly by mapping them to 'Others'.
    Supports multiple languages (tr, en, de, es).
    """

    DEFAULT_EXTENSIONS: Dict[str, Set[str]] = {
        "Documents": {
            ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".tex", ".epub", ".pages", ".md"
        },
        "Images": {
            ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".tiff", ".tif", ".ico", ".heic", ".raw"
        },
        "Videos": {
            ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"
        },
        "Audio": {
            ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".alac", ".aiff"
        },
        "Archives": {
            ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".tgz"
        },
        "Code": {
            ".py", ".js", ".ts", ".html", ".css", ".json", ".java", ".cpp", ".c", ".h", ".hpp",
            ".cs", ".go", ".rs", ".php", ".rb", ".sh", ".bat", ".ps1", ".sql", ".yaml", ".yml",
            ".xml", ".vue", ".jsx", ".tsx"
        },
        "Spreadsheets": {
            ".xls", ".xlsx", ".csv", ".tsv", ".ods", ".numbers"
        },
        "Presentations": {
            ".ppt", ".pptx", ".odp", ".key"
        },
        "Installers": {
            ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".appx", ".apk"
        },
        "Fonts": {
            ".ttf", ".otf", ".woff", ".woff2", ".eot"
        }
    }

    def __init__(self, custom_folders: Optional[Dict[str, str]] = None, language: str = "en"):
        self.language = language
        lang_defaults = LANGUAGE_CATEGORY_NAMES.get(language, LANGUAGE_CATEGORY_NAMES.get("en", {}))
        self.category_folders: Dict[str, str] = dict(lang_defaults) if lang_defaults else {}
        if custom_folders:
            self.category_folders.update(custom_folders)

        # Pre-build extension to category lookup
        self._ext_lookup: Dict[str, str] = {}
        for category, ext_set in self.DEFAULT_EXTENSIONS.items():
            for ext in ext_set:
                self._ext_lookup[ext.lower()] = category

    def set_language(self, language: str):
        self.language = language
        lang_defaults = LANGUAGE_CATEGORY_NAMES.get(language, LANGUAGE_CATEGORY_NAMES.get("en", {}))
        self.category_folders = dict(lang_defaults)

    def classify(self, path: Path) -> str:
        """
        Classify file based on its suffix.
        Returns category name (e.g. 'Documents', 'Images', or 'Others').
        """
        ext = path.suffix.lower().strip()
        if not ext:
            return "Others"
        return self._ext_lookup.get(ext, "Others")

    def get_target_folder_name(self, category: str) -> str:
        """
        Returns folder name for category according to selected language or user customization.
        """
        return self.category_folders.get(category, category)

    @classmethod
    def get_all_categories(cls) -> List[str]:
        return list(cls.DEFAULT_EXTENSIONS.keys()) + ["Others"]
